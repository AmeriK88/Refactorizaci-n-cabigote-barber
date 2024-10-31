from django.core.mail import send_mail
from django.conf import settings

def enviar_confirmacion_cita(usuario_email, cita):
    asunto = 'Confirmación de tu cita en Ca´Bigote Barber Shop'
    mensaje = f"""
    Estimado usuario,

    Gracias por reservar una cita con nosotros. Aquí están los detalles de tu cita:

    Servicio: {cita.servicio.nombre}
    Fecha: {cita.fecha}
    Hora: {cita.hora}
    Comentario: {cita.comentario}

    En caso de no poder asistir, puede editar su cita desde nuestra app!

    ¡Te esperamos!

    Atentamente,
    Ca´Bigote Barber Shop

    ---

    Dirección: Calle Ejemplo 123, Ciudad
    Teléfono: +123 456 789
    Instagram: @cabigote_barber_shop
    ¡Síguenos para más novedades!git a
    """
    send_mail(
        asunto,
        mensaje,
        settings.EMAIL_HOST_USER,
        [usuario_email],
        fail_silently=False,
    )

     # Enviar notificación al administrador
    if settings.ADMINS:
        admin_emails = [admin[1] for admin in settings.ADMINS]
        send_mail(
            'Nueva cita reservada en Ca´Bigote',
            f'Un usuario ha reservado una cita:\n\nServicio: {cita.servicio.nombre}\nFecha: {cita.fecha}\nHora: {cita.hora}',
            settings.EMAIL_HOST_USER,
            admin_emails,
            fail_silently=False,
        )

def enviar_notificacion_eliminacion_cita(usuario_email, cita_detalle):
    asunto = 'Tu cita en Ca´Bigote Barber Shop ha sido eliminada'
    mensaje = f"""
    Estimado usuario,

    Tu cita para el servicio {cita_detalle['servicio']} el {cita_detalle['fecha']} a las {cita_detalle['hora']} ha sido eliminada correctamente.

    Si deseas, puedes volver a agendar una cita desde nuestra aplicación.

    Atentamente,
    Ca´Bigote Barber Shop

    ---

    Dirección: Calle Ejemplo 123, Ciudad
    Teléfono: +123 456 789
    Instagram: @cabigote_barber_shop
    ¡Síguenos para más novedades!
    """
    send_mail(
        asunto,
        mensaje,
        settings.EMAIL_HOST_USER,
        [usuario_email],
        fail_silently=False,
    )
    
    # Enviar notificación al administrador
    if settings.ADMINS:
        admin_emails = [admin[1] for admin in settings.ADMINS]
        send_mail(
            'Cita eliminada en Ca´Bigote',
            f'Un usuario ha eliminado una cita:\n\nServicio: {cita_detalle["servicio"]}\nFecha: {cita_detalle["fecha"]}\nHora: {cita_detalle["hora"]}',
            settings.EMAIL_HOST_USER,
            admin_emails,
            fail_silently=False,
        )


def enviar_notificacion_modificacion_cita(usuario_email, cita):
    asunto = 'Tu cita en Ca´Bigote Barber Shop ha sido modificada'
    mensaje = f"""
    Estimado usuario,

    Tu cita ha sido modificada. Aquí están los nuevos detalles:

    Servicio: {cita.servicio.nombre}
    Nueva fecha: {cita.fecha}
    Nueva hora: {cita.hora}
    Comentario: {cita.comentario}

    Atentamente,
    Ca´Bigote Barber Shop

    ---

    Dirección: Calle Ejemplo 123, Ciudad
    Teléfono: +123 456 789
    Instagram: @cabigote_barber_shop
    ¡Síguenos para más novedades!
    """
    send_mail(
        asunto,
        mensaje,
        settings.EMAIL_HOST_USER,
        [usuario_email],
        fail_silently=False,
    )

    # Enviar notificación al administrador
    if settings.ADMINS:
        admin_emails = [admin[1] for admin in settings.ADMINS]
        send_mail(
            'Cita modificada en Ca´Bigote',
            f'Un usuario ha modificado una cita:\n\nServicio: {cita.servicio.nombre}\nNueva fecha: {cita.fecha}\nNueva hora: {cita.hora}',
            settings.EMAIL_HOST_USER,
            admin_emails,
            fail_silently=False,
        )
