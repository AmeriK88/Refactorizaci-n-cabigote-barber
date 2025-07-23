from django.utils import timezone
from django.conf import settings     
from .models import MensajeEspecial, ContadorVisitas

def mensaje_especial_context(request):
    hoy = timezone.now().date()

    # ACTIVE MESSAGE
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

    # OBTAIN COUNTER FROM DB
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
