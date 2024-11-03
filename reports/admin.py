from django.urls import path
from django.template.response import TemplateResponse
from .models import ReporteMensual
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

@admin.register(ReporteMensual)
class ReporteMensualAdmin(admin.ModelAdmin):
    list_display = ('mes', 'total_citas', 'ingresos_totales', 'ingresos_proyectados')
    readonly_fields = ('mes', 'total_citas', 'ingresos_totales', 'ingresos_proyectados', 'creado_el')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reporte-personalizado/', self.admin_site.admin_view(self.custom_report_view), name='reporte_personalizado'),
        ]
        return custom_urls + urls

    def custom_report_view(self, request):
        reporte = ReporteMensual.objects.last() 
        context = dict(
            self.admin_site.each_context(request),
            reporte=reporte,
        )
        return TemplateResponse(request, "admin/custom_report.html", context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
