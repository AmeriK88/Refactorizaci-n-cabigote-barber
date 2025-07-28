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

# 1) Actualizar pip antes de instalar dependencias
RUN python -m pip install --upgrade pip

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código del proyecto
COPY . .

# Configura las variables de entorno necesarias para la ejecución
ENV PYTHONUNBUFFERED=1

# Expone el puerto para el servidor
EXPOSE 8000

# Ejecuta migraciones, collectstatic y Gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn cabigote.wsgi:application --bind 0.0.0.0:8000"]
