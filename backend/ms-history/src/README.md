# Microservicio de Historial (ms-history)

## Descripción
Este microservicio es un **agregador** que NO tiene base de datos propia. Su función es consumir datos de otros microservicios para generar vistas consolidadas, reportes históricos y métricas del sistema Bus MVP.

## Tecnología Stack
**Go + Gin Framework** - Elegido por su excelente concurrencia y performance para HTTP clients

### Stack Seleccionado:
- **Go 1.21+** - Lenguaje base
- **Gin** - Framework web ligero y rápido
- **net/http** - Cliente HTTP nativo con timeout y retry
- **goroutines** - Concurrencia para llamadas paralelas a microservicios
- **sync.WaitGroup** - Sincronización de goroutines
- **context.Context** - Manejo de timeouts y cancelación
- **encoding/json** - Serialización/deserialización JSON
- **Redis** (opcional) - Cache en memoria para respuestas

### Ventajas del Stack:
- **Concurrencia nativa**: Goroutines para llamadas HTTP paralelas
- **Performance**: Excelente para agregación de datos en tiempo real
- **HTTP client robusto**: Manejo nativo de timeouts, retries y circuit breaker
- **Tipado fuerte**: Evita errores en runtime
- **Memoria eficiente**: Ideal para microservicios agregadores

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

## Estructura del Código (Go + Gin)

```
src/
├── main.go                          # Entry point y servidor
├── handlers/
│   ├── health.go                    # Health check + dependencias
│   ├── passenger_history.go         # Historial de pasajeros
│   ├── trip_history.go             # Historial de viajes
│   ├── route_analytics.go          # Análisis de rutas
│   └── dashboard.go                # Métricas para dashboard
├── services/
│   ├── aggregation_service.go      # Lógica de agregación de datos
│   ├── statistics_service.go       # Cálculos y métricas
│   └── cache_service.go            # Cache opcional (Redis)
├── clients/
│   ├── passengers_client.go        # HTTP client para ms-passengers
│   ├── trips_client.go             # HTTP client para ms-trips
│   ├── tickets_client.go           # HTTP client para ms-tickets
│   └── http_client.go              # Cliente HTTP base con retry
├── models/
│   ├── passenger.go                # Structs para datos de passenger
│   ├── trip.go                     # Structs para datos de trip
│   ├── ticket.go                   # Structs para datos de ticket
│   ├── aggregated_data.go          # Structs para respuestas agregadas
│   └── responses.go                # Structs para API responses
├── middleware/
│   ├── error_handler.go            # Manejo centralizado de errores
│   ├── logger.go                   # Logging estructurado
│   ├── circuit_breaker.go          # Circuit breaker pattern
│   └── rate_limiter.go             # Rate limiting
├── utils/
│   ├── http_utils.go               # Utilidades HTTP (retry, timeout)
│   ├── data_transformers.go        # Transformación de datos
│   └── validators.go               # Validaciones
├── config/
│   └── config.go                   # Configuración del servidor
└── routes/
    └── routes.go                   # Definición de rutas
```

## Tareas Pendientes (Go Implementation)

### HTTP Clients
- [ ] Implementar `PassengersClient` con net/http
- [ ] Implementar `TripsClient` con timeout y retry
- [ ] Implementar `TicketsClient` con circuit breaker
- [ ] Configurar context.Context para cancelación
- [ ] Implementar health checks de dependencias
- [ ] Configurar connection pooling

### API Handlers (Gin)
- [ ] Implementar health handler con estado de dependencias
- [ ] Handler para historial de pasajeros con goroutines
- [ ] Handler para análisis de viajes con cache
- [ ] Handler para dashboard con datos agregados
- [ ] Handler para analytics de rutas populares
- [ ] Middleware de logging y error handling

### Agregación de Datos
- [ ] Service para combinar datos de múltiples fuentes
- [ ] Lógica paralela con sync.WaitGroup
- [ ] Cálculos de estadísticas (total gastado, rutas frecuentes)
- [ ] Transformaciones de datos entre servicios
- [ ] Manejo de datos faltantes con valores por defecto
- [ ] Optimización de consultas paralelas

### Resilience Patterns
- [ ] Circuit breaker con github.com/sony/gobreaker
- [ ] Retry logic con backoff exponencial
- [ ] Timeout handling con context.Context
- [ ] Graceful degradation cuando servicios fallan
- [ ] Fallback responses con datos parciales

### Performance & Concurrencia
- [ ] Cache en memoria con sync.Map
- [ ] Cache con Redis (go-redis/redis)
- [ ] Worker pools para procesar requests
- [ ] Rate limiting con golang.org/x/time/rate
- [ ] Monitoring con goroutines leak detection

### Testing
- [ ] Unit tests con testify/assert
- [ ] HTTP mocks con httptest package
- [ ] Integration tests con testcontainers
- [ ] Benchmark tests para concurrencia
- [ ] Tests de circuit breaker y retry logic

### Monitoring & Observability
- [ ] Health checks detallados con estado de dependencias
- [ ] Métricas de performance de API calls
- [ ] Logging de requests/responses
- [ ] Tracing distribuido
- [ ] Alertas de servicios no disponibles

## Comandos de Desarrollo

### Local Development
```bash
# Instalar Go 1.21+
go mod init ms-history
go mod tidy

# Instalar dependencias
go get github.com/gin-gonic/gin
go get github.com/go-redis/redis/v8
go get github.com/sony/gobreaker

# Ejecutar en modo desarrollo
go run main.go

# O compilar y ejecutar
go build -o ms-history
./ms-history
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
# Unit tests
go test ./...

# Tests con coverage
go test -cover ./...

# Integration tests
go test -tags=integration ./tests/integration/

# Benchmark tests
go test -bench=. ./...

# Tests con verbose output
go test -v ./...
```

## Integración con otros Microservicios

### Consumido por:
- **Frontend** - Para mostrar dashboards, historiales y analíticas

### Consume (agregador):
- **ms-passengers** - Para información de pasajeros
- **ms-trips** - Para información de viajes y rutas
- **ms-tickets** - Para información de boletos y compras

## Flujos de Datos Típicos (Implementación Go)

### Historial de Pasajero
```go
func (h *HistoryHandler) GetPassengerHistory(c *gin.Context) {
    passengerID := c.Param("passenger_id")
    ctx := c.Request.Context()
    
    // 1. Llamadas paralelas usando goroutines
    var wg sync.WaitGroup
    var passenger *models.Passenger
    var tickets []models.Ticket
    var err error
    
    wg.Add(2)
    
    // Goroutine 1: Obtener datos del pasajero
    go func() {
        defer wg.Done()
        passenger, err = h.passengersClient.GetPassenger(ctx, passengerID)
    }()
    
    // Goroutine 2: Obtener historial de tickets
    go func() {
        defer wg.Done()
        tickets, err = h.ticketsClient.GetTicketsByPassenger(ctx, passengerID)
    }()
    
    wg.Wait()
    
    if err != nil {
        c.JSON(500, gin.H{"error": "Failed to fetch data"})
        return
    }
    
    // 2. Para cada ticket, obtener detalles del viaje (paralelo)
    tripDetails := h.fetchTripDetailsParallel(ctx, tickets)
    
    // 3. Agregar y calcular estadísticas
    stats := h.aggregationService.CalculatePassengerStats(tickets, tripDetails)
    
    // 4. Retornar respuesta consolidada
    response := models.PassengerHistoryResponse{
        Passenger:     passenger,
        RecentTickets: tickets[:min(5, len(tickets))],
        Statistics:    stats,
        TravelHistory: tripDetails,
    }
    
    c.JSON(200, response)
}
```

### Dashboard Summary con Circuit Breaker
```go
func (h *HistoryHandler) GetDashboardSummary(c *gin.Context) {
    ctx := c.Request.Context()
    
    // Usar circuit breaker para cada servicio
    passengerStats, _ := h.passengersBreaker.Execute(func() (interface{}, error) {
        return h.passengersClient.GetStats(ctx)
    })
    
    tripStats, _ := h.tripsBreaker.Execute(func() (interface{}, error) {
        return h.tripsClient.GetStats(ctx)
    })
    
    ticketStats, _ := h.ticketsBreaker.Execute(func() (interface{}, error) {
        return h.ticketsClient.GetStats(ctx)
    })
    
    // Agregar datos con fallback para servicios no disponibles
    dashboard := h.aggregationService.BuildDashboard(
        safecast(passengerStats),
        safecast(tripStats), 
        safecast(ticketStats),
    )
    
    c.JSON(200, dashboard)
}
```

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

## Patterns Implementados (Go)

### Circuit Breaker
```go
package clients

import "github.com/sony/gobreaker"

func NewPassengersClient() *PassengersClient {
    cb := gobreaker.NewCircuitBreaker(gobreaker.Settings{
        Name:        "passengers-service",
        MaxRequests: 3,
        Interval:    time.Second * 60,
        Timeout:     time.Second * 30,
        ReadyToTrip: func(counts gobreaker.Counts) bool {
            return counts.ConsecutiveFailures > 3
        },
    })
    
    return &PassengersClient{breaker: cb}
}
```

### Retry Logic con Backoff
```go
func (c *HTTPClient) DoWithRetry(req *http.Request) (*http.Response, error) {
    var resp *http.Response
    var err error
    
    for attempt := 0; attempt < c.maxRetries; attempt++ {
        resp, err = c.client.Do(req)
        if err == nil && resp.StatusCode < 500 {
            return resp, nil
        }
        
        if attempt < c.maxRetries-1 {
            backoff := time.Duration(attempt+1) * c.retryDelay
            time.Sleep(backoff)
        }
    }
    
    return resp, err
}
```

### Concurrencia con Context
```go
func (s *AggregationService) FetchDataParallel(ctx context.Context, passengerID string) (*AggregatedData, error) {
    // Canal para recibir resultados
    type result struct {
        data interface{}
        err  error
        typ  string
    }
    
    resultChan := make(chan result, 3)
    
    // Goroutines con context para cancelación
    go func() {
        data, err := s.passengersClient.Get(ctx, passengerID)
        resultChan <- result{data, err, "passenger"}
    }()
    
    go func() {
        data, err := s.ticketsClient.GetByPassenger(ctx, passengerID)
        resultChan <- result{data, err, "tickets"}
    }()
    
    go func() {
        data, err := s.tripsClient.GetRoutes(ctx)
        resultChan <- result{data, err, "routes"}
    }()
    
    // Recoger resultados con timeout
    aggregated := &AggregatedData{}
    for i := 0; i < 3; i++ {
        select {
        case res := <-resultChan:
            if res.err == nil {
                s.assignResult(aggregated, res.data, res.typ)
            }
        case <-ctx.Done():
            return nil, ctx.Err()
        }
    }
    
    return aggregated, nil
}
```

### Cache Strategy
```bash
# Estrategias de cache recomendadas:
# - Información de rutas: TTL largo (1 hora)
# - Estadísticas de dashboard: TTL medio (5 minutos)
# - Historiales de pasajeros: TTL corto (1 minuto)
# - Datos en tiempo real: Sin cache
```

## Dependencias Go (go.mod ejemplo)

```go
module ms-history

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/go-redis/redis/v8 v8.11.5
    github.com/sony/gobreaker v0.5.0
    golang.org/x/time v0.3.0
)

require (
    github.com/bytedance/sonic v1.9.1 // indirect
    github.com/chenzhuoyu/base64x v0.0.0-20221115062448-fe3a3abad311 // indirect
    github.com/gabriel-vasile/mimetype v1.4.2 // indirect
    github.com/gin-contrib/sse v0.1.0 // indirect
    github.com/go-playground/locales v0.14.1 // indirect
    github.com/go-playground/universal-translator v0.18.1 // indirect
    github.com/go-playground/validator/v10 v10.14.0 // indirect
    github.com/goccy/go-json v0.10.2 // indirect
    github.com/json-iterator/go v1.1.12 // indirect
    github.com/klauspost/cpuid/v2 v2.2.4 // indirect
    github.com/leodido/go-urn v1.2.4 // indirect
    github.com/mattn/go-isatty v0.0.19 // indirect
    github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd // indirect
    github.com/modern-go/reflect2 v1.0.2 // indirect
    github.com/pelletier/go-toml/v2 v2.0.8 // indirect
    github.com/twitchyliquid64/golang-asm v0.15.1 // indirect
    github.com/ugorji/go/codec v1.2.11 // indirect
    golang.org/x/arch v0.3.0 // indirect
    golang.org/x/crypto v0.9.0 // indirect
    golang.org/x/net v0.10.0 // indirect
    golang.org/x/sys v0.8.0 // indirect
    golang.org/x/text v0.9.0 // indirect
    google.golang.org/protobuf v1.30.0 // indirect
    gopkg.in/yaml.v3 v3.0.1 // indirect
)
```

## Notas de Implementación

- **ms-history es un agregador puro**: No tiene base de datos propia
- **Todas las operaciones son read-only**: Solo consulta, nunca modifica datos
- **Concurrencia optimizada**: Uso intensivo de goroutines para paralelización
- **Resilencia crítica**: Debe funcionar aunque servicios estén parcialmente caídos
- **Cache strategy**: Implementar cache inteligente según frecuencia de consultas
- **Context propagation**: Usar context.Context para timeouts y cancelación
- **Monitoring**: Métricas de latencia de cada servicio externo

## Ownership
**Responsable**: @B4 (Backend Developer 4) - Go Specialist
