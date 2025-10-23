#!/bin/bash

# ============================================
# Script para sincronizar credenciales de AWS
# ============================================
# Este script copia las credenciales del archivo .env
# al archivo ~/.aws/credentials para uso con AWS CLI
# ============================================

set -e

echo "=========================================="
echo "🔄 Sincronizando credenciales de AWS"
echo "=========================================="

# Verificar si existe el archivo .env en la raíz del proyecto
ENV_FILE="../.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: No se encontró el archivo .env en la raíz del proyecto"
    echo "   Ruta esperada: $ENV_FILE"
    exit 1
fi

# Crear directorio .aws si no existe
mkdir -p ~/.aws

# Leer variables del archivo .env
source "$ENV_FILE"

# Verificar que las variables existan
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ Error: Las credenciales AWS_ACCESS_KEY_ID o AWS_SECRET_ACCESS_KEY no están definidas en $ENV_FILE"
    exit 1
fi

# Crear/actualizar archivo de credenciales
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id=$AWS_ACCESS_KEY_ID
aws_secret_access_key=$AWS_SECRET_ACCESS_KEY
EOF

# Agregar session token si existe
if [ ! -z "$AWS_SESSION_TOKEN" ]; then
    echo "aws_session_token=$AWS_SESSION_TOKEN" >> ~/.aws/credentials
fi

echo "✅ Credenciales actualizadas en ~/.aws/credentials"

# Crear/actualizar archivo de configuración
if [ ! -z "$AWS_DEFAULT_REGION" ]; then
    cat > ~/.aws/config << EOF
[default]
region=$AWS_DEFAULT_REGION
output=json
EOF
    echo "✅ Configuración actualizada en ~/.aws/config"
fi

# Establecer permisos seguros
chmod 600 ~/.aws/credentials
chmod 600 ~/.aws/config 2>/dev/null || true

echo ""
echo "=========================================="
echo "✅ Sincronización completada"
echo "=========================================="
echo "📁 Archivos actualizados:"
echo "   - ~/.aws/credentials"
[ ! -z "$AWS_DEFAULT_REGION" ] && echo "   - ~/.aws/config"
echo ""
echo "🔒 Permisos establecidos en 600 (solo lectura/escritura para el propietario)"
echo ""
echo "💡 Ahora puedes usar AWS CLI sin especificar credenciales explícitamente"
echo "   Ejemplo: aws s3 ls"
echo "=========================================="
