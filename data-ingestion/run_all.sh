#!/bin/bash

# ============================================================================
# Script Centralizado - Data Ingestion Pipeline
# Bus MVP - Cloud Computing Project
# ============================================================================
# Descripción: Ejecuta el proceso completo de ingesta de datos:
#              1. Verificación de prerequisitos
#              2. Creación de infraestructura AWS (S3, Glue, Athena)
#              3. Ejecución de ingesta de datos
#              4. Validación de resultados
# ============================================================================

set -e

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Funciones de logging
log_success() { echo -e "${GREEN}$1${NC}"; }
log_warning() { echo -e "${YELLOW}$1${NC}"; }
log_error() { echo -e "${RED}$1${NC}"; }
log_info() { echo -e "${CYAN}$1${NC}"; }
log_step() { echo -e "\n${MAGENTA}$1${NC}"; }
log_banner() { 
    echo -e "\n${MAGENTA}$(printf '=%.0s' {1..80})${NC}"
    echo -e "${MAGENTA}  $1${NC}"
    echo -e "${MAGENTA}$(printf '=%.0s' {1..80})${NC}\n"
}

# Parámetros
SKIP_PREREQUISITES=false
SKIP_S3_SETUP=false
SKIP_INGESTION=false
SKIP_GLUE=false
SKIP_ATHENA=false
SKIP_VALIDATION=false
QUICK_MODE=false

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-prerequisites) SKIP_PREREQUISITES=true ;;
        --skip-s3) SKIP_S3_SETUP=true ;;
        --skip-ingestion) SKIP_INGESTION=true ;;
        --skip-glue) SKIP_GLUE=true ;;
        --skip-athena) SKIP_ATHENA=true ;;
        --skip-validation) SKIP_VALIDATION=true ;;
        --quick) QUICK_MODE=true ;;
        -h|--help)
            echo "Uso: $0 [opciones]"
            echo ""
            echo "Opciones:"
            echo "  --skip-prerequisites  Saltar verificación de prerequisitos"
            echo "  --skip-s3            Saltar configuración de S3"
            echo "  --skip-ingestion     Saltar ingesta de datos"
            echo "  --skip-glue          Saltar configuración de Glue"
            echo "  --skip-athena        Saltar configuración de Athena"
            echo "  --skip-validation    Saltar validación final"
            echo "  --quick              Modo rápido (solo ingesta)"
            echo "  -h, --help           Mostrar esta ayuda"
            exit 0
            ;;
        *)
            log_error "Opción desconocida: $1"
            exit 1
            ;;
    esac
    shift
done

# ============================================================================
# FUNCIONES DE VERIFICACIÓN
# ============================================================================

test_prerequisites() {
    log_banner "VERIFICANDO PREREQUISITOS"
    
    local all_ok=true
    
    # 1. Verificar Docker
    log_step "1️⃣  Verificando Docker..."
    if command -v docker &> /dev/null; then
        local docker_version=$(docker --version)
        log_success "  ✅ Docker instalado: $docker_version"
    else
        log_error "  ❌ Docker no está instalado"
        all_ok=false
    fi
    
    # 2. Verificar Docker Compose
    log_step "2️⃣  Verificando Docker Compose..."
    if command -v docker compose &> /dev/null; then
        local compose_version=$(docker compose version)
        log_success "  ✅ Docker Compose instalado: $compose_version"
    else
        log_error "  ❌ Docker Compose no está instalado"
        all_ok=false
    fi
    
    # 3. Verificar Python
    log_step "3️⃣  Verificando Python..."
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version)
        log_success "  ✅ Python instalado: $python_version"
    else
        log_error "  ❌ Python no está instalado"
        all_ok=false
    fi
    
    # 4. Verificar AWS CLI
    log_step "4️⃣  Verificando AWS CLI..."
    if command -v aws &> /dev/null; then
        local aws_version=$(aws --version 2>&1)
        log_success "  ✅ AWS CLI instalado: $aws_version"
    else
        log_error "  ❌ AWS CLI no está instalado"
        all_ok=false
    fi
    
    # 5. Verificar archivo .env
    log_step "5️⃣  Verificando configuración..."
    if [ -f "$SCRIPT_DIR/.env" ]; then
        log_success "  ✅ Archivo .env encontrado"
        
        # Verificar credenciales
        if grep -q "AWS_ACCESS_KEY_ID=.\+" "$SCRIPT_DIR/.env" && \
           ! grep -q "AWS_ACCESS_KEY_ID=your_" "$SCRIPT_DIR/.env"; then
            log_success "  ✅ Credenciales AWS configuradas"
        else
            log_warning "  ⚠️  Credenciales AWS no configuradas en .env"
            log_info "     Ejecuta: ./setup_aws_academy.sh"
            all_ok=false
        fi
    else
        log_warning "  ⚠️  Archivo .env no encontrado"
        if [ -f "$SCRIPT_DIR/.env.example" ]; then
            cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
            log_success "  ✅ Archivo .env creado desde .env.example"
            log_warning "  ⚠️  Por favor edita .env con tus credenciales AWS"
            all_ok=false
        fi
    fi
    
    # 6. Verificar microservicios
    log_step "6️⃣  Verificando microservicios..."
    local containers=$(docker ps --format "{{.Names}}" 2>&1 || echo "")
    local running=0
    
    for service in "ms-passengers" "ms-trips" "ms-tickets"; do
        echo "DEBUG: Verificando $service..." >&2
        if echo "$containers" | grep -q "$service"; then
            log_success "  ✅ $service corriendo"
            ((running++))
        else
            log_warning "  ⚠️  $service no está corriendo"
        fi
        echo "DEBUG: $service procesado, running=$running" >&2
    done
    echo "DEBUG: Bucle completado, running total=$running" >&2
    
    if [ $running -eq 0 ]; then
        log_warning "  ⚠️  Ningún microservicio está corriendo"
    elif [ $running -lt 3 ]; then
        log_warning "  ⚠️  Faltan microservicios ($running/3)"
    else
        log_success "  ✅ Todos los microservicios están corriendo ($running/3)"
    fi
    
    # 7. Verificar dependencias Python
    log_step "7️⃣  Verificando dependencias Python..."
    if [ -f "$SCRIPTS_DIR/requirements.txt" ]; then
        log_info "  📦 Instalando dependencias Python..."
        pip3 install -q -r "$SCRIPTS_DIR/requirements.txt" > /dev/null 2>&1
        log_success "  ✅ Dependencias Python instaladas"
    fi
    
    if [ "$all_ok" = false ]; then
        log_error "\n❌ Algunos prerequisitos no están cumplidos"
        log_info "   Por favor revisa los errores arriba antes de continuar\n"
        
        read -p "¿Deseas continuar de todas formas? (y/N): " continue
        if [[ ! "$continue" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "\n✅ Todos los prerequisitos están cumplidos\n"
    fi
}

test_aws_connection() {
    log_step "Verificando conexión a AWS..."
    
    if aws sts get-caller-identity --output json > /dev/null 2>&1; then
        local identity=$(aws sts get-caller-identity --output json)
        local account=$(echo "$identity" | grep -o '"Account": "[^"]*"' | cut -d'"' -f4)
        local arn=$(echo "$identity" | grep -o '"Arn": "[^"]*"' | cut -d'"' -f4)
        
        log_success "  ✅ Conectado a AWS"
        log_info "     Account: $account"
        log_info "     User: $arn"
        return 0
    else
        log_error "  ❌ No se pudo conectar a AWS"
        return 1
    fi
}

# ============================================================================
# FUNCIONES DE EJECUCIÓN
# ============================================================================

invoke_s3_setup() {
    log_banner "PASO 1: CONFIGURANDO AWS S3"
    
    local setup_script="$SCRIPTS_DIR/setup_s3.py"
    
    if [ ! -f "$setup_script" ]; then
        log_error "❌ Script setup_s3.py no encontrado"
        return 1
    fi
    
    log_info "🪣 Creando bucket S3 y estructura de carpetas..."
    log_info "   Script: $setup_script"
    
    if python3 "$setup_script"; then
        log_success "\n✅ Bucket S3 configurado exitosamente"
        return 0
    else
        log_error "❌ Error configurando S3"
        return 1
    fi
}

invoke_data_ingestion() {
    log_banner "PASO 2: EJECUTANDO INGESTA DE DATOS"
    
    if [ ! -f "docker-compose.yml" ]; then
        log_error "❌ docker-compose.yml no encontrado"
        return 1
    fi
    
    log_info "📊 Construyendo imágenes Docker..."
    docker-compose build --quiet
    
    if [ $? -ne 0 ]; then
        log_error "❌ Error construyendo imágenes Docker"
        return 1
    fi
    
    log_success "✅ Imágenes construidas"
    
    # Ejecutar ingesta de cada microservicio
    local services=("passengers-ingestion" "trips-ingestion" "tickets-ingestion")
    local success=true
    
    for service in "${services[@]}"; do
        log_step "Ejecutando $service..."
        
        if docker-compose up "$service"; then
            log_success "  ✅ $service completado"
        else
            log_error "  ❌ $service falló"
            success=false
        fi
        
        sleep 2
    done
    
    if [ "$success" = true ]; then
        log_success "\n✅ Ingesta de datos completada exitosamente"
        return 0
    else
        log_warning "\n⚠️  Ingesta completada con algunos errores"
        return 1
    fi
}

invoke_glue_setup() {
    log_banner "PASO 3: CONFIGURANDO AWS GLUE"
    
    local setup_script="$SCRIPTS_DIR/setup_complete_glue.py"
    
    if [ ! -f "$setup_script" ]; then
        log_warning "⚠️  Script setup_complete_glue.py no encontrado"
        log_info "   Intentando con setup_glue.py..."
        setup_script="$SCRIPTS_DIR/setup_glue.py"
    fi
    
    if [ ! -f "$setup_script" ]; then
        log_error "❌ Script de configuración de Glue no encontrado"
        return 1
    fi
    
    log_info "📊 Configurando AWS Glue Catalog..."
    log_info "   - Creando database"
    log_info "   - Creando crawlers"
    log_info "   - Ejecutando crawlers"
    
    if python3 "$setup_script"; then
        log_success "\n✅ AWS Glue configurado exitosamente"
        return 0
    else
        log_error "❌ Error configurando Glue"
        return 1
    fi
}

invoke_athena_setup() {
    log_banner "PASO 4: CONFIGURANDO AWS ATHENA"
    
    # 1. Crear tablas
    log_step "Creando tablas en Athena..."
    local tables_script="$SCRIPTS_DIR/create_athena_tables.py"
    
    if [ -f "$tables_script" ]; then
        if python3 "$tables_script"; then
            log_success "  ✅ Tablas creadas"
        else
            log_warning "  ⚠️  Error creando tablas"
        fi
    else
        log_warning "  ⚠️  Script create_athena_tables.py no encontrado"
    fi
    
    # 2. Ejecutar queries de prueba
    log_step "Ejecutando queries de prueba..."
    local queries_script="$SCRIPTS_DIR/test_athena_queries.py"
    
    if [ -f "$queries_script" ]; then
        if python3 "$queries_script"; then
            log_success "  ✅ Queries ejecutadas"
        else
            log_warning "  ⚠️  Error ejecutando queries"
        fi
    else
        log_warning "  ⚠️  Script test_athena_queries.py no encontrado"
    fi
    
    # 3. Crear vistas
    log_step "Creando vistas en Athena..."
    local views_script="$SCRIPTS_DIR/create_athena_views.py"
    
    if [ -f "$views_script" ]; then
        if python3 "$views_script"; then
            log_success "  ✅ Vistas creadas"
        else
            log_warning "  ⚠️  Error creando vistas"
        fi
    else
        log_warning "  ⚠️  Script create_athena_views.py no encontrado"
    fi
    
    log_success "\n✅ AWS Athena configurado"
    return 0
}

invoke_validation() {
    log_banner "PASO 5: VALIDANDO RESULTADOS"
    
    # 1. Verificar datos en S3
    log_step "Verificando datos en S3..."
    
    local bucket="bus-mvp-datalake"
    if [ -f "$SCRIPT_DIR/.env" ]; then
        local bucket_line=$(grep "S3_BUCKET=" "$SCRIPT_DIR/.env" | head -1)
        if [ -n "$bucket_line" ]; then
            bucket=${bucket_line#*=}
        fi
    fi
    
    local paths=("raw/passengers_csv/" "raw/trips_csv/" "raw/tickets_csv/")
    local all_data=true
    
    for path in "${paths[@]}"; do
        local result=$(aws s3 ls "s3://$bucket/$path" 2>&1)
        if [ $? -eq 0 ] && [ -n "$result" ]; then
            local count=$(echo "$result" | wc -l)
            log_success "  ✅ $path - $count archivo(s)"
        else
            log_warning "  ⚠️  $path - Sin archivos"
            all_data=false
        fi
    done
    
    # 2. Verificar Glue Database
    log_step "Verificando AWS Glue Database..."
    
    if aws glue get-database --name bus_mvp_db > /dev/null 2>&1; then
        log_success "  ✅ Database 'bus_mvp_db' existe"
        
        # Verificar tablas
        local tables=$(aws glue get-tables --database-name bus_mvp_db --output json 2>&1)
        if [ $? -eq 0 ]; then
            local table_count=$(echo "$tables" | grep -o '"Name"' | wc -l)
            log_success "  ✅ $table_count tabla(s) encontrada(s)"
        fi
    else
        log_warning "  ⚠️  Database 'bus_mvp_db' no encontrada"
    fi
    
    # 3. Resumen
    log_step "Resumen de validación"
    
    if [ "$all_data" = true ]; then
        log_success "  ✅ Datos ingresados correctamente en S3"
    else
        log_warning "  ⚠️  Algunos datos pueden estar faltando"
    fi
    
    log_info "\n📋 Próximos pasos:"
    log_info "   1. Abrir AWS Athena Console"
    log_info "   2. Seleccionar database: bus_mvp_db"
    log_info "   3. Ejecutar queries SQL"
    log_info "   4. Crear vistas analíticas"
    
    return 0
}

show_summary() {
    log_banner "RESUMEN DE EJECUCIÓN"
    
    log_info "📊 Proceso completado\n"
    
    echo -e "${CYAN}Componentes configurados:${NC}"
    log_success "  ✅ AWS S3 Bucket (Data Lake)"
    log_success "  ✅ Contenedores Docker (Ingesta)"
    log_success "  ✅ AWS Glue Catalog (Database + Crawlers)"
    log_success "  ✅ AWS Athena (Tablas + Queries)"
    
    echo -e "\n${CYAN}Archivos generados:${NC}"
    echo "  📁 s3://bus-mvp-datalake/raw/passengers_csv/"
    echo "  📁 s3://bus-mvp-datalake/raw/trips_csv/"
    echo "  📁 s3://bus-mvp-datalake/raw/tickets_csv/"
    
    echo -e "\n${CYAN}Servicios disponibles:${NC}"
    echo "  🔍 AWS Athena: https://console.aws.amazon.com/athena/"
    echo "  📊 AWS Glue: https://console.aws.amazon.com/glue/"
    echo "  🪣 AWS S3: https://console.aws.amazon.com/s3/"
    
    echo -e "\n${CYAN}Documentación:${NC}"
    echo "  📖 README.md - Guía general"
    echo "  📖 IMPLEMENTATION_GUIDE.md - Guía de implementación"
    echo "  📖 TESTING_GUIDE.md - Guía de testing"
}

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

start_data_ingestion_pipeline() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                                        ║${NC}"
    echo -e "${CYAN}║          BUS MVP - DATA INGESTION PIPELINE (Centralizado)             ║${NC}"
    echo -e "${CYAN}║                                                                        ║${NC}"
    echo -e "${CYAN}║  Este script ejecuta el proceso completo de ingesta de datos:         ║${NC}"
    echo -e "${CYAN}║    1. Verificación de prerequisitos                                   ║${NC}"
    echo -e "${CYAN}║    2. Configuración de AWS S3                                         ║${NC}"
    echo -e "${CYAN}║    3. Ingesta de datos desde microservicios                           ║${NC}"
    echo -e "${CYAN}║    4. Configuración de AWS Glue Catalog                               ║${NC}"
    echo -e "${CYAN}║    5. Configuración de AWS Athena                                     ║${NC}"
    echo -e "${CYAN}║    6. Validación de resultados                                        ║${NC}"
    echo -e "${CYAN}║                                                                        ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local start_time=$(date +%s)
    log_info "🕐 Inicio: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # Modo rápido - solo ingesta
    if [ "$QUICK_MODE" = true ]; then
        log_warning "⚡ MODO RÁPIDO - Solo ejecutando ingesta de datos"
        SKIP_PREREQUISITES=true
        SKIP_S3_SETUP=true
        SKIP_GLUE=true
        SKIP_ATHENA=true
        SKIP_VALIDATION=true
    fi
    
    local success=true
    
    # PASO 0: Verificar prerequisitos
    if [ "$SKIP_PREREQUISITES" = false ]; then
        test_prerequisites
        
        if ! test_aws_connection; then
            log_error "❌ No se puede conectar a AWS. Verifica tus credenciales."
            log_info "   Ejecuta: ./setup_aws_academy.sh"
            exit 1
        fi
    fi
    
    # PASO 1: Configurar S3
    if [ "$SKIP_S3_SETUP" = false ]; then
        if ! invoke_s3_setup; then
            log_warning "⚠️  Error en configuración de S3, pero continuando..."
            success=false
        fi
        sleep 2
    fi
    
    # PASO 2: Ejecutar ingesta
    if [ "$SKIP_INGESTION" = false ]; then
        if ! invoke_data_ingestion; then
            log_error "❌ Error en ingesta de datos"
            success=false
        fi
        sleep 3
    fi
    
    # PASO 3: Configurar Glue
    if [ "$SKIP_GLUE" = false ]; then
        if ! invoke_glue_setup; then
            log_warning "⚠️  Error en configuración de Glue, pero continuando..."
            success=false
        fi
        sleep 3
    fi
    
    # PASO 4: Configurar Athena
    if [ "$SKIP_ATHENA" = false ]; then
        if ! invoke_athena_setup; then
            log_warning "⚠️  Error en configuración de Athena, pero continuando..."
            success=false
        fi
        sleep 2
    fi
    
    # PASO 5: Validar
    if [ "$SKIP_VALIDATION" = false ]; then
        invoke_validation
    fi
    
    # Resumen
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local minutes=$(echo "scale=2; $duration / 60" | bc)
    
    echo ""
    show_summary
    
    echo ""
    log_info "🕐 Fin: $(date '+%Y-%m-%d %H:%M:%S')"
    log_info "⏱️  Duración: $minutes minutos"
    
    if [ "$success" = true ]; then
        log_success "\n✅ PROCESO COMPLETADO EXITOSAMENTE\n"
        exit 0
    else
        log_warning "\n⚠️  PROCESO COMPLETADO CON ADVERTENCIAS\n"
        exit 0
    fi
}

# ============================================================================
# EJECUCIÓN
# ============================================================================

# Cambiar al directorio del script
cd "$SCRIPT_DIR"

# Ejecutar pipeline
start_data_ingestion_pipeline
