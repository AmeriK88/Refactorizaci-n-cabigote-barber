
"""
Compat layer:
Antes existía core/utils.py y se importaba como `from core.utils import ...`.
Ahora `core.utils` es un paquete. Re-exportamos lo viejo para no romper imports.
"""

# Emails (source of truth)
from core.services.emailing import (
    enviar_correo_admin,
    enviar_confirmacion_cita,
    enviar_notificacion_eliminacion_cita,
    enviar_notificacion_modificacion_cita,
    enviar_recordatorio_cita,
)

