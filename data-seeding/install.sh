#!/bin/bash

# Script de instalación y configuración para Data Seeding - Bus MVP

echo "🚀 Configurando Data Seeding para Bus MVP..."
echo "============================================="

# Cambiar al directorio de data-seeding
cd "$(dirname "$0")"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js no está instalado"
    echo "   Instala Node.js 18+ desde https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Error: Se requiere Node.js 18 o superior"
    echo "   Versión actual: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detectado"

# Instalar dependencias
echo "📦 Instalando dependencias..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Error instalando dependencias"
    exit 1
fi

echo "✅ Dependencias instaladas"

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo de configuración .env..."
    cp .env.example .env
    echo "✅ Archivo .env creado desde .env.example"
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones de base de datos"
    echo "   Ubicación: $(pwd)/.env"
    echo ""
else
    echo "ℹ️  Archivo .env ya existe"
fi

# Verificar conexiones (opcional)
echo "🔧 ¿Deseas probar las conexiones a las bases de datos? (y/N): "
read -r TEST_CONNECTIONS

if [[ $TEST_CONNECTIONS =~ ^[Yy]$ ]]; then
    echo "🔍 Probando conexiones..."
    npm run test:connections
else
    echo "⏭️  Prueba de conexiones omitida"
fi

echo ""
echo "🎉 Configuración completada!"
echo ""
echo "📋 Comandos disponibles:"
echo "   npm run seed:all          # Generar todos los datos (20k registros)"
echo "   npm run seed:all:clean    # Limpiar y generar datos"
echo "   npm run stats             # Ver estadísticas actuales"
echo "   npm run clean:all         # Limpiar todas las bases de datos"
echo "   npm run test:connections  # Probar conexiones"
echo ""
echo "🔧 Para configurar las bases de datos, edita:"
echo "   $(pwd)/.env"
echo ""
echo "✅ ¡Todo listo para generar datos!"
