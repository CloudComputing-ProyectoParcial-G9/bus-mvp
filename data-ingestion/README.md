# Data Ingestion - Sistema de Ingesta de Datos

## Descripción
Conjunto de 3 contenedores especializados para la ingesta completa de datos de las bases de datos de los microservicios del sistema Bus MVP. Cada contenedor se especializa en extraer, transformar y cargar todos los datos de una base de datos específica hacia el sistema de análisis.

## Requisitos del Proyecto
- ✅ **3 contenedores de ingesta dockerizados**
- ✅ **Extracción completa de datos de microservicios**
- ✅ **Integración con object storage**
- ✅ **Procesamiento y transformación de datos**
- ✅ **Sincronización de datos transaccionales**

## Prerequisites

### System Requirements
- Docker 20.10+ and Docker Compose 2.0+
- Minimum 8GB RAM, 20GB storage
- Network connectivity to microservices databases

### Database Configuration Requirements
- **PostgreSQL**: WAL level = logical, max_replication_slots ≥ 3
- **MySQL**: binlog_format = ROW, server-id configured
- **MongoDB**: Replica set enabled for change streams

### Required Network Access

#### Docker Network Configuration
```bash
# Main system network (from infra/docker-compose.yml)
bus-mvp-network (bridge): 172.18.0.0/16
  ├── sql-db1 (PostgreSQL): bus-mvp-sql-db1:5432
  ├── sql-db2 (MySQL): bus-mvp-sql-db2:3306  
  ├── nosql-db (MongoDB): bus-mvp-nosql-db:27017
  ├── ms-passengers: bus-mvp-ms-passengers:${MS_PASSENGERS_PORT}
  ├── ms-trips: bus-mvp-ms-trips:${MS_TRIPS_PORT}
  ├── ms-tickets: bus-mvp-ms-tickets:${MS_TICKETS_PORT}
  ├── ms-history: bus-mvp-ms-history:${MS_HISTORY_PORT}
  ├── ms-analytics: bus-mvp-ms-analytics:${MS_ANALYTICS_PORT}
  └── load-balancer: bus-mvp-load-balancer:${LB_PORT}

# Ingestion network (from data-ingestion/docker-compose.yml)  
bus-mvp-ingestion-network (bridge): 172.19.0.0/16
  ├── ms-passengers-db: bus-mvp-passengers-ingestion:8090
  ├── ms-trips-db: bus-mvp-trips-ingestion:8091
  ├── ms-tickets-db: bus-mvp-tickets-ingestion:8092
  └── redis-cache: bus-mvp-ingestion-redis:6380
```

#### Database Connection Requirements
```bash
# PostgreSQL (ms-passengers database)
Host: sql-db1 (internal) / localhost:${SQL1_PORT} (external)
Port: 5432
Database: ${SQL1_DB}
User: ${SQL1_USER}
SSL: Required in production

# MySQL (ms-trips database)  
Host: sql-db2 (internal) / localhost:${SQL2_PORT} (external)
Port: 3306
Database: ${SQL2_DB}
User: ${SQL2_USER}
Binary Log: Enabled for CDC

# MongoDB (ms-tickets database)
Host: nosql-db (internal) / localhost:27017 (external)
Port: 27017
Database: ${NOSQL_DB}
User: ${NOSQL_USER}
Replica Set: Required for change streams
```

#### External Dependencies
```bash
# Object Storage (AWS S3 Only)
AWS S3: https://s3.amazonaws.com

# Health Check Endpoints
ms-passengers-db: http://localhost:8090/health
ms-trips-db: http://localhost:8091/health  
ms-tickets-db: http://localhost:8092/health
```

## Testing

### Network Connectivity Tests
```bash
# Test database connectivity from ingestion containers
docker exec bus-mvp-passengers-ingestion pg_isready -h sql-db1 -p 5432 -U ${SQL1_USER}
docker exec bus-mvp-trips-ingestion mysqladmin ping -h sql-db2 -P 3306 -u ${SQL2_USER} -p${SQL2_PASSWORD}
docker exec bus-mvp-tickets-ingestion mongosh --host nosql-db:27017 --eval "db.adminCommand('ping')"

# Test health check endpoints
curl -f http://localhost:8090/health  # ms-passengers-db ingestion
curl -f http://localhost:8091/health  # ms-trips-db ingestion  
curl -f http://localhost:8092/health  # ms-tickets-db ingestion
```

### Database Setup Tests
```bash
# PostgreSQL CDC setup verification
docker exec bus-mvp-sql-db1 psql -U ${SQL1_USER} -d ${SQL1_DB} -c "
SELECT name, setting FROM pg_settings WHERE name IN ('wal_level', 'max_replication_slots');
SELECT slot_name, plugin, slot_type, active FROM pg_replication_slots;
"

# MySQL Binary Log verification  
docker exec bus-mvp-sql-db2 mysql -u ${SQL2_USER} -p${SQL2_PASSWORD} -e "
SHOW VARIABLES LIKE 'binlog_format';
SHOW VARIABLES LIKE 'server_id';  
SHOW MASTER STATUS;
"

# MongoDB Replica Set verification
docker exec bus-mvp-nosql-db mongosh --eval "
rs.status();
db.adminCommand('ismaster');
"
```

### Data Ingestion Tests
```bash
# Test full data extraction
cd data-ingestion/

# Test ms-passengers ingestion
docker-compose exec ms-passengers-db python -m pytest tests/test_postgres_connection.py -v
docker-compose exec ms-passengers-db python scripts/test_full_extraction.py --table passengers --limit 100

# Test ms-trips ingestion
docker-compose exec ms-trips-db python -m pytest tests/test_mysql_connection.py -v  
docker-compose exec ms-trips-db python scripts/test_full_extraction.py --tables trips,routes --limit 50

# Test ms-tickets ingestion
docker-compose exec ms-tickets-db python -m pytest tests/test_mongo_connection.py -v
docker-compose exec ms-tickets-db python scripts/test_full_extraction.py --collection tickets --limit 200
```

### Integration Tests
```bash
# End-to-end data flow testing
cd data-ingestion/
python -m pytest integration_tests/ -v

# Test data consistency across services
python scripts/test_data_consistency.py --validate-relationships --check-referential-integrity

# Test CDC/Change Streams functionality
python scripts/test_cdc.py --insert-test-data --verify-capture

# Load testing with sample data
python scripts/load_test.py \
  --passengers 10000 \
  --trips 5000 \
  --tickets 20000 \
  --duration 300
```

### Object Storage Tests
```bash
# Test AWS S3 connectivity (production)
aws s3 ls s3://bus-mvp-data-lake

# Test with Python boto3
python scripts/test_cloud_storage.py --provider aws --bucket bus-mvp-data-lake
```

### Performance Tests
```bash
# Database extraction performance
python scripts/benchmark_extraction.py \
  --source postgresql \
  --batch-sizes 100,500,1000,2000 \
  --concurrent-connections 1,2,5,10

python scripts/benchmark_extraction.py \
  --source mysql \
  --batch-sizes 100,500,1000,2000 \
  --concurrent-connections 1,2,5,10

python scripts/benchmark_extraction.py \
  --source mongodb \
  --batch-sizes 500,1000,2000,5000 \
  --concurrent-connections 1,2,5,10

# Network throughput testing
iperf3 -c sql-db1 -p 5432 -t 60 -P 4
iperf3 -c sql-db2 -p 3306 -t 60 -P 4  
iperf3 -c nosql-db -p 27017 -t 60 -P 4
```

### Docker Compose Test Scenarios
```bash
# Test individual containers
docker-compose up ms-passengers-db --build -d
docker-compose logs ms-passengers-db
docker-compose exec ms-passengers-db python scripts/health_check.py

# Test with dependencies
docker-compose up ms-trips-db redis-cache --build -d

# Test full ingestion system
docker-compose up --build -d
docker-compose ps
docker-compose logs -f --tail=100

# Test integration with main system
cd ../infra/
docker-compose -f docker-compose.yml -f ../data-ingestion/docker-compose.yml up --build
```

### Test Data Validation
```bash
# Create test datasets
python scripts/generate_test_data.py \
  --passengers 1000 \
  --trips 100 \
  --tickets 500 \
  --output tests/fixtures/

# Validate extracted data quality
python scripts/validate_extracted_data.py \
  --source s3://bus-mvp-data/ms-passengers/passengers/2024/09/26/ \
  --schema schemas/passenger_schema.json \
  --quality-threshold 0.95

# Compare source vs extracted data
python scripts/compare_data_integrity.py \
  --source-db postgresql://user:pass@sql-db1:5432/passengers_db \
  --extracted-data s3://bus-mvp-data/ms-passengers/ \
  --tolerance 0.01
```

### Monitoring and Alerts Tests
```bash
# Test Prometheus metrics exposure
curl http://localhost:8090/metrics | grep ingestion_records_total
curl http://localhost:8091/metrics | grep ingestion_duration_seconds
curl http://localhost:8092/metrics | grep data_quality_score

# Test alert rules
python scripts/test_alerts.py --simulate-high-lag --duration 600
python scripts/test_alerts.py --simulate-quality-drop --threshold 0.80
python scripts/test_alerts.py --simulate-connection-failure --service postgresql

# Test log aggregation
docker-compose logs --since=1h | grep ERROR
docker-compose logs --since=1h | grep "ingestion_completed" | wc -l
```

## Arquitectura de Ingesta

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   ms-passengers-db  │    │    ms-trips-db      │    │   ms-tickets-db     │
│   (Contenedor 1)    │    │   (Contenedor 2)    │    │   (Contenedor 3)    │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ • PostgreSQL        │    │ • MySQL             │    │ • MongoDB           │
│ • Passenger Data    │    │ • Trip Data         │    │ • Ticket Data       │
│ • Full DB Extract   │    │ • Route Data        │    │ • Booking Data      │
│ • CDC + Batch       │    │ • CDC + Batch       │    │ • CDC + Batch       │
└─────────┬───────────┘    └─────────┬───────────┘    └─────────┬───────────┘
          │                          │                          │
          └──────────────────────────┼──────────────────────────┘
                                     │
                          ┌─────────┴───────────┐
                          │   Object Storage    │
                          │      AWS S3         │
                          └─────────────────────┘
                                     │
                          ┌─────────┴───────────┐
                          │   Data Catalog      │
                          │  (ms-analytics)     │
                          └─────────────────────┘
```

## Estructura de Contenedores

### 1. MS-Passengers Database Ingestion (Contenedor 1)
**Base de Datos**: PostgreSQL  
**Propósito**: Extracción completa de datos de pasajeros desde ms-passengers.

**Tecnologías**:
- Python + SQLAlchemy/psycopg2
- PostgreSQL connector
- Change Data Capture (CDC) con pg_logical
- Batch processing con pandas

**Datos a extraer**:
```sql
-- Tabla: passengers
- passenger_id (Primary Key)
- full_name
- email
- phone
- document_type
- document_number
- date_of_birth
- registration_date
- status
- created_at, updated_at
```

**Estrategia de Ingesta**:
- **Inicial**: Full table scan y extracción completa
- **Incremental**: CDC basado en timestamps (created_at/updated_at)
- **Frecuencia**: Cada 5 minutos para cambios, diaria para full sync

### 2. MS-Trips Database Ingestion (Contenedor 2)
**Base de Datos**: MySQL  
**Propósito**: Extracción completa de datos de viajes y rutas desde ms-trips.

**Tecnologías**:
- Python + SQLAlchemy/PyMySQL
- MySQL connector
- Binary log parsing para CDC
- Batch processing optimizado

**Datos a extraer**:
```sql
-- Tabla: trips
- trip_id (Primary Key)
- route_id (Foreign Key)
- departure_date_time
- arrival_date_time
- bus_capacity
- available_seats
- final_price
- status
- driver_name
- bus_plate
- created_at, updated_at

-- Tabla: routes
- route_id (Primary Key)
- route_name
- origin_city
- destination_city
- distance_km
- estimated_duration
- base_price
- currency
- active
- created_at, updated_at
```

**Estrategia de Ingesta**:
- **Inicial**: Full extraction de trips y routes
- **Incremental**: MySQL binlog CDC + timestamp-based
- **Frecuencia**: Cada 2 minutos para trips activos, cada hora para routes

### 3. MS-Tickets Database Ingestion (Contenedor 3)
**Base de Datos**: MongoDB  
**Propósito**: Extracción completa de datos de tickets y reservas desde ms-tickets.

**Tecnologías**:
- Python + PyMongo
- MongoDB Change Streams
- Document transformation y flattening
- JSON schema validation

**Datos a extraer**:
```json
// Collection: tickets
{
  "_id": "ObjectId",
  "ticket_id": "string",
  "passenger_id": "string", 
  "trip_id": "string",
  "seat_number": "string",
  "booking_status": "string",
  "total_price": "double",
  "currency": "string",
  "created_at": "Instant"
}
```

**Estrategia de Ingesta**:
- **Inicial**: Collection scan completo
- **Incremental**: MongoDB Change Streams
- **Frecuencia**: Tiempo real via change streams + backup diario

## Comandos de Desarrollo

```bash
# Desarrollo individual de cada contenedor
cd data-ingestion/ms-passengers-db
docker build -t bus-mvp-passengers-ingestion .
docker run bus-mvp-passengers-ingestion

cd ../ms-trips-db  
docker build -t bus-mvp-trips-ingestion .
docker run bus-mvp-trips-ingestion

cd ../ms-tickets-db
docker build -t bus-mvp-tickets-ingestion .
docker run bus-mvp-tickets-ingestion

# Desarrollo con docker-compose (usando nombres actuales)
cd data-ingestion/
docker-compose up ms-passengers-db --build -d
docker-compose up ms-trips-db --build -d  
docker-compose up ms-tickets-db --build -d

# Sistema de ingesta completo
docker-compose up --build -d
docker-compose ps
docker-compose logs -f

# Integración con el sistema completo (requiere ambas redes)
cd ../infra/
# Opción 1: Usar redes externas compartidas
docker network create bus-mvp-shared-network
docker-compose -f docker-compose.yml -f ../data-ingestion/docker-compose.yml up --build

# Opción 2: Conectar redes existentes
docker network connect bus-mvp-network bus-mvp-passengers-ingestion
docker network connect bus-mvp-network bus-mvp-trips-ingestion
docker network connect bus-mvp-network bus-mvp-tickets-ingestion
```

## Pipeline de Datos

### Flujo General
1. **Conexión DB** → Cada contenedor se conecta a su base de datos específica
2. **Extracción** → Full sync inicial + CDC incremental para cambios
3. **Transformación** → Normalización, limpieza y enriquecimiento de datos
4. **Storage** → Almacenamiento en object storage con particionado temporal
5. **Cataloging** → Registro en el data catalog para consultas analíticas
6. **Availability** → Datos disponibles para ms-analytics y dashboards

### Estrategias por Base de Datos

#### PostgreSQL (ms-passengers)
- **Full Sync**: `SELECT * FROM passengers WHERE updated_at > last_sync`
- **CDC**: Logical replication slots o trigger-based
- **Particionado**: Por fecha de registro y región

#### MySQL (ms-trips)  
- **Full Sync**: `SELECT * FROM trips/routes WHERE updated_at > last_sync`
- **CDC**: Binary log parsing (mysqlbinlog)
- **Particionado**: Por fecha de viaje y ruta

#### MongoDB (ms-tickets)
- **Full Sync**: Collection scan con cursor
- **CDC**: Change streams nativo de MongoDB
- **Particionado**: Por fecha de creación y estado

### Formato de Datos Estándar
```json
{
  "metadata": {
    "source": "ms-passengers|ms-trips|ms-tickets",
    "source_db": "postgresql|mysql|mongodb", 
    "table_collection": "passengers|trips|routes|tickets",
    "extraction_type": "full|incremental|cdc",
    "timestamp": "2024-01-15T10:30:00Z",
    "extraction_id": "uuid",
    "record_count": 1500,
    "quality_score": 0.98
  },
  "schema": {
    "name": "passenger_data_v1|trip_data_v1|ticket_data_v1",
    "version": "1.0",
    "fields": [
      {
        "name": "passenger_id", 
        "type": "string",
        "nullable": false,
        "primary_key": true
      }
    ]
  },
  "data": [
    {
      // Registros específicos según la tabla/colección
      "passenger_id": "PASS_001",
      "full_name": "Juan Pérez",
      "email": "juan@email.com",
      // ... campos específicos
    }
  ]
}
```

## Configuración de Variables

Cada contenedor tiene configuración específica para conectarse a su base de datos:

### MS-Passengers Ingestion
```env
# PostgreSQL Connection (matches infra/docker-compose.yml)
SQL1_HOST=sql-db1  # Container name from main system
SQL1_PORT=5432
SQL1_DB=${SQL1_DB}  # From main system .env
SQL1_USER=${SQL1_USER}
SQL1_PASSWORD=${SQL1_PASSWORD}

# Network Configuration
DOCKER_NETWORK=bus-mvp-network
CONTAINER_NAME=bus-mvp-passengers-ingestion
HEALTH_CHECK_PORT=8090

# Ingestion Settings
EXTRACTION_INTERVAL=300  # 5 minutos
BATCH_SIZE=1000
CDC_ENABLED=true
FULL_SYNC_HOUR=2  # 2 AM daily full sync
```

### MS-Trips Ingestion  
```env
# MySQL Connection (matches infra/docker-compose.yml)
SQL2_HOST=sql-db2  # Container name from main system
SQL2_PORT=3306
SQL2_DB=${SQL2_DB}  # From main system .env
SQL2_USER=${SQL2_USER}
SQL2_PASSWORD=${SQL2_PASSWORD}

# Network Configuration
DOCKER_NETWORK=bus-mvp-network
CONTAINER_NAME=bus-mvp-trips-ingestion
HEALTH_CHECK_PORT=8091

# Ingestion Settings
EXTRACTION_INTERVAL=120  # 2 minutos
BATCH_SIZE=500
BINLOG_ENABLED=true
ROUTES_SYNC_INTERVAL=3600  # 1 hora
```

### MS-Tickets Ingestion
```env
# MongoDB Connection (matches infra/docker-compose.yml)
NOSQL_HOST=nosql-db  # Container name from main system
NOSQL_PORT=27017
NOSQL_DB=${NOSQL_DB}  # From main system .env
NOSQL_USER=${NOSQL_USER}
NOSQL_PASSWORD=${NOSQL_PASSWORD}
MONGO_URL=mongodb://${NOSQL_USER}:${NOSQL_PASSWORD}@nosql-db:27017/${NOSQL_DB}?authSource=admin

# Network Configuration
DOCKER_NETWORK=bus-mvp-network
CONTAINER_NAME=bus-mvp-tickets-ingestion
HEALTH_CHECK_PORT=8092

# Ingestion Settings
CHANGE_STREAMS=true
BATCH_SIZE=2000
FULL_SYNC_INTERVAL=86400  # 24 horas
```

### Object Storage (Común)
```env
# AWS S3 Configuration
AWS_S3_BUCKET=bus-mvp-data-lake
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Data Catalog
CATALOG_API_URL=http://bus-mvp-ms-analytics:${MS_ANALYTICS_PORT}/catalog
CATALOG_API_KEY=analytics_api_key

# Redis Cache (matches data-ingestion/docker-compose.yml)
REDIS_HOST=bus-mvp-ingestion-redis
REDIS_PORT=6380
REDIS_PASSWORD=defaultpassword
REDIS_URL=redis://:defaultpassword@redis-cache:6380
```

## Monitoreo y Observabilidad

### Métricas Clave por Contenedor
- **Passengers DB**: Registros nuevos/actualizados por minuto
- **Trips DB**: Viajes activos sincronizados, cambios en rutas
- **Tickets DB**: Tickets creados/modificados en tiempo real
- **Común**: Latencia de extracción, calidad de datos, errores de conexión

### Logs Estructurados
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "container": "ms-passengers-db",
  "event": "full_sync_completed",
  "database": "postgresql",
  "table": "passengers",
  "records_extracted": 15000,
  "processing_time_ms": 2500,
  "errors": 0,
  "quality_issues": 12
}
```

### Health Checks
```python
# Cada contenedor expone endpoints de salud
GET /health
{
  "status": "healthy",
  "database_connection": "ok",
  "last_extraction": "2024-01-15T10:25:00Z",
  "records_in_last_batch": 150,
  "cdc_lag_seconds": 5
}
```

## Integración con el Sistema

### Dependencias de Base de Datos
- **PostgreSQL**: Requiere ms-passengers activo y accesible
- **MySQL**: Requiere ms-trips activo con binlog habilitado  
- **MongoDB**: Requiere ms-tickets con change streams configurado

### Flujo de Datos
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  ms-passengers  │───▶│ PostgreSQL CDC   │───▶│ Object Storage  │
│     Service     │    │   Ingestion      │    │                 │
└─────────────────┘    └──────────────────┘    │                 │
                                               │                 │
┌─────────────────┐    ┌──────────────────┐    │                 │
│   ms-trips      │───▶│ MySQL Binlog     │───▶│ Partitioned     │
│   Service       │    │   Ingestion      │    │ by Service      │
└─────────────────┘    └──────────────────┘    │                 │
                                               │                 │
┌─────────────────┐    ┌──────────────────┐    │                 │
│  ms-tickets     │───▶│ MongoDB Streams  │───▶│                 │
│   Service       │    │   Ingestion      │    │                 │ 
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                               ┌─────────▼─────────┐
                                               │   ms-analytics    │
                                               │  Data Catalog &   │
                                               │   Analytics       │
                                               └───────────────────┘
```

### Con Object Storage
- **Estructura**: `/bus-mvp-data/{service}/{table}/{year}/{month}/{day}/`
- **Formato**: Parquet para análisis eficiente
- **Particionado**: Por servicio, tabla y fecha
- **Compresión**: GZIP para optimizar almacenamiento

### Con Microservicios Analíticos
- **ms-analytics**: Consume datos agregados para reporting
- **ms-history**: Accede a datos históricos de todas las fuentes
- **Dashboards**: Visualización unificada de métricas operativas

## Próximos Pasos

1. **Implementar Contenedores** (@A): Desarrollar lógica de conexión y extracción para cada DB
2. **Configurar CDC** (@A): Habilitar change data capture en PostgreSQL y MySQL
3. **Setup MongoDB Streams** (@A): Configurar change streams en MongoDB
4. **Testing de Conectividad** (@A): Pruebas de conexión con cada base de datos
5. **Configurar Object Storage** (@A): Setup de buckets y estructura de particionado
6. **Implementar Transformaciones** (@A): Normalización y limpieza de datos
7. **Monitoreo** (@PM): Dashboard de métricas de ingesta y calidad
8. **Documentación Técnica** (@A): Guías de troubleshooting y operación

## Consideraciones Técnicas

### Seguridad
- Conexiones encriptadas a bases de datos (SSL/TLS)
- Credenciales almacenadas en secrets/vault
- Network policies para acceso restringido
- Audit logs de todas las extracciones

### Performance
- Connection pooling para cada base de datos
- Batch processing optimizado por tipo de DB
- Compresión de datos en tránsito y reposo
- Índices optimizados para queries de extracción

### Reliability
- Retry logic con backoff exponencial
- Dead letter queues para registros fallidos
- Checkpoint/resume para extracciones largas
- Health checks y alertas automáticas

## Enlaces Útiles
- [Object Storage Config](../docs/analytics/catalog_design.md): Diseño del data catalog
- [Analytics Queries](../docs/analytics/queries_and_views.sql): Consultas sobre datos ingestados
- [Docker Compose](../infra/docker-compose.yml): Orquestación completa del sistema
