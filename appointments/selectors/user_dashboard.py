from django.db.models import Count, Sum
from django.utils import timezone

from appointments.models import Cita


def get_user_profile_dashboard(*, user, year=None):
    """
    Selector de lectura (solo queries) para el dashboard del perfil.
    Mantiene compatibilidad con el template users/perfil_usuario.html.
    """
    current_year = year or timezone.localdate().year

    citas_activas = (
        Cita.objects.filter(usuario=user, fecha__gte=timezone.now())
        .select_related("servicio")
        .order_by("fecha", "hora")
    )

    citas_year = (
        Cita.objects.filter(usuario=user, fecha__year=current_year)
        .select_related("servicio")
    )

    total_citas_year = citas_year.count()
    total_gastado_year = citas_year.aggregate(total=Sum("servicio__precio"))["total"] or 0

    fav_service_data = (
        citas_year.values("servicio__nombre")
        .annotate(service_count=Count("servicio"))
        .order_by("-service_count")
        .first()
    )
    favorite_service_year = fav_service_data["servicio__nombre"] if fav_service_data else "N/A"

    return {
        "year": current_year,
        "citas": citas_activas,
        "total_citas": total_citas_year,
        "total_gastado": total_gastado_year,
        "favorite_service": favorite_service_year,
    }
