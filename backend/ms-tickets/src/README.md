# Microservicio de Boletos (ms-tickets)

## Descripción
Este microservicio gestiona toda la información relacionada con boletos, reservas y transacciones del sistema Bus MVP.

## Tecnología Stack
**TODO**: Definir según elección del equipo de desarrollo (debe ser diferente a ms-passengers y ms-trips)

### Opciones sugeridas:
- **Java** + Spring Boot + Spring Data MongoDB
- **Go** + Gin + MongoDB Driver
- **C#** + ASP.NET Core + MongoDB.Driver
- **Python** + FastAPI + Motor (async MongoDB)
- **Node.js** + Express + Mongoose

## Base de Datos
- **Tipo**: NoSQL Database (única base NoSQL del proyecto)
- **Motor**: TODO - Elegir entre MongoDB, CouchDB, DynamoDB, etc.
- **Schema**: Esquema flexible JSON para boletos y metadata

## Endpoints Principales
Ver especificación completa en `openapi.yaml`

### Tickets
- `GET /health` - Health check
- `GET /tickets` - Listar boletos (con filtros)
- `POST /tickets` - Crear nuevo boleto (comprar)
- `GET /tickets/{id}` - Obtener boleto específico
- `PUT /tickets/{id}` - Actualizar boleto
- `POST /tickets/{id}/cancel` - Cancelar boleto
- `GET /tickets/passenger/{passenger_id}/history` - Historial por pasajero

## Variables de Entorno Requeridas

```bash
# Base de datos NoSQL
NOSQL_URL=mongodb://localhost:27017
NOSQL_DB=tickets_db
NOSQL_USER=tickets_user
NOSQL_PASSWORD=secure_password

# Configuración del servicio
MS_TICKETS_PORT=8003
NODE_ENV=development
LOG_LEVEL=info

# Integración con otros microservicios
MS_TRIPS_URL=http://localhost:8002
MS_PASSENGERS_URL=http://localhost:8001

# Para testing
TEST_NOSQL_URL=mongodb://localhost:27017/tickets_test
```

## Estructura del Código (Placeholder)

```
src/
├── controllers/
│   ├── healthController.go
│   └── ticketsController.go
├── models/
│   └── ticket.go
├── routes/
│   ├── health.go
│   └── tickets.go
├── middleware/
│   ├── validation.go
│   ├── errorHandler.go
│   └── logger.go
├── services/
│   ├── ticketService.go
│   ├── paymentService.go
│   └── externalApiService.go
├── config/
│   ├── database.go
│   └── server.go
├── utils/
│   └── helpers.go
└── main.go
```

## Tareas Pendientes

### Base de Datos
- [ ] Definir motor NoSQL específico (MongoDB, CouchDB, etc.)
- [ ] Diseñar esquema de documentos JSON
- [ ] Configurar índices para consultas frecuentes
- [ ] Implementar connection pooling
- [ ] Implementar health check de DB

### API
- [ ] Implementar todos los endpoints según OpenAPI spec
- [ ] Configurar validación de input
- [ ] Implementar paginación y filtros avanzados
- [ ] Añadir búsqueda por múltiples criterios
- [ ] Configurar rate limiting
- [ ] Implementar logging estructurado

### Business Logic
- [ ] Validar disponibilidad de asientos
- [ ] Integrar con ms-trips para verificar viajes
- [ ] Integrar con ms-passengers para validar pasajeros
- [ ] Implementar lógica de cancelación y reembolsos
- [ ] Gestionar códigos promocionales
- [ ] Validar métodos de pago

### Integraciones
- [ ] Cliente para ms-trips (verificar viaje y actualizar asientos)
- [ ] Cliente para ms-passengers (validar pasajero)
- [ ] Mock de payment gateway
- [ ] Manejo de errores de servicios externos

### Testing
- [ ] Unit tests para controllers y services
- [ ] Integration tests para endpoints
- [ ] Tests de base de datos NoSQL
- [ ] Tests de integración con otros microservicios
- [ ] Setup de CI/CD testing

### Monitoring & Observability
- [ ] Configurar health checks detallados
- [ ] Métricas de performance y ventas
- [ ] Logging de transacciones
- [ ] Tracing distribuido
- [ ] Alertas de monitoreo

## Seed Data / Datos Iniciales

El microservicio incluye un sistema automático de poblado de base de datos con datos de prueba.

### Comportamiento Automático
- ✅ Al iniciar el contenedor/aplicación, **automáticamente** se pobla la base de datos con 10 tickets de ejemplo
- ✅ Solo se ejecuta si la base de datos está vacía (no duplica datos)
- ✅ Los tickets se generan con datos realistas (pasajeros, viajes, asientos, precios, etc.)

### Datos Generados
El seed crea 10 tickets con:
- IDs secuenciales: `TICKET001`, `TICKET002`, ..., `TICKET010`
- Referencias a pasajeros existentes: `PASS001` - `PASS010`
- Referencias a viajes: `TRIP001` - `TRIP005`
- Asientos aleatorios: formato "15A", "23B", etc.
- Precios entre €20 y €120
- Estados: mayormente "confirmed", algunos "pending" o "cancelled"
- Fechas de creación de los últimos 90 días
- Moneda: EUR

### Verificar Datos
Después del seed, puedes verificar:
```bash
# Listar todos los tickets
curl http://localhost:8003/api/v1/tickets

# Ver un ticket específico
curl http://localhost:8003/api/v1/tickets/TICKET001

# Tickets por pasajero
curl http://localhost:8003/api/v1/tickets/passenger/PASS001
```

## Comandos de Desarrollo

### Local Development
```bash
# Java con Spring Boot (stack actual)
./mvnw spring-boot:run

# O en Windows
mvnw.cmd spring-boot:run

# El seed se ejecuta automáticamente al iniciar
# Verás en consola: "📦 Seeding database with sample tickets..."
```

### Docker
```bash
# Build
docker build -t ms-tickets .

# Run
docker run -p 8003:8003 --env-file .env ms-tickets

# Con Docker Compose (desde raíz del proyecto)
cd ../../infra
docker-compose up ms-tickets
```

### Testing
```bash
# TODO: Completar según stack elegido

# Ejemplo Go:
# go test ./...

# Ejemplo Java:
# ./mvnw test

# Ejemplo C#:
# dotnet test

# Ejemplo Python:
# pytest
```

## Integración con otros Microservicios

### Consumido por:
- **ms-history** - Para obtener historial de compras
- **Frontend** - Para gestión de boletos en UI

### Consume:
- **ms-trips** - Para verificar disponibilidad y actualizar asientos
- **ms-passengers** - Para validar información del pasajero

## Esquema NoSQL (MongoDB - Ejemplo)

### Colección: tickets
```json
{
  "_id": "ticket_001",
  "passenger_id": "pass_001",
  "trip_id": "trip_001",
  "seat_number": "12A",
  "purchase_date": "2024-01-15T10:30:00Z",
  "total_price": 45.50,
  "currency": "EUR",
  "payment_method": "credit_card",
  "booking_status": "confirmed",
  "special_requirements": "Wheelchair accessible seat",
  "metadata": {
    "booking_reference": "BK123456",
    "payment_transaction_id": "txn_789012",
    "promo_code": "SUMMER2024",
    "discount_applied": 5.00,
    "cancellation_reason": null,
    "refund_amount": null,
    "refund_status": null,
    "passenger_info": {
      "full_name": "Juan Pérez García",
      "email": "juan.perez@email.com",
      "phone": "+1234567890"
    },
    "trip_info": {
      "route_code": "RT001",
      "origin_city": "Madrid",
      "destination_city": "Barcelona",
      "departure_time": "2024-01-20T08:00:00Z",
      "arrival_time": "2024-01-20T14:30:00Z"
    }
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Índices Recomendados
```javascript
// MongoDB índices
db.tickets.createIndex({ "passenger_id": 1 })
db.tickets.createIndex({ "trip_id": 1 })
db.tickets.createIndex({ "booking_status": 1 })
db.tickets.createIndex({ "purchase_date": 1 })
db.tickets.createIndex({ "passenger_id": 1, "booking_status": 1 })
db.tickets.createIndex({ "trip_id": 1, "booking_status": 1 })

// Índice compuesto para búsquedas frecuentes
db.tickets.createIndex({ 
  "passenger_id": 1, 
  "purchase_date": -1, 
  "booking_status": 1 
})

// Índice de texto para búsqueda
db.tickets.createIndex({ 
  "metadata.passenger_info.full_name": "text",
  "metadata.booking_reference": "text"
})
```

## Lógica de Negocio

### Estados de Boletos
- **pending**: Boleto en proceso de compra
- **confirmed**: Boleto confirmado y pagado
- **cancelled**: Boleto cancelado por el usuario
- **refunded**: Boleto cancelado con reembolso procesado

### Reglas de Negocio
- Verificar disponibilidad de asientos antes de crear boleto
- Validar que el pasajero existe en ms-passengers
- Validar que el viaje existe y está disponible en ms-trips
- Actualizar asientos disponibles en ms-trips al confirmar/cancelar
- Aplicar políticas de cancelación según tiempo restante
- Calcular reembolsos según políticas establecidas

### Flujo de Compra
1. Validar pasajero (llamada a ms-passengers)
2. Validar viaje y disponibilidad (llamada a ms-trips)
3. Crear boleto en estado "pending"
4. Procesar pago (mock payment gateway)
5. Confirmar boleto y actualizar asientos en ms-trips
6. Enviar confirmación

## API Calls a Otros Microservicios

### ms-trips Integration
```bash
# Verificar viaje y disponibilidad
GET http://localhost:8002/trips/{trip_id}

# Actualizar asientos disponibles
PUT http://localhost:8002/trips/{trip_id}
Content-Type: application/json
{
  "available_seats": 34
}
```

### ms-passengers Integration
```bash
# Verificar pasajero
GET http://localhost:8001/passengers/{passenger_id}
```

## Notas de Implementación

- **Transacciones**: Usar transacciones NoSQL cuando esté disponible
- **Consistencia Eventual**: Manejar fallos en updates a ms-trips
- **Idempotencia**: Operaciones de compra deben ser idempotentes
- **Performance**: Cache de información de viajes frecuentemente consultados
- **Audit Trail**: Guardar todos los cambios de estado en metadata

## Ownership
**Responsable**: @B2 (Backend Developer 2)
