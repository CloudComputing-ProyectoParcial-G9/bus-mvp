# Microservicio Analítico (ms-analytics)

## Descripción
Este microservicio ejecuta consultas analíticas sobre datos almacenados en object storage (S3/GCS/Blob) usando un motor de consulta serverless (Athena/BigQuery/Synapse). En entorno local retorna datos mock para desarrollo.

## Tecnología Stack
**TODO**: Definir según elección del equipo de desarrollo

### Opciones sugeridas:
- **Python** + FastAPI + boto3/google-cloud/azure-sdk
- **Node.js** + Express + AWS SDK/GCP SDK/Azure SDK
- **Java** + Spring Boot + AWS SDK/GCP SDK/Azure SDK
- **Go** + Gin + cloud SDKs
- **C#** + ASP.NET Core + Azure SDK

## Infraestructura Cloud
- **Object Storage**: S3 (AWS) / Cloud Storage (GCP) / Blob Storage (Azure)
- **Data Catalog**: Glue (AWS) / Data Catalog (GCP) / Purview (Azure)
- **Query Engine**: Athena (AWS) / BigQuery (GCP) / Synapse (Azure)
- **Resultados**: S3/GCS/Blob bucket para outputs de consultas

## Endpoints Principales
Ver especificación completa en `openapi.yaml`

### Analytics Endpoints
- `GET /health` - Health check + estado de servicios cloud
- `GET /analytics/revenue-by-route` - Ingresos por ruta y período
- `GET /analytics/occupancy-trends` - Tendencias de ocupación
- `GET /analytics/customer-segmentation` - Segmentación de clientes
- `GET /analytics/route-performance` - Performance de rutas
- `POST /analytics/query/custom` - Consultas SQL personalizadas (solo nube)

## Variables de Entorno Requeridas

### Configuración General
```bash
# Configuración del servicio
MS_ANALYTICS_PORT=8010
NODE_ENV=development
LOG_LEVEL=info

# Entorno (local = mock data, cloud = real queries)
ENVIRONMENT=local  # o 'cloud'
```

### Variables Cloud (Provider-Agnostic)
```bash
# Almacenamiento de objetos
CLOUD_REGION=us-east-1
OBJECT_STORE_BUCKET=bus-mvp-data-lake
QUERY_OUTPUT_PATH=s3://bus-mvp-data-lake/results/query-outputs/

# Catálogo de datos
CATALOG_DATABASE=bus_mvp_catalog

# Query Engine
QUERY_ENGINE_WORKGROUP=bus-mvp-analytics
QUERY_TIMEOUT_SECONDS=300
MAX_QUERY_RESULTS=10000
```

### Variables específicas por proveedor

#### AWS
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_GLUE_CATALOG_DATABASE=bus_mvp_catalog
AWS_ATHENA_WORKGROUP=bus-mvp-analytics
AWS_S3_BUCKET=bus-mvp-data-lake
```

#### Google Cloud
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCP_PROJECT_ID=bus-mvp-project
GCP_DATASET_ID=bus_mvp_catalog
GCP_BUCKET=bus-mvp-data-lake
BIGQUERY_LOCATION=US
```

#### Azure
```bash
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
AZURE_STORAGE_ACCOUNT=busmvpdatalake
AZURE_CONTAINER=raw-data
AZURE_SYNAPSE_WORKSPACE=bus-mvp-analytics
```

## Estructura del Código (Placeholder)

```
src/
├── controllers/
│   ├── healthController.py
│   ├── revenueAnalyticsController.py
│   ├── occupancyAnalyticsController.py
│   ├── customerAnalyticsController.py
│   ├── routeAnalyticsController.py
│   └── customQueryController.py
├── services/
│   ├── queryEngineService.py
│   ├── dataCatalogService.py
│   ├── objectStorageService.py
│   └── mockDataService.py
├── clients/
│   ├── awsClient.py
│   ├── gcpClient.py
│   └── azureClient.py
├── queries/
│   ├── revenue_queries.sql
│   ├── occupancy_queries.sql
│   ├── customer_queries.sql
│   └── route_queries.sql
├── routes/
│   ├── health.py
│   ├── analytics.py
│   └── custom_query.py
├── middleware/
│   ├── authMiddleware.py
│   ├── errorHandler.py
│   └── logger.py
├── utils/
│   ├── queryBuilder.py
│   ├── dataTransformers.py
│   └── validators.py
├── config/
│   ├── cloudConfig.py
│   └── server.py
└── main.py
```

## Tareas Pendientes

### Configuración Cloud
- [ ] Elegir proveedor cloud (AWS/GCP/Azure)
- [ ] Configurar acceso a object storage
- [ ] Configurar acceso a data catalog
- [ ] Configurar acceso a query engine
- [ ] Implementar autenticación cloud
- [ ] Configurar permisos IAM/RBAC

### Query Engine Integration
- [ ] Implementar cliente para motor de consulta elegido
- [ ] Crear plantillas SQL reutilizables
- [ ] Configurar gestión de resultados de consultas
- [ ] Implementar cache de resultados frecuentes
- [ ] Configurar timeouts y retry logic
- [ ] Implementar monitoring de costos

### Mock Data (Local)
- [ ] Generar datasets mock realistas
- [ ] Implementar service mock que simule query engine
- [ ] Crear respuestas consistentes con schemas cloud
- [ ] Configurar variabilidad en datos mock
- [ ] Implementar delays simulados

### API Implementation
- [ ] Implementar todos los endpoints según OpenAPI spec
- [ ] Configurar validación de parámetros de consulta
- [ ] Implementar transformación de resultados
- [ ] Añadir paginación para resultados grandes
- [ ] Configurar rate limiting
- [ ] Implementar logging estructurado

### Security & Performance
- [ ] Implementar autenticación para consultas custom
- [ ] Validar consultas SQL para prevenir inyección
- [ ] Configurar límites de recursos por consulta
- [ ] Implementar whitelist de tablas accesibles
- [ ] Configurar monitoring de performance
- [ ] Implementar alertas de costos

### Testing
- [ ] Unit tests para controllers y services
- [ ] Integration tests con mocks de cloud services
- [ ] Tests de validación de consultas SQL
- [ ] Tests de performance con datasets grandes
- [ ] Setup de CI/CD testing

### Monitoring & Observability
- [ ] Health checks de servicios cloud
- [ ] Métricas de performance de consultas
- [ ] Logging de costos de consultas
- [ ] Tracing distribuido
- [ ] Alertas de fallos de consulta

## Comandos de Desarrollo

### Local Development
```bash
# TODO: Completar según stack elegido

# Ejemplo Python:
# pip install -r requirements.txt
# uvicorn main:app --reload --port 8010

# Ejemplo Node.js:
# npm install
# npm run dev

# Ejemplo Java:
# ./mvnw spring-boot:run

# Ejemplo Go:
# go mod tidy
# go run main.go
```

### Docker
```bash
# Build
docker build -t ms-analytics .

# Run (local mode)
docker run -p 8010:8010 -e ENVIRONMENT=local ms-analytics

# Run (cloud mode)
docker run -p 8010:8010 --env-file .env.cloud ms-analytics

# Con Docker Compose (desde raíz del proyecto)
cd ../../infra
docker-compose up ms-analytics
```

### Testing
```bash
# TODO: Completar según stack elegido

# Ejemplo Python:
# pytest
# pytest tests/integration/

# Ejemplo Node.js:
# npm test
# npm run test:integration

# Ejemplo Java:
# ./mvnw test

# Ejemplo Go:
# go test ./...
```

## Integración con otros Microservicios

### Consumido por:
- **Frontend** - Para mostrar dashboards y reportes analíticos
- **ms-history** - Puede consumir análisis para enriquecer historiales

### Consume:
- **Object Storage** - Lee datos CSV/JSON depositados por data ingestion
- **Data Catalog** - Consulta metadata de tablas disponibles
- **Query Engine** - Ejecuta consultas SQL sobre datos

## Queries SQL Base (Ver docs/analytics/queries_and_views.sql)

### Revenue by Route
```sql
-- Ver implementación completa en docs/analytics/queries_and_views.sql
SELECT 
    t.route_code,
    t.origin_city,
    t.destination_city,
    DATE(t.departure_time) as travel_date,
    COUNT(tk.ticket_id) as total_tickets,
    SUM(tk.total_price) as total_revenue
FROM trips_raw t
JOIN tickets_raw tk ON t.trip_id = tk.trip_id
WHERE t.year >= 2024 AND tk.booking_status = 'confirmed'
GROUP BY t.route_code, t.origin_city, t.destination_city, DATE(t.departure_time)
ORDER BY total_revenue DESC;
```

### Occupancy Trends
```sql
-- Ver implementación completa en docs/analytics/queries_and_views.sql
SELECT 
    EXTRACT(dow FROM t.departure_time) as day_of_week,
    COUNT(DISTINCT t.trip_id) as total_trips,
    COUNT(tk.ticket_id) as tickets_sold,
    SUM(t.bus_capacity) as total_capacity,
    ROUND(COUNT(tk.ticket_id) * 100.0 / SUM(t.bus_capacity), 2) as avg_occupancy_rate
FROM trips_raw t
LEFT JOIN tickets_raw tk ON t.trip_id = tk.trip_id 
WHERE t.status = 'completed' AND tk.booking_status = 'confirmed'
GROUP BY EXTRACT(dow FROM t.departure_time)
ORDER BY day_of_week;
```

## Mock Data (Local Environment)

### Revenue by Route Mock
```python
# Ejemplo de datos mock para desarrollo local
mock_revenue_data = [
    {
        "route_code": "RT001",
        "route_name": "Madrid - Barcelona Express",
        "origin_city": "Madrid",
        "destination_city": "Barcelona", 
        "period": "2024-01",
        "total_revenue": 25750.50,
        "total_tickets": 567,
        "total_trips": 25,
        "average_price": 45.42,
        "revenue_growth": 12.5
    },
    # ... más datos mock
]
```

## Cloud Provider Integration

### AWS Implementation
```python
import boto3

# Athena client
athena_client = boto3.client('athena', region_name=AWS_REGION)

# S3 client for results
s3_client = boto3.client('s3', region_name=AWS_REGION)

# Execute query
def execute_athena_query(sql_query):
    response = athena_client.start_query_execution(
        QueryString=sql_query,
        QueryExecutionContext={'Database': CATALOG_DATABASE},
        ResultConfiguration={'OutputLocation': QUERY_OUTPUT_PATH}
    )
    return response['QueryExecutionId']
```

### Google Cloud Implementation
```python
from google.cloud import bigquery

# BigQuery client
client = bigquery.Client(project=GCP_PROJECT_ID)

# Execute query
def execute_bigquery_query(sql_query):
    query_job = client.query(sql_query)
    results = query_job.result()
    return [dict(row) for row in results]
```

### Azure Implementation
```python
import pyodbc
from azure.identity import DefaultAzureCredential

# Synapse connection
def execute_synapse_query(sql_query):
    conn_string = f"Driver={{ODBC Driver 17 for SQL Server}};Server={SYNAPSE_ENDPOINT};Database={DATABASE};Authentication=ActiveDirectoryDefault"
    with pyodbc.connect(conn_string) as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        return cursor.fetchall()
```

## Patterns Implementados

### Query Template Pattern
```python
# Plantillas SQL parametrizables
REVENUE_BY_ROUTE_QUERY = """
SELECT 
    t.route_code,
    SUM(tk.total_price) as total_revenue,
    COUNT(tk.ticket_id) as total_tickets
FROM trips_raw t
JOIN tickets_raw tk ON t.trip_id = tk.trip_id
WHERE t.year >= {year_from}
    AND t.month >= {month_from}
    {route_filter}
    {date_filter}
GROUP BY t.route_code
ORDER BY total_revenue DESC
LIMIT {limit}
"""
```

### Result Caching
```python
# Cache de resultados para consultas frecuentes
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_result(query_hash):
    cached = redis_client.get(query_hash)
    return json.loads(cached) if cached else None

def cache_result(query_hash, result, ttl=300):
    redis_client.setex(query_hash, ttl, json.dumps(result))
```

## Notas de Implementación

- **Dual Mode**: Debe funcionar en local (mock) y nube (real queries)
- **Cost Control**: Implementar límites de costo y time-out
- **Security**: Validar y sanitizar todas las consultas SQL
- **Performance**: Cache resultados frecuentes, optimizar consultas
- **Monitoring**: Track costos, performance y errores de consultas

## Documentación Cloud

Ver [docs/analytics/catalog_design.md](../../docs/analytics/catalog_design.md) para:
- Configuración del catálogo de datos
- Estructura de tablas en object storage
- Variables de configuración por proveedor
- Políticas de particionado y lifecycle

Ver [docs/analytics/queries_and_views.sql](../../docs/analytics/queries_and_views.sql) para:
- Consultas SQL de ejemplo completas
- Vistas analíticas predefinidas
- Optimizaciones de performance
- Consideraciones de costos

## Ownership
**Responsable**: @A (Analytics & Data Science Team)
