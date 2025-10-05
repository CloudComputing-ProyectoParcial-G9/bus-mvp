# Analytics Service

API REST para consultas analíticas usando AWS Athena.

## 🚀 Quick Start

```bash
# Build
docker build -t analytics-api .

# Run
docker run -p 5000:5000 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e GLUE_DATABASE=bus_mvp_db \
  -e ATHENA_OUTPUT_LOCATION=s3://bus-mvp-datalake/athena-results/ \
  analytics-api
```

## 📋 Endpoints

### GET /
Información del servicio

### GET /api/analytics/top-passengers
Top pasajeros con más tickets

Parámetros:
- `limit` (opcional): Número de resultados (default: 10)

### GET /api/analytics/popular-routes
Rutas más populares

Parámetros:
- `limit` (opcional): Número de resultados (default: 10)

### GET /api/analytics/daily-sales
Ventas diarias

Parámetros:
- `days` (opcional): Número de días (default: 30)

### GET /api/analytics/occupancy-rate
Tasa de ocupación promedio

### GET /api/analytics/revenue-by-route
Ingresos por ruta

### GET /api/analytics/customer-tiers
Distribución de clientes por tier

### GET /api/analytics/trip-performance
Performance de viajes

Parámetros:
- `rating` (opcional): Filtrar por rating (Excelente, Bueno, Regular, Bajo)
- `limit` (opcional): Número de resultados (default: 50)

### GET /api/analytics/summary
Resumen general

### POST /api/analytics/custom-query
Ejecutar query personalizada

Body:
```json
{
  "query": "SELECT * FROM passengers LIMIT 10"
}
```

### GET /health
Health check

## 🔐 Variables de Entorno

- `AWS_ACCESS_KEY_ID`: AWS Access Key
- `AWS_SECRET_ACCESS_KEY`: AWS Secret Key
- `AWS_DEFAULT_REGION`: AWS Region (default: us-east-1)
- `GLUE_DATABASE`: Nombre de la database en Glue (default: bus_mvp_db)
- `ATHENA_OUTPUT_LOCATION`: S3 location para resultados de Athena
- `PORT`: Puerto del servidor (default: 5000)
