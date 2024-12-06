from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from appointments.models import Cita
from reports.utils import calcular_reporte, limpiar_reportes
from django.utils.timezone import now

@receiver(post_save, sender=Cita)
@receiver(post_delete, sender=Cita)
def actualizar_reporte(sender, instance, **kwargs):
    limpiar_reportes()  
    calcular_reporte(now().date().replace(day=1))
