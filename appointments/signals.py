from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from appointments.models import Cita
from reports.utils import calcular_reporte, limpiar_reportes, calcular_reporte_diario, limpiar_reportes, limpiar_reportes_diarios 
from django.utils.timezone import now

@receiver(post_save, sender=Cita)
@receiver(post_delete, sender=Cita)
def actualizar_reporte(sender, instance, **kwargs):
    # Limpiar y recalcular reportes mensuales
    limpiar_reportes()  
    calcular_reporte(now().date().replace(day=1))

    # Limpiar y recalcular reportes diarios
    limpiar_reportes_diarios()
    calcular_reporte_diario()
