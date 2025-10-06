# 🚀 Bus MVP - Data Science Pipeline
## Documentación Completa del Proyecto

**Versión**: 1.0.0  
**Fecha**: Octubre 2025  
**Grupo**: 9 - Cloud Computing

---

## 📚 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Cumplimiento de Requisitos](#cumplimiento-de-requisitos)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Tecnologías Utilizadas](#tecnologías-utilizadas)
5. [Instalación y Configuración](#instalación-y-configuración)
6. [Componentes del Sistema](#componentes-del-sistema)
7. [AWS Services](#aws-services)
8. [Consultas y Vistas SQL](#consultas-y-vistas-sql)
9. [APIs Implementadas](#apis-implementadas)
10. [Guía de Deployment](#guía-de-deployment)
11. [Testing y Validación](#testing-y-validación)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Resumen Ejecutivo

Este proyecto implementa un **pipeline completo de Data Science** para el sistema Bus MVP, extrayendo datos de 3 microservicios diferentes, almacenándolos en un data lake S3, catalogándolos con AWS Glue, y proporcionando capacidades analíticas mediante AWS Athena y APIs REST.

### Características Principales

- ✅ **3 Contenedores de Ingesta Docker**: Extracción 100% de datos desde microservicios
- ✅ **Data Lake S3**: Almacenamiento dual (CSV + JSON) con estructura particionada
- ✅ **AWS Glue Catalog**: Metadata management con crawlers automáticos
- ✅ **AWS Athena**: 6+ consultas SQL complejas con JOINs
- ✅ **4 Vistas SQL**: Vistas materializadas para analytics
- ✅ **2 APIs REST**: 
  - `analytics-service` (Flask) - 8 endpoints para consultas Athena
  - `ms-analytics` (FastAPI) - Microservicio completo con documentación OpenAPI
- ✅ **Automatización**: Scripts de setup y deployment
- ✅ **Documentación**: Diagramas ER, guías, y ejemplos

---

## ✅ Cumplimiento de Requisitos

### Requisitos Obligatorios

| # | Requisito | Estado | Evidencia |
|---|-----------|--------|-----------|
| 1 | **MV Ingesta (EC2)** | ✅ | `AWS_EC2_DEPLOYMENT.md` - Guía completa de deployment |
| 2 | **Bucket S3** | ✅ | `scripts/setup_s3.py` - Bucket con estructura `/raw/`, `/processed/`, `/athena-results/` |
| 3 | **3 Contenedores Docker** | ✅ | `passengers-ingestion/`, `trips-ingestion/`, `tickets-ingestion/` |
| 4 | **Estrategia Pull 100%** | ✅ | Cada contenedor extrae todos los registros vía `GET /api/*` |
| 5 | **Archivos CSV + JSON** | ✅ | Cada ingesta genera ambos formatos con timestamp en carpetas separadas |
| 6 | **AWS Glue Catalog** | ✅ | `scripts/setup_glue.py` - Database + 3 crawlers automáticos |
| 7 | **Diagrama ER** | ✅ | `docs/er-diagrams/data_catalog_er.md` |
| 8 | **4+ Consultas SQL** | ✅ | `docs/analytics/queries_and_views.sql` - 6 consultas complejas |
| 9 | **2+ Vistas SQL** | ✅ | `docs/analytics/queries_and_views.sql` - 4 vistas materializadas |
| 10 | **Repositorio GitHub** | ✅ | https://github.com/CloudComputing-ProyectoParcial-G9/bus-mvp |

### Features Adicionales (Valor Agregado)

| Feature | Descripción | Ubicación |
|---------|-------------|-----------|
| **MS-Analytics (FastAPI)** | Microservicio completo con OpenAPI/Swagger | `../backend/ms-analytics/` |
| **8+ Endpoints REST** | API completa para analytics con documentación interactiva | Ver sección APIs |
| **Docker Compose** | Orquestación de 4 servicios (3 ingesta + 1 API) | `docker-compose.yml` |
| **Scripts de Automatización** | Setup S3, Glue, crawlers, vistas | `scripts/` |
| **Validación de Datos** | Health checks y validación de esquemas | Todos los contenedores |
| **Logging Estructurado** | Logs con timestamps y niveles con Loguru | `ms-analytics/logs/` |
| **Documentación OpenAPI** | Swagger UI y ReDoc interactivos | http://localhost:8005/docs |
| **Testing Automatizado** | Suite de tests con pytest y coverage | `ms-analytics/tests/` |

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MICROSERVICIOS FUENTE                           │
├─────────────────────────────────────────────────────────────────────┤
│  ms-passengers      │    ms-trips         │    ms-tickets           │
│  (PostgreSQL)       │    (PostgreSQL)     │    (MongoDB)            │
│  Flask API          │    Node.js API      │    Spring Boot API      │
│  Port: 3001         │    Port: 3002       │    Port: 3003           │
└──────┬──────────────┴──────────┬───────────────────┬────────────────┘
       │                         │                    │
       │ HTTP GET /api           │                    │
       │                         │                    │
┌──────▼─────────────────────────▼────────────────────▼───────────────┐
│              CAPA DE INGESTA - CONTENEDORES PYTHON                   │
├──────────────────────────────────────────────────────────────────────┤
│  passengers-        │   trips-            │   tickets-              │
│  ingestion          │   ingestion         │   ingestion             │
│  - Extract (API)    │   - Extract (API)   │   - Extract (API)       │
│  - Transform (Pandas)│  - Transform        │   - Transform           │
│  - Load S3 (CSV+JSON)│  - Load S3          │   - Load S3             │
└──────┬──────────────┴──────────┬───────────────────┬────────────────┘
       │                         │                    │
       │ boto3 put_object        │                    │
       │                         │                    │
       ▼                         ▼                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   AWS S3 DATA LAKE (bus-mvp-datalake-1)                │
├──────────────────────────────────────────────────────────────────────┤
│  s3://bus-mvp-datalake-1/                                              │
│  ├── raw/                                                            │
│  │   ├── passengers_csv/*.csv                                        │
│  │   ├── passengers_json/*.json                                      │
│  │   ├── trips_csv/*.csv                                             │
│  │   ├── trips_json/*.json                                           │
│  │   ├── tickets_csv/*.csv                                           │
│  │   └── tickets_json/*.json                                         │
│  ├── processed/                                                      │
│  └── athena-results/                                                 │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       │ AWS Glue Crawlers
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   AWS GLUE DATA CATALOG                              │
├──────────────────────────────────────────────────────────────────────┤
│  Database: bus_mvp_db                                                │
│  ├── passengers_csv (table)  - Schema auto-detected                 │
│  ├── trips_csv (table)       - Partitioned by year/month/day        │
│  └── tickets_csv (table)     - Metadata indexed                     │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       │ SQL Queries (Boto3/JDBC)
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       AWS ATHENA (Query Engine)                      │
├──────────────────────────────────────────────────────────────────────┤
│  - 6 Consultas SQL complejas con JOINs                               │
│  - 4 Vistas materializadas                                           │
│  - Resultados en s3://athena-results/                                │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       │ boto3.client('athena')
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    CAPA DE ANALYTICS - API REST                      │
├──────────────────────────────────────────────────────────────────────┤
│                     MS-Analytics (FastAPI)                           │
│                         Port: 8005                                   │
│                                                                      │
│  - GET /api/v1/analytics/summary     (Dashboard KPIs)               │
│  - GET /api/v1/analytics/passengers  (Segmentación clientes)        │
│  - GET /api/v1/analytics/revenue     (Análisis ingresos)            │
│  - GET /api/v1/analytics/occupancy   (Niveles ocupación)            │
│  - GET /api/v1/analytics/trips       (Estadísticas viajes)          │
│  - GET /docs                         (Swagger UI)                   │
│  - GET /redoc                        (ReDoc)                        │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       │ HTTP REST / JSON
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + TypeScript)                   │
│                     AnalyticsSection.tsx                             │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Tecnologías Utilizadas

### Lenguajes de Programación

| Lenguaje | Uso | Versión |
|----------|-----|---------|
| **Python** | Contenedores de ingesta, APIs de analytics | 3.11 |
| **SQL** | Consultas y vistas en AWS Athena | ANSI SQL |
| **Bash** | Scripts de automatización y deployment | - |
| **TypeScript** | Frontend (opcional) | 5.x |

### Frameworks y Librerías Python

| Framework/Librería | Propósito | Versión |
|-------------------|-----------|---------|
| **FastAPI** | Microservicio ms-analytics | 0.104.1 |
| **Pandas** | Transformación de datos en ingesta | Latest |
| **Boto3** | SDK de AWS | 1.34.34 |
| **Requests** | Cliente HTTP para consumir APIs | Latest |
| **Uvicorn** | ASGI server para FastAPI | 0.24.0 |
| **Pydantic** | Validación de datos y settings | 2.5.0 |
| **Loguru** | Logging estructurado | 0.7.2 |

### AWS Services

| Servicio | Propósito | Configuración |
|----------|-----------|---------------|
| **EC2** | Máquina virtual de ingesta | t3.medium (opcional) |
| **S3** | Data Lake | bucket: `bus-mvp-datalake-1` |
| **Glue** | Data Catalog y Crawlers | database: `bus_mvp_db` |
| **Athena** | Query engine SQL serverless | Workgroup: primary |
| **IAM** | Gestión de permisos | Roles/Users con políticas |

### DevOps y Contenedores

| Herramienta | Uso |
|-------------|-----|
| **Docker** | Contenedorización de servicios |
| **Docker Compose** | Orquestación multi-contenedor |
| **Git** | Control de versiones |

---

## 🚀 Instalación y Configuración

### Prerequisitos

1. **Software requerido**:
   - Docker 20.10+
   - Docker Compose 2.0+
   - Python 3.8+
   - AWS CLI 2.0+
   - Git

2. **Cuenta AWS** con permisos para EC2, S3, Glue, Athena, IAM

3. **Microservicios corriendo**:
   - ms-passengers (puerto 3001)
   - ms-trips (puerto 3002)
   - ms-tickets (puerto 3003)

### Setup Inicial

#### 1. Clonar Repositorio

```bash
git clone https://github.com/CloudComputing-ProyectoParcial-G9/bus-mvp.git
cd bus-mvp/data-ingestion
```

#### 2. Configurar Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar con tus credenciales
nano .env
```

**Contenido de `.env`**:
```env
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_SESSION_TOKEN=FwoGZXIvYXdzE...  # Solo para AWS Academy
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration
S3_BUCKET=bus-mvp-datalake-1

# Microservices URLs
PASSENGERS_API_URL=http://localhost:3001/api
TRIPS_API_URL=http://localhost:3002/api
TICKETS_API_URL=http://localhost:3003/api

# Glue Configuration
GLUE_DATABASE=bus_mvp_db

# Athena Configuration
ATHENA_OUTPUT_LOCATION=s3://bus-mvp-datalake-1/athena-results/

# API Configuration
DEBUG=True
LOG_LEVEL=INFO
```

#### 3. Crear Bucket S3

```bash
# Instalar dependencias
pip install -r scripts/requirements.txt

# Ejecutar script de setup
python scripts/setup_s3.py
```

Esto creará:
- Bucket: `bus-mvp-datalake-1`
- Carpetas: `raw/`, `processed/`, `athena-results/`

#### 4. Configurar AWS Glue

```bash
# Editar account ID en setup_glue.py
# Reemplazar YOUR_ACCOUNT_ID con tu AWS Account ID
nano scripts/setup_glue.py

# Ejecutar setup
python scripts/setup_glue.py
```

Esto creará:
- Database: `bus_mvp_db`
- 3 Crawlers: `passengers-crawler`, `trips-crawler`, `tickets-crawler`

---

## 📦 Componentes del Sistema

### 1. Contenedores de Ingesta

Cada contenedor extrae el 100% de los datos desde un microservicio y los carga a S3.

#### Passengers Ingestion

**Ubicación**: `passengers-ingestion/`

**Funcionalidad**:
- Extrae todos los pasajeros desde `GET /api/passengers`
- Transforma a DataFrame con Pandas
- Genera CSV y JSON con timestamp
- Carga a S3 en carpetas separadas:
  - `s3://bus-mvp-datalake-1/raw/passengers_csv/`
  - `s3://bus-mvp-datalake-1/raw/passengers_json/`

**Ejecución**:
```bash
docker-compose up passengers-ingestion
```

#### Trips Ingestion

**Ubicación**: `trips-ingestion/`

**Funcionalidad**:
- Extrae todos los viajes desde `GET /api/trips`
- Similar a passengers-ingestion
- Carpetas:
  - `s3://bus-mvp-datalake-1/raw/trips_csv/`
  - `s3://bus-mvp-datalake-1/raw/trips_json/`

**Ejecución**:
```bash
docker-compose up trips-ingestion
```

#### Tickets Ingestion

**Ubicación**: `tickets-ingestion/`

**Funcionalidad**:
- Extrae todos los tickets desde `GET /api/tickets`
- Similar a anteriores
- Carpetas:
  - `s3://bus-mvp-datalake-1/raw/tickets_csv/`
  - `s3://bus-mvp-datalake-1/raw/tickets_json/`

**Ejecución**:
```bash
docker-compose up tickets-ingestion
```

#### Ejecutar Todas las Ingestas

```bash
# Todas en paralelo
docker-compose up passengers-ingestion trips-ingestion tickets-ingestion

# O simplemente
docker-compose up
```

### 2. MS-Analytics (FastAPI)

**Ubicación**: `../backend/ms-analytics/`

**Descripción**: Microservicio completo con FastAPI, documentación OpenAPI, logging estructurado, y mejores prácticas.

**Tecnología**:
- FastAPI 0.104.1
- Uvicorn (ASGI server)
- Pydantic para validación
- Loguru para logging
- Boto3 para AWS

**Endpoints principales**:

- `GET /` - Root con info del servicio
- `GET /api/v1/health` - Health check con validación de Athena
- `GET /api/v1/analytics/summary` - Dashboard summary (KPIs ejecutivos)
- `GET /api/v1/analytics/passengers` - Análisis y segmentación de pasajeros
- `GET /api/v1/analytics/revenue` - Análisis de ingresos por ruta
- `GET /api/v1/analytics/occupancy` - Análisis de ocupación de buses
- `GET /api/v1/analytics/trips` - Estadísticas de viajes
- `GET /docs` - Swagger UI (documentación interactiva)
- `GET /redoc` - ReDoc (documentación alternativa)

**Ejecución**:
```bash
docker-compose up ms-analytics
# O localmente:
cd ../backend/ms-analytics
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8005
```

**URLs**:
- API: http://localhost:8005
- Swagger: http://localhost:8005/docs
- ReDoc: http://localhost:8005/redoc

**Estructura**:
```
ms-analytics/
├── src/
│   ├── main.py              # App FastAPI
│   ├── config.py            # Settings con Pydantic
│   ├── api/v1/endpoints/
│   │   ├── health.py
│   │   └── analytics.py
│   ├── services/
│   │   ├── athena_service.py
│   │   └── analytics_service.py
│   ├── models/
│   │   └── responses.py
│   └── core/
│       ├── logging.py
│       └── exceptions.py
├── tests/
├── logs/
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## ☁️ AWS Services

### AWS S3 - Data Lake

**Bucket**: `bus-mvp-datalake-1`

**Estructura**:
```
s3://bus-mvp-datalake-1/
├── raw/
│   ├── passengers_csv/
│   │   ├── passengers_20251005_143022.csv
│   │   └── passengers_20251005_150000.csv
│   ├── passengers_json/
│   │   ├── passengers_20251005_143022.json
│   │   └── passengers_20251005_150000.json
│   ├── trips_csv/
│   │   └── trips_20251005_143025.csv
│   ├── trips_json/
│   │   └── trips_20251005_143025.json
│   ├── tickets_csv/
│   │   └── tickets_20251005_143028.csv
│   └── tickets_json/
│       └── tickets_20251005_143028.json
├── processed/
└── athena-results/
    └── query-results/
```

**Ventajas**:
- Almacenamiento dual (CSV + JSON) para flexibilidad
- Carpetas separadas por tipo de dato
- Versionado con timestamp
- Costos bajos (S3 Standard)

### AWS Glue - Data Catalog

**Database**: `bus_mvp_db`

**Tablas catalogadas**:

1. **passengers_csv**
   - Fuente: `s3://bus-mvp-datalake-1/raw/passengers_csv/`
   - Schema: passenger_id, name, email, phone, status, etc.
   - Crawler: `passengers-crawler`

2. **trips_csv**
   - Fuente: `s3://bus-mvp-datalake-1/raw/trips_csv/`
   - Schema: trip_id, route_code, origin_city, destination_city, departure_time, bus_capacity, status, etc.
   - Crawler: `trips-crawler`

3. **tickets_csv**
   - Fuente: `s3://bus-mvp-datalake-1/raw/tickets_csv/`
   - Schema: ticket_id, passenger_id, trip_id, seat_number, price, booking_status, purchase_date, etc.
   - Crawler: `tickets-crawler`

**Crawlers**:
- Se ejecutan automáticamente para detectar esquemas
- Actualizan metadata cuando cambian los datos
- Configurados con IAM role adecuado

**Verificar tablas**:
```bash
aws glue get-tables --database-name bus_mvp_db
```

### AWS Athena - Query Engine

**Configuración**:
- Database: `bus_mvp_db`
- Workgroup: `primary`
- Output: `s3://bus-mvp-datalake-1/athena-results/`

**Características**:
- SQL serverless (sin infraestructura)
- Pago por datos escaneados
- Soporte ANSI SQL
- Integración con Glue Catalog

**Acceso**:
1. AWS Console → Athena
2. Seleccionar database: `bus_mvp_db`
3. Configurar results location
4. Ejecutar queries

---

## 🔍 Consultas y Vistas SQL

### Consultas SQL Implementadas (6+)

#### 1. Ingresos por Ruta y Fecha

**Propósito**: Analizar revenue por ruta y día

```sql
SELECT 
    t.route_code,
    t.origin_city,
    t.destination_city,
    DATE(t.departure_time) as travel_date,
    COUNT(tk.ticket_id) as total_tickets,
    SUM(tk.total_price) as total_revenue,
    AVG(tk.total_price) as avg_ticket_price,
    t.base_price,
    (SUM(tk.total_price) - (COUNT(tk.ticket_id) * t.base_price)) as price_variance
FROM trips_csv t
JOIN tickets_csv tk ON t.trip_id = tk.trip_id
WHERE t.year >= 2024 
    AND t.status = 'completed'
    AND tk.booking_status = 'confirmed'
GROUP BY 
    t.route_code, 
    t.origin_city, 
    t.destination_city,
    DATE(t.departure_time),
    t.base_price
ORDER BY total_revenue DESC, travel_date DESC;
```

#### 2. Top Rutas por Tickets Vendidos

**Propósito**: Identificar rutas más populares

```sql
SELECT 
    t.route_code,
    CONCAT(t.origin_city, ' → ', t.destination_city) as route_description,
    COUNT(DISTINCT t.trip_id) as total_trips,
    COUNT(tk.ticket_id) as total_tickets_sold,
    SUM(tk.total_price) as total_revenue,
    AVG(t.bus_capacity) as avg_bus_capacity,
    ROUND(COUNT(tk.ticket_id) * 100.0 / (COUNT(DISTINCT t.trip_id) * AVG(t.bus_capacity)), 2) as occupancy_rate_percent,
    AVG(tk.total_price) as avg_ticket_price
FROM trips_csv t
LEFT JOIN tickets_csv tk ON t.trip_id = tk.trip_id 
    AND tk.booking_status = 'confirmed'
WHERE t.year = 2024 
GROUP BY 
    t.route_code, 
    t.origin_city, 
    t.destination_city
HAVING COUNT(tk.ticket_id) > 0
ORDER BY total_tickets_sold DESC
LIMIT 20;
```

#### 3. Análisis de Ocupación por Día de Semana

**Propósito**: Patrones de demanda según día

```sql
SELECT 
    EXTRACT(dow FROM t.departure_time) as day_of_week,
    CASE EXTRACT(dow FROM t.departure_time)
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
    END as day_name,
    COUNT(DISTINCT t.trip_id) as total_trips,
    COUNT(tk.ticket_id) as tickets_sold,
    SUM(t.bus_capacity) as total_capacity,
    ROUND(COUNT(tk.ticket_id) * 100.0 / SUM(t.bus_capacity), 2) as avg_occupancy_rate,
    SUM(tk.total_price) as daily_revenue
FROM trips_csv t
LEFT JOIN tickets_csv tk ON t.trip_id = tk.trip_id 
    AND tk.booking_status = 'confirmed'
WHERE t.year = 2024 
    AND t.status = 'completed'
GROUP BY EXTRACT(dow FROM t.departure_time)
ORDER BY day_of_week;
```

#### 4. Segmentación de Pasajeros

**Propósito**: Clasificar clientes por comportamiento

```sql
SELECT 
    p.passenger_id,
    p.full_name,
    p.email,
    COUNT(tk.ticket_id) as total_trips,
    SUM(tk.total_price) as total_spent,
    AVG(tk.total_price) as avg_ticket_price,
    MIN(tk.purchase_date) as first_purchase,
    MAX(tk.purchase_date) as last_purchase,
    COUNT(DISTINCT t.route_code) as routes_used,
    CASE 
        WHEN COUNT(tk.ticket_id) >= 20 THEN 'VIP'
        WHEN COUNT(tk.ticket_id) >= 10 THEN 'Frequent'
        WHEN COUNT(tk.ticket_id) >= 5 THEN 'Regular'
        ELSE 'Occasional'
    END as customer_segment
FROM passengers_csv p
JOIN tickets_csv tk ON p.passenger_id = tk.passenger_id
JOIN trips_csv t ON tk.trip_id = t.trip_id
WHERE p.status = 'active'
    AND tk.booking_status = 'confirmed'
GROUP BY p.passenger_id, p.full_name, p.email
HAVING COUNT(tk.ticket_id) >= 3
ORDER BY total_spent DESC;
```

#### 5. Revenue por Ruta (Simple JOIN)

```sql
SELECT 
    t.origin_city,
    t.destination_city,
    COUNT(tk.ticket_id) as tickets,
    SUM(tk.total_price) as revenue
FROM trips_csv t
JOIN tickets_csv tk ON t.trip_id = tk.trip_id
WHERE tk.booking_status = 'confirmed'
GROUP BY t.origin_city, t.destination_city
ORDER BY revenue DESC;
```

#### 6. Pasajeros Frecuentes por Ruta

```sql
SELECT 
    p.full_name,
    t.origin_city,
    t.destination_city,
    COUNT(*) as trips_count
FROM passengers_csv p
JOIN tickets_csv tk ON p.passenger_id = tk.passenger_id
JOIN trips_csv t ON tk.trip_id = t.trip_id
WHERE tk.booking_status = 'confirmed'
GROUP BY p.passenger_id, p.full_name, t.origin_city, t.destination_city
HAVING COUNT(*) >= 2
ORDER BY trips_count DESC;
```

### Vistas SQL (4)

#### Vista 1: daily_kpis

**Propósito**: KPIs diarios para dashboards

```sql
CREATE VIEW daily_kpis AS
SELECT 
    DATE(t.departure_time) as report_date,
    t.year,
    t.month,
    t.day,
    COUNT(DISTINCT t.trip_id) as total_trips,
    COUNT(DISTINCT t.route_code) as active_routes,
    SUM(t.bus_capacity) as total_capacity,
    COUNT(tk.ticket_id) as tickets_sold,
    COUNT(CASE WHEN tk.booking_status = 'confirmed' THEN 1 END) as confirmed_tickets,
    COUNT(CASE WHEN tk.booking_status = 'cancelled' THEN 1 END) as cancelled_tickets,
    SUM(CASE WHEN tk.booking_status = 'confirmed' THEN tk.total_price ELSE 0 END) as daily_revenue,
    AVG(CASE WHEN tk.booking_status = 'confirmed' THEN tk.total_price END) as avg_ticket_price,
    ROUND(COUNT(tk.ticket_id) * 100.0 / NULLIF(SUM(t.bus_capacity), 0), 2) as occupancy_rate,
    COUNT(DISTINCT tk.passenger_id) as unique_passengers
FROM trips_csv t
LEFT JOIN tickets_csv tk ON t.trip_id = tk.trip_id
WHERE t.status IN ('completed', 'in_progress')
GROUP BY DATE(t.departure_time), t.year, t.month, t.day
ORDER BY report_date DESC;
```

**Uso**:
```sql
SELECT * FROM daily_kpis WHERE report_date >= CURRENT_DATE - INTERVAL '30' DAY;
```

#### Vista 2: route_performance_ranking

**Propósito**: Ranking de rutas por performance

```sql
CREATE VIEW route_performance_ranking AS
SELECT 
    t.route_code,
    CONCAT(t.origin_city, ' → ', t.destination_city) as route_name,
    t.origin_city,
    t.destination_city,
    COUNT(DISTINCT t.trip_id) as total_trips,
    COUNT(DISTINCT DATE(t.departure_time)) as operating_days,
    AVG(t.bus_capacity) as avg_capacity,
    COUNT(tk.ticket_id) as total_tickets,
    COUNT(CASE WHEN tk.booking_status = 'confirmed' THEN 1 END) as confirmed_tickets,
    SUM(CASE WHEN tk.booking_status = 'confirmed' THEN tk.total_price ELSE 0 END) as total_revenue,
    AVG(CASE WHEN tk.booking_status = 'confirmed' THEN tk.total_price END) as avg_price,
    ROUND(COUNT(CASE WHEN tk.booking_status = 'confirmed' THEN 1 END) * 100.0 / 
          NULLIF(COUNT(DISTINCT t.trip_id) * AVG(t.bus_capacity), 0), 2) as avg_occupancy_rate,
    COUNT(DISTINCT tk.passenger_id) as unique_passengers,
    ROW_NUMBER() OVER (ORDER BY SUM(CASE WHEN tk.booking_status = 'confirmed' THEN tk.total_price ELSE 0 END) DESC) as revenue_rank
FROM trips_csv t
LEFT JOIN tickets_csv tk ON t.trip_id = tk.trip_id
WHERE t.year = 2024 AND t.status IN ('completed', 'in_progress')
GROUP BY t.route_code, t.origin_city, t.destination_city
HAVING COUNT(DISTINCT t.trip_id) >= 5
ORDER BY total_revenue DESC;
```

**Uso**:
```sql
SELECT * FROM route_performance_ranking WHERE revenue_rank <= 10;
```

#### Vista 3: passenger_sales_summary

**Propósito**: Resumen de ventas por pasajero

```sql
CREATE VIEW passenger_sales_summary AS
SELECT 
    p.passenger_id,
    p.full_name,
    p.email,
    COUNT(tk.ticket_id) as total_tickets,
    SUM(tk.total_price) as total_spent,
    AVG(tk.total_price) as avg_ticket_price,
    MIN(tk.purchase_date) as first_purchase,
    MAX(tk.purchase_date) as last_purchase,
    CASE 
        WHEN COUNT(tk.ticket_id) >= 10 OR SUM(tk.total_price) > 500 THEN 'VIP'
        WHEN COUNT(tk.ticket_id) >= 6 OR SUM(tk.total_price) > 300 THEN 'Frequent'
        WHEN COUNT(tk.ticket_id) >= 3 OR SUM(tk.total_price) > 100 THEN 'Regular'
        ELSE 'Occasional'
    END as customer_tier
FROM passengers_csv p
LEFT JOIN tickets_csv tk ON p.passenger_id = tk.passenger_id
    AND tk.booking_status = 'confirmed'
GROUP BY p.passenger_id, p.full_name, p.email;
```

#### Vista 4: trip_occupancy_revenue

**Propósito**: Ocupación y revenue por viaje

```sql
CREATE VIEW trip_occupancy_revenue AS
SELECT 
    t.trip_id,
    t.route_code,
    t.origin_city,
    t.destination_city,
    t.departure_time,
    t.bus_capacity,
    COUNT(tk.ticket_id) as tickets_sold,
    ROUND(COUNT(tk.ticket_id) * 100.0 / t.bus_capacity, 2) as occupancy_percent,
    SUM(CASE WHEN tk.booking_status = 'confirmed' THEN tk.total_price ELSE 0 END) as trip_revenue,
    CASE 
        WHEN ROUND(COUNT(tk.ticket_id) * 100.0 / t.bus_capacity, 2) > 90 THEN 'Full'
        WHEN ROUND(COUNT(tk.ticket_id) * 100.0 / t.bus_capacity, 2) > 70 THEN 'High'
        WHEN ROUND(COUNT(tk.ticket_id) * 100.0 / t.bus_capacity, 2) > 50 THEN 'Medium'
        ELSE 'Low'
    END as occupancy_level
FROM trips_csv t
LEFT JOIN tickets_csv tk ON t.trip_id = tk.trip_id
GROUP BY t.trip_id, t.route_code, t.origin_city, t.destination_city, 
         t.departure_time, t.bus_capacity;
```

---

## 🎯 APIs Implementadas

### MS-Analytics (FastAPI) - Puerto 8005

**Microservicio completo de analytics con FastAPI**

Ubicación: `backend/ms-analytics/`

#### Características

- ✅ Framework moderno: FastAPI 0.104.1
- ✅ Documentación automática: Swagger UI + ReDoc
- ✅ Validación con Pydantic
- ✅ Logging estructurado con Loguru
- ✅ Tests automatizados con pytest
- ✅ Async/await para mejor performance
- ✅ Health checks con validación de Athena

#### Endpoints Principales

##### 1. Root & Health

**Root**
```bash
GET /

Response:
{
  "service": "Bus MVP Analytics API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "health": "/api/v1/health"
}
```

##### 2. Health Check (con validación Athena)
```bash
GET /api/v1/health

Response:
{
  "status": "healthy",
  "service": "ms-analytics",
  "version": "1.0.0",
  "timestamp": "2025-10-05T10:30:00",
  "athena_connection": true,
  "database": "bus_mvp_db"
}
```

##### 3. Dashboard Summary
```bash
GET /api/v1/analytics/summary

Response:
{
  "timestamp": "2025-10-05T10:30:00",
  "summary": {
    "total_passengers": 150,
    "active_trips": 12,
    "tickets_sold": 450,
    "total_revenue": 45000.0,
    "average_occupancy": 75.5,
    "cancellation_rate": 5.2
  },
  "trends": {
    "revenue_growth": 12.3,
    "passenger_growth": 8.7
  }
}
```

##### 4. Passenger Analytics
```bash
GET /api/v1/analytics/passengers

Response:
{
  "segments": {
    "VIP": {
      "count": 15,
      "total_spent": 12500.00,
      "avg_tickets": 18.5
    },
    "Frequent": {
      "count": 35,
      "total_spent": 8750.00,
      "avg_tickets": 8.2
    }
  }
}
```

**Segmentación de clientes**:
- **VIP**: >10 tickets o >$500
- **Frequent**: 6-10 tickets o $301-$500
- **Regular**: 3-5 tickets o $101-$300
- **Occasional**: 1-2 tickets o <$100

##### 5. Revenue Analytics
```bash
GET /api/v1/analytics/revenue

Response:
{
  "by_route": [...],
  "by_status": {
    "confirmed": 42500.00,
    "cancelled": 2500.00
  },
  "total": 45000.00
}
```

##### 6. Occupancy Analytics
```bash
GET /api/v1/analytics/occupancy

Response:
{
  "levels": {
    "Full": { "count": 45, "percentage": 10.0 },
    "High": { "count": 135, "percentage": 30.0 },
    "Medium": { "count": 180, "percentage": 40.0 },
    "Low": { "count": 90, "percentage": 20.0 }
  },
  "average": 75.5
}
```

**Niveles de ocupación**:
- **Full**: >90%
- **High**: 70-90%
- **Medium**: 50-70%
- **Low**: 30-50%
- **Very Low**: <30%

##### 7. Trip Analytics
```bash
GET /api/v1/analytics/trips

Response:
{
  "total_trips": 450,
  "by_status": {
    "completed": 420,
    "in_progress": 20,
    "cancelled": 10
  },
  "avg_occupancy": 75.5
}
```

##### 8. Swagger UI (Documentación Interactiva)
```bash
GET /docs
```

Interfaz web interactiva para:
- Ver todos los endpoints
- Probar las APIs directamente
- Ver modelos de request/response
- Autenticación (si está configurada)

**URL**: http://localhost:8005/docs

##### 9. ReDoc (Documentación Detallada)
```bash
GET /redoc
```

Documentación alternativa más detallada y profesional.

**URL**: http://localhost:8005/redoc

#### Ejemplo de Uso

```bash
# Health check
curl http://localhost:8005/api/v1/health

# Dashboard summary
curl http://localhost:8005/api/v1/analytics/summary

# Passenger analytics
curl http://localhost:8005/api/v1/analytics/passengers

# Con parámetros
curl "http://localhost:8005/api/v1/analytics/trips?status=completed"
```

#### Testing

El microservicio incluye tests automatizados:

```bash
cd backend/ms-analytics

# Ejecutar tests
pytest

# Con coverage
pytest --cov=src --cov-report=html

# Ver reporte HTML
# Abrir htmlcov/index.html en navegador
```

---

## 🚀 Guía de Deployment

### Deployment Local (Desarrollo)

#### Opción 1: Docker Compose (Recomendado)

```bash
# Desde data-ingestion/
docker-compose up

# En background
docker-compose up -d

# Logs
docker-compose logs -f

# Detener
docker-compose down
```

Esto inicia:
- 3 contenedores de ingesta (passengers, trips, tickets)
- ms-analytics (puerto 8005)

#### Opción 2: Local Python

```bash
# MS-Analytics
cd backend/ms-analytics
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8005
```

### Deployment en AWS EC2

Ver guía completa: `AWS_EC2_DEPLOYMENT.md`

#### Resumen Rápido

**1. Lanzar EC2**:
```bash
aws ec2 run-instances \
    --image-id ami-0c7217cdde317cfec \
    --instance-type t3.medium \
    --key-name your-key \
    --security-group-ids sg-xxxxxxxx
```

**2. Conectar**:
```bash
ssh -i "your-key.pem" ubuntu@<PUBLIC_IP>
```

**3. Instalar Docker**:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

**4. Clonar y configurar**:
```bash
git clone https://github.com/CloudComputing-ProyectoParcial-G9/bus-mvp.git
cd bus-mvp/data-ingestion
cp .env.example .env
nano .env  # Configurar credenciales
```

**5. Ejecutar**:
```bash
# Con IAM Role (recomendado)
docker-compose up -d

# O con credenciales
# Asegurarse de tener AWS_ACCESS_KEY_ID, etc. en .env
docker-compose up -d
```

**6. Verificar**:
```bash
# Ver logs
docker-compose logs -f

# Health check
curl http://localhost:8005/api/v1/health

# Ver archivos en S3
aws s3 ls s3://bus-mvp-datalake-1/raw/ --recursive
```

### Deployment con IAM Roles (Seguridad Mejorada)

En EC2, es mejor usar IAM Roles en lugar de credenciales hardcoded:

**1. Crear IAM Role**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::bus-mvp-datalake-1",
        "arn:aws:s3:::bus-mvp-datalake-1/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "glue:GetDatabase",
        "glue:GetTable",
        "glue:GetTables",
        "glue:StartCrawler"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "athena:StartQueryExecution",
        "athena:GetQueryExecution",
        "athena:GetQueryResults"
      ],
      "Resource": "*"
    }
  ]
}
```

**2. Asociar a EC2**:
- EC2 Console → Instances → Actions → Security → Modify IAM Role
- Seleccionar el role creado

**3. No necesitas AWS credentials en `.env`**:
```env
# NO incluir:
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...

# Solo configurar:
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET=bus-mvp-datalake-1
# ... resto de variables
```

---

## 🧪 Testing y Validación

### Validar Ingesta

```bash
# 1. Ejecutar ingestas
docker-compose up passengers-ingestion trips-ingestion tickets-ingestion

# 2. Verificar archivos en S3
aws s3 ls s3://bus-mvp-datalake-1/raw/passengers_csv/
aws s3 ls s3://bus-mvp-datalake-1/raw/trips_csv/
aws s3 ls s3://bus-mvp-datalake-1/raw/tickets_csv/

# 3. Descargar y verificar contenido
aws s3 cp s3://bus-mvp-datalake-1/raw/passengers_csv/passengers_latest.csv - | head -10
```

### Validar AWS Glue

```bash
# 1. Listar tablas
aws glue get-tables --database-name bus_mvp_db

# 2. Ver schema de una tabla
aws glue get-table --database-name bus_mvp_db --name passengers_csv

# 3. Ejecutar crawler
aws glue start-crawler --name passengers-crawler

# 4. Verificar status
aws glue get-crawler --name passengers-crawler
```

### Validar Athena

**AWS Console**:
1. AWS Console → Athena
2. Seleccionar database: `bus_mvp_db`
3. Query editor:

```sql
-- Ver conteo
SELECT COUNT(*) FROM passengers_csv;
SELECT COUNT(*) FROM trips_csv;
SELECT COUNT(*) FROM tickets_csv;

-- Ver sample
SELECT * FROM passengers_csv LIMIT 10;

-- Probar JOIN
SELECT 
    p.full_name,
    COUNT(tk.ticket_id) as tickets
FROM passengers_csv p
JOIN tickets_csv tk ON p.passenger_id = tk.passenger_id
GROUP BY p.full_name
LIMIT 10;
```

### Validar APIs

```bash
# MS-Analytics (FastAPI)
curl http://localhost:8005/api/v1/health
curl http://localhost:8005/api/v1/analytics/summary

# Ver Swagger UI
# Abrir en navegador: http://localhost:8005/docs
```

### Tests Automatizados

**MS-Analytics tiene tests**:

```bash
cd ../backend/ms-analytics

# Ejecutar tests
pytest

# Con coverage
pytest --cov=src --cov-report=html

# Ver reporte
# Abrir htmlcov/index.html
```

---

## 🐛 Troubleshooting

### Problema: No puede conectar a microservicios

**Error**:
```
❌ Error fetching passengers: Connection refused
```

**Solución**:
```bash
# 1. Verificar que microservicios estén corriendo
docker ps | grep ms-

# 2. Verificar puertos
curl http://localhost:3001/api/passengers
curl http://localhost:3002/api/trips
curl http://localhost:3003/api/tickets

# 3. Verificar URLs en .env
cat .env | grep API_URL

# 4. Si estás en Docker, usar host.docker.internal
PASSENGERS_API_URL=http://host.docker.internal:3001/api
```

### Problema: Access Denied S3

**Error**:
```
botocore.exceptions.ClientError: Access Denied
```

**Solución**:
```bash
# 1. Verificar credenciales
aws sts get-caller-identity

# 2. Verificar permisos
aws s3 ls s3://bus-mvp-datalake-1/

# 3. Si usas AWS Academy, renovar session token
# Copiar nuevo AWS_SESSION_TOKEN al .env

# 4. Verificar que el bucket exista
aws s3 mb s3://bus-mvp-datalake-1
```

### Problema: Glue Crawler falla

**Error**:
```
Crawler failed: Unable to retrieve table metadata
```

**Solución**:
```bash
# 1. Verificar que haya datos en S3
aws s3 ls s3://bus-mvp-datalake-1/raw/passengers_csv/

# 2. Verificar formato de archivos
aws s3 cp s3://bus-mvp-datalake-1/raw/passengers_csv/passengers_latest.csv - | head -5

# 3. Verificar IAM role del crawler
aws glue get-crawler --name passengers-crawler

# 4. Re-ejecutar crawler
aws glue start-crawler --name passengers-crawler
```

### Problema: Athena query falla

**Error**:
```
SYNTAX_ERROR: Table does not exist
```

**Solución**:
```bash
# 1. Verificar que las tablas existan
aws glue get-tables --database-name bus_mvp_db

# 2. Ejecutar crawlers primero
python scripts/setup_glue.py

# 3. Verificar nombre de tabla
# Usar: passengers_csv NO passengers

# 4. Verificar permisos Athena
# IAM → Tu usuario → Policies
```

### Problema: Import errors en ms-analytics

**Error**:
```
ImportError: No module named 'fastapi'
```

**Solución**:
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Verificar virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows

# 3. Re-instalar
pip install -r requirements.txt
```

### Problema: Docker build falla

**Error**:
```
ERROR [stage-1 3/5] RUN pip install -r requirements.txt
```

**Solución**:
```bash
# 1. Limpiar cache
docker-compose build --no-cache

# 2. Verificar Dockerfile
cat passengers-ingestion/Dockerfile

# 3. Verificar requirements.txt
cat passengers-ingestion/requirements.txt

# 4. Build individual
cd passengers-ingestion
docker build -t passengers-ingestion:test .
```

---

## 📊 Estructura de Archivos

```
bus-mvp/
├── data-ingestion/
│   ├── DOCUMENTATION.md                 # ESTE ARCHIVO - Documentación completa
│   ├── README.md                        # Quick reference
│   ├── AWS_EC2_DEPLOYMENT.md            # Guía deployment AWS
│   ├── docker-compose.yml               # Orquestación (3 ingesta + ms-analytics)
│   ├── .env.example                     # Template configuración
│   │
│   ├── passengers-ingestion/
│   │   ├── Dockerfile
│   │   ├── ingest.py                    # Script ETL Python
│   │   └── requirements.txt
│   │
│   ├── trips-ingestion/
│   │   ├── Dockerfile
│   │   ├── ingest.py
│   │   └── requirements.txt
│   │
│   ├── tickets-ingestion/
│   │   ├── Dockerfile
│   │   ├── ingest.py
│   │   └── requirements.txt
│   │
│   └── scripts/
│       ├── setup_s3.py                  # Crear bucket S3
│       ├── setup_glue.py                # Configurar Glue Catalog
│       ├── create_athena_views.py       # Crear vistas SQL
│       └── requirements.txt
│
├── backend/
│   └── ms-analytics/                    # FastAPI microservice
│       ├── src/
│       │   ├── main.py                  # App FastAPI
│       │   ├── config.py                # Settings Pydantic
│       │   ├── api/v1/endpoints/
│       │   │   ├── health.py
│       │   │   └── analytics.py
│       │   ├── services/
│       │   │   ├── athena_service.py    # Servicio AWS Athena
│       │   │   └── analytics_service.py # Lógica de negocio
│       │   ├── models/
│       │   │   └── responses.py         # Modelos Pydantic
│       │   └── core/
│       │       ├── logging.py           # Logging con Loguru
│       │       └── exceptions.py        # Excepciones custom
│       ├── tests/
│       │   ├── test_health.py
│       │   └── test_analytics.py
│       ├── logs/                        # Logs aplicación
│       ├── requirements.txt
│       ├── Dockerfile
│       ├── README.md
│       └── openapi.yaml                 # Spec OpenAPI
│
└── docs/
    ├── analytics/
    │   ├── queries_and_views.sql        # 6 consultas + 4 vistas SQL
    │   ├── athena_queries.sql
    │   └── athena_views.sql
    └── er-diagrams/
        └── data_catalog_er.md           # Diagrama ER del catálogo
```

---

## 📈 Métricas del Proyecto

### Código
- **Archivos Python**: 15+
- **Archivos Dockerfile**: 4
- **Scripts de automatización**: 4
- **Líneas de código**: ~3,500+
- **Archivos de documentación**: 8

### Funcionalidad
- **Contenedores Docker**: 4 (3 ingesta + 1 API)
- **Endpoints REST**: 8+ (ms-analytics FastAPI)
- **Consultas SQL**: 6+
- **Vistas SQL**: 4
- **Servicios AWS**: 4 (EC2, S3, Glue, Athena)
- **Tablas catalogadas**: 3

### Documentación
- **Páginas de documentación**: 8+
- **Diagramas**: 2 (Arquitectura + ER)
- **READMEs**: 4
- **OpenAPI spec**: 1 (ms-analytics)

---

## ✅ Checklist de Implementación

### Infraestructura AWS
- [x] Bucket S3 creado (`bus-mvp-datalake-1`)
- [x] Estructura de carpetas en S3
- [x] EC2 configurada (opcional)
- [x] Security Groups configurados
- [x] IAM Roles/Policies creados

### Código
- [x] 3 contenedores de ingesta implementados
- [x] MS-Analytics (FastAPI) implementado
- [x] Docker Compose configurado
- [x] Scripts de automatización creados

### AWS Services
- [x] S3 bucket con datos CSV + JSON
- [x] Glue database creada (`bus_mvp_db`)
- [x] 3 Glue crawlers configurados y ejecutados
- [x] 3 tablas catalogadas (passengers_csv, trips_csv, tickets_csv)
- [x] Consultas SQL probadas en Athena
- [x] 4 vistas creadas en Athena

### Documentación
- [x] Documentación principal (este archivo)
- [x] README principal
- [x] Guía de deployment AWS
- [x] Diagrama ER
- [x] Consultas SQL documentadas
- [x] API endpoints documentados
- [x] OpenAPI spec (ms-analytics)

### Testing
- [x] Ingesta de passengers verificada
- [x] Ingesta de trips verificada
- [x] Ingesta de tickets verificada
- [x] Archivos CSV generados y en S3
- [x] Archivos JSON generados y en S3
- [x] Crawlers ejecutados exitosamente
- [x] Consultas SQL funcionando
- [x] Vistas creadas y verificadas
- [x] MS-Analytics funcionando
- [x] Tests automatizados (ms-analytics)

---

## 🎓 Conclusión

Este proyecto implementa un **pipeline completo de Data Science en AWS** que:

### ✅ Cumple todos los requisitos
1. MV Ingesta (EC2)
2. Bucket S3 con data lake
3. 3 contenedores Docker
4. Estrategia pull 100%
5. Archivos CSV + JSON
6. AWS Glue Catalog
7. Diagrama ER
8. 6+ consultas SQL
9. 4 vistas SQL
10. Repositorio GitHub

### 🎁 Añade valor adicional
- **API REST completa**: FastAPI con documentación OpenAPI
- **8+ endpoints**: Para diversos análisis de negocio
- **Documentación OpenAPI**: Con Swagger UI interactivo
- **Automatización completa**: Scripts de setup y deployment
- **Testing**: Tests automatizados con pytest
- **Logging estructurado**: Con Loguru para mejor debugging
- **Mejores prácticas**: Pydantic, async/await, validación de datos

### 🚀 Listo para
- ✅ Deployment en producción
- ✅ Integración con frontend
- ✅ Escalamiento horizontal
- ✅ Monitoreo y alertas
- ✅ CI/CD automation

---

## 📚 Links y Referencias

### Repositorio
- **GitHub**: https://github.com/CloudComputing-ProyectoParcial-G9/bus-mvp

### AWS Console
- **S3**: https://console.aws.amazon.com/s3/
- **Glue**: https://console.aws.amazon.com/glue/
- **Athena**: https://console.aws.amazon.com/athena/
- **EC2**: https://console.aws.amazon.com/ec2/

### APIs Locales
- **MS-Analytics**: http://localhost:8005
- **Swagger UI**: http://localhost:8005/docs
- **ReDoc**: http://localhost:8005/redoc

### Documentación AWS
- **Boto3**: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- **AWS Glue**: https://docs.aws.amazon.com/glue/
- **AWS Athena**: https://docs.aws.amazon.com/athena/
- **AWS S3**: https://docs.aws.amazon.com/s3/

### Frameworks
- **FastAPI**: https://fastapi.tiangolo.com/
- **Flask**: https://flask.palletsprojects.com/
- **Pandas**: https://pandas.pydata.org/

---

## 👥 Autores

**Grupo 9 - Cloud Computing**  
Proyecto Parcial - 2025

---

## 📄 Licencia

MIT License

---

**Última actualización**: Octubre 2025  
**Versión**: 1.0.0
