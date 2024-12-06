import os
import logging
from logging.handlers import RotatingFileHandler

# Crea el directorio 'logs' si no existe
os.makedirs('logs', exist_ok=True)

# Configuración del logger
logger = logging.getLogger('mi_logger')
handler = RotatingFileHandler('logs/log.error', maxBytes=500000, backupCount=5)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Ejemplo de log para probar la creación del archivo
logger.error("Este es un mensaje de prueba de error")
