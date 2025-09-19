# External APIs Collector Container
# ========================================
#
# Contenedor especializado en recolección de datos desde APIs externas
# Maneja web scraping, APIs de terceros, y normalización de datos
#
# TODO (@A): Completar implementación con APIs específicas

FROM python:3.11-slim

# Información de la imagen
LABEL maintainer="Bus MVP Analytics Team <analytics@busmvp.com>"
LABEL description="External APIs data collector for Bus MVP system"
LABEL version="1.0.0"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    ca-certificates \
    chromium \
    chromium-driver \
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
RUN mkdir -p /app/logs /app/data /app/cache /app/downloads && \
    chown -R appuser:appgroup /app

# Configurar Chromium para Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER_PATH=/usr/bin/chromedriver

# Cambiar a usuario no-root
USER appuser

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Exponer puerto para health checks
EXPOSE 8092

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8092/health || exit 1

# Comando de inicio
CMD ["python", "run.py"]
