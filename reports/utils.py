from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from .models import ReporteMensual
from appointments.models import Cita

def calcular_reporte(mes_actual, meses_ahead=5):
    from django.db.models import F, Sum
    reports = []

    for i in range(meses_ahead):
        # Calcular el mes actual y el siguiente mes correctamente
        mes = mes_actual + relativedelta(months=i)
        siguiente_mes = mes + relativedelta(months=1)

        # Asegurarse de que las fechas son "aware"
        mes = make_aware(datetime.combine(mes, datetime.min.time()))
        siguiente_mes = make_aware(datetime.combine(siguiente_mes, datetime.min.time()))

        # Obtener citas en el rango de fechas
        citas = Cita.objects.filter(fecha__gte=mes, fecha__lt=siguiente_mes)

        # Calcular total de citas
        total_citas = citas.count()

        # Sumar ingresos totales: servicios + productos
        total_ingresos = citas.annotate(
            # Sumar el precio del producto si está seleccionado
            precio_total=F('servicio__precio') + F('producto__precio')
        ).aggregate(Sum('precio_total'))['precio_total__sum'] or 0

        # Crear o actualizar el reporte
        report, created = ReporteMensual.objects.update_or_create(
            mes=mes,
            defaults={
                'total_citas': total_citas,
                'ingresos_totales': total_ingresos,
                'ingresos_proyectados': total_ingresos,  # Igualamos proyectados a los totales
            }
        )
        reports.append(report)

    return reports


def limpiar_reportes():
    mes_actual = now().date().replace(day=1)
    for i in range(5):
        # Usar relativedelta para avanzar correctamente de mes
        mes = mes_actual + relativedelta(months=i)
        siguiente_mes = mes + relativedelta(months=1)

        # Asegurarse de que las fechas son "aware"
        mes = make_aware(datetime.combine(mes, datetime.min.time()))
        siguiente_mes = make_aware(datetime.combine(siguiente_mes, datetime.min.time()))

        citas = Cita.objects.filter(fecha__gte=mes, fecha__lt=siguiente_mes)

        if not citas.exists():
            ReporteMensual.objects.filter(mes=mes).delete()
            print(f"Reporte para {mes.strftime('%B %Y')} eliminado.")
        else:
            print(f"Reporte para {mes.strftime('%B %Y')} no se elimina porque tiene citas.")
