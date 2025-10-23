#!/bin/bash

# ============================================
# Setup Script para Máquina de Ingesta
# ============================================
# Este script configura la máquina de ingesta para conectarse
# a las máquinas de producción via Load Balancer
#
# Infraestructura:
# - Load Balancer: LB-Prod-308585431.us-east-1.elb.amazonaws.com
# - Producción 1: 54.161.1.30
# - Producción 2: 52.200.140.111
# - Ingesta: 52.73.204.244
# ============================================

set -e  # Exit on error

echo "============================================"
echo "🚀 CONFIGURACIÓN MÁQUINA DE INGESTA"
echo "============================================"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================
# 1. Verificar que estamos en la máquina de ingesta
# ============================================
echo -e "\n${YELLOW}[1/5]${NC} Verificando máquina..."

PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "unknown")
echo "IP Pública de esta máquina: ${PUBLIC_IP}"

if [ "$PUBLIC_IP" != "52.73.204.244" ]; then
    echo -e "${YELLOW}⚠️  ADVERTENCIA: Esta no parece ser la máquina de ingesta (IP esperada: 52.73.204.244)${NC}"
    echo "¿Deseas continuar de todos modos? (s/n)"
    read -r response
    if [[ ! "$response" =~ ^[Ss]$ ]]; then
        echo "Instalación cancelada."
        exit 0
    fi
fi

# ============================================
# 2. Verificar estructura del proyecto
# ============================================
echo -e "\n${YELLOW}[2/5]${NC} Verificando estructura del proyecto..."

if [ ! -d "/root/bus-mvp/data-ingestion" ]; then
    echo -e "${RED}❌ ERROR: Directorio /root/bus-mvp/data-ingestion no encontrado${NC}"
    echo "Asegúrate de estar en el directorio correcto."
    exit 1
fi

cd /root/bus-mvp

# ============================================
# 3. Configurar archivo .env
# ============================================
echo -e "\n${YELLOW}[3/5]${NC} Configurando archivo .env..."

# Backup del .env existente si existe
if [ -f ".env" ]; then
    echo "Creando backup del .env existente..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Crear/actualizar .env con las configuraciones necesarias
cat > .env << 'EOF'
# ========================================
# Bus MVP - Configuración Máquina de Ingesta
# ========================================
# Generado automáticamente por setup_ingestion_machine.sh
# Fecha: $(date)

# ========================================
# AWS CONFIGURATION
# ========================================
# IMPORTANTE: Estas credenciales deben ser actualizadas con tus credenciales de AWS Academy
# Ejecuta: bash data-ingestion/setup_aws_academy.sh para configurarlas automáticamente

AWS_ACCESS_KEY_ID=ASIAVC25COXH2KQQXSDC
AWS_SECRET_ACCESS_KEY=imC3zYVUXzbHumRMoAptEvT5awIu8lQnkcjuUTcZ
AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjEI7//////////wEaCXVzLXdlc3QtMiJGMEQCIFN72hGTk0pGYndbjPLB8ov9iC4nbIkM5WcHh6vv1KH8AiBFRbtp09LHySn31LYy62VIzAoTvcJZhXSZgMrfZ1Xyriq6AghHEAIaDDM0OTY5ODE2MDA3OSIMRW6TvnmiI/MDMzj5KpcCICpPS14q8zobHnyi+2h7NdPk1OnilnYUNjF4w/1scnXOiNuZkXvDVnx9vfGX3Vrn+gaLlpGGYMjNJXOlwgMKZ0EqD1k3t0v7rIH5ze6xD4AMA3hZHyECIBq9mfwDfoHVM9CsSpyPqR8TiI1DbUmvQNINkKWhK+2MdNi32r0kbKjELS2r/yl2gu/nL/IL1Un/5Ixfk//X3yG2RscIl99BC4q6cF+oVG4ZrKsXelkDXtyLiBSPj9W8oic3DPfViLdijJ+6huo8AtogffdWSGgiPbCsF/Hi+cJTHmgTgcn+z1Wb+5cgTCmcJkebbPfGsSG8c3DQaZiCXJFy9s+c4LCHU/4yvxIrjbJALKJ71VexvTtLQ+7s6EDRMIXj6McGOp4B67zmYxABuy7KOfEZso2jbxx4OXvpuJELwfXpUX1a75Oq3E3Yx7/KHthBbTC7dUGlizEzKdOFyRf8oB0HKlnmBzgXJgubsNvYSMNuBRFbEdDBsk/I+T+uVPTFqcOxPsUYD/jiM+YG2TdZ2N4qpPwLd7JBGwfk5HOyfVrrXzs5bNWt3Wsb5Obs1vMoxtl+ZxaulHqaDhup/ckWTpXOxa0=
AWS_DEFAULT_REGION=us-east-1

# ========================================
# S3 CONFIGURATION
# ========================================
S3_BUCKET=bus-mvp-datalake-1

# ========================================
# GLUE & ATHENA CONFIGURATION
# ========================================
GLUE_DATABASE=bus_mvp_db
ATHENA_OUTPUT_LOCATION=s3://bus-mvp-datalake-1/athena-results/

# ========================================
# DATA INGESTION - APIs URLs
# ========================================
# Todas las URLs apuntan al Load Balancer que distribuye
# las peticiones entre las 2 máquinas de producción

# Load Balancer DNS
LOAD_BALANCER_DNS=LB-Prod-308585431.us-east-1.elb.amazonaws.com

# API URLs (via Load Balancer)
PASSENGERS_API_URL=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8001/api/v1
TRIPS_API_URL=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8002/api/v1
TICKETS_API_URL=http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8003/api/v1

# ========================================
# PRODUCTION MACHINES IPs (Para referencia)
# ========================================
# Producción 1: 54.161.1.30
# Producción 2: 52.200.140.111
# Ingesta: 52.73.204.244
EOF

echo -e "${GREEN}✅ Archivo .env configurado${NC}"

# ============================================
# 4. Verificar conectividad con Load Balancer
# ============================================
echo -e "\n${YELLOW}[4/5]${NC} Verificando conectividad con Load Balancer..."

LB_URL="http://LB-Prod-308585431.us-east-1.elb.amazonaws.com:8001/api/v1/passengers"

echo "Probando conexión a: ${LB_URL}"
if curl -s --connect-timeout 10 --max-time 30 "${LB_URL}?page=1&limit=1" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Conexión exitosa con Load Balancer${NC}"
else
    echo -e "${YELLOW}⚠️  No se pudo conectar con el Load Balancer${NC}"
    echo "Posibles causas:"
    echo "  - El Load Balancer no está activo"
    echo "  - Los security groups no permiten tráfico desde esta IP"
    echo "  - Los microservicios no están ejecutándose"
    echo ""
    echo "Continúa la configuración, pero verifica estos puntos antes de ejecutar la ingesta."
fi

# ============================================
# 5. Mostrar instrucciones finales
# ============================================
echo -e "\n${YELLOW}[5/5]${NC} Configuración completada"

echo ""
echo "============================================"
echo -e "${GREEN}✅ CONFIGURACIÓN COMPLETADA${NC}"
echo "============================================"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo ""
echo "1. Actualizar credenciales de AWS (si expiraron):"
echo "   cd /root/bus-mvp/data-ingestion"
echo "   bash setup_aws_academy.sh"
echo ""
echo "2. Ejecutar la ingesta de datos:"
echo "   cd /root/bus-mvp/data-ingestion"
echo "   docker-compose up -d"
echo ""
echo "3. Ver logs de ingesta:"
echo "   docker logs -f passengers-ingestion"
echo "   docker logs -f trips-ingestion"
echo "   docker logs -f tickets-ingestion"
echo ""
echo "4. Para auto-sincronización (cada 5 minutos):"
echo "   bash start_auto_sync.sh"
echo ""
echo "============================================"
echo -e "${GREEN}🎉 ¡Listo para ingestar datos!${NC}"
echo "============================================"
