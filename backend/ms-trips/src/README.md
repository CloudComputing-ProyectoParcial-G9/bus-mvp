# Microservicio de Viajes (ms-trips)

## Descripción
Este microservicio gestiona toda la información relacionada con viajes, rutas y horarios del sistema Bus MVP. Implementado con contexto peruano incluyendo ciudades como Lima, Cusco, Arequipa, Trujillo, Puno e Ica.

## Tecnología Stack
- **Node.js** v18+ con Express.js
- **Sequelize ORM** para manejo de base de datos
- **MySQL 8.0** como motor de base de datos
- **Swagger/OpenAPI 3.0** para documentación de API
- **Winston** para logging estructurado
- **Docker** para containerización

## Base de Datos
- **Tipo**: SQL Database (MySQL 8.0)
- **Puerto**: 3306
- **Schema**: Incluye tablas `routes` y `trips` con relaciones
- **Contexto**: Datos peruanos con ciudades y moneda PEN

## Endpoints Principales
✅ **Implementados y funcionando**

### Trips
- `GET /api/v1/health` - Health check del servicio
- `GET /api/v1/trips` - Listar viajes (con paginación y filtros)
- `POST /api/v1/trips` - Crear nuevo viaje
- `GET /api/v1/trips/search` - Buscar viajes por origen, destino y fecha
- `PUT /api/v1/trips/{tripId}` - Actualizar viaje existente
- `DELETE /api/v1/trips/{tripId}` - Eliminar viaje

### Routes
- `GET /api/v1/routes` - Listar rutas disponibles
- `GET /api/v1/routes/{routeId}` - Obtener ruta específica

### Admin (Desarrollo)
- `POST /api/v1/admin/seed` - Poblar BD con datos de prueba
- `GET /api/v1/admin/data-status` - Estado actual de los datos
- `DELETE /api/v1/admin/clear-data` - Limpiar todos los datos

### Documentación
- `GET /docs/` - Swagger UI interactiva
- `GET /api-docs` - Especificación OpenAPI JSON

## Variables de Entorno Requeridas

```bash
# Base de datos MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=trips_db
MYSQL_USER=trips_user
MYSQL_PASSWORD=secure_password
MYSQL_ROOT_PASSWORD=root_password

# Configuración del servicio
PORT=8002
NODE_ENV=development
LOG_LEVEL=info

# Para desarrollo
API_VERSION=v1
```

## Estructura del Código (Implementada)

```
src/
├── controllers/
│   ├── healthController.js      # Health check endpoints
│   ├── tripController.js        # CRUD de viajes y búsqueda
│   ├── routeController.js       # Gestión de rutas
│   └── adminController.js       # Endpoints administrativos
├── models/
│   ├── Trip.js                  # Modelo Sequelize para viajes
│   └── Route.js                 # Modelo Sequelize para rutas
├── routes/
│   ├── healthRoutes.js          # Rutas de health check
│   ├── tripRoutes.js            # Rutas de viajes
│   ├── routeRoutes.js           # Rutas de rutas 🙂
│   └── adminRoutes.js           # Rutas administrativas
├── middleware/
│   ├── validation.js            # Validación de entrada
│   ├── errorHandler.js          # Manejo centralizado de errores
│   └── logger.js                # Configuración de Winston
├── config/
│   ├── database.js              # Configuración Sequelize/MySQL
│   └── swagger.js               # Configuración OpenAPI
├── seeders/
│   └── dataSeeder.js            # Población automática de datos
├── utils/
│   └── helpers.js               # Funciones auxiliares
├── app.js                       # Configuración Express
└── server.js                    # Punto de entrada
```

## 🚀 Instrucciones de Inicio Rápido

### Prerrequisitos
- **Node.js** v18 o superior
- **Docker** y **Docker Compose**
- **curl** para testing (opcional)

### 1. Levantar MySQL con Docker
```bash
# Desde el directorio del microservicio
cd /home/leonardo/Cursos/Cloud/proyecto-parcial/bus-mvp/backend/ms-trips

# Levantar MySQL en segundo plano
docker-compose up -d mysql

# Verificar que MySQL esté corriendo
docker-compose ps
```

### 2. Instalar Dependencias de Node.js
```bash
# Instalar dependencias
npm install

# Verificar que package.json esté presente
ls package.json
```

### 3. Iniciar el Microservicio
```bash
# Ejecutar el servidor
node src/server.js

# El servicio estará disponible en: http://localhost:8002
```

### 4. Poblar Datos de Prueba
```bash
# Ejecutar el seeder para crear rutas y viajes de ejemplo
curl -X POST "http://localhost:8002/api/v1/admin/seed" \
  -H "Content-Type: application/json" \
  -d '{"clearData": true, "testData": true}'

# Verificar que los datos se crearon
curl "http://localhost:8002/api/v1/admin/data-status"
```

### 5. Verificar Funcionalidad
```bash
# Health check
curl "http://localhost:8002/api/v1/health"

# Listar rutas disponibles
curl "http://localhost:8002/api/v1/routes"

# Listar viajes
curl "http://localhost:8002/api/v1/trips"

# Buscar viajes Lima -> Cusco
curl "http://localhost:8002/api/v1/trips/search?origin=Lima&destination=Cusco&departureDate=2025-09-22"
```

### 6. Explorar Documentación Swagger
Abrir en navegador: **http://localhost:8002/docs/**

## 📊 Datos de Prueba Incluidos

### Rutas Peruanas (6 rutas)
- **Lima → Cusco Express** (LIM_CUZ_001) - 1,165 km - S/ 120.00
- **Lima → Arequipa Ejecutivo** (LIM_ARE_002) - 1,009 km - S/ 95.50  
- **Lima → Trujillo Directo** (LIM_TRU_003) - 561 km - S/ 75.00
- **Arequipa → Cusco Turístico** (ARE_CUZ_004) - 315 km - S/ 60.00
- **Cusco → Puno Altiplano** (CUZ_PUN_005) - 389 km - S/ 65.00
- **Lima → Ica Express** (LIM_ICA_006) - 303 km - S/ 45.00

### Viajes de Ejemplo (5 viajes)
- **TRP_20250921_LIM_CUZ_01** - Lima → Cusco (22/09/2025 03:00)
- **TRP_20250921_LIM_ARE_02** - Lima → Arequipa (22/09/2025 04:30)
- **TRP_20250921_LIM_TRU_03** - Lima → Trujillo (21/09/2025 11:00)
- **TRP_20250922_ARE_CUZ_04** - Arequipa → Cusco (22/09/2025 13:00)
- **TRP_20250922_CUZ_PUN_05** - Cusco → Puno (22/09/2025 19:30)

## Comandos de Desarrollo

### Desarrollo Local
```bash
# Instalar dependencias
npm install

# Iniciar en modo desarrollo (con auto-reload)
npm run dev
# O manualmente:
node src/server.js

# Ver logs en tiempo real
tail -f logs/app.log
```

### Docker
```bash
# ============================================
# OPCIÓN 1: Desarrollo Local (Actual)
# ============================================
# MySQL local + Node.js local
docker-compose up -d mysql
npm install
node src/server.js

# ============================================
# OPCIÓN 2: Testing Completo con Contenedores  
# ============================================
# ms-trips + MySQL ambos en contenedores
docker-compose -f docker-compose.test.yml up --build -d

# Ver logs del contenedor
docker-compose -f docker-compose.test.yml logs -f ms-trips

# Poblar datos en contenedor
curl -X POST "http://localhost:8002/api/v1/admin/seed" \
  -H "Content-Type: application/json" \
  -d '{"clearData": true, "testData": true}'

# Detener contenedores
docker-compose -f docker-compose.test.yml down -v

# ============================================
# OPCIÓN 3: Infraestructura Completa (Producción)
# ============================================
# Desde directorio infra/ - Levanta todo el sistema
cd ../../infra
cp .env.example .env  # Configurar variables
docker-compose up --build -d

# Ver logs de ms-trips en infra
docker-compose logs -f ms-trips

# Acceso vía Load Balancer
curl "http://localhost:8080/api/v1/trips/health"
```

### Testing Manual
```bash
# Health check
curl "http://localhost:8002/api/v1/health"

# Crear un viaje nuevo
curl -X POST "http://localhost:8002/api/v1/trips" \
  -H "Content-Type: application/json" \
  -d '{
    "tripId": "TRP_20250924_LIM_ICA_07",
    "routeId": "LIM_ICA_006",
    "departureDateTime": "2025-09-24T08:00:00Z",
    "arrivalDateTime": "2025-09-24T12:30:00Z",
    "busCapacity": 35,
    "availableSeats": 35,
    "finalPrice": 45.00,
    "status": "scheduled",
    "driverName": "Maria Gonzalez"
  }'

# Actualizar viaje
curl -X PUT "http://localhost:8002/api/v1/trips/TRP_20250924_LIM_ICA_07" \
  -H "Content-Type: application/json" \
  -d '{
    "availableSeats": 30,
    "status": "in_progress"
  }'

# Eliminar viaje
curl -X DELETE "http://localhost:8002/api/v1/trips/TRP_20250924_LIM_ICA_07"

# Buscar viajes con filtros
curl "http://localhost:8002/api/v1/trips/search?origin=Lima&destination=Ica&departureDate=2025-09-24&minSeats=5&maxPrice=50"
```

## Integración con otros Microservicios

### Consumido por:
- **ms-history** - Para obtener historial de viajes
- **ms-tickets** - Para verificar disponibilidad de viajes
- **Frontend** - Para búsqueda y visualización de viajes

### Consume:
- Ninguno (microservicio base con DB)

## Schema de Base de Datos (Implementado)

### Tabla: routes
```sql
CREATE TABLE routes (
    routeId VARCHAR(20) PRIMARY KEY,
    routeName VARCHAR(255) NOT NULL,
    originCity VARCHAR(100) NOT NULL,
    destinationCity VARCHAR(100) NOT NULL,
    distanceKm DECIMAL(8,2) NOT NULL,
    estimatedDuration TIME NOT NULL,
    basePrice DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'PEN',
    active BOOLEAN DEFAULT TRUE,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Índices implementados
CREATE INDEX idx_routes_cities ON routes(originCity, destinationCity);
CREATE INDEX idx_routes_active ON routes(active);
```

### Tabla: trips
```sql
CREATE TABLE trips (
    tripId VARCHAR(50) PRIMARY KEY,
    routeId VARCHAR(20) NOT NULL,
    departureDateTime DATETIME NOT NULL,
    arrivalDateTime DATETIME NOT NULL,
    busCapacity INT NOT NULL CHECK (busCapacity > 0),
    availableSeats INT NOT NULL CHECK (availableSeats >= 0),
    finalPrice DECIMAL(10,2) NOT NULL CHECK (finalPrice >= 0),
    status ENUM('scheduled', 'in_progress', 'completed', 'cancelled') DEFAULT 'scheduled',
    driverName VARCHAR(100),
    busPlate VARCHAR(20),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints implementados
    CHECK (availableSeats <= busCapacity),
    CHECK (arrivalDateTime > departureDateTime)
);

-- Índices implementados
CREATE INDEX idx_trips_route ON trips(routeId);
CREATE INDEX idx_trips_departure ON trips(departureDateTime);
CREATE INDEX idx_trips_status ON trips(status);
```

## Lógica de Negocio (Implementada)

### Estados de Viajes
- **scheduled**: Viaje programado, aceptando reservas ✅
- **in_progress**: Viaje en curso ✅
- **completed**: Viaje completado ✅
- **cancelled**: Viaje cancelado ✅

### Reglas de Negocio Implementadas
- ✅ Los asientos disponibles no pueden exceder la capacidad
- ✅ La hora de llegada debe ser posterior a la de salida
- ✅ No se pueden crear viajes en el pasado
- ✅ Los precios deben ser positivos
- ✅ Validación de formato de IDs (TRP_YYYYMMDD_ORG_DST_NN)
- ✅ Validación de rutas existentes antes de crear viajes
- ✅ Búsqueda por origen, destino, fecha, asientos mínimos y precio máximo
- ✅ Funciones auxiliares para reserva y liberación de asientos

### Características Especiales
- **Contexto Peruano**: Ciudades reales (Lima, Cusco, Arequipa, etc.)
- **Moneda Local**: Precios en Soles Peruanos (PEN)
- **Logging Estructurado**: Winston con rotación de archivos
- **Documentación Interactiva**: Swagger UI con ejemplos peruanos
- **Seeder Automatizado**: Población de datos de prueba realistas

## Notas de Implementación

- ✅ **Time Zones**: Fechas manejadas en UTC con conversión local
- ✅ **Concurrency**: Validaciones Sequelize para actualizaciones concurrentes
- ✅ **Performance**: Índices optimizados para búsquedas frecuentes
- ✅ **Data Integrity**: Constraints y validaciones a nivel DB y aplicación
- ✅ **Error Handling**: Middleware centralizado con códigos HTTP apropiados
- ✅ **Logging**: Winston con rotación diaria y diferentes niveles
- ✅ **Documentation**: OpenAPI 3.0 con ejemplos interactivos
- ✅ **Development Tools**: Seeder automatizado y endpoints administrativos

## API Reference - Ejemplos Completos

### 🔍 Búsqueda de Viajes
```bash
# Búsqueda básica por ciudades
curl "http://localhost:8002/api/v1/trips/search?origin=Lima&destination=Cusco"

# Búsqueda con fecha específica
curl "http://localhost:8002/api/v1/trips/search?origin=Lima&destination=Arequipa&departureDate=2025-09-22"

# Búsqueda con filtros avanzados
curl "http://localhost:8002/api/v1/trips/search?origin=Lima&destination=Cusco&departureDate=2025-09-22&minSeats=5&maxPrice=100"

# Respuesta incluye información de la ruta
{
  "data": [{
    "tripId": "TRP_20250921_LIM_CUZ_01",
    "routeId": "LIM_CUZ_001", 
    "departureDateTime": "2025-09-22T03:00:00.000Z",
    "arrivalDateTime": "2025-09-22T23:00:00.000Z",
    "busCapacity": 45,
    "availableSeats": 45,
    "finalPrice": "120.00",
    "status": "scheduled",
    "driverName": "Carlos Mendoza",
    "Route": {
      "routeId": "LIM_CUZ_001",
      "routeName": "Lima - Cusco Express",
      "originCity": "Lima",
      "destinationCity": "Cusco",
      "distanceKm": "1165.50",
      "estimatedDuration": "20:00:00"
    }
  }],
  "pagination": {
    "currentPage": 1,
    "totalPages": 1,
    "totalItems": 1,
    "itemsPerPage": 20
  }
}
```

### 📊 Gestión de Datos
```bash
# Estado actual de la base de datos
curl "http://localhost:8002/api/v1/admin/data-status"

# Limpiar todos los datos
curl -X DELETE "http://localhost:8002/api/v1/admin/clear-data"

# Poblar con datos de prueba
curl -X POST "http://localhost:8002/api/v1/admin/seed" \
  -H "Content-Type: application/json" \
  -d '{"clearData": true, "testData": true}'
```

### 🚌 CRUD de Viajes
```bash
# Crear viaje (requiere ruta existente)
curl -X POST "http://localhost:8002/api/v1/trips" \
  -H "Content-Type: application/json" \
  -d '{
    "tripId": "TRP_20250925_LIM_TRU_08",
    "routeId": "LIM_TRU_003",
    "departureDateTime": "2025-09-25T06:00:00Z",
    "arrivalDateTime": "2025-09-25T14:45:00Z",
    "busCapacity": 40,
    "availableSeats": 40,
    "finalPrice": 75.00,
    "status": "scheduled",
    "driverName": "Juan Perez"
  }'

# Actualizar viaje
curl -X PUT "http://localhost:8002/api/v1/trips/TRP_20250925_LIM_TRU_08" \
  -H "Content-Type: application/json" \
  -d '{
    "availableSeats": 35,
    "status": "in_progress"
  }'

# Eliminar viaje
curl -X DELETE "http://localhost:8002/api/v1/trips/TRP_20250925_LIM_TRU_08"
```

## Integración con otros Microservicios

### Consumido por:
- **ms-history** - Para obtener historial de viajes completados
- **ms-tickets** - Para verificar disponibilidad y reservar asientos
- **Frontend Web Portal** - Para búsqueda y visualización de viajes
- **Load Balancer** - Para distribución de carga

### Consume:
- **MySQL Database** - Persistencia de rutas y viajes
- *(Independiente de otros microservicios)*

### Endpoints de Integración:
- `GET /api/v1/health` - Health check para load balancer
- `GET /api/v1/trips/search` - Búsqueda para frontend
- `PUT /api/v1/trips/{id}` - Actualización de asientos por ms-tickets

## 🔧 Troubleshooting

### Problemas Comunes

**Error de conexión a MySQL**
```bash
# Verificar que MySQL esté corriendo
docker-compose ps mysql

# Revisar logs de MySQL
docker-compose logs mysql

# Reiniciar si es necesario
docker-compose restart mysql
```

**Puerto 8002 ocupado**
```bash
# Encontrar proceso usando el puerto
lsof -i :8002

# Matar proceso si es necesario
pkill -f "node src/server.js"
```

**Datos de prueba no se crean**
```bash
# Verificar logs del seeder
curl -X POST "http://localhost:8002/api/v1/admin/seed" \
  -H "Content-Type: application/json" \
  -d '{"clearData": true, "testData": true}'

# Verificar estado de la BD
curl "http://localhost:8002/api/v1/admin/data-status"
```

**Swagger UI no carga**
- Verificar que el servicio esté en http://localhost:8002/docs/
- Revisar logs en `logs/app.log`
- Asegurar que todas las dependencias estén instaladas

## 📋 Checklist de Verificación

### ✅ Funcionalidad Básica
- [ ] MySQL corriendo en puerto 3306
- [ ] Servicio Node.js en puerto 8002  
- [ ] Health check responde OK
- [ ] Datos de prueba poblados (6 rutas, 5 viajes)
- [ ] Swagger UI accesible en /docs/

### ✅ Operaciones CRUD
- [ ] Crear viaje con validaciones
- [ ] Leer viajes con paginación
- [ ] Actualizar viaje existente
- [ ] Eliminar viaje
- [ ] Buscar viajes por criterios

### ✅ Endpoints Administrativos
- [ ] Ejecutar seeder exitosamente
- [ ] Verificar estado de datos
- [ ] Limpiar base de datos
- [ ] Logs estructurados funcionando

## Ownership
**Implementado por**: @B2 (Backend Developer 2)  
**Stack**: Node.js + Express + Sequelize + MySQL  
**Status**: ✅ **COMPLETAMENTE FUNCIONAL**
