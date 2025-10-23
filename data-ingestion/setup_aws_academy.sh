#!/bin/bash

# AWS Academy Credentials Helper
# Script para configurar credenciales temporales de AWS Academy Lab

echo "=============================================="
echo "🎓 AWS Academy Lab - Credentials Setup"
echo "=============================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Este script te ayudará a configurar las credenciales de AWS Academy Lab${NC}"
echo ""
echo -e "${BLUE}Pasos:${NC}"
echo "1. Ve a AWS Academy → Learner Lab"
echo "2. Click en 'AWS Details' (arriba a la derecha)"
echo "3. Click en 'Show' junto a AWS CLI"
echo "4. Copia las credenciales"
echo ""
echo -e "${YELLOW}NOTA: Este script configurará el archivo .env en la raíz del proyecto${NC}"
echo -e "${YELLOW}      Todas las partes del proyecto (ingesta, analytics, etc.) usarán este archivo.${NC}"
echo ""

# Verificar si .env existe en la raíz
if [ -f "../.env" ]; then
    echo -e "${YELLOW}⚠️  El archivo ../.env ya existe.${NC}"
    echo -e "${YELLOW}¿Quieres actualizar las credenciales de AWS? (y/n)${NC}"
    read -r overwrite
    if [ "$overwrite" != "y" ]; then
        echo -e "${RED}Cancelado.${NC}"
        exit 0
    fi
else
    # Si no existe, crearlo desde el ejemplo de la raíz
    if [ -f "../.env.example" ]; then
        cp ../.env.example ../.env
        echo -e "${GREEN}✅ Archivo ../.env creado desde .env.example${NC}"
    else
        echo -e "${RED}❌ Error: No se encontró ../.env.example${NC}"
        exit 1
    fi
fi

echo ""

# Solicitar credenciales
echo -e "${BLUE}Ahora ingresa las credenciales de AWS Academy:${NC}"
echo ""

echo -e "${YELLOW}AWS Access Key ID:${NC}"
read -r access_key
echo ""

echo -e "${YELLOW}AWS Secret Access Key:${NC}"
read -r secret_key
echo ""

echo -e "${YELLOW}AWS Session Token (el más largo):${NC}"
read -r session_token
echo ""

# Actualizar .env en la raíz del proyecto
if [ -n "$access_key" ] && [ -n "$secret_key" ] && [ -n "$session_token" ]; then
    # Usar sed en Linux/Mac
    if command -v sed &> /dev/null; then
        sed -i "s|AWS_ACCESS_KEY_ID=.*|AWS_ACCESS_KEY_ID=$access_key|" ../.env
        sed -i "s|AWS_SECRET_ACCESS_KEY=.*|AWS_SECRET_ACCESS_KEY=$secret_key|" ../.env
        sed -i "s|AWS_SESSION_TOKEN=.*|AWS_SESSION_TOKEN=$session_token|" ../.env

        # Agregar variables de data-ingestion si no existen
        if ! grep -q "S3_BUCKET=" ../.env; then
            echo "" >> ../.env
            echo "# Data Ingestion Configuration" >> ../.env
            echo "S3_BUCKET=bus-mvp-datalake-1" >> ../.env
        fi
        if ! grep -q "PASSENGERS_API_URL=" ../.env; then
            echo "PASSENGERS_API_URL=http://host.docker.internal:8001/api/v1" >> ../.env
        fi
        if ! grep -q "TRIPS_API_URL=" ../.env; then
            echo "TRIPS_API_URL=http://host.docker.internal:8002/api/v1" >> ../.env
        fi
        if ! grep -q "TICKETS_API_URL=" ../.env; then
            echo "TICKETS_API_URL=http://host.docker.internal:8003/api/v1" >> ../.env
        fi
    fi
    
    echo -e "${GREEN}✅ Credenciales configuradas exitosamente${NC}"
    echo ""
    
    # Verificar credenciales
    echo -e "${BLUE}Verificando credenciales...${NC}"
    export AWS_ACCESS_KEY_ID=$access_key
    export AWS_SECRET_ACCESS_KEY=$secret_key
    export AWS_SESSION_TOKEN=$session_token
    export AWS_DEFAULT_REGION=us-east-1

    if aws sts get-caller-identity &> /dev/null; then
        echo -e "${GREEN}✅ Credenciales válidas${NC}"
        aws sts get-caller-identity
        echo ""

        # Obtener Account ID y agregarlo al .env
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        if ! grep -q "AWS_ACCOUNT_ID=" ../.env; then
            echo "AWS_ACCOUNT_ID=$ACCOUNT_ID" >> ../.env
        else
            sed -i "s|AWS_ACCOUNT_ID=.*|AWS_ACCOUNT_ID=$ACCOUNT_ID|" ../.env
        fi
        echo ""
        echo -e "${BLUE}Tu Account ID es: ${GREEN}$ACCOUNT_ID${NC}"
        echo ""

        echo -e "${GREEN}=============================================="
        echo "✅ Setup completado!"
        echo "=============================================="
        echo -e "${NC}"
        echo "Proximos pasos:"
        echo -e "1. ${GREEN}El Account ID ($ACCOUNT_ID) fue guardado en ../.env${NC}"
        echo "2. Crear bucket S3: cd data-ingestion && python3 scripts/setup_s3.py"
        echo "3. Configurar Glue: python3 scripts/setup_glue.py"
        echo "4. Ejecutar ingesta: docker-compose up"
        echo ""
        echo -e "${YELLOW}⏰ RECORDATORIO: Las credenciales expiran en 4 horas${NC}"
        echo "   Ejecuta este script nuevamente cuando expire"
        echo ""

    else
        echo -e "${RED}❌ Error: Credenciales inválidas${NC}"
        echo "Por favor verifica que copiaste correctamente desde AWS Academy"
        exit 1
    fi
else
    echo -e "${RED}❌ Error: No se ingresaron todas las credenciales${NC}"
    exit 1
fi
