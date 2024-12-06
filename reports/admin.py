from django.urls import path, reverse
from django.template.response import TemplateResponse
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from .models import ReporteMensual
from .utils import calcular_reporte, limpiar_reportes
from django.utils.html import format_html

@admin.register(ReporteMensual)
class ReporteMensualAdmin(admin.ModelAdmin):
    list_display = ('mes', 'total_citas', 'ingresos_totales', 'ingresos_proyectados', 'descargar_reporte_link')
    readonly_fields = ('mes', 'total_citas', 'ingresos_totales', 'ingresos_proyectados', 'creado_el')

    # Enlace de descarga en la lista de reportes
    def descargar_reporte_link(self, obj):
        url = reverse('admin:descargar_reporte')
        return format_html('<a href="{}">Descargar</a>', url)

    descargar_reporte_link.short_description = _("Descargar Reporte")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reporte-personalizado/', self.admin_site.admin_view(self.custom_report_view), name='reporte_personalizado'),
            path('descargar-reporte/', self.admin_site.admin_view(self.descargar_reporte), name='descargar_reporte'),
        ]
        return custom_urls + urls

    def custom_report_view(self, request):
        limpiar_reportes()
        reports = calcular_reporte(now().date().replace(day=1))
        context = dict(
            self.admin_site.each_context(request),
            reportes=reports,
        )
        return TemplateResponse(request, "admin/custom_report.html", context)

    def descargar_reporte(self, request):
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
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


   
