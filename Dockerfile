# Usa una imagen base con Python
FROM python:3.12-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de dependencias al contenedor
COPY requirements.txt .

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código del proyecto al contenedor
COPY . .

# Establece las variables de entorno necesarias
ENV PYTHONUNBUFFERED=1

# Ejecuta migraciones y recopila archivos estáticos antes de iniciar el servidor
RUN python manage.py collectstatic --noinput && python manage.py migrate

# Expone el puerto para el servidor
EXPOSE 8000

# Comando para iniciar Gunicorn
CMD ["gunicorn", "cabigote.wsgi:application", "--bind", "0.0.0.0:8000"]
