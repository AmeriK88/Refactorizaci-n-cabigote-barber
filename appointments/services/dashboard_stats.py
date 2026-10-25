"""
Consultas de solo lectura para el dashboard administrativo.

Los permisos NO se comprueban aquí: el llamador debe verificar el permiso de
consulta de `Cita` antes de invocar estas funciones.

Semántica de `Cita.fecha` y `Cita.hora`
---------------------------------------
`fecha` (DateTimeField con zona horaria) es la fuente de verdad: la usan el
cálculo de solapamientos, el .ics, la cancelación, `dias_restantes`, los filtros
Hoy/Mañana/Año y los informes. `hora` (TimeField) es un dato redundante que solo
se muestra y se usa para listar horas ocupadas. Los flujos públicos las
escriben siempre coherentes (`normalize_booking_datetime`), pero el formulario
del admin permite editarlas por separado, de modo que pueden contradecirse.
Por eso aquí se filtra y se ordena únicamente por `fecha`.
"""
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from appointments.models import Cita

ZERO = Value(Decimal("0.00"), output_field=DecimalField(max_digits=12, decimal_places=2))
ESTIMATED_VALUE = ExpressionWrapper(
    F("servicio__precio") + Coalesce(F("producto__precio"), ZERO),
    output_field=DecimalField(max_digits=12, decimal_places=2),
)


def _aware_midnight(day, tz):
    return timezone.make_aware(datetime.combine(day, time.min), tz)


def local_day_bounds(day=None):
    """[inicio, fin) del día natural local indicado (por defecto, hoy)."""
    tz = timezone.get_current_timezone()
    day = day or timezone.localdate()
    return _aware_midnight(day, tz), _aware_midnight(day + timedelta(days=1), tz)


def appointment_day_summary(day=None):
    """
    Devuelve (nº de citas, valor estimado de reservas) del día local indicado
    con una sola consulta.

    El valor estimado es servicio.precio + producto.precio (si hay producto y
    tiene precio). Es el importe de las reservas, no dinero cobrado: el modelo no
    tiene estados de cita ni pagos.
    """
    start, end = local_day_bounds(day)
    result = Cita.objects.filter(fecha__gte=start, fecha__lt=end).aggregate(
        total=Count("pk"),
        value=Coalesce(Sum(ESTIMATED_VALUE), ZERO),
    )
    return result["total"], result["value"]


def dashboard_appointment_summary(day=None, now=None):
    """
    Resumen de citas para la portada con una sola consulta. Devuelve un dict:

    - `today`: nº de citas del día local indicado.
    - `estimated_value`: valor estimado de reservas de ese día (no es dinero cobrado).
    - `pending_review`: citas próximas (`fecha` >= ahora) que aún no se han marcado
      como vistas (`Cita.vista` False, que solo cambia con la acción
      «Marcar como vistas»). Las citas pasadas se excluyen a propósito: ninguna
      ruta pública marca `vista`, así que el histórico siempre sería «sin ver».
    """
    start, end = local_day_bounds(day)
    now = now or timezone.now()
    today = Q(fecha__gte=start, fecha__lt=end)
    return Cita.objects.filter(fecha__gte=min(start, now)).aggregate(
        today=Count("pk", filter=today),
        estimated_value=Coalesce(Sum(ESTIMATED_VALUE, filter=today), ZERO),
        pending_review=Count("pk", filter=Q(fecha__gte=now, vista=False)),
    )


def month_windows(months=12, now=None):
    """
    Lista de `months` meses naturales consecutivos en la zona horaria actual,
    terminando en el mes de `now`. Cada elemento es (etiqueta 'YYYY-MM', inicio, fin).
    """
    if months < 1:
        raise ValueError("months debe ser >= 1")
    tz = timezone.get_current_timezone()
    local_now = timezone.localtime(now or timezone.now(), tz)
    index = local_now.year * 12 + (local_now.month - 1)

    def bounds(i):
        year, month = divmod(i, 12)
        return _aware_midnight(datetime(year, month + 1, 1).date(), tz)

    windows = []
    for i in range(index - months + 1, index + 1):
        year, month = divmod(i, 12)
        windows.append((f"{year}-{month + 1:02d}", bounds(i), bounds(i + 1)))
    return windows


def monthly_appointment_counts(months=12, now=None):
    """
    (labels, counts) de los últimos `months` meses naturales, incluido el actual.
    Todos los meses aparecen, también los que no tienen citas. Una sola consulta.

    Los límites se calculan en Python con la zona horaria actual y se cuentan con
    agregación condicional: así no depende de las tablas de zonas horarias de
    MySQL (que TruncMonth necesitaría) y respeta exactamente los cambios de mes
    locales.
    """
    windows = month_windows(months, now)
    counts = Cita.objects.filter(
        fecha__gte=windows[0][1], fecha__lt=windows[-1][2]
    ).aggregate(
        **{f"m{i}": Count("pk", filter=Q(fecha__gte=start, fecha__lt=end))
           for i, (_, start, end) in enumerate(windows)}
    )
    return [w[0] for w in windows], [counts[f"m{i}"] for i in range(len(windows))]


def upcoming_appointments(*, limit=10, now=None):
    """
    Próximas citas: las que tienen `fecha` >= ahora, de la más cercana a la más
    lejana (desempate por id). Una cita en curso (empezó hace menos de su
    duración) no se considera próxima. Una consulta, sin N+1.
    """
    now = now or timezone.now()
    return list(
        Cita.objects.filter(fecha__gte=now)
        .select_related("usuario", "servicio", "producto")
        .order_by("fecha", "pk")[:limit]
    )


def fecha_hora_mismatch(cita):
    """True si `hora` no coincide (a nivel de minuto) con la hora local de `fecha`."""
    local = timezone.localtime(cita.fecha)
    return (local.hour, local.minute) != (cita.hora.hour, cita.hora.minute)
