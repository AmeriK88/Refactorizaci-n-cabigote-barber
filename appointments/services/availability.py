"""
Lógica de disponibilidad de citas:
- slots disponibles
- solapamientos
- duración de servicios
"""
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils import timezone

from appointments.models import Cita, FechaBloqueada, BloqueoHora
from services.models import Servicio


# Horas válidas (source of truth para availability).
# Copiadas de CitaForm.HORA_CHOICES (sin el placeholder "").
VALID_HOURS_CHOICES = [
    ("09:30", "09:30 AM"),
    ("10:00", "10:00 AM"),
    ("10:30", "10:30 AM"),
    ("11:00", "11:00 AM"),
    ("11:30", "11:30 AM"),
    ("12:00", "12:00 PM"),
    ("12:30", "12:30 PM"),
    ("16:00", "04:00 PM"),
    ("16:30", "04:30 PM"),
    ("17:00", "05:00 PM"),
    ("17:30", "05:30 PM"),
    ("18:00", "06:00 PM"),
    ("18:30", "06:30 PM"),
    ("19:00", "07:00 PM"),
    ("19:30", "07:30 PM"),
]

VALID_HOURS_VALUES = [h for h, _ in VALID_HOURS_CHOICES]



def build_calendar_constraints(*, exclude_cita_id=None):
    """
    Devuelve toda la info necesaria para el calendario:
    - fechas_ocupadas
    - fechas_bloqueadas
    - horas_ocupadas_por_fecha
    - bloqueos_por_fecha

    exclude_cita_id: para editar cita, excluye la cita actual del cálculo.
    """
    valid_hours_str = VALID_HOURS_VALUES

    qs_citas = Cita.objects.filter(hora__in=valid_hours_str)
    if exclude_cita_id:
        qs_citas = qs_citas.exclude(id=exclude_cita_id)

    # Fechas llenas
    horas_por_dia = (
        qs_citas.values("fecha__date")
        .annotate(total_citas=Count("hora"))
        .filter(total_citas=len(valid_hours_str))
    )
    fechas_ocupadas = [e["fecha__date"].isoformat() for e in horas_por_dia]

    # Fechas bloqueadas
    fechas_bloqueadas = [
        f.isoformat() for f in FechaBloqueada.objects.values_list("fecha", flat=True)
    ]

    # Horas ocupadas por fecha
    horas_ocupadas_por_fecha = {}
    for c in qs_citas.select_related(None):
        fecha_str = c.fecha.date().isoformat()
        horas_ocupadas_por_fecha.setdefault(fecha_str, []).append(
            c.hora.strftime("%H:%M")
        )

    # Horas bloqueadas por fecha
    bloqueos_por_fecha = {}
    for bloqueo in BloqueoHora.objects.all():
        fecha_str = bloqueo.fecha.isoformat()
        bloqueos_por_fecha.setdefault(fecha_str, [])
        for hour_str in valid_hours_str:
            opt_time = datetime.strptime(hour_str, "%H:%M").time()
            if bloqueo.hora_inicio <= opt_time < bloqueo.hora_fin:
                bloqueos_por_fecha[fecha_str].append(hour_str)

    return fechas_ocupadas, fechas_bloqueadas, horas_ocupadas_por_fecha, bloqueos_por_fecha


def validate_datetime_for_booking(
    *, fecha, hora, fecha_hora, service_minutes, exclude_cita_id=None
):
    """
    Lanza ValidationError si la fecha/hora no es válida.
    """
    # Fecha bloqueada
    if FechaBloqueada.objects.filter(fecha=fecha).exists():
        raise ValidationError({"fecha": "Esta fecha está bloqueada. Selecciona otra."})

    # Bloqueo por intervalo completo (inicio -> fin del servicio)
    for bloqueo in BloqueoHora.objects.filter(fecha=fecha):
        if overlaps_block(fecha_hora, service_minutes, bloqueo):
            raise ValidationError({
                "hora": (
                    f"¡Chavalote! La duración del servicio pisa un bloqueo administrativo en esa fecha. "
                    f"({bloqueo.hora_inicio:%H:%M} - {bloqueo.hora_fin:%H:%M})."
                )
            })


    # Conflicto por duración (solapes)
    if has_duration_conflict(
        fecha_hora_inicio=fecha_hora,
        new_minutes=service_minutes,
        exclude_cita_id=exclude_cita_id,
    ):
        raise ValidationError("Ya hay una cita que se solapa con ese horario.")


def overlaps(existing_start, existing_minutes, new_start, new_minutes):
    """
    Devuelve True si dos intervalos de tiempo se solapan.
    """
    existing_end = existing_start + timedelta(minutes=existing_minutes)
    new_end = new_start + timedelta(minutes=new_minutes)
    return max(existing_start, new_start) < min(existing_end, new_end)

def overlaps_block(start_dt, minutes, bloqueo):
    """
    True si el rango [start_dt, start_dt+minutes) pisa un bloqueo (hora_inicio-hora_fin).
    """
    end_dt = start_dt + timedelta(minutes=minutes)

    block_start = timezone.make_aware(
        datetime.combine(bloqueo.fecha, bloqueo.hora_inicio),
        timezone.get_current_timezone(),
    )
    block_end = timezone.make_aware(
        datetime.combine(bloqueo.fecha, bloqueo.hora_fin),
        timezone.get_current_timezone(),
    )

    # solape de intervalos
    return max(start_dt, block_start) < min(end_dt, block_end)



def has_duration_conflict(*, fecha_hora_inicio, new_minutes, exclude_cita_id=None):
    """
    True si la nueva cita solapa con otra existente ese día, considerando duración.
    """
    day = fecha_hora_inicio.date()
    qs = Cita.objects.filter(fecha__date=day)

    if exclude_cita_id:
        qs = qs.exclude(id=exclude_cita_id)

    for c in qs.select_related("servicio"):
        existing_start = c.fecha
        existing_minutes = int(getattr(c.servicio, "duracion", 30) or 30)
        if overlaps(existing_start, existing_minutes, fecha_hora_inicio, new_minutes):
            return True

    return False


def build_unavailable_hours_by_date(*, service_minutes, exclude_cita_id=None, citas_qs=None):
    """
    Devuelve un dict:
    {
      "YYYY-MM-DD": ["10:00", "10:30", ...]
    }
    Marcando como no disponibles las horas de inicio que generarían solape
    con citas existentes (considerando duración del servicio).
    """
    valid_hours_str = VALID_HOURS_VALUES
    valid_times = [datetime.strptime(h, "%H:%M").time() for h in valid_hours_str]

    # agrupamos citas por día
    qs = citas_qs if citas_qs is not None else Cita.objects.all()

    unavailable = {}

    # Pre-cargar citas por día (y su duración)
    citas_por_dia = {}
    for c in qs.select_related("servicio"):
        day = c.fecha.date().isoformat()
        citas_por_dia.setdefault(day, []).append(c)

    for day_str, citas in citas_por_dia.items():
        bloqueos = list(BloqueoHora.objects.filter(fecha=datetime.fromisoformat(day_str).date()))

        for t in valid_times:
            start_dt = timezone.make_aware(
                datetime.combine(datetime.fromisoformat(day_str).date(), t),
                timezone.get_current_timezone(),
            )

            conflict = False

            # 1) bloqueos admin
            for b in bloqueos:
                if overlaps_block(start_dt, service_minutes, b):
                    conflict = True
                    break

            # 2) citas existentes
            if not conflict:
                for c in citas:
                    existing_minutes = int(getattr(c.servicio, "duracion", 30) or 30)
                    if overlaps(c.fecha, existing_minutes, start_dt, service_minutes):
                        conflict = True
                        break

            if conflict:
                unavailable.setdefault(day_str, []).append(t.strftime("%H:%M"))

    return unavailable


def build_unavailable_by_service(*, exclude_cita_id=None):
    """
    Devuelve:
    {
      "service_id": { "YYYY-MM-DD": ["10:00", ...] }
    }
    Optimizado: carga citas una vez y reutiliza.
    """
    citas_qs = Cita.objects.select_related("servicio")
    if exclude_cita_id:
        citas_qs = citas_qs.exclude(id=exclude_cita_id)

    unavailable_by_service = {}
    for s in Servicio.objects.only("id", "duracion"):
        minutes = int(getattr(s, "duracion", 30) or 30)
        unavailable_by_service[str(s.id)] = build_unavailable_hours_by_date( # type: ignore[arg-type] 
            service_minutes=minutes,
            citas_qs=citas_qs,
        )

    return unavailable_by_service


def normalize_booking_datetime(*, fecha, hora):
    """
    Normaliza inputs del form y devuelve:
    (fecha_date, hora_time, fecha_hora_aware)
    """
    if isinstance(fecha, datetime):
        fecha = fecha.date()

    if isinstance(hora, str):
        hora = datetime.strptime(hora, "%H:%M").time()

    fecha_hora = timezone.make_aware(
        datetime.combine(fecha, hora),
        timezone.get_current_timezone(),
    )
    return fecha, hora, fecha_hora



def get_unavailable_start_hours_for_date(*, day, service_minutes, exclude_cita_id=None):
    """
    Devuelve ["10:00", "10:30", ...] para un día concreto.
    1 query de citas + 1 query de bloqueos.
    """
    tz = timezone.get_current_timezone()
    valid_times = [datetime.strptime(h, "%H:%M").time() for h in VALID_HOURS_VALUES]

    qs = Cita.objects.filter(fecha__date=day).select_related("servicio")
    if exclude_cita_id:
        qs = qs.exclude(id=exclude_cita_id)
    citas = list(qs)

    bloqueos = list(BloqueoHora.objects.filter(fecha=day))

    unavailable = []
    for t in valid_times:
        start_dt = timezone.make_aware(datetime.combine(day, t), tz)

        # Bloqueos
        if any(overlaps_block(start_dt, service_minutes, b) for b in bloqueos):
            unavailable.append(t.strftime("%H:%M"))
            continue

        # Solapes con citas
        conflict = False
        for c in citas:
            existing_minutes = int(getattr(c.servicio, "duracion", 30) or 30)
            if overlaps(c.fecha, existing_minutes, start_dt, service_minutes):
                conflict = True
                break

        if conflict:
            unavailable.append(t.strftime("%H:%M"))

    return unavailable

