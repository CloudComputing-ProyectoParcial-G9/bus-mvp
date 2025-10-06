# MS-Analytics - Bus MVP Analytics API

Microservicio de analítica para el proyecto Bus MVP. Consume datos de AWS Athena para generar insights de negocio.

## 🎯 Características

- **Dashboard Summary**: Métricas ejecutivas (pasajeros, viajes, ingresos, ocupación)
- **Passenger Analytics**: Segmentación de clientes y top customers
- **Revenue Analytics**: Análisis de ingresos por ruta y estado
- **Occupancy Analytics**: Niveles de ocupación de buses
- **Trip Analytics**: Estadísticas de viajes

## 🛠️ Stack Tecnológico

- **Framework**: FastAPI 0.104.1
- **Python**: 3.11
- **AWS Services**: Athena, S3, Glue
- **Async**: uvicorn con soporte async/await
- **Validación**: Pydantic 2.5
- **Logging**: Loguru
- **Testing**: pytest + httpx

## 📋 Requisitos Previos

1. **AWS Configurado**:
   - Bucket S3: `bus-mvp-datalake`
   - Glue Database: `bus_mvp_db`
   - Tablas: `passengers_csv`, `trips_csv`, `tickets_csv`
   - Vistas: `passenger_sales_summary`, `trip_occupancy_revenue`

2. **Credenciales AWS**:
   - Access Key ID
   - Secret Access Key
   - Session Token (si usas AWS Academy)

3. **Datos Ingestados**:
   - Ejecutar contenedores de ingesta
   - Ejecutar crawlers de Glue
   - Crear vistas de Athena

## 🚀 Quick Start

### 1. Configurar Variables de Entorno

```bash
# Copiar ejemplo
cp .env.example .env

# Editar .env con tus credenciales AWS
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar en Desarrollo

```bash
# Desde la carpeta backend/ms-analytics
uvicorn src.main:app --reload --port 8005
```

### 4. Acceder a la Documentación

- **Swagger UI**: http://localhost:8005/docs
- **ReDoc**: http://localhost:8005/redoc
- **Health Check**: http://localhost:8005/api/v1/health

## 🐳 Docker

### Build

```bash
docker build -t ms-analytics:latest .
```

### Run

```bash
docker run -d \
  --name ms-analytics \
  -p 8005:8005 \
  --env-file .env \
  ms-analytics:latest
```

### Docker Compose

```yaml
ms-analytics:
  build: ./backend/ms-analytics
  container_name: ms-analytics
  ports:
    - "8005:8005"
  environment:
    - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
    - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    - AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}
    - GLUE_DATABASE=bus_mvp_db
    - ATHENA_OUTPUT_LOCATION=s3://bus-mvp-datalake/athena-results/
  networks:
    - bus-mvp-network
```

## 📡 API Endpoints

### Health Check

```bash
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ms-analytics",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00",
  "athena_connection": true
}
```

### Dashboard Summary

```bash
GET /api/v1/analytics/summary
```

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
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

### Passenger Analytics

```bash
GET /api/v1/analytics/passengers
```

**Segmentos:**
- **VIP**: >10 tickets o >$500
- **Frequent**: 6-10 tickets o $301-$500
- **Regular**: 3-5 tickets o $101-$300
- **Occasional**: 1-2 tickets o <$100

### Revenue Analytics

```bash
GET /api/v1/analytics/revenue
```

Incluye desglose por ruta y estado (confirmed/cancelled).

### Occupancy Analytics

```bash
GET /api/v1/analytics/occupancy
```

**Niveles:**
- Full: >90%
- High: 70-90%
- Medium: 50-70%
- Low: 30-50%
- Very Low: <30%

### Trip Analytics

```bash
GET /api/v1/analytics/trips
```

Estadísticas de viajes por estado y ocupación.

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=src --cov-report=html

# Test específico
pytest tests/test_analytics.py -v
```

## 📁 Estructura del Proyecto

```
backend/ms-analytics/
├── src/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI
│   ├── config.py            # Configuración con Pydantic Settings
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── health.py      # Health check
│   │           └── analytics.py   # Endpoints de analytics
│   ├── services/
│   │   ├── athena_service.py     # Servicio de Athena
│   │   └── analytics_service.py  # Lógica de negocio
│   ├── models/
│   │   └── responses.py          # Modelos Pydantic
│   └── core/
│       ├── logging.py            # Configuración de logs
│       └── exceptions.py         # Excepciones custom
├── tests/
│   ├── test_health.py
│   └── test_analytics.py
├── logs/                    # Logs de aplicación
├── requirements.txt
├── Dockerfile
├── .env.example
├── .dockerignore
└── README.md
```

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_SESSION_TOKEN` | Session Token (AWS Academy) | `FwoGZXIvYXd...` |
| `AWS_DEFAULT_REGION` | AWS Region | `us-east-1` |
| `GLUE_DATABASE` | Nombre de base Glue | `bus_mvp_db` |
| `ATHENA_OUTPUT_LOCATION` | S3 output para Athena | `s3://bucket/athena-results/` |
| `DEBUG` | Modo debug | `True` / `False` |
| `LOG_LEVEL` | Nivel de logs | `INFO` / `DEBUG` |

### Settings en config.py

```python
from src.config import get_settings

settings = get_settings()
print(settings.glue_database)  # bus_mvp_db
```

## 🔍 Troubleshooting

### Error: "Import could not be resolved"

```bash
# Los errores de import son normales antes de instalar dependencias
pip install -r requirements.txt
```

### Error: "Athena connection test failed"

- Verifica credenciales AWS en `.env`
- Confirma que el bucket S3 existe
- Verifica que Glue Database tiene tablas
- Revisa permisos IAM

### Error: "No data found"

- Ejecuta ingesta de datos primero
- Ejecuta crawlers de Glue
- Crea las vistas de Athena con scripts

### Query Timeout

```python
# Aumentar timeout en .env
ATHENA_QUERY_TIMEOUT=120
```

## 📊 Dependencias de AWS

```mermaid
graph LR
    A[MS-Analytics] --> B[AWS Athena]
    B --> C[AWS Glue Database]
    C --> D[AWS S3 Bucket]
    D --> E[Data Ingestion]
```

## 🔄 Workflow Completo

1. **Ingesta**: Ejecutar contenedores de ingesta → S3
2. **Catalog**: Ejecutar crawlers de Glue → Tablas
3. **Views**: Crear vistas de Athena → Analytics
4. **API**: Ejecutar ms-analytics → Consultar endpoints

## 📝 Logs

Los logs se guardan en:
- `logs/app_YYYY-MM-DD.log` (rotación diaria, 7 días retención)
- STDOUT con formato colorizado

## 🤝 Contribuir

1. Fork del proyecto
2. Crear feature branch
3. Commit cambios
4. Push al branch
5. Crear Pull Request

## 📄 Licencia

MIT

## 👥 Autores

Bus MVP Team

---

**Versión**: 1.0.0  
**Puerto**: 8005  
**Documentación**: http://localhost:8005/docs
