# Microservicio de Pasajeros (ms-passengers)

## Descripción
Este microservicio gestiona toda la información relacionada con los pasajeros del sistema Bus MVP.

## Tecnología Stack
**TODO**: Definir según elección del equipo de desarrollo

### Opciones sugeridas:
- **Node.js** + Express + TypeScript
- **Python** + FastAPI + SQLAlchemy
- **Java** + Spring Boot + JPA
- **Go** + Gin + GORM
- **C#** + ASP.NET Core + Entity Framework

## Base de Datos
- **Tipo**: SQL Database 1 (primera de las dos bases SQL requeridas)
- **Motor**: TODO - Elegir entre MySQL, PostgreSQL, SQL Server, etc.
- **Schema**: Ver `docs/er-diagrams/sql_db1.er.md`

## Endpoints Principales
Ver especificación completa en `openapi.yaml`

- `GET /health` - Health check
- `GET /passengers` - Listar pasajeros (paginado)
- `POST /passengers` - Crear nuevo pasajero
- `GET /passengers/{id}` - Obtener pasajero específico
- `PUT /passengers/{id}` - Actualizar pasajero

## Variables de Entorno Requeridas

```bash
# Base de datos SQL 1
SQL1_HOST=localhost
SQL1_PORT=5432
SQL1_DB=passengers_db
SQL1_USER=passengers_user
SQL1_PASSWORD=secure_password

# Configuración del servicio
MS_PASSENGERS_PORT=8001
NODE_ENV=development
LOG_LEVEL=info

# Para testing
TEST_DB_URL=sqlite:///:memory:
```

## Estructura del Código (Placeholder)

```
src/
├── controllers/
│   ├── healthController.js
│   └── passengersController.js
├── models/
│   └── passenger.js
├── routes/
│   ├── health.js
│   └── passengers.js
├── middleware/
│   ├── validation.js
│   ├── errorHandler.js
│   └── logger.js
├── config/
│   ├── database.js
│   └── server.js
├── utils/
│   └── helpers.js
└── app.js
```

## Tareas Pendientes

### Base de Datos
- [ ] Definir motor SQL específico (PostgreSQL/MySQL/etc.)
- [ ] Crear migrations para tablas de pasajeros
- [ ] Implementar seeds de datos de prueba
- [ ] Configurar connection pooling
- [ ] Implementar health check de DB

### API
- [ ] Implementar todos los endpoints según OpenAPI spec
- [ ] Configurar validación de input
- [ ] Implementar paginación
- [ ] Añadir filtros de búsqueda
- [ ] Configurar rate limiting
- [ ] Implementar logging estructurado

### Testing
- [ ] Unit tests para controllers
- [ ] Integration tests para endpoints
- [ ] Tests de base de datos
- [ ] Tests de validación
- [ ] Setup de CI/CD testing

### Seguridad
- [ ] Validación y sanitización de inputs
- [ ] Protección contra SQL injection
- [ ] Configurar CORS apropiadamente


## Request/Response examples
Estas son las definiciones de request y response para los endpoints principales del servicio `ms-passengers`. Mantener consistencia con `openapi.yaml`.

1) GET /health
Request: ninguno
Response (200):
```json
{
    "status": "healthy",
    "timestamp": "2025-09-20T10:00:00Z",
    "version": "1.0.0",
    "database": "connected"
}
```

2) GET /passengers
Request (query params opcionales): page, limit, status, search
Ejemplo: GET /passengers?page=1&limit=20&status=active
Response (200):
```json
{
    "data": [ { "passenger_id": "pass_001", "full_name": "Juan Pérez", "email": "juan@mail.com" } ],
    "pagination": { "page": 1, "limit": 20, "total": 150, "pages": 8 }
}
```

3) POST /passengers
Request body (application/json):
```json
{
    "full_name": "María López",
    "email": "maria@mail.com",
    "phone": "+51987654321",
    "document_type": "DNI",
    "document_number": "87654321",
    "date_of_birth": "1995-04-10"
}
```
Response (201):
```json
{
    "message": "Passenger created successfully",
    "data": { "passenger_id": "pass_123", "full_name": "María López", "email": "maria@mail.com" }
}
```

4) GET /passengers/{id}
Request: path param `id` (ej: pass_123)
Response (200):
```json
{ "data": { "passenger_id": "pass_123", "full_name": "María López", "email": "maria@mail.com", "status": "active" } }
```

5) PUT /passengers/{id}
Request body (application/json):
```json
{ "phone": "+51911122233", "status": "active" }
```
Response (200):
```json
{ "message": "Passenger updated successfully", "data": { "passenger_id": "pass_123", "phone": "+51911122233" } }
```
- [ ] Implementar authentication/authorization (si requerido)
- [ ] Configurar HTTPS en producción

### Monitoring & Observability
- [ ] Configurar health checks detallados
- [ ] Métricas de performance
- [ ] Logging de errores
- [ ] Tracing distribuido
- [ ] Alertas de monitoreo

## Seed Data / Datos Iniciales

El microservicio incluye un sistema automático de poblado de base de datos con datos de prueba.

### Comportamiento Automático
- ✅ Al iniciar el contenedor/aplicación, **automáticamente** se pobla la base de datos con 10 pasajeros de ejemplo
- ✅ Solo se ejecuta si la base de datos está vacía (no duplica datos)
- ✅ Los pasajeros se generan con datos realistas (nombres, emails, teléfonos, documentos, etc.)

### Seed Manual (Opcional)
Si necesitas poblar la base de datos manualmente:

```bash
# Opción 1: Script standalone
python seed.py

# Opción 2: Módulo directo
python -m src.seed_data
```

### Datos Generados
El seed crea 10 pasajeros con:
- IDs secuenciales: `PASS001`, `PASS002`, ..., `PASS010`
- Nombres completos realistas
- Emails válidos basados en los nombres
- Teléfonos españoles (+34...)
- Tipos de documento: DNI, PASSPORT, CE
- Fechas de nacimiento (18-70 años)
- Fechas de registro (últimos 2 años)
- 90% activos, 10% inactivos

### Verificar Datos
Después del seed, puedes verificar:
```bash
# Listar todos los pasajeros
curl http://localhost:8001/api/v1/passengers

# Ver un pasajero específico
curl http://localhost:8001/api/v1/passengers/PASS001
```

## Comandos de Desarrollo

### Local Development
```bash
# Python con FastAPI (stack actual)
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8001

# El seed se ejecuta automáticamente al iniciar
# Verás en consola: "📦 Seeding database with sample passengers..."
```

### Docker
```bash
# Build
docker build -t ms-passengers .

# Run
docker run -p 8001:8001 --env-file .env ms-passengers

# Con Docker Compose (desde raíz del proyecto)
cd ../../infra
docker-compose up ms-passengers
```

### Testing
```bash
# TODO: Completar según stack elegido

# Ejemplo Node.js:
# npm test
# npm run test:coverage

# Ejemplo Python:
# pytest
# pytest --cov=src

# Ejemplo Java:
# ./mvnw test

# Ejemplo Go:
# go test ./...
```

## Integración con otros Microservicios

### Consumido por:
- **ms-history** - Para obtener historial de pasajeros
- **Frontend** - Para gestión de pasajeros en UI

### Consume:
- Ninguno (microservicio base con DB)

## Schema de Base de Datos (Preliminar)

### Tabla: passengers
```sql
-- TODO: Ajustar según motor SQL elegido
CREATE TABLE passengers (
    passenger_id VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    document_type VARCHAR(20) NOT NULL,
    document_number VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Índices recomendados
CREATE INDEX idx_passengers_email ON passengers(email);
CREATE INDEX idx_passengers_status ON passengers(status);
CREATE INDEX idx_passengers_document ON passengers(document_type, document_number);
```

## Notas de Implementación

- **UUID vs Auto-increment**: Considerar UUID para distribuibilidad
- **Soft Delete**: Implementar borrado lógico si se requiere auditoría
- **Auditoría**: Registrar cambios en tabla de auditoría si es necesario
- **Performance**: Configurar índices según patrones de consulta
- **Backup**: Política de respaldo según criticidad de datos

## Ownership
**Responsable**: @B1 (Backend Developer 1)
