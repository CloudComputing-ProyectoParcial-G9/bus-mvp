# Microservicio Analítico (ms-analytics)

## Descripción
Este microservicio ejecuta consultas analíticas sobre datos almacenados en Amazon S3 usando Amazon Athena como motor de consulta serverless. Utiliza AWS Glue como catálogo de datos para gestionar metadata de las tablas. En entorno local retorna datos mock para desarrollo.

## Tecnología Stack
- **Framework**: FastAPI (Python)
- **AWS SDK**: boto3
- **HTTP Client**: httpx
- **Validation**: Pydantic
- **Testing**: pytest
- **Documentation**: OpenAPI/Swagger integrado con FastAPI

## Infraestructura AWS
- **Object Storage**: Amazon S3 - Almacenamiento del data lake
- **Data Catalog**: AWS Glue - Catálogo de metadata y esquemas
- **Query Engine**: Amazon Athena - Motor de consultas SQL serverless
- **Results Storage**: S3 bucket dedicado para outputs de consultas
- **Authentication**: AWS IAM roles y políticas

## Endpoints Principales
Ver especificación completa en `openapi.yaml`

### Analytics Endpoints (FastAPI)
- `GET /` - Redirect a documentación interactiva de FastAPI
- `GET /health` - Health check + estado de servicios AWS
- `GET /docs` - Documentación Swagger UI generada automáticamente por FastAPI
- `GET /redoc` - Documentación alternativa ReDoc
- `GET /analytics/revenue-by-route` - Ingresos por ruta y período
- `GET /analytics/occupancy-trends` - Tendencias de ocupación por día/hora
- `GET /analytics/customer-segmentation` - Segmentación de clientes
- `GET /analytics/route-performance` - Performance y métricas de rutas
- `POST /analytics/query/custom` - Consultas SQL personalizadas (solo AWS cloud mode)

## Variables de Entorno Requeridas

### Configuración General (FastAPI)
```bash
# Configuración del servicio FastAPI
MS_ANALYTICS_PORT=8010
FASTAPI_HOST=0.0.0.0
FASTAPI_RELOAD=true
FASTAPI_DEBUG=true
LOG_LEVEL=info

# Entorno (local = mock data, aws = real AWS queries)
ENVIRONMENT=local  # o 'aws'
```

### Variables AWS
```bash
# Configuración AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_PROFILE=default  # Opcional, para desarrollo local

# Amazon S3
AWS_S3_BUCKET=bus-mvp-data-lake
AWS_S3_RESULTS_BUCKET=bus-mvp-query-results
QUERY_OUTPUT_PATH=s3://bus-mvp-query-results/athena-outputs/

# AWS Glue Data Catalog
AWS_GLUE_CATALOG_DATABASE=bus_mvp_catalog
AWS_GLUE_TABLE_PREFIX=bus_mvp_

# Amazon Athena
AWS_ATHENA_WORKGROUP=bus-mvp-analytics
AWS_ATHENA_QUERY_TIMEOUT_SECONDS=300
AWS_ATHENA_MAX_RESULTS=10000
AWS_ATHENA_RESULT_LOCATION=s3://bus-mvp-query-results/athena-outputs/
```

```

## Estructura del Código (FastAPI)

```
src/
├── main.py                          # Punto de entrada FastAPI
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                  # Dependencias FastAPI (AWS clients, etc.)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py               # Router principal
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── health.py        # Health check endpoints
│   │           ├── analytics.py     # Analytics endpoints
│   │           └── custom_query.py  # Custom SQL queries
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Configuración Pydantic Settings
│   │   ├── logging.py               # Configuración logging
│   │   └── security.py              # Autenticación y autorización
│   ├── models/
│   │   ├── __init__.py
│   │   ├── analytics.py             # Modelos Pydantic para analytics
│   │   ├── requests.py              # Request models
│   │   └── responses.py             # Response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── aws_service.py           # Servicio AWS (Athena, S3, Glue)
│   │   ├── athena_service.py        # Cliente Amazon Athena
│   │   ├── s3_service.py            # Cliente Amazon S3
│   │   ├── glue_service.py          # Cliente AWS Glue
│   │   ├── analytics_service.py     # Lógica de negocio analytics
│   │   └── mock_service.py          # Mock data para desarrollo local
│   ├── queries/
│   │   ├── __init__.py
│   │   ├── templates/
│   │   │   ├── revenue_queries.sql
│   │   │   ├── occupancy_queries.sql
│   │   │   ├── customer_queries.sql
│   │   │   └── route_queries.sql
│   │   └── query_builder.py         # Constructor de queries SQL
│   └── utils/
│       ├── __init__.py
│       ├── aws_helpers.py           # Helpers específicos para AWS
│       ├── data_transformers.py     # Transformaciones de datos
│       └── validators.py            # Validadores custom
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Configuración pytest
│   ├── test_main.py                 # Tests FastAPI app
│   ├── test_analytics.py            # Tests endpoints analytics
│   ├── test_aws_services.py         # Tests servicios AWS
│   └── test_mock_services.py        # Tests mock services
└── requirements.txt                 # Dependencias Python
```

## Tareas Pendientes

### Configuración AWS
- [x] **Proveedor cloud elegido**: AWS
- [ ] Configurar bucket S3 para data lake
- [ ] Configurar bucket S3 para resultados de Athena
- [ ] Configurar AWS Glue Data Catalog
- [ ] Configurar workgroup de Amazon Athena
- [ ] Implementar autenticación AWS (IAM roles)
- [ ] Configurar políticas IAM para acceso a S3, Athena y Glue

### FastAPI Implementation
- [ ] Configurar aplicación FastAPI base
- [ ] Implementar modelos Pydantic para requests/responses
- [ ] Configurar Pydantic Settings para variables de entorno
- [ ] Implementar dependency injection para servicios AWS
- [ ] Configurar middleware de logging y error handling
- [ ] Implementar validación automática de schemas
- [ ] Configurar documentación OpenAPI automática

### AWS Services Integration
- [ ] Implementar cliente Amazon Athena con boto3
- [ ] Implementar cliente Amazon S3 para lectura de resultados
- [ ] Implementar cliente AWS Glue para metadata
- [ ] Crear service layer para abstracción de AWS
- [ ] Configurar gestión de resultados de consultas Athena
- [ ] Implementar retry logic y manejo de errores AWS
- [ ] Configurar monitoring de costos Athena

### Query Engine (Amazon Athena)
- [ ] Implementar ejecución de queries en Athena
- [ ] Crear plantillas SQL optimizadas para Athena
- [ ] Configurar gestión de query execution IDs
- [ ] Implementar polling de resultados asíncrono
- [ ] Configurar cache de resultados frecuentes (Redis opcional)
- [ ] Implementar timeouts y limits para queries
- [ ] Implementar logging de costos por query

### Mock Data (Local)
- [ ] Generar datasets mock realistas
- [ ] Implementar service mock que simule query engine
- [ ] Crear respuestas consistentes con schemas cloud
- [ ] Configurar variabilidad en datos mock
- [ ] Implementar delays simulados

### API Implementation (FastAPI)
- [ ] Implementar todos los endpoints según OpenAPI spec
- [ ] Configurar validación automática con Pydantic
- [ ] Implementar transformación de resultados Athena
- [ ] Añadir paginación para resultados grandes
- [ ] Configurar rate limiting (slowapi)
- [ ] Implementar logging estructurado con FastAPI
- [ ] Configurar CORS para frontend integration

### Security & Performance
- [ ] Implementar autenticación JWT para consultas custom
- [ ] Validar y sanitizar consultas SQL para Athena
- [ ] Configurar límites de recursos por consulta
- [ ] Implementar whitelist de tablas Glue accesibles
- [ ] Configurar monitoring de performance FastAPI
- [ ] Implementar alertas de costos AWS
- [ ] Configurar circuit breakers para servicios AWS

### Testing (pytest)
- [ ] Unit tests para endpoints FastAPI
- [ ] Unit tests para services AWS
- [ ] Integration tests con mocks de boto3
- [ ] Tests de validación de consultas SQL Athena
- [ ] Tests de performance con datasets mock grandes
- [ ] Setup de CI/CD testing con GitHub Actions

### Monitoring & Observability
- [ ] Health checks de servicios AWS (Athena, S3, Glue)
- [ ] Métricas de performance de consultas Athena
- [ ] Logging de costos de consultas AWS
- [ ] Tracing distribuido (opcional: AWS X-Ray)
- [ ] Alertas de fallos de consulta Athena
- [ ] Dashboard de métricas FastAPI + AWS

## Comandos de Desarrollo

### Local Development (FastAPI)
```bash
# Instalación de dependencias
pip install -r requirements.txt

# Desarrollo local con reload automático
uvicorn main:app --reload --host 0.0.0.0 --port 8010

# Con variables de entorno para modo local
ENVIRONMENT=local uvicorn main:app --reload --port 8010

# Con variables de entorno para AWS
ENVIRONMENT=aws uvicorn main:app --reload --port 8010
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

### Testing (pytest)
```bash
# Ejecutar todos los tests
pytest

# Tests con coverage
pytest --cov=src

# Tests de integración
pytest tests/integration/

# Tests específicos
pytest tests/test_analytics.py -v

# Tests con mock de AWS
pytest tests/test_aws_services.py --mock-aws
```

## Integración con otros Microservicios

### Consumido por:
- **Frontend Web Portal** - Para mostrar dashboards y reportes analíticos
- **ms-history** - Puede consumir análisis para enriquecer historiales de viajes

### Consume datos de:
- **Amazon S3** - Lee datos CSV/JSON depositados por data ingestion pipeline
- **AWS Glue Data Catalog** - Consulta metadata y esquemas de tablas
- **Amazon Athena** - Ejecuta consultas SQL sobre datos del data lake

### Interacciones API:
- **Expone**: REST API con FastAPI para consultas analíticas
- **Autentica**: Via JWT tokens (para consultas custom)
- **Formato**: JSON responses con modelos Pydantic validados

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

## AWS Implementation Details

### Amazon Athena Integration
```python
import boto3
from botocore.exceptions import ClientError

class AthenaService:
    def __init__(self):
        self.athena_client = boto3.client('athena', region_name=AWS_REGION)
        self.s3_client = boto3.client('s3', region_name=AWS_REGION)
    
    async def execute_query(self, sql_query: str) -> str:
        """Ejecuta query en Athena y retorna execution ID"""
        try:
            response = self.athena_client.start_query_execution(
                QueryString=sql_query,
                QueryExecutionContext={'Database': AWS_GLUE_CATALOG_DATABASE},
                ResultConfiguration={'OutputLocation': AWS_ATHENA_RESULT_LOCATION},
                WorkGroup=AWS_ATHENA_WORKGROUP
            )
            return response['QueryExecutionId']
        except ClientError as e:
            # Handle AWS errors
            raise HTTPException(status_code=500, detail=f"Athena error: {e}")
    
    async def get_query_results(self, execution_id: str) -> List[Dict]:
        """Obtiene resultados de query ejecutada"""
        try:
            # Wait for query completion
            waiter = self.athena_client.get_waiter('query_succeeded')
            waiter.wait(QueryExecutionId=execution_id)
            
            # Get results
            response = self.athena_client.get_query_results(
                QueryExecutionId=execution_id,
                MaxResults=AWS_ATHENA_MAX_RESULTS
            )
            return self._format_results(response)
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving results: {e}")
```

### FastAPI Main Application
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="MS Analytics - Bus MVP",
    description="Microservicio de análisis de datos usando AWS Athena",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "MS Analytics - FastAPI + AWS", "docs": "/docs"}
```

### Pydantic Configuration
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    # FastAPI
    app_name: str = "ms-analytics"
    debug: bool = False
    
    # AWS
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    aws_s3_bucket: str
    aws_athena_workgroup: str
    aws_glue_catalog_database: str
    
    # Environment
    environment: str = "local"  # local or aws
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Patterns Implementados

### Query Template Pattern (Athena Optimized)
```python
from string import Template

# Plantillas SQL optimizadas para Athena
REVENUE_BY_ROUTE_QUERY = Template("""
SELECT 
    t.route_code,
    t.origin_city,
    t.destination_city,
    SUM(tk.total_price) as total_revenue,
    COUNT(tk.ticket_id) as total_tickets,
    AVG(tk.total_price) as avg_ticket_price
FROM ${catalog_db}.trips_raw t
JOIN ${catalog_db}.tickets_raw tk ON t.trip_id = tk.trip_id
WHERE t.year >= ${year_from}
    AND t.month >= ${month_from}
    AND tk.booking_status = 'confirmed'
    ${route_filter}
    ${date_filter}
GROUP BY t.route_code, t.origin_city, t.destination_city
ORDER BY total_revenue DESC
LIMIT ${limit}
""")

class QueryBuilder:
    def __init__(self):
        self.catalog_db = AWS_GLUE_CATALOG_DATABASE
    
    def build_revenue_query(self, year_from: int, month_from: int = 1, 
                           route_codes: List[str] = None, limit: int = 100):
        filters = []
        if route_codes:
            route_list = "', '".join(route_codes)
            filters.append(f"AND t.route_code IN ('{route_list}')")
        
        return REVENUE_BY_ROUTE_QUERY.substitute(
            catalog_db=self.catalog_db,
            year_from=year_from,
            month_from=month_from,
            route_filter=' '.join(filters),
            date_filter='',
            limit=limit
        )
```

### FastAPI Dependency Injection
```python
from fastapi import Depends
from app.services.aws_service import AthenaService
from app.services.mock_service import MockAnalyticsService
from app.core.config import settings

def get_analytics_service():
    """Dependency que retorna el servicio apropiado según environment"""
    if settings.environment == "aws":
        return AthenaService()
    else:
        return MockAnalyticsService()

# Usage in endpoints
@router.get("/revenue-by-route")
async def get_revenue_by_route(
    service: AnalyticsService = Depends(get_analytics_service)
):
    return await service.get_revenue_by_route()
```

### Result Caching (Optional - Redis)
```python
import redis
import json
from typing import Optional

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host, 
            port=settings.redis_port, 
            db=0,
            decode_responses=True
        )
    
    async def get_cached_result(self, query_hash: str) -> Optional[Dict]:
        """Obtiene resultado cacheado"""
        try:
            cached = self.redis_client.get(f"analytics:{query_hash}")
            return json.loads(cached) if cached else None
        except (redis.RedisError, json.JSONDecodeError):
            return None
    
    async def cache_result(self, query_hash: str, result: Dict, ttl: int = 300):
        """Cachea resultado de query"""
        try:
            self.redis_client.setex(
                f"analytics:{query_hash}", 
                ttl, 
                json.dumps(result, default=str)
            )
        except redis.RedisError:
            pass  # Log error but don't fail
```

## Notas de Implementación

- **FastAPI Framework**: Aprovecha validación automática, documentación OpenAPI y async/await
- **Dual Mode**: Funciona en modo local (mock data) y AWS (real Athena queries)  
- **AWS Cost Control**: Implementa límites de costo, timeouts y workgroups Athena
- **Security**: Validación Pydantic, sanitización SQL, JWT auth para custom queries
- **Performance**: Resultados cacheados, queries optimizadas para Athena, async processing
- **Monitoring**: Health checks AWS, logging estructurado, métricas de performance
- **Error Handling**: Circuit breakers, retry logic con exponential backoff
- **Documentation**: OpenAPI docs automáticas con FastAPI, ejemplos de request/response

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
