# Usa una imagen base con Python (>=3.11 para contourpy 1.3.3)
FROM python:3.12-slim

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libmariadb-dev-compat \
    libmariadb-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn cabigote.wsgi:application --bind 0.0.0.0:8000"]
