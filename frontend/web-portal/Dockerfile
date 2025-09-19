# Dockerfile para Frontend SPA
# ========================================
#
# Multi-stage build para optimizar tamaño de imagen
# Compatible con React, Vue, Angular, Next.js, etc.
#
# TODO (@F): Ajustar según framework específico elegido

# ========================================
# STAGE 1: Build Stage
# ========================================
FROM node:18-alpine AS builder

# Información de la imagen
LABEL maintainer="Bus MVP Team <team@busmvp.com>"
LABEL description="Frontend SPA para sistema Bus MVP"
LABEL version="1.0.0"

# Instalar dependencias del sistema
RUN apk add --no-cache \
    git \
    python3 \
    make \
    g++

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración de dependencias
COPY package*.json ./
# COPY yarn.lock ./  # Si usas Yarn
# COPY pnpm-lock.yaml ./  # Si usas PNPM

# Instalar dependencias
RUN npm ci --only=production --silent

# Copiar código fuente
COPY . .

# Variables de entorno para build
ARG NODE_ENV=production
ARG VITE_API_BASE_URL=http://localhost:8080
ARG VITE_APP_NAME="Bus MVP Portal"
ARG VITE_APP_VERSION="1.0.0"

ENV NODE_ENV=$NODE_ENV
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_NAME=$VITE_APP_NAME
ENV VITE_APP_VERSION=$VITE_APP_VERSION

# Construir aplicación para producción
RUN npm run build

# ========================================
# STAGE 2: Production Stage
# ========================================
FROM nginx:1.25-alpine AS production

# Instalar dependencias adicionales
RUN apk add --no-cache \
    curl \
    ca-certificates

# Crear usuario no-root
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# Configurar nginx
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Crear directorios necesarios
RUN mkdir -p /var/log/nginx /var/cache/nginx/client_temp && \
    chown -R appuser:appgroup /var/log/nginx /var/cache/nginx /usr/share/nginx/html && \
    chmod -R 755 /var/log/nginx /var/cache/nginx /usr/share/nginx/html

# Script de inicio personalizado
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Configurar permisos
RUN chown appuser:appgroup /docker-entrypoint.sh

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Comando de inicio
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]

# ========================================
# CONFIGURACIONES ALTERNATIVAS
# ========================================

# Para frameworks específicos, descomentar según necesidad:

# ----------------------------------------
# REACT (Create React App)
# ----------------------------------------
# FROM node:18-alpine AS react-builder
# WORKDIR /app
# COPY package*.json ./
# RUN npm ci --silent
# COPY . .
# RUN npm run build
# 
# FROM nginx:1.25-alpine
# COPY --from=react-builder /app/build /usr/share/nginx/html
# EXPOSE 80

# ----------------------------------------
# VUE.JS
# ----------------------------------------
# FROM node:18-alpine AS vue-builder
# WORKDIR /app
# COPY package*.json ./
# RUN npm ci --silent
# COPY . .
# RUN npm run build
# 
# FROM nginx:1.25-alpine
# COPY --from=vue-builder /app/dist /usr/share/nginx/html
# EXPOSE 80

# ----------------------------------------
# ANGULAR
# ----------------------------------------
# FROM node:18-alpine AS angular-builder
# WORKDIR /app
# COPY package*.json ./
# RUN npm ci --silent
# RUN npm install -g @angular/cli
# COPY . .
# RUN ng build --configuration production
# 
# FROM nginx:1.25-alpine
# COPY --from=angular-builder /app/dist /usr/share/nginx/html
# EXPOSE 80

# ----------------------------------------
# NEXT.JS (si se usa como SPA)
# ----------------------------------------
# FROM node:18-alpine AS nextjs-builder
# WORKDIR /app
# COPY package*.json ./
# RUN npm ci --silent
# COPY . .
# RUN npm run build
# RUN npm run export  # Para static export
# 
# FROM nginx:1.25-alpine
# COPY --from=nextjs-builder /app/out /usr/share/nginx/html
# EXPOSE 80

# ----------------------------------------
# SVELTE/SVELTEKIT
# ----------------------------------------
# FROM node:18-alpine AS svelte-builder
# WORKDIR /app
# COPY package*.json ./
# RUN npm ci --silent
# COPY . .
# RUN npm run build
# 
# FROM nginx:1.25-alpine
# COPY --from=svelte-builder /app/build /usr/share/nginx/html
# EXPOSE 80

# ========================================
# VARIABLES DE ENTORNO DISPONIBLES
# ========================================
# 
# Las siguientes variables pueden ser pasadas en build time:
# 
# docker build \
#   --build-arg NODE_ENV=production \
#   --build-arg VITE_API_BASE_URL=https://api.busmvp.com \
#   --build-arg VITE_APP_NAME="Bus MVP Portal" \
#   --build-arg VITE_APP_VERSION="1.0.0" \
#   -t bus-mvp-frontend .
#
# ========================================
# COMANDOS DE CONSTRUCCIÓN Y EJECUCIÓN
# ========================================
#
# Construcción:
# docker build -t bus-mvp-frontend .
#
# Ejecución:
# docker run -d \
#   --name bus-mvp-frontend \
#   -p 3000:3000 \
#   --env-file .env \
#   bus-mvp-frontend
#
# Con Docker Compose:
# docker-compose up --build frontend
#
# ========================================
