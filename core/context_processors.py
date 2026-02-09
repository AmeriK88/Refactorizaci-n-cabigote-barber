from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import MensajeEspecial, ContadorVisitas


def mensaje_especial_context(request):
    hoy = timezone.now().date()

    # Mensaje activo (1º capa)
    mensaje = (
        MensajeEspecial.objects
        .filter(
            activo=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy
        )
        .order_by('-fecha_inicio', '-id')
        .first()
    )

    # Contador global (con fallback seguro)
    try:
        contador_global = (
            ContadorVisitas.objects
            .only('total')
            .get(pk=1)
            .total
        )
    except ContadorVisitas.DoesNotExist:
        contador_global = 0

    # Usuarios totales (activos)
    User = get_user_model()
    try:
        total_usuarios = User.objects.filter(is_active=True).count()
    except Exception:
        total_usuarios = 0

    # APP_VERSION (fallback por si no existe en settings)
    app_version = getattr(settings, 'APP_VERSION', 'dev')

    return {
        'special_message': mensaje,
        'contador_global': contador_global,
        'total_usuarios': total_usuarios,
        'APP_VERSION': app_version,
    }
