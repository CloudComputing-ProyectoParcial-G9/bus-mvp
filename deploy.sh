#!/bin/bash

# ========================================
# Bus MVP - Deploy Script
# ========================================
# Script para facilitar el despliegue del sistema Bus MVP
# Uso: ./deploy.sh [command] [options]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar prerrequisitos
check_prerequisites() {
    log_info "Verificando prerrequisitos..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker no está instalado"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose no está instalado"
        exit 1
    fi
    
    if [ ! -f .env ]; then
        log_warning "Archivo .env no encontrado. Copiando desde .env.example..."
        cp .env.example .env
        log_info "Por favor, edita el archivo .env con los valores correctos"
    fi
    
    log_success "Prerrequisitos verificados"
}

# Construir servicios
build_services() {
    log_info "Construyendo servicios..."
    cd infra
    docker-compose build --no-cache
    cd ..
    log_success "Servicios construidos exitosamente"
}

# Iniciar servicios
start_services() {
    log_info "Iniciando servicios..."
    cd infra
    docker-compose up -d
    cd ..
    log_success "Servicios iniciados"
}

# Parar servicios
stop_services() {
    log_info "Deteniendo servicios..."
    cd infra
    docker-compose down
    cd ..
    log_success "Servicios detenidos"
}

# Reiniciar servicios
restart_services() {
    log_info "Reiniciando servicios..."
    stop_services
    start_services
}

# Ver logs
view_logs() {
    local service=${1:-""}
    cd infra
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$service"
    fi
    cd ..
}

# Verificar estado de servicios
check_health() {
    log_info "Verificando estado de servicios..."
    cd infra
    
    services=("ms-passengers" "ms-trips" "ms-tickets" "ms-history" "ms-analytics")
    ports=(8001 8002 8003 8004 8005)
    
    for i in "${!services[@]}"; do
        service="${services[$i]}"
        port="${ports[$i]}"
        
        if curl -f -s "http://localhost:$port/health" > /dev/null; then
            log_success "$service está saludable (puerto $port)"
        else
            log_error "$service no responde (puerto $port)"
        fi
    done
    
    # Verificar load balancer
    if curl -f -s "http://localhost:8080/health" > /dev/null; then
        log_success "Load balancer está saludable (puerto 8080)"
    else
        log_error "Load balancer no responde (puerto 8080)"
    fi
    
    cd ..
}

# Limpiar sistema
clean_system() {
    log_warning "Esta operación eliminará todos los contenedores, volúmenes e imágenes relacionadas"
    read -p "¿Estás seguro? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Limpiando sistema..."
        cd infra
        docker-compose down -v --rmi all
        cd ..
        log_success "Sistema limpiado"
    else
        log_info "Operación cancelada"
    fi
}

# Mostrar ayuda
show_help() {
    echo "Bus MVP Deploy Script"
    echo
    echo "Uso: $0 [COMANDO] [OPCIONES]"
    echo
    echo "COMANDOS:"
    echo "  build       Construir todas las imágenes Docker"
    echo "  start       Iniciar todos los servicios"
    echo "  stop        Detener todos los servicios"
    echo "  restart     Reiniciar todos los servicios"
    echo "  logs        Ver logs de todos los servicios"
    echo "  logs [svc]  Ver logs de un servicio específico"
    echo "  health      Verificar estado de salud de servicios"
    echo "  clean       Limpiar sistema completo (CUIDADO: elimina datos)"
    echo "  help        Mostrar esta ayuda"
    echo
    echo "EJEMPLOS:"
    echo "  $0 build"
    echo "  $0 start"
    echo "  $0 logs ms-history"
    echo "  $0 health"
    echo
    echo "SERVICIOS DISPONIBLES:"
    echo "  ms-passengers (puerto 8001)"
    echo "  ms-trips (puerto 8002)"
    echo "  ms-tickets (puerto 8003)"
    echo "  ms-history (puerto 8004)"
    echo "  ms-analytics (puerto 8005)"
    echo "  load-balancer (puerto 8080)"
}

# Función principal
main() {
    case "${1:-help}" in
        "build")
            check_prerequisites
            build_services
            ;;
        "start")
            check_prerequisites
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "logs")
            view_logs "$2"
            ;;
        "health")
            check_health
            ;;
        "clean")
            clean_system
            ;;
        "deploy")
            check_prerequisites
            build_services
            start_services
            sleep 10
            check_health
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Ejecutar función principal con todos los argumentos
main "$@"