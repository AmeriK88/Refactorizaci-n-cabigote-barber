from django.urls import path, reverse
from django.template.response import TemplateResponse
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.utils.html import format_html
from django import forms
from .models import ReporteMensual, ReporteDiario
from .utils import calcular_reporte, limpiar_reportes, calcular_reporte_diario

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
        fields = ['mes']  # Solo permitimos al usuario seleccionar el mes

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

    # 'mes' ya NO se define como readonly, porque queremos que el usuario lo seleccione.
    # Los demás campos calculados sí se mantienen en solo lectura.
    readonly_fields = (
        'total_citas',
        'ingresos_totales',
        'ingresos_proyectados',
        'creado_el'
    )

    def descargar_reporte_link(self, obj):
        """
        Devuelve un enlace (HTML) que permite descargar un archivo .txt con el reporte completo.
        Para el reverso de la URL, se utiliza el nombre definido en get_urls.
        """
        # Si tienes problemas con el reverse, podrías usar la fórmula:
        # url = reverse("admin:%s_%s_descargar_reporte" % (self.model._meta.app_label, self.model._meta.model_name))
        url = reverse('admin:descargar_reporte')
        return format_html('<a href="{}">Descargar</a>', url)
    descargar_reporte_link.short_description = _("Descargar Reporte")

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
        Vista personalizada para generar automáticamente (ejemplo) 5 meses de reportes 
        y mostrarlos en una plantilla. Se invoca desde el Admin.
        """
        limpiar_reportes()  # Elimina todos los reportes existentes
        # Genera 5 meses a partir del primer día del mes actual
        reports = calcular_reporte(now().date().replace(day=1))
        context = dict(
            self.admin_site.each_context(request),
            reportes=reports,
        )
        return TemplateResponse(request, "admin/custom_report.html", context)

    def descargar_reporte(self, request):
        """
        Genera un archivo de texto con la información de todos los ReporteMensual ordenados por fecha.
        """
        reports = ReporteMensual.objects.all().order_by('mes')
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="reporte_mensual.txt"'
        for report in reports:
            response.write(f"Mes: {report.mes.strftime('%B %Y')}\n")
            response.write(f"Total de Citas: {report.total_citas}\n")
            response.write(f"Ingresos Totales: {report.ingresos_totales}\n")
            response.write(f"Ingresos Proyectados: {report.ingresos_proyectados}\n")
            response.write("-" * 40 + "\n")
        return response

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
        Al guardar, se genera/actualiza el reporte mensual para el mes indicado.
        - Se fuerza el día a 1 para que el reporte se corresponda siempre con el primer día del mes.
        - Se llama a 'calcular_reporte' con 'meses_ahead=1' para calcular solo ese mes.
        """
        # Forzar el día a 1 en caso de que el usuario seleccione otro día del mes
        mes_inicial = obj.mes.replace(day=1)
        obj.mes = mes_inicial

        # Guarda inicialmente el objeto con los valores por defecto (evitando que queden campos en NULL)
        # Esto es necesario para que la BD no lance un error de integridad.
        obj.total_citas = obj.total_citas or 0
        obj.ingresos_totales = obj.ingresos_totales or 0
        obj.ingresos_proyectados = obj.ingresos_proyectados or 0
        super().save_model(request, obj, form, change)

        # Llamamos a la función que calcula el reporte para el mes indicado.
        calcular_reporte(mes_inicial, meses_ahead=1)

        # Actualizamos el objeto con los nuevos datos calculados
        obj.refresh_from_db()

        self.message_user(
            request, 
            f"✅ Reporte mensual generado/actualizado para {mes_inicial.strftime('%B %Y')}"
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
    Formulario para ReporteDiario que sólo edita el campo 'dia'.
    Los demás campos se calculan automáticamente.
    """
    class Meta:
        model = ReporteDiario
        fields = ['dia']
        widgets = {
            'dia': forms.DateInput(attrs={'type': 'date'})
        }

# ------------------------------------------------------------------------------
# Admin para ReporteDiario
# ------------------------------------------------------------------------------
@admin.register(ReporteDiario)
class ReporteDiarioAdmin(admin.ModelAdmin):
    list_display = ('dia', 'total_citas', 'ingresos_totales', 'creado_el')
    readonly_fields = ('total_citas', 'ingresos_totales', 'creado_el')  # Solo se edita la fecha

    def has_add_permission(self, request):
        return True  # Permitir añadir reportes manualmente

    def has_delete_permission(self, request, obj=None):
        return True  # Permitir eliminar reportes

    def save_model(self, request, obj, form, change):
        """
        Al guardar, generar el reporte automáticamente.
        """
        from .utils import calcular_reporte_diario
        calcular_reporte_diario(obj.dia)  # Generar el reporte con la fecha seleccionada
        self.message_user(request, f"✅ Reporte generado para el día {obj.dia.strftime('%d/%m/%Y')}")

# ------------------------------------------------------------------------------
# Metadata del archivo
# ------------------------------------------------------------------------------
# Autor: José Félix Gordo Castaño
# Copyright (C) 2024 José Félix Gordo Castaño
# Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje.
# No se permite la venta ni el uso comercial sin autorización expresa del autor.
