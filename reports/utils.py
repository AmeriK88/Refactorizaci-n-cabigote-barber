from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta
from django.db.models import Sum
from .models import ReporteMensual
from appointments.models import Cita

def calcular_reporte(mes_actual, meses_ahead=4):
    reports = []
    for i in range(meses_ahead):
        mes = (mes_actual + timedelta(days=30 * i)).replace(day=1)
        siguiente_mes = (mes.replace(day=28) + timedelta(days=4)).replace(day=1)

        # Asegurarse de que las fechas son "aware"
        mes = make_aware(datetime.combine(mes, datetime.min.time()))
        siguiente_mes = make_aware(datetime.combine(siguiente_mes, datetime.min.time()))

        citas = Cita.objects.filter(fecha__gte=mes, fecha__lt=siguiente_mes)
        total_citas = citas.count()
        total_ingresos = citas.aggregate(Sum('servicio__precio'))['servicio__precio__sum'] or 0

        report, created = ReporteMensual.objects.update_or_create(
            mes=mes,
            defaults={
                'total_citas': total_citas,
                'ingresos_totales': total_ingresos,
                'ingresos_proyectados': total_ingresos,
            }
        )
        reports.append(report)
    return reports

def limpiar_reportes():
    mes_actual = now().date().replace(day=1)
    for i in range(4):
        mes = (mes_actual + timedelta(days=30 * i)).replace(day=1)
        siguiente_mes = (mes.replace(day=28) + timedelta(days=4)).replace(day=1)

        # Asegurarse de que las fechas son "aware"
        mes = make_aware(datetime.combine(mes, datetime.min.time()))
        siguiente_mes = make_aware(datetime.combine(siguiente_mes, datetime.min.time()))

        citas = Cita.objects.filter(fecha__gte=mes, fecha__lt=siguiente_mes)

        if not citas.exists():
            ReporteMensual.objects.filter(mes=mes).delete()
            print(f"Reporte para {mes.strftime('%B %Y')} eliminado.")
        else:
            print(f"Reporte para {mes.strftime('%B %Y')} no se elimina porque tiene citas.")
