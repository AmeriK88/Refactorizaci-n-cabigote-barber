from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


def _formatear_fecha_hora(dt):
    """
    Convierte un DateTimeField (aware o UTC) a la zona Atlantic/Canary
    y devuelve una tupla (dd/mm/aaaa, HH:MM).
    """
    local = timezone.localtime(dt)
    return local.strftime("%d/%m/%Y"), local.strftime("%H:%M")


def enviar_correo_admin(asunto, mensaje):
    """Envía un correo electrónico a los administradores definidos en settings.ADMINS."""
    if settings.ADMINS:
        admin_emails = [admin[1] for admin in settings.ADMINS]
        send_mail(
            asunto,
            mensaje,
            settings.EMAIL_HOST_USER,
            admin_emails,
            fail_silently=False,
        )


# ══════════════════════════════════════════════════════════════
# 1) CONFIRMATION NOTIFICATION
# ══════════════════════════════════════════════════════════════
def enviar_confirmacion_cita(usuario_email, cita):
    fecha_str, hora_str = _formatear_fecha_hora(cita.fecha)

    asunto = "Confirmación de tu cita en Ca´Bigote Barber Shop"
    mensaje = f"""
    Estimado usuario,

    Gracias por reservar una cita con nosotros. Aquí están los detalles de tu cita:

    Servicio : {cita.servicio.nombre}
    Fecha    : {fecha_str}
    Hora     : {hora_str}
    Comentario: {cita.comentario or 'Sin comentarios'}

    En caso de no poder asistir, puedes editar tu cita desde nuestra app.

    ¡Te esperamos!

    Atentamente,
    Ca´Bigote Barber Shop

    ---

    Dirección: calle el rafael 43, Arrecife
    Teléfono : +34 699 85 99 61
    ¡Síguenos para más novedades!
    """
    send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [usuario_email])

    mensaje_admin = f"""Un usuario ha reservado una cita:

    Usuario    : {getattr(cita.usuario, 'username', 'Usuario no disponible')}
    Comentario : {cita.comentario or 'Sin comentarios'}

    Servicio : {cita.servicio.nombre}
    Fecha    : {fecha_str}
    Hora     : {hora_str}
    """
    enviar_correo_admin("Nueva cita reservada en Ca´Bigote", mensaje_admin)


# ══════════════════════════════════════════════════════════════
# 2) DELETE NOTIFICATIONS
# ══════════════════════════════════════════════════════════════
def enviar_notificacion_eliminacion_cita(usuario_email, cita_detalle):
    fecha_str, hora_str = _formatear_fecha_hora(cita_detalle["fecha"])

    asunto = "Tu cita en Ca´Bigote Barber Shop ha sido eliminada"
    mensaje = f"""
    Estimado usuario,

    Tu cita para el servicio {cita_detalle['servicio']}
    el {fecha_str} a las {hora_str} ha sido eliminada correctamente.

    Si lo deseas, puedes volver a agendar una cita desde nuestra aplicación.

    Atentamente,
    Ca´Bigote Barber Shop

    ---

    Dirección: calle el rafael 43, Arrecife
    Teléfono : +34 699 85 99 61
    ¡Síguenos para más novedades!
    """
    send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [usuario_email])

    # ADMIN NOTIFICATIONS
    mensaje_admin = f"""Un usuario ha eliminado una cita:

    Usuario    : {cita_detalle.get('usuario', 'Usuario no disponible')}
    Comentario : {cita_detalle.get('comentario', 'Sin comentarios')}

    Servicio : {cita_detalle['servicio']}
    Fecha    : {fecha_str}
    Hora     : {hora_str}
    """
    enviar_correo_admin("Cita eliminada en Ca´Bigote", mensaje_admin)


# ══════════════════════════════════════════════════════════════
# 3) UPDATE EMAIL
# ══════════════════════════════════════════════════════════════
def enviar_notificacion_modificacion_cita(usuario_email, cita):
    fecha_str, hora_str = _formatear_fecha_hora(cita.fecha)

    asunto = "Tu cita en Ca´Bigote Barber Shop ha sido modificada"
    mensaje = f"""
    Estimado usuario,

    Tu cita ha sido modificada. Aquí están los nuevos detalles:

    Servicio : {cita.servicio.nombre}
    Nueva fecha : {fecha_str}
    Nueva hora  : {hora_str}
    Comentario  : {cita.comentario or 'Sin comentarios'}

    Atentamente,
    Ca´Bigote Barber Shop

    ---

    Dirección: calle el rafael 43, Arrecife
    Teléfono : +34 699 85 99 61
    ¡Síguenos para más novedades!
    """
    send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [usuario_email])

    # Notificar a los administradores
    mensaje_admin = f"""Un usuario ha modificado una cita:

    Usuario    : {getattr(cita.usuario, 'username', 'Usuario no disponible')}
    Comentario : {cita.comentario or 'Sin comentarios'}

    Servicio : {cita.servicio.nombre}
    Nueva fecha : {fecha_str}
    Nueva hora  : {hora_str}
    """
    enviar_correo_admin("Cita modificada en Ca´Bigote", mensaje_admin)


# ══════════════════════════════════════════════════════════════
# 4) REMINDERS
# ══════════════════════════════════════════════════════════════
def enviar_recordatorio_cita(usuario_email, cita):
    fecha_str, hora_str = _formatear_fecha_hora(cita.fecha)

    asunto = "Recordatorio de tu cita en Ca´Bigote Barber Shop"
    mensaje = f"""
    Estimado usuario,

    Te recordamos que tienes una cita programada para mañana:

    Servicio : {cita.servicio.nombre}
    Fecha    : {fecha_str}
    Hora     : {hora_str}
    Comentario: {cita.comentario or 'Sin comentarios'}

    Por favor, asegúrate de llegar a tiempo.  
    Si no puedes asistir, recuerda que puedes modificar tu cita desde nuestra app web.

    ¡Te esperamos!

    Atentamente,
    Ca´Bigote Barber Shop

    Dirección: calle el rafael 43, Arrecife
    Teléfono : +34 699 85 99 61
    """
    send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [usuario_email])


# Autor: José Félix Gordo Castaño
# Licencia: Uso educativo, no comercial
