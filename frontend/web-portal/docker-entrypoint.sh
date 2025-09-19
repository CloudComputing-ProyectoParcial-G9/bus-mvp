#!/bin/sh
# ========================================
# Docker Entrypoint para Frontend SPA
# ========================================
#
# Script de inicialización que prepara el entorno
# antes de iniciar nginx
#
# TODO (@F): Ajustar según necesidades específicas

set -e

# Función para logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Iniciando Frontend SPA Bus MVP..."

# ========================================
# VALIDACIÓN DE VARIABLES DE ENTORNO
# ========================================

# Variables requeridas
REQUIRED_VARS="VITE_API_BASE_URL"

for var in $REQUIRED_VARS; do
    if [ -z "$(eval echo \$$var)" ]; then
        log "ERROR: Variable de entorno requerida $var no está definida"
        exit 1
    fi
done

log "Variables de entorno validadas correctamente"

# ========================================
# CONFIGURACIÓN DINÁMICA
# ========================================

# Crear archivo de configuración JavaScript con variables de entorno
# Esto permite usar variables de entorno en runtime
cat > /usr/share/nginx/html/config.js << EOF
window.ENV = {
    API_BASE_URL: '${VITE_API_BASE_URL:-http://localhost:8080}',
    APP_NAME: '${VITE_APP_NAME:-Bus MVP Portal}',
    APP_VERSION: '${VITE_APP_VERSION:-1.0.0}',
    ENVIRONMENT: '${VITE_ENVIRONMENT:-production}',
    LOG_LEVEL: '${VITE_LOG_LEVEL:-error}',
    ENABLE_ANALYTICS: ${VITE_ENABLE_ANALYTICS:-false}
};
EOF

log "Archivo de configuración dinámico creado"

# ========================================
# CONFIGURACIÓN DE NGINX
# ========================================

# Crear directorio de logs si no existe
mkdir -p /var/log/nginx

# Configurar nginx con variables de entorno
if [ -f "/etc/nginx/templates/default.conf.template" ]; then
    log "Procesando template de nginx..."
    envsubst '${VITE_API_BASE_URL} ${LB_PORT}' \
        < /etc/nginx/templates/default.conf.template \
        > /etc/nginx/conf.d/default.conf
fi

# ========================================
# VALIDACIÓN DE ARCHIVOS
# ========================================

# Verificar que exista index.html
if [ ! -f "/usr/share/nginx/html/index.html" ]; then
    log "ERROR: index.html no encontrado"
    exit 1
fi

# Verificar configuración de nginx
nginx -t || {
    log "ERROR: Configuración de nginx inválida"
    exit 1
}

log "Configuración de nginx validada"

# ========================================
# CONFIGURACIÓN DE PERMISOS
# ========================================

# Asegurar permisos correctos para archivos estáticos
find /usr/share/nginx/html -type f -exec chmod 644 {} \;
find /usr/share/nginx/html -type d -exec chmod 755 {} \;

log "Permisos configurados correctamente"

# ========================================
# HEALTH CHECK INICIAL
# ========================================

# Función para verificar salud del contenedor
health_check() {
    log "Ejecutando health check inicial..."
    
    # Verificar que nginx puede iniciar
    nginx -t >/dev/null 2>&1 || {
        log "ERROR: Nginx no puede iniciar"
        return 1
    }
    
    # Verificar archivos críticos
    [ -f "/usr/share/nginx/html/index.html" ] || {
        log "ERROR: index.html no encontrado"
        return 1
    }
    
    [ -f "/usr/share/nginx/html/config.js" ] || {
        log "ERROR: config.js no encontrado"
        return 1
    }
    
    log "Health check inicial exitoso"
    return 0
}

health_check || exit 1

# ========================================
# CONFIGURACIÓN DE SEÑALES
# ========================================

# Función para manejo de señales
signal_handler() {
    log "Recibida señal de terminación, cerrando gracefully..."
    nginx -s quit
    wait $!
    log "Nginx cerrado correctamente"
    exit 0
}

# Configurar handlers para señales
trap signal_handler SIGTERM SIGINT

# ========================================
# MODO DEBUG (opcional)
# ========================================

if [ "${VITE_DEBUG_MODE:-false}" = "true" ]; then
    log "Modo debug habilitado"
    log "Variables de entorno:"
    env | grep -E '^(VITE_|REACT_APP_|VUE_APP_|NEXT_PUBLIC_)' | sort
    
    log "Archivos en /usr/share/nginx/html:"
    ls -la /usr/share/nginx/html/
    
    log "Configuración de nginx:"
    cat /etc/nginx/conf.d/default.conf
fi

# ========================================
# INICIALIZACIÓN COMPLETADA
# ========================================

log "Inicialización completada, iniciando nginx..."
log "Frontend SPA disponible en puerto 3000"
log "API Base URL: ${VITE_API_BASE_URL}"

# Ejecutar comando pasado como argumentos o nginx por defecto
if [ "$1" = "nginx" ]; then
    exec "$@"
else
    exec nginx -g "daemon off;"
fi
