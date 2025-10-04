# 🚀 Inicio Rápido - ms-trips

## Comandos de Una Línea

### 1. Levantar Todo
```bash
# Desde el directorio ms-trips
cd /home/leonardo/Cursos/Cloud/proyecto-parcial/bus-mvp/backend/ms-trips

# Levantar MySQL
docker-compose up -d mysql && sleep 10

# Instalar dependencias (si es primera vez)
npm install

# Iniciar aplicación
node src/server.js &
```

### 2. Poblar Datos de Prueba
```bash
# Esperar 5 segundos y poblar datos
sleep 5 && curl -X POST "http://localhost:8002/api/v1/admin/seed" \
  -H "Content-Type: application/json" \
  -d '{"clearData": true, "testData": true}'
```

### 3. Verificar Funcionamiento
```bash
# Health check
curl "http://localhost:8002/api/v1/health"

# Buscar viajes Lima -> Cusco
curl "http://localhost:8002/api/v1/trips/search?origin=Lima&destination=Cusco&departureDate=2025-09-22"

# Ver Swagger UI
echo "Abrir: http://localhost:8002/docs/"
```

## Script de Automatización Completa

```bash
#!/bin/bash
# quick_start.sh

echo "🚀 Iniciando ms-trips..."

# Ir al directorio
cd /home/leonardo/Cursos/Cloud/proyecto-parcial/bus-mvp/backend/ms-trips

# Levantar MySQL
echo "📊 Levantando MySQL..."
docker-compose up -d mysql
sleep 10

# Instalar dependencias si no existen
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

# Iniciar aplicación
echo "🔥 Iniciando aplicación..."
node src/server.js &
sleep 5

# Poblar datos
echo "🌱 Poblando datos de prueba..."
curl -X POST "http://localhost:8002/api/v1/admin/seed" \
  -H "Content-Type: application/json" \
  -d '{"clearData": true, "testData": true}'

# Verificar funcionamiento
echo "✅ Verificando funcionamiento..."
curl "http://localhost:8002/api/v1/health"

echo ""
echo "🎉 ¡ms-trips está listo!"
echo "📖 Swagger UI: http://localhost:8002/docs/"
echo "🔍 Búsqueda de ejemplo: curl \"http://localhost:8002/api/v1/trips/search?origin=Lima&destination=Cusco&departureDate=2025-09-22\""
```

## URLs Importantes

- **Aplicación**: http://localhost:8002
- **Health Check**: http://localhost:8002/api/v1/health
- **Swagger UI**: http://localhost:8002/docs/
- **API Spec**: http://localhost:8002/api-docs

## Datos de Prueba Disponibles

### Rutas (6)
- Lima → Cusco (S/ 120.00)
- Lima → Arequipa (S/ 95.50) 
- Lima → Trujillo (S/ 75.00)
- Arequipa → Cusco (S/ 60.00)
- Cusco → Puno (S/ 65.00)
- Lima → Ica (S/ 45.00)

### Viajes (5)
- TRP_20250921_LIM_CUZ_01 (22/09 03:00)
- TRP_20250921_LIM_ARE_02 (22/09 04:30)
- TRP_20250921_LIM_TRU_03 (21/09 11:00)
- TRP_20250922_ARE_CUZ_04 (22/09 13:00)
- TRP_20250922_CUZ_PUN_05 (22/09 19:30)

## Comandos Útiles

```bash
# Ver estado de datos
curl "http://localhost:8002/api/v1/admin/data-status"

# Limpiar datos
curl -X DELETE "http://localhost:8002/api/v1/admin/clear-data"

# Parar aplicación
pkill -f "node src/server.js"

# Ver logs
tail -f logs/app.log
```