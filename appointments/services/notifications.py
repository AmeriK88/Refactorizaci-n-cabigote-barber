"""
BOOKING NOTIFICATIONS.
Module used when core.services.emailing
"""
from core.services.emailing import (
    enviar_confirmacion_cita,
    enviar_notificacion_modificacion_cita,
    enviar_notificacion_eliminacion_cita,
)


def notify_booking_created(email, cita):
    return enviar_confirmacion_cita(email, cita)


def notify_booking_updated(email, cita):
    return enviar_notificacion_modificacion_cita(email, cita)


def notify_booking_deleted(email, cita_detalle):
    return enviar_notificacion_eliminacion_cita(email, cita_detalle)
