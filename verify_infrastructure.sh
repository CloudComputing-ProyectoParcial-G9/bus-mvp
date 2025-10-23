#!/bin/bash

# ============================================
# Script de Verificación de Infraestructura
# ============================================
# Verifica la configuración y conectividad entre
# máquinas de producción e ingesta
# ============================================

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "============================================"
echo "🔍 VERIFICACIÓN DE INFRAESTRUCTURA"
echo "============================================"

# ============================================
# 1. Identificar máquina actual
# ============================================
echo -e "\n${BLUE}[1/6]${NC} Identificando máquina actual..."

PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "unknown")
PRIVATE_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4 2>/dev/null || echo "unknown")

echo "  IP Pública: ${PUBLIC_IP}"
echo "  IP Privada: ${PRIVATE_IP}"

# Determinar tipo de máquina
MACHINE_TYPE="unknown"
case "$PUBLIC_IP" in
    "54.161.1.30")
        MACHINE_TYPE="Producción 1"
        ;;
    "52.200.140.111")
        MACHINE_TYPE="Producción 2"
        ;;
    "52.73.204.244")
        MACHINE_TYPE="Ingesta"
        ;;
    *)
        MACHINE_TYPE="Desconocida"
        ;;
esac

echo -e "  Tipo: ${YELLOW}${MACHINE_TYPE}${NC}"

# ============================================
# 2. Verificar archivo .env
# ============================================
echo -e "\n${BLUE}[2/6]${NC} Verificando archivo .env..."

if [ -f ".env" ]; then
    echo -e "  ${GREEN}✅ Archivo .env encontrado${NC}"

    # Verificar variables críticas
    if grep -q "LB-Prod-308585431.us-east-1.elb.amazonaws.com" .env; then
        echo -e "  ${GREEN}✅ Configurado para usar Load Balancer${NC}"
    else
        echo -e "  ${YELLOW}⚠️  No parece estar configurado para Load Balancer${NC}"
    fi

    if grep -q "PASSENGERS_API_URL" .env; then
        PASSENGERS_URL=$(grep "PASSENGERS_API_URL" .env | cut -d'=' -f2)
        echo -e "  Passengers API: ${PASSENGERS_URL}"
    fi

    if grep -q "AWS_ACCESS_KEY_ID" .env; then
        echo -e "  ${GREEN}✅ Credenciales de AWS configuradas${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Credenciales de AWS no encontradas${NC}"
    fi
else
    echo -e "  ${RED}❌ Archivo .env NO encontrado${NC}"
fi

# ============================================
# 3. Verificar conectividad a Load Balancer
# ============================================
echo -e "\n${BLUE}[3/6]${NC} Verificando conectividad a Load Balancer..."

LB_HOST="LB-Prod-308585431.us-east-1.elb.amazonaws.com"

# Test DNS resolution
if host "$LB_HOST" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ DNS del Load Balancer resuelve correctamente${NC}"
    LB_IP=$(host "$LB_HOST" | grep "has address" | head -1 | awk '{print $NF}')
    echo -e "  IP del LB: ${LB_IP}"
else
    echo -e "  ${RED}❌ No se puede resolver DNS del Load Balancer${NC}"
fi

# Test conectividad a puertos
PORTS=(8001 8002 8003 8004 8005)
for PORT in "${PORTS[@]}"; do
    if timeout 5 bash -c "echo >/dev/tcp/${LB_HOST}/${PORT}" 2>/dev/null; then
        echo -e "  ${GREEN}✅ Puerto ${PORT} accesible${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Puerto ${PORT} no accesible${NC}"
    fi
done

# ============================================
# 4. Verificar APIs (si Load Balancer accesible)
# ============================================
echo -e "\n${BLUE}[4/6]${NC} Verificando APIs..."

# Test Passengers API
if curl -s --connect-timeout 5 "http://${LB_HOST}:8001/api/v1/passengers?page=1&limit=1" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Passengers API respondiendo${NC}"
else
    echo -e "  ${YELLOW}⚠️  Passengers API no responde${NC}"
fi

# Test Trips API
if curl -s --connect-timeout 5 "http://${LB_HOST}:8002/api/v1/trips" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Trips API respondiendo${NC}"
else
    echo -e "  ${YELLOW}⚠️  Trips API no responde${NC}"
fi

# Test Tickets API (diferente path)
if curl -s --connect-timeout 5 "http://${LB_HOST}:8003/tickets" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Tickets API respondiendo${NC}"
else
    echo -e "  ${YELLOW}⚠️  Tickets API no responde${NC}"
fi

# ============================================
# 5. Verificar Docker (si aplica)
# ============================================
echo -e "\n${BLUE}[5/6]${NC} Verificando Docker..."

if command -v docker &> /dev/null; then
    echo -e "  ${GREEN}✅ Docker instalado${NC}"

    # Ver contenedores corriendo
    RUNNING_CONTAINERS=$(docker ps --format '{{.Names}}' 2>/dev/null | wc -l)
    echo -e "  Contenedores corriendo: ${RUNNING_CONTAINERS}"

    if [ "$RUNNING_CONTAINERS" -gt 0 ]; then
        docker ps --format 'table {{.Names}}\t{{.Status}}' | while read line; do
            echo -e "    $line"
        done
    fi
else
    echo -e "  ${YELLOW}⚠️  Docker no instalado${NC}"
fi

# ============================================
# 6. Verificar AWS CLI (para máquina de ingesta)
# ============================================
echo -e "\n${BLUE}[6/6]${NC} Verificando AWS CLI..."

if command -v aws &> /dev/null; then
    echo -e "  ${GREEN}✅ AWS CLI instalado${NC}"

    # Test credenciales
    if aws sts get-caller-identity > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Credenciales de AWS válidas${NC}"

        # Test acceso a S3
        if aws s3 ls s3://bus-mvp-datalake-1/ > /dev/null 2>&1; then
            echo -e "  ${GREEN}✅ Acceso a S3 bucket confirmado${NC}"
        else
            echo -e "  ${YELLOW}⚠️  No se puede acceder al S3 bucket${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠️  Credenciales de AWS no válidas o expiradas${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠️  AWS CLI no instalado${NC}"
fi

# ============================================
# Resumen final
# ============================================
echo ""
echo "============================================"
echo -e "${GREEN}✅ VERIFICACIÓN COMPLETADA${NC}"
echo "============================================"
echo ""
echo "📋 RESUMEN:"
echo "  Máquina: ${MACHINE_TYPE} (${PUBLIC_IP})"
echo ""

# Recomendaciones basadas en el tipo de máquina
case "$MACHINE_TYPE" in
    "Producción 1"|"Producción 2")
        echo "📌 RECOMENDACIONES PARA PRODUCCIÓN:"
        echo "  1. Asegúrate de que todos los microservicios estén corriendo"
        echo "  2. Verifica que el frontend esté accesible"
        echo "  3. Verifica Security Groups para permitir tráfico del LB"
        echo ""
        echo "🚀 COMANDOS ÚTILES:"
        echo "  docker-compose ps                 # Ver servicios"
        echo "  docker-compose logs -f            # Ver logs"
        echo "  docker-compose restart            # Reiniciar servicios"
        ;;
    "Ingesta")
        echo "📌 RECOMENDACIONES PARA INGESTA:"
        echo "  1. Actualiza credenciales de AWS si expiraron:"
        echo "     cd data-ingestion && bash setup_aws_academy.sh"
        echo ""
        echo "  2. Ejecuta la ingesta:"
        echo "     cd data-ingestion && docker-compose up -d"
        echo ""
        echo "  3. Configura auto-sync (opcional):"
        echo "     cd data-ingestion && bash start_auto_sync.sh"
        echo ""
        echo "🚀 COMANDOS ÚTILES:"
        echo "  docker logs -f passengers-ingestion  # Ver logs"
        echo "  aws s3 ls s3://bus-mvp-datalake-1/  # Ver archivos S3"
        ;;
    *)
        echo "⚠️  Máquina no identificada"
        echo "  Verifica que estás en una de las máquinas correctas"
        ;;
esac

echo ""
echo "============================================"
