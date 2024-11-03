from django.shortcuts import render
from .models import ReporteMensual
from appointments.models import Cita
from django.utils.timezone import now
from django.db.models import Sum
from datetime import timedelta

def generate_monthly_report(request):
    current_month = now().date().replace(day=1)
    next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)

    # Filtrar las citas del mes actual
    citas = Cita.objects.filter(fecha__gte=current_month, fecha__lt=next_month)

    # Calcular estadísticas
    total_citas = citas.count()
    total_ingresos = citas.aggregate(Sum('servicio__precio'))['servicio__precio__sum'] or 0
    ingresos_proyectados = citas.aggregate(Sum('servicio__precio'))['servicio__precio__sum'] or 0

    # Actualizar o crear el reporte mensual
    report, created = ReporteMensual.objects.update_or_create(
        mes=current_month,
        defaults={
            'total_citas': total_citas,
            'ingresos_totales': total_ingresos,
            'ingresos_proyectados': ingresos_proyectados,
        }
    )

    return render(request, 'reports/report.html', {'reporte': report})

