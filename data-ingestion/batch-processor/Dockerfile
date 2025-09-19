# Batch Data Processor Container
# ========================================
#
# Contenedor especializado en procesamiento de datos por lotes
# Maneja archivos CSV, logs del sistema, y ETL de datos históricos
#
# TODO (@A): Completar implementación con fuentes de datos específicas

FROM python:3.11-slim

# Información de la imagen
LABEL maintainer="Bus MVP Analytics Team <analytics@busmvp.com>"
LABEL description="Batch data processor for Bus MVP system"
LABEL version="1.0.0"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    ca-certificates \
    cron \
    logrotate \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Configurar directorio de trabajo
WORKDIR /app

# Copiar requirements primero para mejor cache de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/data /app/temp /app/processed /app/failed && \
    chown -R appuser:appgroup /app

# Configurar cron para tareas programadas
COPY crontab /etc/cron.d/batch-processor
RUN chmod 0644 /etc/cron.d/batch-processor && \
    crontab /etc/cron.d/batch-processor

# Cambiar a usuario no-root
USER appuser

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Exponer puerto para health checks
EXPOSE 8091

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8091/health || exit 1

# Comando de inicio
CMD ["python", "run.py"]
