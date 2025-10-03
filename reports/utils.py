from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

from django.db.models import F, Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.utils.timezone import make_aware, now, get_current_timezone

from .models import ReporteMensual, ReporteDiario
from appointments.models import Cita

logger = logging.getLogger(__name__)
TZ = get_current_timezone()

# ---------- MENSUAL -------------------------------------------------
def calcular_reporte(mes_actual, meses_ahead: int = 1):
    """
    Crea/actualiza ReporteMensual para `mes_actual` (date) y los N meses siguientes.
    Solo LEE Cita; no las modifica.
    """
    # forzamos día 1 por si llega un date con otro día
    mes_base = mes_actual.replace(day=1)
    reports = []

    for i in range(meses_ahead):
        inicio_mes = mes_base + relativedelta(months=i)
        fin_mes    = inicio_mes + relativedelta(months=1)

        inicio_aware = make_aware(datetime.combine(inicio_mes, datetime.min.time()), TZ)
        fin_aware    = make_aware(datetime.combine(fin_mes,   datetime.min.time()), TZ)

        # Evitar N+1 al calcular precios
        citas = (
            Cita.objects
            .filter(fecha__gte=inicio_aware, fecha__lt=fin_aware)
            .select_related("servicio", "producto")
        )

        total_citas = citas.count()
        total_ingresos = (
            citas.annotate(
                precio_total=F("servicio__precio")
                + Coalesce(F("producto__precio"), Value(0), output_field=DecimalField())
            )
            .aggregate(total=Coalesce(Sum("precio_total"), Value(0), output_field=DecimalField()))["total"]
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

    logger.info("Reporte mensual actualizado desde %s por %s meses (count=%d)",
                mes_base.isoformat(), meses_ahead, len(reports))
    return reports

# ---------- DIARIO --------------------------------------------------
def calcular_reporte_diario(fecha):
    """
    Genera/actualiza un ReporteDiario para `fecha` (date).
    """
    inicio = make_aware(datetime.combine(fecha, datetime.min.time()), TZ)
    fin    = inicio + timedelta(days=1)

    citas = (
        Cita.objects
        .filter(fecha__gte=inicio, fecha__lt=fin)
        .select_related("servicio", "producto")
    )

    total_citas = citas.count()
    total_ingresos = (
        citas.annotate(
            precio_total=F("servicio__precio")
            + Coalesce(F("producto__precio"), Value(0), output_field=DecimalField())
        )
        .aggregate(total=Coalesce(Sum("precio_total"), Value(0), output_field=DecimalField()))["total"]
    )

    ReporteDiario.objects.update_or_create(
        dia=fecha,
        defaults={
            "total_citas": total_citas,
            "ingresos_totales": total_ingresos,
        },
    )
    logger.info("Reporte diario actualizado para %s (citas=%d)", fecha.isoformat(), total_citas)

# ---------- SOLO ADMIN: LIMPIAR Y REGENERAR -------------------------
def limpiar_reportes_admin(mes_actual=None, meses_ahead: int = 1):
    """
    SOLO uso manual desde Admin. Borra TODOS los ReporteMensual y regenera.
    No toca Cita.
    """
    if mes_actual is None:
        mes_actual = now().date().replace(day=1)

    borrados, _ = ReporteMensual.objects.all().delete()
    logger.warning("Admin request: todos los reportes mensuales eliminados (count=%d).", borrados)

    return calcular_reporte(mes_actual, meses_ahead)
