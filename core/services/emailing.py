# Autor: José Félix Gordo Castaño
# Licencia: Uso educativo, no comercial

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils import timezone


def _formatear_fecha_hora(dt):
    """Convierte la fecha de la cita a la zona horaria configurada en Django."""
    local = timezone.localtime(dt)
    return local.strftime("%d/%m/%Y"), local.strftime("%H:%M")


def _enviar_email_cliente(
    destinatario,
    asunto,
    mensaje,
    *,
    tipo,
    servicio,
    fecha,
    hora,
    comentario=None,
):
    """Envía una alternativa de texto plano y una versión HTML del mismo aviso."""
    contexto = {
        "tipo": tipo,
        "servicio": servicio,
        "fecha": fecha,
        "hora": hora,
        "comentario": comentario or "Sin comentarios",
    }

    html = render_to_string(
        "emails/appointment_notification.html",
        contexto,
    )

    email = EmailMultiAlternatives(
        subject=asunto,
        body=mensaje.strip(),
        from_email=settings.EMAIL_HOST_USER,
        to=[destinatario],
    )
    email.attach_alternative(html, "text/html")
    email.send()


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


# ============================================================
# 1. CONFIRMACIÓN DE CITA
# ============================================================

def enviar_confirmacion_cita(usuario_email, cita):
    fecha_str, hora_str = _formatear_fecha_hora(cita.fecha)

    asunto = "Confirmación de tu cita en Ca’Bigote Barber Shop"

    mensaje = f"""¡Tu cita está confirmada!

Gracias por reservar una cita con nosotros.

Servicio: {cita.servicio.nombre}
Fecha: {fecha_str}
Hora: {hora_str}
Comentario: {cita.comentario or 'Sin comentarios'}

Si no puedes asistir, puedes modificar tu cita desde nuestra aplicación.

¡Te esperamos!
Ca’Bigote Barber Shop

Dirección: Calle El Rafael 43, Arrecife
Teléfono: +34 699 85 99 61
"""

    _enviar_email_cliente(
        usuario_email,
        asunto,
        mensaje,
        tipo="confirmacion",
        servicio=cita.servicio.nombre,
        fecha=fecha_str,
        hora=hora_str,
        comentario=cita.comentario,
    )

    mensaje_admin = f"""Un usuario ha reservado una cita:

Usuario: {getattr(cita.usuario, 'username', 'Usuario no disponible')}
Comentario: {cita.comentario or 'Sin comentarios'}
Servicio: {cita.servicio.nombre}
Fecha: {fecha_str}
Hora: {hora_str}
"""

    enviar_correo_admin(
        "Nueva cita reservada en Ca’Bigote",
        mensaje_admin,
    )


# ============================================================
# 2. CANCELACIÓN DE CITA
# ============================================================

def enviar_notificacion_eliminacion_cita(usuario_email, cita_detalle):
    fecha_str, hora_str = _formatear_fecha_hora(
        cita_detalle["fecha"]
    )

    asunto = "Tu cita en Ca’Bigote Barber Shop ha sido cancelada"

    mensaje = f"""Tu cita ha sido cancelada correctamente.

Servicio: {cita_detalle['servicio']}
Fecha: {fecha_str}
Hora: {hora_str}

Si lo deseas, puedes volver a reservar desde nuestra aplicación.

Ca’Bigote Barber Shop
Dirección: Calle El Rafael 43, Arrecife
Teléfono: +34 699 85 99 61
"""

    _enviar_email_cliente(
        usuario_email,
        asunto,
        mensaje,
        tipo="cancelacion",
        servicio=cita_detalle["servicio"],
        fecha=fecha_str,
        hora=hora_str,
    )

    mensaje_admin = f"""Un usuario ha eliminado una cita:

Usuario: {cita_detalle.get('usuario', 'Usuario no disponible')}
Comentario: {cita_detalle.get('comentario', 'Sin comentarios')}
Servicio: {cita_detalle['servicio']}
Fecha: {fecha_str}
Hora: {hora_str}
"""

    enviar_correo_admin(
        "Cita eliminada en Ca’Bigote",
        mensaje_admin,
    )


# ============================================================
# 3. MODIFICACIÓN DE CITA
# ============================================================

def enviar_notificacion_modificacion_cita(usuario_email, cita):
    fecha_str, hora_str = _formatear_fecha_hora(cita.fecha)

    asunto = "Tu cita en Ca’Bigote Barber Shop ha sido modificada"

    mensaje = f"""Tu cita ha sido modificada. Estos son los nuevos detalles:

Servicio: {cita.servicio.nombre}
Nueva fecha: {fecha_str}
Nueva hora: {hora_str}
Comentario: {cita.comentario or 'Sin comentarios'}

Ca’Bigote Barber Shop
Dirección: Calle El Rafael 43, Arrecife
Teléfono: +34 699 85 99 61
"""

    _enviar_email_cliente(
        usuario_email,
        asunto,
        mensaje,
        tipo="modificacion",
        servicio=cita.servicio.nombre,
        fecha=fecha_str,
        hora=hora_str,
        comentario=cita.comentario,
    )

    mensaje_admin = f"""Un usuario ha modificado una cita:

Usuario: {getattr(cita.usuario, 'username', 'Usuario no disponible')}
Comentario: {cita.comentario or 'Sin comentarios'}
Servicio: {cita.servicio.nombre}
Nueva fecha: {fecha_str}
Nueva hora: {hora_str}
"""

    enviar_correo_admin(
        "Cita modificada en Ca’Bigote",
        mensaje_admin,
    )


# ============================================================
# 4. RECORDATORIO DE CITA
# ============================================================

def enviar_recordatorio_cita(usuario_email, cita):
    fecha_str, hora_str = _formatear_fecha_hora(cita.fecha)

    asunto = "Recordatorio de tu cita en Ca’Bigote Barber Shop"

    mensaje = f"""¡Te esperamos mañana!

Servicio: {cita.servicio.nombre}
Fecha: {fecha_str}
Hora: {hora_str}
Comentario: {cita.comentario or 'Sin comentarios'}

Por favor, llega a tiempo. Si no puedes asistir, recuerda que puedes modificar tu cita desde nuestra aplicación.

Ca’Bigote Barber Shop
Dirección: Calle El Rafael 43, Arrecife
Teléfono: +34 699 85 99 61
"""

    _enviar_email_cliente(
        usuario_email,
        asunto,
        mensaje,
        tipo="recordatorio",
        servicio=cita.servicio.nombre,
        fecha=fecha_str,
        hora=hora_str,
        comentario=cita.comentario,
    )


# Autor: José Félix Gordo Castaño
# Licencia: Uso educativo, no comercial
