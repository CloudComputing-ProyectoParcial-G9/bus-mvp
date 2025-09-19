# Microservicio de Viajes (ms-trips)

## Descripción
Este microservicio gestiona toda la información relacionada con viajes, rutas y horarios del sistema Bus MVP.

## Tecnología Stack
**TODO**: Definir según elección del equipo de desarrollo (debe ser diferente a ms-passengers)

### Opciones sugeridas:
- **Python** + FastAPI + SQLAlchemy
- **Java** + Spring Boot + JPA
- **Go** + Gin + GORM
- **C#** + ASP.NET Core + Entity Framework
- **PHP** + Laravel + Eloquent

## Base de Datos
- **Tipo**: SQL Database 2 (segunda de las dos bases SQL requeridas)
- **Motor**: TODO - Elegir entre MySQL, PostgreSQL, SQL Server, etc. (diferente a ms-passengers)
- **Schema**: Ver `docs/er-diagrams/sql_db2.er.md`

## Endpoints Principales
Ver especificación completa en `openapi.yaml`

### Trips
- `GET /health` - Health check
- `GET /trips` - Listar viajes (con filtros)
- `POST /trips` - Crear nuevo viaje
- `GET /trips/{id}` - Obtener viaje específico
- `PUT /trips/{id}` - Actualizar viaje

### Routes
- `GET /routes` - Listar rutas disponibles
- `POST /routes` - Crear nueva ruta

## Variables de Entorno Requeridas

```bash
# Base de datos SQL 2
SQL2_HOST=localhost
SQL2_PORT=3306
SQL2_DB=trips_db
SQL2_USER=trips_user
SQL2_PASSWORD=secure_password

# Configuración del servicio
MS_TRIPS_PORT=8002
NODE_ENV=development
LOG_LEVEL=info

# Para testing
TEST_DB_URL=sqlite:///:memory:
```

## Estructura del Código (Placeholder)

```
src/
├── controllers/
│   ├── healthController.py
│   ├── tripsController.py
│   └── routesController.py
├── models/
│   ├── trip.py
│   └── route.py
├── routes/
│   ├── health.py
│   ├── trips.py
│   └── routes.py
├── middleware/
│   ├── validation.py
│   ├── errorHandler.py
│   └── logger.py
├── config/
│   ├── database.py
│   └── server.py
├── utils/
│   └── helpers.py
└── main.py
```

## Tareas Pendientes

### Base de Datos
- [ ] Definir motor SQL específico (diferente a ms-passengers)
- [ ] Crear migrations para tablas de trips y routes
- [ ] Implementar seeds de datos de prueba
- [ ] Configurar connection pooling
- [ ] Implementar health check de DB

### API
- [ ] Implementar todos los endpoints según OpenAPI spec
- [ ] Configurar validación de input
- [ ] Implementar paginación y filtros
- [ ] Añadir búsqueda por origen/destino/fecha
- [ ] Configurar rate limiting
- [ ] Implementar logging estructurado

### Business Logic
- [ ] Validar disponibilidad de asientos
- [ ] Calcular precios dinámicos
- [ ] Gestionar estados de viajes
- [ ] Implementar reglas de cancelación
- [ ] Validar fechas y horarios

### Testing
- [ ] Unit tests para controllers
- [ ] Integration tests para endpoints
- [ ] Tests de base de datos
- [ ] Tests de validación de negocio
- [ ] Setup de CI/CD testing

### Monitoring & Observability
- [ ] Configurar health checks detallados
- [ ] Métricas de performance
- [ ] Logging de errores
- [ ] Tracing distribuido
- [ ] Alertas de monitoreo

## Comandos de Desarrollo

### Local Development
```bash
# TODO: Completar según stack elegido

# Ejemplo Python:
# pip install -r requirements.txt
# uvicorn main:app --reload --port 8002

# Ejemplo Java:
# ./mvnw spring-boot:run

# Ejemplo Go:
# go mod tidy
# go run main.go

# Ejemplo C#:
# dotnet run
```

### Docker
```bash
# Build
docker build -t ms-trips .

# Run
docker run -p 8002:8002 --env-file .env ms-trips

# Con Docker Compose (desde raíz del proyecto)
cd ../../infra
docker-compose up ms-trips
```

### Testing
```bash
# TODO: Completar según stack elegido

# Ejemplo Python:
# pytest
# pytest --cov=src

# Ejemplo Java:
# ./mvnw test

# Ejemplo Go:
# go test ./...

# Ejemplo C#:
# dotnet test
```

## Integración con otros Microservicios

### Consumido por:
- **ms-history** - Para obtener historial de viajes
- **ms-tickets** - Para verificar disponibilidad de viajes
- **Frontend** - Para búsqueda y visualización de viajes

### Consume:
- Ninguno (microservicio base con DB)

## Schema de Base de Datos (Preliminar)

### Tabla: routes
```sql
-- TODO: Ajustar según motor SQL elegido
CREATE TABLE routes (
    route_code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    origin_city VARCHAR(50) NOT NULL,
    destination_city VARCHAR(50) NOT NULL,
    distance_km DECIMAL(8,2) NOT NULL,
    estimated_duration TIME NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_routes_cities ON routes(origin_city, destination_city);
CREATE INDEX idx_routes_active ON routes(active);
```

### Tabla: trips
```sql
-- TODO: Ajustar según motor SQL elegido
CREATE TABLE trips (
    trip_id VARCHAR(50) PRIMARY KEY,
    route_code VARCHAR(10) NOT NULL,
    departure_time TIMESTAMP NOT NULL,
    arrival_time TIMESTAMP NOT NULL,
    bus_capacity INT NOT NULL CHECK (bus_capacity > 0),
    available_seats INT NOT NULL CHECK (available_seats >= 0),
    base_price DECIMAL(10,2) NOT NULL CHECK (base_price >= 0),
    currency VARCHAR(3) DEFAULT 'EUR',
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (route_code) REFERENCES routes(route_code),
    CHECK (available_seats <= bus_capacity),
    CHECK (arrival_time > departure_time)
);

-- Índices
CREATE INDEX idx_trips_route ON trips(route_code);
CREATE INDEX idx_trips_departure ON trips(departure_time);
CREATE INDEX idx_trips_status ON trips(status);
CREATE INDEX idx_trips_cities_date ON trips(route_code, departure_time);
```

## Lógica de Negocio

### Estados de Viajes
- **scheduled**: Viaje programado, aceptando reservas
- **in_progress**: Viaje en curso
- **completed**: Viaje completado
- **cancelled**: Viaje cancelado

### Reglas de Negocio
- Los asientos disponibles no pueden exceder la capacidad
- La hora de llegada debe ser posterior a la de salida
- No se pueden crear viajes en el pasado
- Los precios deben ser positivos
- Las rutas deben estar activas para crear viajes

## Notas de Implementación

- **Time Zones**: Manejar zonas horarias apropiadamente
- **Concurrency**: Proteger actualizaciones de asientos disponibles
- **Performance**: Índices optimizados para búsquedas frecuentes
- **Data Integrity**: Foreign keys y constraints de negocio
- **Caching**: Considerar cache para rutas populares

## Ownership
**Responsable**: @B2 (Backend Developer 2)
