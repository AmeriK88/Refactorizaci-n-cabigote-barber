from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .models import ReporteMensual
from .models import ReporteDiario
from appointments.models import Cita
from django.db.models import F, Sum, Value, DecimalField
from django.db.models.functions import Coalesce


def calcular_reporte(mes_actual, meses_ahead=1):
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
            precio_total=F('servicio__precio') + Coalesce(F('producto__precio'), Value(0), output_field=DecimalField())
        ).aggregate(Sum('precio_total'))['precio_total__sum'] or 0

        # Crear o actualizar el reporte
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

def calcular_reporte_diario(fecha):
    """
    Genera el reporte diario solo para la fecha especificada.
    """
    fecha_inicio = make_aware(datetime.combine(fecha, datetime.min.time()))
    fecha_fin = fecha_inicio + timedelta(days=1)

    citas = Cita.objects.filter(fecha__gte=fecha_inicio, fecha__lt=fecha_fin)

    total_citas = citas.count()
    total_ingresos = citas.annotate(
        precio_total=F('servicio__precio') + Coalesce(F('producto__precio'), Value(0), output_field=DecimalField())
    ).aggregate(Sum('precio_total'))['precio_total__sum'] or 0

    ReporteDiario.objects.update_or_create(
        dia=fecha,
        defaults={
            'total_citas': total_citas,
            'ingresos_totales': total_ingresos,
        }
    )
    print(f"✅ Reporte diario generado para {fecha.strftime('%d/%m/%Y')}")


def limpiar_reportes(mes_actual=None, meses_ahead=1):
    # Si no se pasa `mes_actual`, usar el primer día del mes actual
    if mes_actual is None:
        mes_actual = now().date().replace(day=1)

    # Eliminar todos los reportes existentes
    ReporteMensual.objects.all().delete()
    print("Todos los reportes eliminados.")

    # Recalcular los reportes
    for i in range(meses_ahead):
        # Calcular el mes actual y el siguiente mes
        mes = mes_actual + relativedelta(months=i)
        siguiente_mes = mes + relativedelta(months=1)

        # Asegurar que las fechas sean "aware"
        mes = make_aware(datetime.combine(mes, datetime.min.time()))
        siguiente_mes = make_aware(datetime.combine(siguiente_mes, datetime.min.time()))

        # Obtener citas en el rango de fechas
        citas = Cita.objects.filter(fecha__gte=mes, fecha__lt=siguiente_mes)

        # Calcular total de citas
        total_citas = citas.count()

        # Sumar ingresos totales (servicios + productos)
        total_ingresos = citas.annotate(
            precio_total=F('servicio__precio') + F('producto__precio')
        ).aggregate(Sum('precio_total'))['precio_total__sum'] or 0

        # Crear reporte mensual
        ReporteMensual.objects.create(
            mes=mes,
            total_citas=total_citas,
            ingresos_totales=total_ingresos,
            ingresos_proyectados=total_ingresos, 
        )
        print(f"Reporte para {mes.strftime('%B %Y')} creado: {total_citas} citas, {total_ingresos:.2f} ingresos totales.")

