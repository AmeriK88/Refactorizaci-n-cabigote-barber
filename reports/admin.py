from django.urls import path, reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.utils.html import format_html
from django import forms
from dateutil.relativedelta import relativedelta
from .models import ReporteMensual, ReporteDiario
from .utils import calcular_reporte, calcular_reporte_diario, totales_mes

DEFAULT_MONTHS = 5
MAX_MONTHS = 24


def _parse_months(raw, default=None):
    """Devuelve un entero 1..MAX_MONTHS, `default` si falta, o None si es inválido."""
    if raw in (None, ""):
        return default
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return None
    return n if 1 <= n <= MAX_MONTHS else None

# ------------------------------------------------------------------------------
# Formulario personalizado para ReporteMensual
# ------------------------------------------------------------------------------
class ReporteMensualForm(forms.ModelForm):
    """
    Formulario para ReporteMensual que solo incluye el campo 'mes'.
    De esta forma, se evita que campos como 'ingresos_totales', 'total_citas'
    reciban valores None, pues se calcularán automáticamente.
    """
    class Meta:
        model = ReporteMensual
        fields = ['mes']  

# ------------------------------------------------------------------------------
# Admin para ReporteMensual
# ------------------------------------------------------------------------------
@admin.register(ReporteMensual)
class ReporteMensualAdmin(admin.ModelAdmin):
    """
    Admin para gestionar los reportes mensuales.
    Se ha modificado para permitir la creación manual de reportes (solo se edita el mes)
    y para generar/actualizar los datos automáticamente en 'save_model'.
    """
    # Se asocia nuestro formulario personalizado para evitar que se envíen nulos
    form = ReporteMensualForm

    list_display = (
        'mes',
        'total_citas',
        'ingresos_totales',
        'ingresos_proyectados',
        'descargar_reporte_link'
    )

    readonly_fields = (
        'total_citas',
        'ingresos_totales',
        'ingresos_proyectados',
        'creado_el'
    )

    def descargar_reporte_link(self, obj):
        url = reverse('admin:descargar_reporte')
        return format_html(
            '<a class="btn-admin-action" href="{}" download>📥 Descargar</a>',
            url
        )
    descargar_reporte_link.short_description = _("Descargar")

    def get_urls(self):
        """
        Inserta dos URLs personalizadas:
        - 'reporte-personalizado/': invoca la vista custom_report_view para generar 5 meses de reportes.
        - 'descargar-reporte/': invoca la vista descargar_reporte para obtener un archivo con todos los reportes.
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                'reporte-personalizado/', 
                self.admin_site.admin_view(self.custom_report_view), 
                name='reporte_personalizado'
            ),
            path(
                'descargar-reporte/', 
                self.admin_site.admin_view(self.descargar_reporte), 
                name='descargar_reporte'
            ),
        ]
        return custom_urls + urls

    def _can_generate(self, request):
        return self.has_add_permission(request) and self.has_change_permission(request)

    def custom_report_view(self, request):
        """
        GET: muestra los informes ya guardados (solo lectura, permiso de consulta).
        POST: genera/actualiza y guarda N meses (permiso de alta y modificación, CSRF).
        """
        if not self.has_view_permission(request):
            raise PermissionDenied
        if request.method not in ("GET", "HEAD", "POST"):
            return HttpResponseNotAllowed(["GET", "HEAD", "POST"])

        base = now().date().replace(day=1)

        if request.method == "POST":
            if not self._can_generate(request):
                raise PermissionDenied
            months = _parse_months(request.POST.get("months"), default=DEFAULT_MONTHS)
            if months is None:
                return HttpResponseBadRequest("Invalid 'months' parameter.")
            calcular_reporte(base, meses_ahead=months)
            self.message_user(request, _("Reports generated for %(n)s month(s).") % {"n": months})
            return redirect(request.path)

        fin = base + relativedelta(months=DEFAULT_MONTHS)
        reports = ReporteMensual.objects.filter(mes__gte=base, mes__lt=fin).order_by("mes")
        context = dict(
            self.admin_site.each_context(request),
            reportes=reports,
            can_generate=self._can_generate(request),
            default_months=DEFAULT_MONTHS,
        )
        return TemplateResponse(request, "admin/custom_report.html", context)

    def descargar_reporte(self, request):
        """
        Descarga de solo lectura (GET/HEAD): calcula los totales al vuelo y NO escribe en la BD.
        - Meses incluidos: los guardados + el actual.
        - ?months=N (1..MAX_MONTHS) -> N meses desde el actual en lugar de los guardados.
        Guardar informes se hace con POST en 'reporte-personalizado/'.
        """
        if not self.has_view_permission(request):
            raise PermissionDenied
        if request.method not in ("GET", "HEAD"):
            return HttpResponseNotAllowed(["GET", "HEAD"])

        mes_actual = now().date().replace(day=1)
        months_param = request.GET.get("months")
        if months_param:
            n = _parse_months(months_param)
            if n is None:
                return HttpResponseBadRequest("Invalid 'months' parameter.")
            meses = [mes_actual + relativedelta(months=i) for i in range(n)]
        else:
            meses = set(ReporteMensual.objects.values_list("mes", flat=True))
            meses.add(mes_actual)
            meses = sorted(m.replace(day=1) for m in meses)

        resp = HttpResponse(content_type="text/plain; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="reporte_mensual_{now().date():%Y_%m_%d}.txt"'
        for mes in meses:
            total_citas, ingresos = totales_mes(mes)
            resp.write(f"Mes: {mes.strftime('%B %Y')}\n")
            resp.write(f"Total de Citas: {total_citas}\n")
            resp.write(f"Ingresos Totales: {ingresos}\n")
            resp.write(f"Ingresos Proyectados: {ingresos}\n")
            resp.write("-" * 40 + "\n")
        return resp

    def save_model(self, request, obj, form, change):
        """
        Genera/actualiza el reporte del mes indicado SIN insertar manualmente
        para no violar la unicidad. No llamamos a super().save_model().
        """
        # Normaliza al día 1
        mes_inicial = obj.mes.replace(day=1)

        # ¿Ya existía?
        existed = ReporteMensual.objects.filter(mes=mes_inicial).exists()

        # Genera/actualiza vía util (idempotente)
        calcular_reporte(mes_inicial, meses_ahead=1)

        # Mensaje amigable
        if existed:
            self.message_user(
                request,
                f"♻️ Reporte mensual ACTUALIZADO para {mes_inicial.strftime('%B %Y')}"
            )
        else:
            self.message_user(
                request,
                f"✅ Reporte mensual CREADO para {mes_inicial.strftime('%B %Y')}"
            )

# ------------------------------------------------------------------------------
# Formularios para uso en vistas custom (opcional)
# ------------------------------------------------------------------------------
class FechaReporteForm(forms.Form):
    """
    Formulario simple para seleccionar una fecha.
    """
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Selecciona una fecha"
    )


class ReporteDiarioForm(forms.ModelForm):
    """
    Form del Admin para ReporteDiario:
    - Desactiva la validación de unicidad del ModelForm (_validate_unique = False)
      para que el POST no se bloquee cuando ya exista el día.
    - El guardado real lo hace save_model() de forma idempotente.
    """
    class Meta:
        model = ReporteDiario
        fields = ['dia']
        widgets = {
            'dia': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Clave: evitar que el ModelForm invoque instance.validate_unique()
        self._validate_unique = False

    def clean_dia(self):
        d = self.cleaned_data['dia']
        return d


# ------------------------------------------------------------------------------
# Admin para ReporteDiario
# ------------------------------------------------------------------------------
@admin.register(ReporteDiario)
class ReporteDiarioAdmin(admin.ModelAdmin):
    form = ReporteDiarioForm
    list_display = ('dia', 'total_citas', 'ingresos_totales', 'creado_el')
    readonly_fields = ('total_citas', 'ingresos_totales', 'creado_el')  # Solo se edita la fecha

    def save_model(self, request, obj, form, change):
        """
        Genera/actualiza el reporte diario SIN insertar manualmente (no llamamos a super()).
        De este modo, si ya existe, se actualiza; si no, se crea.
        """
        dia = form.cleaned_data['dia']  # usa el valor limpio del form
        existed = ReporteDiario.objects.filter(dia=dia).exists()

        # Idempotente: crea o actualiza
        calcular_reporte_diario(dia)

        # Mensaje al admin
        if existed:
            self.message_user(request, f"♻️ Reporte diario ACTUALIZADO para {dia:%d/%m/%Y}")
        else:
            self.message_user(request, f"✅ Reporte diario CREADO para {dia:%d/%m/%Y}")
        # Ojo: no llamamos a super().save_model() para no intentar un INSERT que viole unicidad.

# ------------------------------------------------------------------------------
# Metadata del archivo
# ------------------------------------------------------------------------------
# Autor: José Félix Gordo Castaño
# Copyright (C) 2024 José Félix Gordo Castaño
# Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje.
# No se permite la venta ni el uso comercial sin autorización expresa del autor.
