# ========================================
# Dockerfile - ms-trips
# ========================================
# Microservicio de Viajes del Bus MVP
# Stack: Node.js + Express + Sequelize + MySQL
# Puerto: 8002

# ========================================
# STAGE 1: Build dependencies
# ========================================
FROM node:18-alpine AS dependencies

# Instalar dependencias del sistema necesarias
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    && rm -rf /var/cache/apk/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias de producción
RUN npm ci --only=production && npm cache clean --force

# ========================================
# STAGE 2: Production image
# ========================================
FROM node:18-alpine AS production

# Metadatos
LABEL maintainer="Bus MVP Team"
LABEL service="ms-trips"
LABEL version="1.0.0"
LABEL description="Microservicio de gestión de viajes y rutas"

# Crear usuario no-root para seguridad
RUN addgroup -g 1001 -S nodejs && \
    adduser -S trips -u 1001 -G nodejs

# Instalar curl para health checks
RUN apk add --no-cache curl && \
    rm -rf /var/cache/apk/*

# Crear directorios necesarios
WORKDIR /app
RUN mkdir -p logs && \
    chown -R trips:nodejs /app

# Copiar dependencias desde stage anterior
COPY --from=dependencies --chown=trips:nodejs /app/node_modules ./node_modules

# Copiar código fuente
COPY --chown=trips:nodejs . .

# Variables de entorno por defecto
ENV NODE_ENV=production
ENV PORT=8002
ENV LOG_LEVEL=info
ENV API_VERSION=v1

# Variables de conexión a MySQL (se sobrescriben en docker-compose)
ENV MYSQL_HOST=sql-db2
ENV MYSQL_PORT=3306
ENV MYSQL_DATABASE=trips_db
ENV MYSQL_USER=trips_user
ENV MYSQL_PASSWORD=secure_password

# Configuración adicional
ENV SWAGGER_ENABLED=true
ENV PROJECT_NAME=ms-trips
ENV PROJECT_VERSION=1.0.0

# Cambiar a usuario no-root
USER trips

# Exponer puerto
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8002/api/v1/health || exit 1

# Comando por defecto
CMD ["node", "src/server.js"]

# ========================================
# Build instructions:
# ========================================
# docker build -t ms-trips .
# docker run -p 8002:8002 --env-file .env ms-trips
#
# Con docker-compose (recomendado):
# cd infra && docker-compose up ms-trips
# ========================================
