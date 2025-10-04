#!/bin/bash
# quick_start.sh - Script de inicio rápido para ms-trips

set -e  # Salir si algún comando falla

echo "🚀 Iniciando ms-trips - Microservicio de Viajes..."
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    echo "❌ Error: Ejecutar desde el directorio ms-trips"
    echo "   cd /home/leonardo/Cursos/Cloud/proyecto-parcial/bus-mvp/backend/ms-trips"
    exit 1
fi

# 1. Levantar MySQL
echo "📊 Levantando MySQL..."
docker-compose up -d mysql
echo "   Esperando que MySQL esté listo..."
sleep 10

# Verificar que MySQL esté corriendo
if ! docker-compose ps mysql | grep -q "Up"; then
    echo "❌ Error: MySQL no pudo iniciarse"
    exit 1
fi
echo "✅ MySQL está corriendo"

# 2. Instalar dependencias si no existen
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias de Node.js..."
    npm install
    echo "✅ Dependencias instaladas"
else
    echo "✅ Dependencias ya instaladas"
fi

# 3. Iniciar aplicación
echo "🔥 Iniciando aplicación Node.js..."
# Matar procesos previos si existen
pkill -f "node src/server.js" 2>/dev/null || true
sleep 2

# Iniciar nueva instancia
node src/server.js &
APP_PID=$!
echo "   Aplicación iniciada con PID: $APP_PID"
echo "   Esperando que la aplicación esté lista..."
sleep 5

# 4. Verificar que la aplicación responda
echo "🔍 Verificando health check..."
if curl -s "http://localhost:8002/api/v1/health" > /dev/null; then
    echo "✅ Aplicación respondiendo correctamente"
else
    echo "❌ Error: La aplicación no responde"
    echo "   Revisar logs en logs/app.log"
    exit 1
fi

# 5. Poblar datos de prueba
echo "🌱 Poblando datos de prueba..."
SEED_RESPONSE=$(curl -s -X POST "http://localhost:8002/api/v1/admin/seed" \
  -H "Content-Type: application/json" \
  -d '{"clearData": true, "testData": true}')

if echo "$SEED_RESPONSE" | grep -q "creadas exitosamente\|created successfully"; then
    echo "✅ Datos de prueba poblados correctamente"
else
    echo "⚠️  Advertencia: Hubo problemas poblando datos"
    echo "   Respuesta: $SEED_RESPONSE"
fi

# 6. Verificar estado final
echo "📊 Verificando estado de los datos..."
DATA_STATUS=$(curl -s "http://localhost:8002/api/v1/admin/data-status")
ROUTES_COUNT=$(echo "$DATA_STATUS" | grep -o '"totalRoutes":[0-9]*' | cut -d':' -f2)
TRIPS_COUNT=$(echo "$DATA_STATUS" | grep -o '"totalTrips":[0-9]*' | cut -d':' -f2)

echo "   📍 Rutas creadas: $ROUTES_COUNT"
echo "   🚌 Viajes creados: $TRIPS_COUNT"

# 7. Prueba de búsqueda
echo "🔍 Probando búsqueda de viajes..."
SEARCH_RESULT=$(curl -s "http://localhost:8002/api/v1/trips/search?origin=Lima&destination=Cusco&departureDate=2025-09-22")
FOUND_TRIPS=$(echo "$SEARCH_RESULT" | grep -o '"totalItems":[0-9]*' | cut -d':' -f2)

if [ "$FOUND_TRIPS" -gt 0 ]; then
    echo "✅ Búsqueda funcionando - Encontrados $FOUND_TRIPS viajes Lima → Cusco"
else
    echo "⚠️  No se encontraron viajes en la búsqueda de prueba"
fi

echo ""
echo "🎉 ¡ms-trips está listo y funcionando!"
echo ""
echo "📋 Información importante:"
echo "   🌐 Aplicación:      http://localhost:8002"
echo "   💓 Health Check:    http://localhost:8002/api/v1/health"
echo "   📖 Swagger UI:      http://localhost:8002/docs/"
echo "   📊 Estado de datos: http://localhost:8002/api/v1/admin/data-status"
echo ""
echo "🧪 Comandos de prueba:"
echo "   # Buscar viajes"
echo "   curl \"http://localhost:8002/api/v1/trips/search?origin=Lima&destination=Cusco&departureDate=2025-09-22\""
echo ""
echo "   # Ver todas las rutas"
echo "   curl \"http://localhost:8002/api/v1/routes\""
echo ""
echo "   # Ver todos los viajes"
echo "   curl \"http://localhost:8002/api/v1/trips\""
echo ""
echo "📝 Para detener:"
echo "   pkill -f \"node src/server.js\""
echo "   docker-compose down"
echo ""
echo "📋 Para ver logs:"
echo "   tail -f logs/app.log"