from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.utils.timezone import localtime
from django.conf import settings

from appointments.models import Cita
from .utils import calcular_reporte, calcular_reporte_diario

@receiver(post_save, sender=Cita, dispatch_uid="reports_cita_post_save")
def actualizar_reportes_post_save(sender, instance, created, **kwargs):
    # Evitar ejecutar durante loaddata/fixtures
    if kwargs.get("raw"):
        return

    def _recalc():
        fecha_local = localtime(instance.fecha).date()
        calcular_reporte_diario(fecha_local)
        calcular_reporte(fecha_local.replace(day=1), meses_ahead=1)

    transaction.on_commit(_recalc)

@receiver(post_delete, sender=Cita, dispatch_uid="reports_cita_post_delete")
def actualizar_reportes_post_delete(sender, instance, **kwargs):
    def _recalc():
        fecha_local = localtime(instance.fecha).date()
        calcular_reporte_diario(fecha_local)
        calcular_reporte(fecha_local.replace(day=1), meses_ahead=1)

    transaction.on_commit(_recalc)
