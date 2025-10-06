# Diagrama Entidad-Relación - Catálogo de Datos AWS Glue

## Modelo Conceptual

```
┌──────────────────────────────────────┐
│           PASSENGERS                 │
├──────────────────────────────────────┤
│ passenger_id        INT    PK        │
│ full_name           VARCHAR          │
│ email               VARCHAR          │
│ phone               VARCHAR          │
│ document_type       VARCHAR          │
│ document_number     VARCHAR          │
│ date_of_birth       DATE             │
│ registration_date   TIMESTAMP        │
│ status              VARCHAR          │
│ ingestion_timestamp TIMESTAMP        │
└──────────────────────────────────────┘
                  │
                  │ 1
                  │
                  │
                  │ N
      ┌───────────┴───────────┐
      │                       │
┌─────▼───────────────────────────────┐
│             TICKETS                 │
├─────────────────────────────────────┤
│ ticket_id          VARCHAR    PK    │
│ passenger_id       INT        FK ───┼──┐
│ trip_id            INT        FK ───┼──┼──┐
│ seat_number        INT              │  │  │
│ total_price        DECIMAL          │  │  │
│ currency           VARCHAR          │  │  │
│ booking_status     VARCHAR          │  │  │
│ purchase_date      TIMESTAMP        │  │  │
│ ingestion_timestamp TIMESTAMP       │  │  │
└─────────────────────────────────────┘  │  │
                                         │  │
                                         │  │
      ┌──────────────────────────────────┘  │
      │                                     │
      │ N                                   │ N
      │                                     │
      │ 1                                   │ 1
┌─────▼───────────────────────────────┐    │
│           PASSENGERS                │    │
│         (referencia arriba)         │    │
└─────────────────────────────────────┘    │
                                           │
                                           │
                  ┌────────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│               TRIPS                     │
├─────────────────────────────────────────┤
│ trip_id            INT        PK        │
│ route_id           VARCHAR              │
│ departure_time     TIMESTAMP            │
│ arrival_time       TIMESTAMP            │
│ bus_capacity       INT                  │
│ available_seats    INT                  │
│ final_price        DECIMAL              │
│ status             VARCHAR              │
│ driver_name        VARCHAR              │
│ bus_plate          VARCHAR              │
│ ingestion_timestamp TIMESTAMP           │
└─────────────────────────────────────────┘
```

## Relaciones

### 1. PASSENGERS → TICKETS (1:N)
- **Cardinalidad**: Un pasajero puede tener múltiples tickets
- **Clave Foránea**: `tickets.passenger_id` → `passengers.passenger_id`
- **Tipo**: Identificadora (el ticket no existe sin pasajero)
- **Descripción**: Cada ticket está asociado a un único pasajero que realizó la compra

### 2. TRIPS → TICKETS (1:N)
- **Cardinalidad**: Un viaje puede tener múltiples tickets
- **Clave Foránea**: `tickets.trip_id` → `trips.trip_id`
- **Tipo**: Identificadora (el ticket no existe sin viaje)
- **Descripción**: Cada ticket está asociado a un único viaje específico

### 3. PASSENGERS ↔ TRIPS (N:M a través de TICKETS)
- **Cardinalidad**: Muchos a muchos
- **Tabla Intermedia**: `tickets` actúa como tabla de relación
- **Descripción**: Un pasajero puede viajar en múltiples viajes, y un viaje puede tener múltiples pasajeros

## Restricciones de Integridad

### Passengers
- `passenger_id` es clave primaria única
- `email` debe ser único
- `document_number` debe ser único
- `status` puede ser: 'active', 'inactive', 'blocked'

### Trips
- `trip_id` es clave primaria única
- `available_seats` <= `bus_capacity`
- `departure_time` < `arrival_time`
- `status` puede ser: 'scheduled', 'in_progress', 'completed', 'cancelled'

### Tickets
- `ticket_id` es clave primaria única (puede ser UUID o compuesto)
- `passenger_id` debe existir en tabla passengers
- `trip_id` debe existir en tabla trips
- `seat_number` debe ser único por trip_id
- `seat_number` debe ser <= bus_capacity del trip
- `booking_status` puede ser: 'reserved', 'confirmed', 'cancelled', 'completed'

## Índices Recomendados

```sql
-- Índices para optimizar JOIN operations
CREATE INDEX idx_tickets_passenger_id ON tickets(passenger_id);
CREATE INDEX idx_tickets_trip_id ON tickets(trip_id);
CREATE INDEX idx_tickets_booking_status ON tickets(booking_status);

-- Índices para filtros comunes
CREATE INDEX idx_trips_departure_time ON trips(departure_time);
CREATE INDEX idx_trips_status ON trips(status);
CREATE INDEX idx_passengers_email ON passengers(email);
CREATE INDEX idx_passengers_status ON passengers(status);
```

## Modelo Físico en AWS Glue

### Configuración de Tablas

**Database**: `bus_mvp_db`

**Tablas**:
1. `passengers` - Particionada por `registration_date`
2. `trips` - Particionada por `departure_time` (fecha)
3. `tickets` - Particionada por `purchase_date`

**Formatos de Archivo**:
- CSV en carpetas `*_csv/`
- JSON en carpetas `*_json/`

**Ubicación S3**:
```
s3://bus-mvp-datalake/
├── raw/
│   ├── passengers_csv/
│   ├── passengers_json/
│   ├── trips_csv/
│   ├── trips_json/
│   ├── tickets_csv/
│   └── tickets_json/
```

## Diagrama de Flujo de Datos

```
┌─────────────────┐
│  ms-passengers  │ (MySQL)
│   Port 8001     │
└────────┬────────┘
         │
         │ HTTP GET /api/passengers
         ▼
┌─────────────────────────┐
│ passengers-ingestion    │
└────────┬────────────────┘
         │
         │ CSV + JSON
         ▼
┌─────────────────────────┐
│   S3 Data Lake          │
│   passengers_csv/       │
│   passengers_json/      │
└────────┬────────────────┘
         │
         │ AWS Glue Crawler
         ▼
┌─────────────────────────┐
│   Glue Catalog          │
│   Table: passengers     │
└────────┬────────────────┘
         │
         │ SQL Queries
         ▼
┌─────────────────────────┐
│   AWS Athena            │
│   (Query Engine)        │
└─────────────────────────┘
```

## Métricas y Análisis Disponibles

Con este modelo se pueden realizar análisis como:

1. **Ocupación de viajes**: % de asientos vendidos por viaje
2. **Ingresos por ruta**: Total de ventas agrupadas por route_id
3. **Pasajeros frecuentes**: Número de tickets por pasajero
4. **Tendencias temporales**: Ventas por día/mes/año
5. **Análisis de cancelaciones**: Tasa de tickets cancelados
6. **Rentabilidad**: Ingresos vs capacidad del bus

## Notas de Implementación

- Las tablas en Glue se crean automáticamente mediante Crawlers
- Los tipos de datos se infieren del contenido de los archivos CSV/JSON
- Las particiones mejoran el rendimiento de queries en Athena
- Los archivos CSV y JSON están separados en carpetas distintas para evitar conflictos en el esquema
- El campo `ingestion_timestamp` permite rastrear cuándo se ingirió cada registro
