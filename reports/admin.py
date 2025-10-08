from django.urls import path, reverse
from django.template.response import TemplateResponse
from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.utils.html import format_html
from django import forms
from .models import ReporteMensual, ReporteDiario
from .utils import calcular_reporte, calcular_reporte_diario

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
        url = reverse('admin:descargar_reporte') + '?force=1'
        return format_html(
            '<a class="button btn-admin-action" href="{}" download>📥 Descargar</a>',
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

    def custom_report_view(self, request):
        """
        Genera/actualiza 5 meses a partir del primero del mes actual (SIN borrar).
        """
        base = now().date().replace(day=1)
        reports = calcular_reporte(base, meses_ahead=5)
        context = dict(self.admin_site.each_context(request), reportes=reports)
        return TemplateResponse(request, "admin/custom_report.html", context)


    def descargar_reporte(self, request):
        """
        Genera/actualiza reportes antes de descargar.
        - ?force=1  -> recalcula TODOS los meses existentes + mes actual
        - ?months=N -> recalcula N meses desde el mes actual (incluido)
        - sin params -> asegura el mes actual (crea si no existe)
        """
        force = request.GET.get("force") == "1"
        months_param = request.GET.get("months")
        hoy = now().date()
        mes_actual = hoy.replace(day=1)

        def add_month(d, n):
            y, m = d.year, d.month + n
            y += (m - 1) // 12
            m = ((m - 1) % 12) + 1
            return d.replace(year=y, month=m, day=1)

        qs = ReporteMensual.objects.all().order_by("mes")
        existe_algo = qs.exists()

        if months_param:
            # Recalcula un rango explícito N meses desde el actual
            try:
                n = max(1, int(months_param))
            except ValueError:
                n = 1
            calcular_reporte(mes_actual, meses_ahead=n)

        elif force and existe_algo:
            # Recalcula cada mes ya presente en BD y garantiza el actual
            meses_db = list(qs.values_list("mes", flat=True))
            for m in meses_db:
                calcular_reporte(m.replace(day=1), meses_ahead=1)
            if mes_actual not in meses_db:
                calcular_reporte(mes_actual, meses_ahead=1)

        else:
            # Modo normal: asegura el mes actual; si no hay nada en BD, crea al menos éste
            if not qs.filter(mes=mes_actual).exists():
                calcular_reporte(mes_actual, meses_ahead=1)

        # Refresca y compone el TXT
        reports = ReporteMensual.objects.all().order_by("mes")
        resp = HttpResponse(content_type="text/plain; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="reporte_mensual_{now().date():%Y_%m_%d}.txt"'
        if not reports.exists():
            resp.write("Sin datos de ReporteMensual.\n")
            return resp

        for report in reports:
            resp.write(f"Mes: {report.mes.strftime('%B %Y')}\n")
            resp.write(f"Total de Citas: {report.total_citas}\n")
            resp.write(f"Ingresos Totales: {report.ingresos_totales}\n")
            resp.write(f"Ingresos Proyectados: {report.ingresos_proyectados}\n")
            resp.write("-" * 40 + "\n")
        return resp


    def has_add_permission(self, request):
        """
        Permitir crear nuevos reportes mensuales manualmente.
        """
        return True

    def has_delete_permission(self, request, obj=None):
        """
        Permitir eliminar reportes mensuales manualmente.
        """
        return True

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

    def has_add_permission(self, request):
        return True  # Permitir añadir reportes manualmente

    def has_delete_permission(self, request, obj=None):
        return True  # Permitir eliminar reportes

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
