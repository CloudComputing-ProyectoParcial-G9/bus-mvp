# Real-Time Data Ingestion Container
# ========================================
#
# Contenedor especializado en ingesta de datos en tiempo real
# Maneja GPS tracking, IoT sensors, y eventos del sistema
#
# TODO (@A): Completar implementación con fuentes de datos reales

FROM python:3.11-slim

# Información de la imagen
LABEL maintainer="Bus MVP Analytics Team <analytics@busmvp.com>"
LABEL description="Real-time data ingestion for Bus MVP system"
LABEL version="1.0.0"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    ca-certificates \
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
RUN mkdir -p /app/logs /app/data /app/temp && \
    chown -R appuser:appgroup /app

# Cambiar a usuario no-root
USER appuser

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Exponer puerto para health checks
EXPOSE 8090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8090/health || exit 1

# Comando de inicio
CMD ["python", "run.py"]
