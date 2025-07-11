# reports/utils.py
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import F, Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.utils.timezone import make_aware, now, get_current_timezone

from .models import ReporteMensual, ReporteDiario
from appointments.models import Cita

# evita llamadas repetidas
TZ = get_current_timezone()


# ---------- MENSUAL -------------------------------------------------
def calcular_reporte(mes_actual, meses_ahead: int = 1):
    """
    Crea / actualiza ReporteMensual para `mes_actual` y los N meses siguientes.
    Solo LEE citas; no las modifica.
    """
    reports = []

    for i in range(meses_ahead):
        inicio_mes = mes_actual + relativedelta(months=i)
        fin_mes    = inicio_mes + relativedelta(months=1)

        inicio_aware = make_aware(datetime.combine(inicio_mes,  datetime.min.time()), TZ)
        fin_aware    = make_aware(datetime.combine(fin_mes,    datetime.min.time()), TZ)

        citas = Cita.objects.filter(fecha__gte=inicio_aware, fecha__lt=fin_aware)

        total_citas = citas.count()
        total_ingresos = (
            citas.annotate(
                precio_total=F("servicio__precio")
                + Coalesce(F("producto__precio"), Value(0), output_field=DecimalField())
            )
            .aggregate(Sum("precio_total"))["precio_total__sum"]
            or 0
        )

        report, _ = ReporteMensual.objects.update_or_create(
            mes=inicio_aware.date(),               
            defaults={
                "total_citas": total_citas,
                "ingresos_totales": total_ingresos,
                "ingresos_proyectados": total_ingresos,
            },
        )
        reports.append(report)

    return reports


# ---------- DIARIO --------------------------------------------------
def calcular_reporte_diario(fecha):
    """
    Genera (o actualiza) un ReporteDiario para `fecha`.
    """
    inicio = make_aware(datetime.combine(fecha, datetime.min.time()), TZ)
    fin    = inicio + timedelta(days=1)

    citas = Cita.objects.filter(fecha__gte=inicio, fecha__lt=fin)

    total_citas = citas.count()
    total_ingresos = (
        citas.annotate(
            precio_total=F("servicio__precio")
            + Coalesce(F("producto__precio"), Value(0), output_field=DecimalField())
        )
        .aggregate(Sum("precio_total"))["precio_total__sum"]
        or 0
    )

    ReporteDiario.objects.update_or_create(
        dia=fecha,
        defaults={
            "total_citas": total_citas,
            "ingresos_totales": total_ingresos,
        },
    )
    print(f"✅ Reporte diario generado para {fecha:%d/%m/%Y}")


# ---------- LIMPIAR Y REGENERAR -------------------------------------
def limpiar_reportes(mes_actual=None, meses_ahead: int = 1):
    """
    Borra todos los ReporteMensual y los regenera a partir de las citas.
    *No* toca objetos Cita, así evitamos datetimes naïve.
    """
    if mes_actual is None:
        mes_actual = now().date().replace(day=1)

    ReporteMensual.objects.all().delete()
    print("Todos los reportes eliminados.")

    calcular_reporte(mes_actual, meses_ahead)
