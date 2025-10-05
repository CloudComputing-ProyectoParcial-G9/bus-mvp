#!/bin/bash

# Quick Start Script - Bus MVP Data Ingestion
# Este script automatiza el setup inicial del proyecto

set -e

echo "=============================================="
echo "🚀 Bus MVP Data Ingestion - Quick Start"
echo "=============================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.yml not found${NC}"
    echo "Please run this script from the data-ingestion directory"
    exit 1
fi

# Verificar Docker
echo -e "\n${YELLOW}📦 Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo "Por favor instala Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✅ Docker instalado${NC}"

# Verificar Docker Compose
echo -e "\n${YELLOW}📦 Verificando Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    echo "Por favor instala Docker Compose"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose instalado${NC}"

# Crear archivo .env si no existe
echo -e "\n${YELLOW}⚙️  Configurando variables de entorno...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Archivo .env creado${NC}"
    echo -e "${YELLOW}⚠️  Por favor edita el archivo .env con tus credenciales AWS${NC}"
    echo -e "${YELLOW}   Presiona ENTER cuando hayas terminado...${NC}"
    read
else
    echo -e "${GREEN}✅ Archivo .env ya existe${NC}"
fi

# Verificar credenciales AWS
echo -e "\n${YELLOW}🔐 Verificando credenciales AWS...${NC}"
if ! grep -q "your_access_key_here" .env && ! grep -q "your_secret_key_here" .env; then
    echo -e "${GREEN}✅ Credenciales AWS configuradas${NC}"
else
    echo -e "${RED}❌ Credenciales AWS no configuradas${NC}"
    echo -e "${YELLOW}Por favor edita el archivo .env con tus credenciales${NC}"
    exit 1
fi

# Preguntar si quiere crear bucket S3
echo -e "\n${YELLOW}🪣 ¿Quieres crear el bucket S3? (y/n)${NC}"
read -r create_bucket
if [ "$create_bucket" = "y" ]; then
    echo -e "${YELLOW}📦 Instalando dependencias de Python...${NC}"
    pip3 install -r scripts/requirements.txt
    
    echo -e "${YELLOW}🪣 Creando bucket S3...${NC}"
    python3 scripts/setup_s3.py
    echo -e "${GREEN}✅ Bucket S3 creado${NC}"
fi

# Build de contenedores
echo -e "\n${YELLOW}🐳 Building Docker containers...${NC}"
docker-compose build
echo -e "${GREEN}✅ Contenedores construidos${NC}"

# Preguntar si quiere ejecutar la ingesta
echo -e "\n${YELLOW}🚀 ¿Quieres ejecutar la ingesta ahora? (y/n)${NC}"
read -r run_ingestion
if [ "$run_ingestion" = "y" ]; then
    echo -e "${YELLOW}📊 Ejecutando ingesta...${NC}"
    docker-compose up
else
    echo -e "${YELLOW}⏭️  Puedes ejecutar la ingesta después con: docker-compose up${NC}"
fi

# Preguntar si quiere configurar Glue
echo -e "\n${YELLOW}📊 ¿Quieres configurar AWS Glue Catalog? (y/n)${NC}"
read -r setup_glue
if [ "$setup_glue" = "y" ]; then
    echo -e "${YELLOW}⚠️  Antes de continuar, asegúrate de:${NC}"
    echo -e "${YELLOW}   1. Haber ejecutado la ingesta al menos una vez${NC}"
    echo -e "${YELLOW}   2. Tener archivos en S3${NC}"
    echo -e "${YELLOW}   3. Haber actualizado el role_arn en scripts/setup_glue.py${NC}"
    echo -e "${YELLOW}   ¿Continuar? (y/n)${NC}"
    read -r continue_glue
    if [ "$continue_glue" = "y" ]; then
        echo -e "${YELLOW}📊 Configurando AWS Glue...${NC}"
        python3 scripts/setup_glue.py
        echo -e "${GREEN}✅ AWS Glue configurado${NC}"
    fi
fi

echo -e "\n${GREEN}=============================================="
echo "✅ Setup completado!"
echo "=============================================="
echo -e "${NC}"
echo "Próximos pasos:"
echo "1. Verificar archivos en S3:"
echo "   aws s3 ls s3://bus-mvp-datalake/raw/ --recursive"
echo ""
echo "2. Ejecutar ingesta:"
echo "   docker-compose up"
echo ""
echo "3. Iniciar Analytics API:"
echo "   docker-compose up -d analytics-service"
echo ""
echo "4. Verificar salud del API:"
echo "   curl http://localhost:5000/health"
echo ""
echo "5. Consultar documentación completa:"
echo "   - README.md"
echo "   - AWS_EC2_DEPLOYMENT.md"
echo ""
