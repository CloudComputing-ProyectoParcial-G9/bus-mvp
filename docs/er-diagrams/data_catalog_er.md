# Diagrama Entidad-Relación - Bus MVP Data Catalog

## 📊 Modelo de Datos Completo

### Vista General del Modelo

```
                              BUS MVP - DATA MODEL
                              
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│                         PASSENGERS                                          │
│  ┌──────────────────────────────────────────────────────────────┐        │
│  │  PK  passenger_id         INT/VARCHAR                         │        │
│  │      name                 VARCHAR(255)   NOT NULL             │        │
│  │  UK  email                VARCHAR(255)   UNIQUE               │        │
│  │      phone                VARCHAR(20)                         │        │
│  │  UK  dni                  VARCHAR(20)    UNIQUE               │        │
│  │      created_at           TIMESTAMP                           │        │
│  │      updated_at           TIMESTAMP                           │        │
│  │      ingestion_timestamp  TIMESTAMP                           │        │
│  └──────────────────────────┬───────────────────────────────────┘        │
│                              │                                              │
│                              │ 1:N                                          │
│                              │ (Un pasajero → Muchos tickets)               │
│                              ▼                                              │
│                         TICKETS                                             │
│  ┌──────────────────────────────────────────────────────────────┐        │
│  │  PK  ticket_id            VARCHAR                             │        │
│  │      _id                  VARCHAR (MongoDB ObjectId)          │        │
│  │  FK  passenger_id ────────┼───────────────────────────────────┼──►     │
│  │  FK  trip_id ─────────────┼───────────────────────────────────┼──►     │
│  │      seat_number          VARCHAR(10)                         │        │
│  │      price                DECIMAL(10,2)  >= 0                 │        │
│  │      status               VARCHAR(50)                         │        │
│  │      purchase_date        TIMESTAMP      NOT NULL             │        │
│  │      created_at           TIMESTAMP                           │        │
│  │      updated_at           TIMESTAMP                           │        │
│  │      ingestion_timestamp  TIMESTAMP                           │        │
│  └──────────────────────────┬───────────────────────────────────┘        │
│                              │                                              │
│                              │ N:1                                          │
│                              │ (Muchos tickets → Un viaje)                  │
│                              ▼                                              │
│                          TRIPS                                              │
│  ┌──────────────────────────────────────────────────────────────┐        │
│  │  PK  trip_id              INT/VARCHAR                         │        │
│  │      bus_id               VARCHAR(50)                         │        │
│  │      origin               VARCHAR(100)   NOT NULL             │        │
│  │      destination          VARCHAR(100)   NOT NULL             │        │
│  │      departure_time       TIMESTAMP      NOT NULL             │        │
│  │      arrival_time         TIMESTAMP                           │        │
│  │      price                DECIMAL(10,2)  >= 0                 │        │
│  │      available_seats      INT            >= 0                 │        │
│  │      status               VARCHAR(50)                         │        │
│  │      created_at           TIMESTAMP                           │        │
│  │      updated_at           TIMESTAMP                           │        │
│  │      ingestion_timestamp  TIMESTAMP                           │        │
│  └──────────────────────────────────────────────────────────────┘        │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## 🔗 Relaciones Detalladas

### Relación 1: PASSENGERS ←→ TICKETS (One-to-Many)

```
PASSENGERS                           TICKETS
┌──────────────┐                    ┌──────────────┐
│passenger_id  │◄──────────────────┤passenger_id  │
│(PK)          │      1        N   │(FK)          │
└──────────────┘                    └──────────────┘

Cardinalidad: 1:N
Descripción: Un pasajero puede comprar múltiples tickets
             Un ticket pertenece a exactamente un pasajero
             
Integridad Referencial:
  - tickets.passenger_id REFERENCES passengers.passenger_id
  - ON DELETE: RESTRICT (no permitir borrar pasajero con tickets)
  - ON UPDATE: CASCADE
```

### Relación 2: TRIPS ←→ TICKETS (One-to-Many)

```
TRIPS                                TICKETS
┌──────────────┐                    ┌──────────────┐
│trip_id       │◄──────────────────┤trip_id       │
│(PK)          │      1        N   │(FK)          │
└──────────────┘                    └──────────────┘

Cardinalidad: 1:N
Descripción: Un viaje puede tener múltiples tickets vendidos
             Un ticket corresponde a exactamente un viaje
             
Integridad Referencial:
  - tickets.trip_id REFERENCES trips.trip_id
  - ON DELETE: RESTRICT (no permitir borrar viaje con tickets)
  - ON UPDATE: CASCADE
```

### Relación 3: PASSENGERS ←→ TRIPS (Many-to-Many a través de TICKETS)

```
PASSENGERS                  TICKETS                    TRIPS
┌──────────────┐           ┌──────────────┐          ┌──────────────┐
│passenger_id  │◄─────────┤passenger_id  │          │              │
│              │     1  N  │              │          │              │
│              │           │trip_id       ├─────────►│trip_id       │
│              │           │              │  N    1  │              │
└──────────────┘           └──────────────┘          └──────────────┘

Cardinalidad: N:M
Descripción: Un pasajero puede viajar en múltiples viajes
             Un viaje puede tener múltiples pasajeros
             TICKETS actúa como tabla de unión (junction table)
             
Reglas de Negocio:
  - Un pasajero puede comprar múltiples tickets para el mismo viaje
  - Cada ticket debe tener un seat_number único por viaje
```

## 📐 Índices y Optimizaciones

### PASSENGERS
```sql
CREATE INDEX idx_passengers_email ON passengers(email);
CREATE INDEX idx_passengers_dni ON passengers(dni);
CREATE INDEX idx_passengers_created ON passengers(created_at);
```

### TRIPS
```sql
CREATE INDEX idx_trips_route ON trips(origin, destination);
CREATE INDEX idx_trips_departure ON trips(departure_time);
CREATE INDEX idx_trips_status ON trips(status);
```

### TICKETS
```sql
CREATE INDEX idx_tickets_passenger ON tickets(passenger_id);
CREATE INDEX idx_tickets_trip ON tickets(trip_id);
CREATE INDEX idx_tickets_purchase ON tickets(purchase_date);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE UNIQUE INDEX idx_tickets_seat ON tickets(trip_id, seat_number);
```

## 🎯 Reglas de Negocio Implementadas

### Validaciones en PASSENGERS
- ✅ Email debe ser único
- ✅ DNI debe ser único
- ✅ Nombre es obligatorio
- ✅ Email debe tener formato válido

### Validaciones en TRIPS
- ✅ Origen y destino son obligatorios
- ✅ Departure time es obligatorio
- ✅ Precio debe ser >= 0
- ✅ Asientos disponibles >= 0
- ✅ Origen ≠ Destino

### Validaciones en TICKETS
- ✅ Passenger_id debe existir en PASSENGERS
- ✅ Trip_id debe existir en TRIPS
- ✅ Precio debe ser >= 0
- ✅ Seat_number único por viaje
- ✅ Purchase_date es obligatorio
- ✅ No se puede vender más tickets que asientos disponibles

## 📊 Vistas Materializadas

### top_passengers
```
Combina: PASSENGERS + TICKETS
Propósito: Ranking de mejores clientes
Actualización: Diaria
```

### popular_routes
```
Combina: TRIPS + TICKETS
Propósito: Análisis de rutas más populares
Actualización: Cada hora
```

### daily_sales_summary
```
Combina: TICKETS + TRIPS
Propósito: Reporte de ventas diarias
Actualización: Cada hora
```

### trip_performance
```
Combina: TRIPS + TICKETS
Propósito: Análisis de ocupación de viajes
Actualización: En tiempo real
```

## 🔍 Consultas Típicas

### Query 1: Pasajeros con más viajes
```sql
SELECT 
    p.name,
    COUNT(DISTINCT t.ticket_id) as total_tickets,
    COUNT(DISTINCT tr.trip_id) as total_trips,
    SUM(t.price) as total_spent
FROM passengers p
JOIN tickets t ON p.passenger_id = t.passenger_id
JOIN trips tr ON t.trip_id = tr.trip_id
GROUP BY p.passenger_id, p.name
ORDER BY total_tickets DESC;
```

### Query 2: Rutas con mejor ocupación
```sql
SELECT 
    tr.origin,
    tr.destination,
    COUNT(t.ticket_id) as tickets_sold,
    tr.available_seats,
    ROUND(COUNT(t.ticket_id) * 100.0 / 
          (COUNT(t.ticket_id) + tr.available_seats), 2) as occupancy_rate
FROM trips tr
LEFT JOIN tickets t ON tr.trip_id = t.trip_id
GROUP BY tr.trip_id, tr.origin, tr.destination, tr.available_seats
ORDER BY occupancy_rate DESC;
```

### Query 3: Revenue por pasajero
```sql
SELECT 
    p.passenger_id,
    p.name,
    p.email,
    SUM(t.price) as lifetime_value,
    COUNT(t.ticket_id) as purchase_count,
    AVG(t.price) as avg_purchase
FROM passengers p
JOIN tickets t ON p.passenger_id = t.passenger_id
GROUP BY p.passenger_id, p.name, p.email
ORDER BY lifetime_value DESC;
```

## 🎨 Normalización

Este modelo está en **3NF (Third Normal Form)**:

- ✅ **1NF**: Todos los atributos son atómicos
- ✅ **2NF**: Todos los atributos no-clave dependen completamente de la clave primaria
- ✅ **3NF**: No hay dependencias transitivas

## 💾 Particionamiento en S3

Para optimizar queries en Athena:

```
s3://bus-mvp-datalake-1/raw/
├── passengers/
│   └── year=2025/
│       └── month=10/
│           └── day=05/
│               └── passengers_20251005_120000.csv
├── trips/
│   └── year=2025/
│       └── month=10/
│           └── day=05/
│               └── trips_20251005_120000.csv
└── tickets/
    └── year=2025/
        └── month=10/
            └── day=05/
                └── tickets_20251005_120000.csv
```

## 🔐 Políticas de Seguridad

### Row-Level Security
```sql
-- Solo ver tickets propios
CREATE POLICY passenger_tickets_policy ON tickets
FOR SELECT
USING (passenger_id = current_user_id());
```

### Column-Level Security
```sql
-- Ocultar información sensible
GRANT SELECT ON passengers(passenger_id, name, email) TO analytics_role;
DENY SELECT ON passengers(dni, phone) TO analytics_role;
```

---

Esta estructura de datos soporta todas las operaciones de analytics necesarias
y está optimizada para consultas en AWS Athena.
