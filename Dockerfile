# Usa una imagen base con Python
FROM python:3.10-slim

# Actualiza el sistema e instala las dependencias necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libmariadb-dev-compat \
    libmariadb-dev \
    && apt-get clean

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de dependencias
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código del proyecto
COPY . .

# Configura las variables de entorno
ENV PYTHONUNBUFFERED=1

# Configura una clave secreta temporal durante la construcción
ENV SECRET_KEY=temp-secret-key

# Ejecuta las migraciones y recopila los archivos estáticos
RUN python manage.py collectstatic --noinput && python manage.py migrate

# Expone el puerto para el servidor
EXPOSE 8000

# Comando para iniciar Gunicorn
CMD ["gunicorn", "cabigote.wsgi:application", "--bind", "0.0.0.0:8000"]
