from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import MensajeEspecial, ContadorVisitas


def mensaje_especial_context(request):
    """
    Datos del sitio público (banner, visitas, usuarios activos). Se calculan de
    forma perezosa: solo se consulta la BD si la plantilla usa el valor, de modo
    que el admin (que no los usa) no paga 3 consultas por petición.
    """
    return {
        'special_message': _memoize(_active_message),
        'contador_global': _memoize(_global_counter),
        'total_usuarios': _memoize(_active_users),
        'APP_VERSION': getattr(settings, 'APP_VERSION', 'dev'),
    }


def _memoize(func):
    cache = []

    def wrapper():
        if not cache:
            cache.append(func())
        return cache[0]

    return wrapper


def _active_message():
    hoy = timezone.now().date()
    return (
        MensajeEspecial.objects
        .filter(
            activo=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy
        )
        .order_by('-fecha_inicio', '-id')
        .first()
    )


def _global_counter():
    try:
        return ContadorVisitas.objects.only('total').get(pk=1).total
    except ContadorVisitas.DoesNotExist:
        return 0


def _active_users():
    try:
        return get_user_model().objects.filter(is_active=True).count()
    except Exception:
        return 0
