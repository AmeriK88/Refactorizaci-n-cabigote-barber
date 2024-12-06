import qrcode
import os
from dotenv import load_dotenv

# Cargar las variables de entorno del archivo .env
load_dotenv()

# URL a la que se redirigirá el código QR
url = os.getenv('QR_URL')

# Crear una instancia del generador de QR
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

qr.add_data(url)
qr.make(fit=True)

# Crear una imagen del QR
img = qr.make_image(fill='black', back_color='white')

img.save('registro_qr.png')
