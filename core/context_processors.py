from django.utils import timezone
from django.conf import settings     
from .models import MensajeEspecial, ContadorVisitas

def mensaje_especial_context(request):
    hoy = timezone.now().date()

    # Obtener el mensaje especial activo
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

    # Obtener el contador desde la BD
    try:
        contador_obj = ContadorVisitas.objects.get(pk=1)
        contador_global = contador_obj.total
    except ContadorVisitas.DoesNotExist:
        contador_global = 0

    return {
       'special_message': mensaje,
       'contador_global': contador_global,
       'APP_VERSION': settings.APP_VERSION,  
    }
