from django.shortcuts import render
from .models import ReporteMensual
from appointments.models import Cita
from django.utils.timezone import now
from django.db.models import Sum
from datetime import timedelta
from django.template.response import TemplateResponse


def custom_report_view(self, request):
    current_month = now().date().replace(day=1)

    reports = []
    # Generar reporte para el mes actual y los dos siguientes
    for i in range(3):  
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

