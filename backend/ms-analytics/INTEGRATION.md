# MS-Analytics - Integración con Bus MVP

Este documento explica cómo MS-Analytics se integra con el ecosistema completo de Bus MVP.

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                        BUS MVP ECOSYSTEM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐      ┌──────────────────────────────┐    │
│  │  Microservicios │      │    Data Ingestion Layer      │    │
│  ├─────────────────┤      ├──────────────────────────────┤    │
│  │ ms-passengers   │──┐   │ passengers-ingestion ────────┼─┐  │
│  │   (Port 3001)   │  │   │ trips-ingestion      ────────┼─┼─►│
│  │                 │  │   │ tickets-ingestion    ────────┼─┤  │
│  │ ms-trips        │──┤   │                               │ │  │
│  │   (Port 3002)   │  │   │ Strategy: 100% PULL           │ │  │
│  │                 │  │   │ Format: CSV + JSON            │ │  │
│  │ ms-tickets      │──┤   └───────────────────────────────┘ │  │
│  │   (Port 3003)   │  │                                      │  │
│  │                 │  │                                      │  │
│  │ ms-payment      │  │                                      │  │
│  │   (Port 3004)   │  │                                      │  │
│  └─────────────────┘  │                                      │  │
│                       │   ┌───────────────────────────────┐  │  │
│                       │   │       AWS S3 Bucket           │  │  │
│                       │   ├───────────────────────────────┤  │  │
│                       └──►│ bus-mvp-datalake/             │◄─┘  │
│                           │   raw/passengers_csv/         │     │
│                           │   raw/passengers_json/        │     │
│                           │   raw/trips_csv/              │     │
│                           │   raw/trips_json/             │     │
│                           │   raw/tickets_csv/            │     │
│                           │   raw/tickets_json/           │     │
│                           │   athena-results/             │     │
│                           └────────────┬──────────────────┘     │
│                                        │                         │
│                           ┌────────────▼──────────────────┐     │
│                           │     AWS Glue Catalog          │     │
│                           ├───────────────────────────────┤     │
│                           │ Database: bus_mvp_db          │     │
│                           │ Tables:                       │     │
│                           │   - passengers_csv            │     │
│                           │   - trips_csv                 │     │
│                           │   - tickets_csv               │     │
│                           │ Views:                        │     │
│                           │   - passenger_sales_summary   │     │
│                           │   - trip_occupancy_revenue    │     │
│                           └────────────┬──────────────────┘     │
│                                        │                         │
│                           ┌────────────▼──────────────────┐     │
│                           │       AWS Athena              │     │
│                           ├───────────────────────────────┤     │
│                           │ SQL Query Engine              │     │
│                           │ - 6 Queries                   │     │
│                           │ - 2 Views                     │     │
│                           │ - Analytics Processing        │     │
│                           └────────────┬──────────────────┘     │
│                                        │                         │
│  ┌────────────────────────────────────▼──────────────────────┐ │
│  │              MS-Analytics (Port 8005)                      │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ FastAPI + Python 3.11                                      │ │
│  │ Endpoints:                                                 │ │
│  │   GET /api/v1/analytics/summary      - Dashboard           │ │
│  │   GET /api/v1/analytics/passengers   - Passenger Analytics │ │
│  │   GET /api/v1/analytics/revenue      - Revenue Analytics   │ │
│  │   GET /api/v1/analytics/occupancy    - Occupancy Analytics │ │
│  │   GET /api/v1/analytics/trips        - Trip Analytics      │ │
│  │                                                             │ │
│  │ Documentation:                                             │ │
│  │   /docs  - Swagger UI                                      │ │
│  │   /redoc - ReDoc                                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## 🔄 Flujo de Datos Completo

### Paso 1: Operación de Microservicios
```
Usuario → ms-passengers → PostgreSQL (Pasajeros)
Usuario → ms-trips → PostgreSQL (Viajes)
Usuario → ms-tickets → MongoDB (Tickets)
```

### Paso 2: Ingesta de Datos (100% PULL)
```
passengers-ingestion → GET ms-passengers API → Transform → S3 (CSV + JSON)
trips-ingestion → GET ms-trips API → Transform → S3 (CSV + JSON)
tickets-ingestion → GET ms-tickets API → Transform → S3 (CSV + JSON)
```

### Paso 3: Catalogación
```
AWS Glue Crawlers → Scan S3 → Create/Update Tables → Glue Data Catalog
```

### Paso 4: Analytics Processing
```
Athena Queries → Query Glue Tables → Generate Results → S3
Athena Views → CREATE VIEW statements → Virtual Tables
```

### Paso 5: Exposición de Analytics
```
MS-Analytics → Query Athena → Transform Results → FastAPI Endpoints → JSON Response
```

## 📊 Dependencias de MS-Analytics

### Dependencias Directas

1. **AWS Athena**
   - Ejecuta queries SQL
   - Lee desde Glue Catalog
   - Escribe resultados a S3

2. **AWS Glue Database** (`bus_mvp_db`)
   - Tablas: `passengers_csv`, `trips_csv`, `tickets_csv`
   - Vistas: `passenger_sales_summary`, `trip_occupancy_revenue`

3. **AWS S3 Bucket** (`bus-mvp-datalake`)
   - Lee datos desde `raw/*_csv/`
   - Lee resultados desde `athena-results/`

### Dependencias Indirectas

4. **Data Ingestion Containers**
   - Deben ejecutarse para poblar S3
   - Sin datos → MS-Analytics retorna "No data found"

5. **Microservicios (ms-passengers, ms-trips, ms-tickets)**
   - Fuente de datos para ingesta
   - Deben estar corriendo para ingesta inicial

6. **AWS Glue Crawlers**
   - Deben ejecutarse para crear/actualizar tablas
   - Sin crawlers → Athena no puede consultar datos

## 🚀 Workflow de Deployment Completo

### Orden Recomendado

```bash
# 1. Levantar microservicios base
cd backend
docker-compose up -d ms-passengers ms-trips ms-tickets

# 2. Poblar datos (si es necesario)
# seed scripts o crear datos vía APIs

# 3. Ejecutar ingesta
cd ../data-ingestion
docker-compose up passengers-ingestion trips-ingestion tickets-ingestion

# 4. Configurar AWS Glue
python scripts/setup_complete_glue.py

# 5. Crear vistas de Athena
python scripts/create_athena_views.py

# 6. Ejecutar MS-Analytics
docker-compose up -d ms-analytics

# 7. Verificar
curl http://localhost:8005/api/v1/health
curl http://localhost:8005/api/v1/analytics/summary
```

## 🔌 Puertos del Ecosistema

| Servicio | Puerto | Tipo | Documentación |
|----------|--------|------|---------------|
| ms-passengers | 3001 | REST API | - |
| ms-trips | 3002 | REST API | - |
| ms-tickets | 3003 | REST API | - |
| ms-payment | 3004 | REST API | - |
| analytics-service | 5000 | Flask (Legacy) | - |
| **ms-analytics** | **8005** | **FastAPI** | **/docs** |
| frontend | 3000/5173 | Web Portal | - |

## 🔗 Endpoints de Integración

### MS-Analytics expone datos para:

1. **Frontend Dashboard**
   ```javascript
   // React/Vue/Angular
   const summary = await fetch('http://localhost:8005/api/v1/analytics/summary')
   const passengers = await fetch('http://localhost:8005/api/v1/analytics/passengers')
   ```

2. **Reporting Tools**
   ```python
   # Power BI, Tableau, etc.
   import requests
   response = requests.get('http://localhost:8005/api/v1/analytics/revenue')
   ```

3. **Automated Monitoring**
   ```bash
   # Cron job para health checks
   */5 * * * * curl http://localhost:8005/api/v1/health
   ```

## 🛡️ Seguridad y Configuración

### Variables de Entorno Compartidas

El archivo `.env` en `data-ingestion/` se comparte entre:
- passengers-ingestion
- trips-ingestion
- tickets-ingestion
- analytics-service (Flask)
- **ms-analytics (FastAPI)**

```env
# AWS Credentials (Compartido)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...
AWS_DEFAULT_REGION=us-east-1

# Athena Config (Compartido)
GLUE_DATABASE=bus_mvp_db
ATHENA_OUTPUT_LOCATION=s3://bus-mvp-datalake/athena-results/

# MS-Analytics Específico
APP_NAME=Bus MVP Analytics API
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO
```

### CORS Configuration

MS-Analytics permite requests desde:
```python
CORS_ORIGINS = [
    "http://localhost:3000",   # Frontend React
    "http://localhost:5173",   # Frontend Vite
    "http://localhost:8080"    # Frontend alternativo
]
```

## 📈 Escalabilidad

### Horizontal Scaling

```yaml
# docker-compose.yml
ms-analytics:
  deploy:
    replicas: 3
  ports:
    - "8005-8007:8005"
```

### Load Balancer Integration

```nginx
upstream ms_analytics {
    server localhost:8005;
    server localhost:8006;
    server localhost:8007;
}

server {
    location /api/v1/analytics {
        proxy_pass http://ms_analytics;
    }
}
```

## 🧪 Testing de Integración

### Test End-to-End

```bash
# 1. Verificar microservicios
curl http://localhost:3001/api/passengers | jq
curl http://localhost:3002/api/trips | jq
curl http://localhost:3003/api/tickets | jq

# 2. Ejecutar ingesta
docker-compose up passengers-ingestion

# 3. Verificar S3
aws s3 ls s3://bus-mvp-datalake/raw/passengers_csv/

# 4. Verificar Glue
aws glue get-table --database-name bus_mvp_db --name passengers_csv

# 5. Verificar Athena
# (Usar scripts/run_athena_queries.py)

# 6. Verificar MS-Analytics
curl http://localhost:8005/api/v1/analytics/summary | jq
```

## 📝 Logs y Monitoreo

### Centralización de Logs

```bash
# MS-Analytics logs
tail -f backend/ms-analytics/logs/app_*.log

# Ingestion logs
docker logs -f passengers-ingestion
docker logs -f trips-ingestion
docker logs -f tickets-ingestion

# AWS CloudWatch (opcional)
# Configurar en Dockerfile con awslogs driver
```

### Health Checks

```bash
# Script de monitoreo
while true; do
  echo -n "$(date) - "
  curl -s http://localhost:8005/api/v1/health | jq -r '.status'
  sleep 60
done
```

## 🎯 Best Practices

1. **Orden de ejecución**: Siempre seguir el workflow completo
2. **Credenciales AWS**: Renovar cada 4 horas (AWS Academy)
3. **Data refresh**: Re-ejecutar ingesta periódicamente
4. **Cache Athena**: Los resultados se cachean en S3
5. **Logs rotation**: Configurado a 7 días de retención
6. **Error handling**: MS-Analytics retorna HTTP 500 si Athena falla

## 🔄 Mantenimiento

### Actualizar Datos

```bash
# Re-ejecutar ingesta completa
cd data-ingestion
docker-compose up passengers-ingestion trips-ingestion tickets-ingestion

# Re-ejecutar crawlers
python scripts/setup_complete_glue.py

# MS-Analytics reflejará nuevos datos automáticamente
```

### Limpiar Cache

```bash
# Limpiar resultados de Athena
aws s3 rm s3://bus-mvp-datalake/athena-results/ --recursive

# MS-Analytics ejecutará queries frescas
```

## 📚 Documentación Relacionada

- **Proyecto**: `README.md` (raíz)
- **MS-Analytics**: `backend/ms-analytics/README.md`
- **Quick Start**: `backend/ms-analytics/QUICK_START.md`
- **Data Ingestion**: `data-ingestion/README.md`
- **Verificación**: `GUIA_VERIFICACION_REQUISITOS.md`
- **Athena Queries**: `docs/analytics/athena_queries.sql`
- **ER Diagram**: `docs/analytics/data_catalog_er.md`

---

**Versión**: 1.0.0  
**Última actualización**: 2024-01-15  
**Microservicio**: MS-Analytics (Port 8005)
