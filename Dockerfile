# Use a lightweight Python base image
FROM python:3.10-slim

# Install system dependencies in a single layer and clean up
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       default-libmysqlclient-dev \
       pkg-config \
       libmariadb-dev-compat \
       libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN useradd --create-home appuser

# Set working directory
WORKDIR /home/appuser/app

# Switch to non-root user
USER appuser

# Copy and install Python dependencies (including Gunicorn)
COPY --chown=appuser:appuser requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the application code
COPY --chown=appuser:appuser . .

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=cabigote.settings

# Expose port for the application
EXPOSE 8000

# Optional healthcheck to ensure the app is running
HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:8000/healthz/ || exit 1

# Use Gunicorn as the entrypoint; migrations and static collection
# are handled in the Railway "Release Command" configuration
CMD ["gunicorn", "cabigote.wsgi:application", "--bind", "0.0.0.0:$(PORT)"]
