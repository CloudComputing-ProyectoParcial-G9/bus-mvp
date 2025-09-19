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
- [ ] Implementar authentication/authorization (si requerido)
- [ ] Configurar HTTPS en producción

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

# Ejemplo Node.js:
# npm install
# npm run dev

# Ejemplo Python:
# pip install -r requirements.txt
# uvicorn main:app --reload --port 8001

# Ejemplo Java:
# ./mvnw spring-boot:run

# Ejemplo Go:
# go mod tidy
# go run main.go
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
