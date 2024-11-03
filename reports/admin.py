from django.urls import path
from django.template.response import TemplateResponse
from .models import ReporteMensual
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from appointments.models import Cita
from django.db.models import Sum
from datetime import timedelta

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
        current_month = now().date().replace(day=1)

        reports = []
        for i in range(3):  # Mes actual y dos meses siguientes
            month = (current_month + timedelta(days=30 * i)).replace(day=1)
            next_month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)

            # Filtrar las citas del mes actual
            citas = Cita.objects.filter(fecha__gte=month, fecha__lt=next_month)
            total_citas = citas.count()
            total_ingresos = citas.aggregate(Sum('servicio__precio'))['servicio__precio__sum'] or 0
            ingresos_proyectados = citas.aggregate(Sum('servicio__precio'))['servicio__precio__sum'] or 0

            # Actualizar o crear el reporte mensual
            report, created = ReporteMensual.objects.update_or_create(
                mes=month,
                defaults={
                    'total_citas': total_citas,
                    'ingresos_totales': total_ingresos,
                    'ingresos_proyectados': ingresos_proyectados,
                }
            )
            reports.append(report)

        context = dict(
            self.admin_site.each_context(request),
            reportes=reports,
        )
        return TemplateResponse(request, "admin/custom_report.html", context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
