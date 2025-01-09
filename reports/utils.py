from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .models import ReporteMensual
from .models import ReporteDiario
from appointments.models import Cita
from django.db.models import F, Sum, Value, DecimalField
from django.db.models.functions import Coalesce


def calcular_reporte(mes_actual, meses_ahead=5):
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
                'ingresos_proyectados': total_ingresos,  # Igualamos proyectados a los totales
            }
        )
        reports.append(report)

    return reports

def calcular_reporte_diario():
    # Obtener la fecha más temprana y más tardía con citas
    try:
        primera_fecha = make_aware(datetime.combine(Cita.objects.earliest('fecha').fecha, datetime.min.time()))
        ultima_fecha = make_aware(datetime.combine(Cita.objects.latest('fecha').fecha, datetime.min.time()))
    except Cita.DoesNotExist:
        print("No hay citas disponibles para calcular los reportes diarios.")
        return

    # Iterar desde la primera fecha hasta la última
    current_date = primera_fecha
    while current_date <= ultima_fecha:
        siguiente_dia = current_date + timedelta(days=1)

        citas = Cita.objects.filter(fecha__gte=current_date, fecha__lt=siguiente_dia)

        total_citas = citas.count()
        total_ingresos = citas.annotate(
            precio_total=F('servicio__precio') + Coalesce(F('producto__precio'), Value(0), output_field=DecimalField())
        ).aggregate(Sum('precio_total'))['precio_total__sum'] or 0

        ReporteDiario.objects.update_or_create(
            dia=current_date.date(),
            defaults={
                'total_citas': total_citas,
                'ingresos_totales': total_ingresos,
            }
        )

        current_date = siguiente_dia


def limpiar_reportes_diarios(num_dias=30):
    """
    Elimina los reportes diarios sin citas en los últimos 'num_dias'.
    Por ejemplo, si num_dias=7, revisará 7 días hacia atrás.
    """
    from django.utils.timezone import now

    fecha_hoy = now().date()
    for i in range(num_dias):
        dia = fecha_hoy - timedelta(days=i)

        # Filtrar el rango del día "aware"
        dia_inicio = make_aware(datetime.combine(dia, datetime.min.time()))
        dia_fin = dia_inicio + timedelta(days=1)

        citas_en_el_dia = Cita.objects.filter(fecha__gte=dia_inicio, fecha__lt=dia_fin)

        if not citas_en_el_dia.exists():
            ReporteDiario.objects.filter(dia=dia).delete()
            print(f"Reporte diario para {dia.strftime('%d/%m/%Y')} eliminado.")


def limpiar_reportes(mes_actual=None, meses_ahead=5):
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
            ingresos_proyectados=total_ingresos,  # Igualamos proyectados a los totales
        )
        print(f"Reporte para {mes.strftime('%B %Y')} creado: {total_citas} citas, {total_ingresos:.2f} ingresos totales.")

