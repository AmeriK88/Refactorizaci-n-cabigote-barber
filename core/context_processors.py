from django.utils import timezone
from .models import MensajeEspecial

def mensaje_especial_context(request):
    hoy = timezone.now().date()
    mensaje = MensajeEspecial.objects.filter(
        activo=True,
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    ).order_by('-fecha_inicio', '-id').first()
    return {
       'special_message': mensaje
    }
