# Usa una imagen base con Python
FROM python:3.10-slim

# Dependencias del sistema (MySQL/MariaDB si las necesitas)
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libmariadb-dev-compat \
    libmariadb-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia e instala dependencias
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia el código (incluye start.sh)
COPY . .

# Asegura permisos de ejecución y corrige CRLF si viniera de Windows
RUN chmod +x /app/start.sh && \
    sed -i 's/\r$//' /app/start.sh

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Forma JSON recomendada: sin shell, sin warnings del linter
CMD ["/app/start.sh"]
