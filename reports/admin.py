from django.urls import path
from django.template.response import TemplateResponse
from .models import ReporteMensual
from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from .utils import calcular_reporte, limpiar_reportes
from django.utils.timezone import now

@admin.register(ReporteMensual)
class ReporteMensualAdmin(admin.ModelAdmin):
    list_display = ('mes', 'total_citas', 'ingresos_totales', 'ingresos_proyectados')
    readonly_fields = ('mes', 'total_citas', 'ingresos_totales', 'ingresos_proyectados', 'creado_el')

    # Define la acción personalizada
    actions = ['eliminar_reportes_seleccionados']

    # Función para eliminar reportes seleccionados
    def eliminar_reportes_seleccionados(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} reportes eliminados.", messages.SUCCESS)

    eliminar_reportes_seleccionados.short_description = _("Eliminar reportes seleccionados")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reporte-personalizado/', self.admin_site.admin_view(self.custom_report_view), name='reporte_personalizado'),
        ]
        return custom_urls + urls

    def custom_report_view(self, request):
         # Limpia los reportes sin citas antes de recalcular
        limpiar_reportes() 
        reports = calcular_reporte(now().date().replace(day=1))
        context = dict(
            self.admin_site.each_context(request),
            reportes=reports,
        )
        return TemplateResponse(request, "admin/custom_report.html", context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
