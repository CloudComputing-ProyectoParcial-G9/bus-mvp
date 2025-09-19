# Microservicio de Historial (ms-history)

## Descripción
Este microservicio es un **agregador** que NO tiene base de datos propia. Su función es consumir datos de otros microservicios para generar vistas consolidadas, reportes históricos y métricas del sistema Bus MVP.

## Tecnología Stack
**TODO**: Definir según elección del equipo de desarrollo

### Opciones sugeridas:
- **Node.js** + Express + Axios (para HTTP requests)
- **Python** + FastAPI + httpx/requests (async HTTP)
- **Java** + Spring Boot + WebClient/RestTemplate
- **Go** + Gin + net/http
- **C#** + ASP.NET Core + HttpClient

## Base de Datos
- **Tipo**: Ninguna (Microservicio agregador)
- **Caché**: Opcional - Redis/Memcached para cache de respuestas
- **Almacenamiento**: Solo en memoria para datos temporales

## Endpoints Principales
Ver especificación completa en `openapi.yaml`

### Core Endpoints
- `GET /health` - Health check + estado de dependencias
- `GET /history/passenger/{passenger_id}` - Historial completo del pasajero
- `GET /history/trip/{trip_id}` - Historial de un viaje específico
- `GET /history/route/{route_code}/summary` - Resumen histórico de ruta
- `GET /history/dashboard/summary` - Métricas para dashboard
- `GET /history/analytics/popular-routes` - Análisis de rutas populares

## Variables de Entorno Requeridas

```bash
# URLs de microservicios a consumir
MS_PASSENGERS_URL=http://localhost:8001
MS_TRIPS_URL=http://localhost:8002
MS_TICKETS_URL=http://localhost:8003

# Configuración del servicio
MS_HISTORY_PORT=8004
NODE_ENV=development
LOG_LEVEL=info

# Timeouts y retry policy
HTTP_TIMEOUT_MS=5000
MAX_RETRIES=3
RETRY_DELAY_MS=1000

# Cache (opcional)
REDIS_URL=redis://localhost:6379
CACHE_TTL_SECONDS=300

# Para testing
TEST_MODE=false
MOCK_EXTERNAL_SERVICES=false
```

## Estructura del Código (Placeholder)

```
src/
├── controllers/
│   ├── healthController.js
│   ├── passengerHistoryController.js
│   ├── tripHistoryController.js
│   ├── routeHistoryController.js
│   ├── dashboardController.js
│   └── analyticsController.js
├── services/
│   ├── externalApiService.js
│   ├── dataAggregationService.js
│   ├── cacheService.js
│   └── statisticsService.js
├── clients/
│   ├── passengersClient.js
│   ├── tripsClient.js
│   └── ticketsClient.js
├── routes/
│   ├── health.js
│   ├── passengerHistory.js
│   ├── tripHistory.js
│   ├── routeHistory.js
│   ├── dashboard.js
│   └── analytics.js
├── middleware/
│   ├── errorHandler.js
│   ├── logger.js
│   ├── circuitBreaker.js
│   └── rateLimiter.js
├── utils/
│   ├── httpClient.js
│   ├── dataTransformers.js
│   └── validators.js
├── config/
│   └── server.js
└── app.js
```

## Tareas Pendientes

### Clientes HTTP
- [ ] Implementar cliente para ms-passengers
- [ ] Implementar cliente para ms-trips  
- [ ] Implementar cliente para ms-tickets
- [ ] Configurar timeouts y retry logic
- [ ] Implementar circuit breaker pattern
- [ ] Configurar health checks de dependencias

### API Endpoints
- [ ] Implementar todos los endpoints según OpenAPI spec
- [ ] Configurar aggregation logic para cada endpoint
- [ ] Implementar transformación de datos entre services
- [ ] Añadir filtros y parámetros de consulta
- [ ] Configurar paginación donde sea necesario
- [ ] Implementar logging estructurado

### Data Aggregation
- [ ] Lógica para combinar datos de múltiples sources
- [ ] Cálculos de estadísticas y métricas
- [ ] Transformaciones de datos para diferentes vistas
- [ ] Manejo de datos faltantes o inconsistentes
- [ ] Optimización de consultas paralelas

### Error Handling & Resilience
- [ ] Manejo de errores de servicios externos
- [ ] Fallback responses cuando services no están disponibles
- [ ] Circuit breaker para servicios problemáticos
- [ ] Retry logic con backoff exponencial
- [ ] Graceful degradation

### Performance & Caching
- [ ] Implementar cache de respuestas frecuentes
- [ ] Cache de datos de configuración (rutas, etc.)
- [ ] Optimizar llamadas HTTP paralelas
- [ ] Implementar rate limiting
- [ ] Monitoring de performance

### Testing
- [ ] Unit tests para controllers y services
- [ ] Integration tests con mocks de external APIs
- [ ] Tests de resilience (circuit breaker, retries)
- [ ] Tests de performance y carga
- [ ] Setup de CI/CD testing

### Monitoring & Observability
- [ ] Health checks detallados con estado de dependencias
- [ ] Métricas de performance de API calls
- [ ] Logging de requests/responses
- [ ] Tracing distribuido
- [ ] Alertas de servicios no disponibles

## Comandos de Desarrollo

### Local Development
```bash
# TODO: Completar según stack elegido

# Ejemplo Node.js:
# npm install
# npm run dev

# Ejemplo Python:
# pip install -r requirements.txt
# uvicorn main:app --reload --port 8004

# Ejemplo Java:
# ./mvnw spring-boot:run

# Ejemplo Go:
# go mod tidy
# go run main.go
```

### Docker
```bash
# Build
docker build -t ms-history .

# Run
docker run -p 8004:8004 --env-file .env ms-history

# Con Docker Compose (desde raíz del proyecto)
cd ../../infra
docker-compose up ms-history
```

### Testing
```bash
# TODO: Completar según stack elegido

# Ejemplo Node.js:
# npm test
# npm run test:integration

# Ejemplo Python:
# pytest
# pytest tests/integration/

# Ejemplo Java:
# ./mvnw test

# Ejemplo Go:
# go test ./...
```

## Integración con otros Microservicios

### Consumido por:
- **Frontend** - Para mostrar dashboards, historiales y analíticas

### Consume (agregador):
- **ms-passengers** - Para información de pasajeros
- **ms-trips** - Para información de viajes y rutas
- **ms-tickets** - Para información de boletos y compras

## Flujos de Datos Típicos

### Historial de Pasajero
1. Recibir request con `passenger_id`
2. Llamar a `ms-passengers` para obtener info del pasajero
3. Llamar a `ms-tickets` para obtener historial de boletos
4. Para cada boleto, llamar a `ms-trips` para obtener info del viaje
5. Agregar y transformar datos
6. Calcular estadísticas (total gastado, ruta favorita, etc.)
7. Retornar respuesta consolidada

### Dashboard Summary
1. Llamar en paralelo a los 3 microservicios
2. `ms-passengers`: total de pasajeros registrados
3. `ms-trips`: total de viajes, rutas activas
4. `ms-tickets`: total de boletos, ingresos
5. Calcular métricas derivadas
6. Retornar dashboard consolidado

## API Calls a Otros Microservicios

### ms-passengers Integration
```bash
# Obtener información de pasajero
GET http://localhost:8001/passengers/{passenger_id}

# Listar pasajeros (para estadísticas)
GET http://localhost:8001/passengers?page=1&limit=100
```

### ms-trips Integration
```bash
# Obtener información de viaje
GET http://localhost:8002/trips/{trip_id}

# Listar viajes por ruta
GET http://localhost:8002/trips?route_code=RT001&page=1&limit=100

# Obtener rutas
GET http://localhost:8002/routes
```

### ms-tickets Integration
```bash
# Historial de boletos por pasajero
GET http://localhost:8003/tickets/passenger/{passenger_id}/history

# Boletos por viaje
GET http://localhost:8003/tickets?trip_id={trip_id}

# Listar boletos con filtros
GET http://localhost:8003/tickets?status=confirmed&purchase_date_from=2024-01-01
```

## Patterns Implementados

### Circuit Breaker
```javascript
// Ejemplo conceptual
const CircuitBreaker = require('opossum');

const options = {
  timeout: 5000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000
};

const passengersBreaker = new CircuitBreaker(passengersClient.get, options);
```

### Retry Logic
```python
# Ejemplo conceptual Python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_external_service(url):
    # HTTP call logic
    pass
```

### Cache Strategy
```bash
# Estrategias de cache recomendadas:
# - Información de rutas: TTL largo (1 hora)
# - Estadísticas de dashboard: TTL medio (5 minutos)
# - Historiales de pasajeros: TTL corto (1 minuto)
# - Datos en tiempo real: Sin cache
```

## Notas de Implementación

- **Consistencia Eventual**: Los datos pueden estar ligeramente desactualizados
- **Fault Tolerance**: Debe funcionar aunque algunos servicios estén caídos
- **Performance**: Optimizar para consultas frecuentes con cache
- **Idempotencia**: Las consultas deben ser idempotentes
- **Rate Limiting**: Evitar sobrecargar servicios dependientes

## Ownership
**Responsable**: @B1 (Backend Developer 1)
