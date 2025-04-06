from django.core.mail import send_mail
from django.conf import settings


def enviar_correo_admin(asunto, mensaje):
    """
    Envía un correo electrónico a los administradores configurados en settings.ADMINS.
    """
    if settings.ADMINS:
        admin_emails = [admin[1] for admin in settings.ADMINS]
        send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, admin_emails, fail_silently=False)

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

    Dirección: calle el rafael 43, Arrecife
    Teléfono: +34 699 85 99 61
    ¡Síguenos para más novedades!
    """
    send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [usuario_email], fail_silently=False)

    # Notificar a los administradores
    mensaje_admin = f"""Un usuario ha reservado una cita:

    Usuario: {cita.usuario.username if hasattr(cita, 'usuario') else 'Usuario no disponible'}
    Comentario: {cita.comentario if cita.comentario else 'Sin comentarios'}

    Servicio: {cita.servicio.nombre}
    Fecha: {cita.fecha}
    Hora: {cita.hora}
    """
    enviar_correo_admin('Nueva cita reservada en Ca´Bigote', mensaje_admin)

def enviar_notificacion_eliminacion_cita(usuario_email, cita_detalle):
    asunto = 'Tu cita en Ca´Bigote Barber Shop ha sido eliminada'
    mensaje = f"""
    Estimado usuario,

    Tu cita para el servicio {cita_detalle['servicio']} el {cita_detalle['fecha']} a las {cita_detalle['hora']} ha sido eliminada correctamente.

    Si deseas, puedes volver a agendar una cita desde nuestra aplicación.

    Atentamente,
    Ca´Bigote Barber Shop

    ---

    Dirección: calle el rafael 43, Arrecife
    Teléfono: +34 699 85 99 61
    ¡Síguenos para más novedades!
    """
    send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [usuario_email], fail_silently=False)

    # Notificar a los administradores
    mensaje_admin = f"""Un usuario ha eliminado una cita:

    Usuario: {cita_detalle['usuario'] if 'usuario' in cita_detalle else 'Usuario no disponible'}
    Comentario: {cita_detalle['comentario'] if 'comentario' in cita_detalle else 'Sin comentarios'}

    Servicio: {cita_detalle['servicio']}
    Fecha: {cita_detalle['fecha']}
    Hora: {cita_detalle['hora']}
    """
    enviar_correo_admin('Cita eliminada en Ca´Bigote', mensaje_admin)

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

    Dirección: calle el rafael 43, Arrecife
    Teléfono: +34 699 85 99 61
    ¡Síguenos para más novedades!
    """
    send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [usuario_email], fail_silently=False)

    # Notificar a los administradores
    mensaje_admin = f"""Un usuario ha modificado una cita:

    Usuario: {cita.usuario.username if cita.usuario else 'Usuario no disponible'}
    Comentario: {cita.comentario if cita.comentario else 'Sin comentarios'}

    Servicio: {cita.servicio.nombre}
    Nueva fecha: {cita.fecha}
    Nueva hora: {cita.hora}
    """
    enviar_correo_admin('Cita modificada en Ca´Bigote', mensaje_admin)


def enviar_recordatorio_cita(usuario_email, cita):
    asunto = 'Recordatorio de tu cita en Ca´Bigote Barber Shop'
    mensaje = f"""
    Estimado usuario,

    Te recordamos que tienes una cita programada para mañana:

    Servicio: {cita.servicio.nombre}
    Fecha: {cita.fecha}
    Hora: {cita.hora}
    Comentario: {cita.comentario if cita.comentario else 'Sin comentarios'}

    Por favor, asegúrate de llegar a tiempo. Si no puedes asistir, recuerda que puedes modificar tu cita desde nuestra app web.

    ¡Te esperamos!

    Atentamente,
    Ca´Bigote Barber Shop

    Dirección: calle el rafael 43, Arrecife
    Teléfono: +34 699 85 99 61
    """
    send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [usuario_email], fail_silently=False)

# Autor: José Félix Gordo Castaño
# Copyright (C) 2024 José Félix Gordo Castaño
# Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje. 
# No se permite la venta ni el uso comercial sin autorización expresa del autor.
