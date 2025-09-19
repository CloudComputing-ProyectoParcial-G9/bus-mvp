# Diseño del Catálogo de Datos - Bus MVP

## Visión General

El catálogo de datos mapea los archivos CSV/JSON depositados en el almacenamiento de objetos por los contenedores de ingesta, permitiendo consultas SQL sobre los datos usando un motor de consulta serverless.

## Arquitectura del Catálogo

### Almacenamiento de Objetos
**Bucket/Container**: `bus-mvp-data-lake`

```
bus-mvp-data-lake/
├── raw/
│   ├── passengers/
│   │   ├── year=2024/month=01/day=01/
│   │   │   ├── passengers_20240101_001.csv
│   │   │   └── passengers_20240101_002.csv
│   │   └── year=2024/month=01/day=02/
│   ├── trips/
│   │   ├── year=2024/month=01/day=01/
│   │   │   ├── trips_20240101_001.csv
│   │   │   └── trips_20240101_002.csv
│   │   └── year=2024/month=01/day=02/
│   └── tickets/
│       ├── year=2024/month=01/day=01/
│       │   ├── tickets_20240101_001.json
│       │   └── tickets_20240101_002.json
│       └── year=2024/month=01/day=02/
├── processed/
│   ├── aggregated/
│   └── analytics/
└── results/
    └── query-outputs/
```

## Tablas del Catálogo

### 1. Tabla: `passengers_raw`
**Fuente**: ms-passengers (SQL DB 1)
**Formato**: CSV
**Particionado**: Por año/mes/día

| Columna | Tipo | Descripción |
|---------|------|-------------|
| passenger_id | string | Identificador único del pasajero |
| full_name | string | Nombre completo |
| email | string | Correo electrónico |
| phone | string | Número de teléfono |
| document_type | string | Tipo de documento (DNI, Passport, etc.) |
| document_number | string | Número de documento |
| date_of_birth | date | Fecha de nacimiento |
| registration_date | timestamp | Fecha de registro |
| status | string | Estado del pasajero (active, inactive) |
| year | int | Año (partición) |
| month | int | Mes (partición) |
| day | int | Día (partición) |

**Ubicación**: `s3://bus-mvp-data-lake/raw/passengers/year={year}/month={month}/day={day}/`

### 2. Tabla: `trips_raw`
**Fuente**: ms-trips (SQL DB 2)
**Formato**: CSV
**Particionado**: Por año/mes/día

| Columna | Tipo | Descripción |
|---------|------|-------------|
| trip_id | string | Identificador único del viaje |
| route_code | string | Código de la ruta |
| origin_city | string | Ciudad de origen |
| destination_city | string | Ciudad de destino |
| departure_time | timestamp | Hora de salida |
| arrival_time | timestamp | Hora de llegada |
| bus_capacity | int | Capacidad del autobús |
| available_seats | int | Asientos disponibles |
| base_price | decimal(10,2) | Precio base del viaje |
| currency | string | Moneda |
| status | string | Estado del viaje |
| year | int | Año (partición) |
| month | int | Mes (partición) |
| day | int | Día (partición) |

**Ubicación**: `s3://bus-mvp-data-lake/raw/trips/year={year}/month={month}/day={day}/`

### 3. Tabla: `tickets_raw`
**Fuente**: ms-tickets (NoSQL DB)
**Formato**: JSON
**Particionado**: Por año/mes/día

| Columna | Tipo | Descripción |
|---------|------|-------------|
| ticket_id | string | Identificador único del boleto |
| passenger_id | string | ID del pasajero |
| trip_id | string | ID del viaje |
| seat_number | string | Número de asiento |
| purchase_date | timestamp | Fecha de compra |
| total_price | decimal(10,2) | Precio total pagado |
| payment_method | string | Método de pago |
| booking_status | string | Estado de la reserva |
| special_requirements | string | Requerimientos especiales |
| metadata | string | Metadatos adicionales (JSON string) |
| year | int | Año (partición) |
| month | int | Mes (partición) |
| day | int | Día (partición) |

**Ubicación**: `s3://bus-mvp-data-lake/raw/tickets/year={year}/month={month}/day={day}/`

## Configuración del Catálogo

### AWS Glue / Google Data Catalog / Azure Data Catalog

```json
{
  "database_name": "bus_mvp_catalog",
  "tables": [
    {
      "name": "passengers_raw",
      "storage_descriptor": {
        "location": "s3://bus-mvp-data-lake/raw/passengers/",
        "input_format": "org.apache.hadoop.mapred.TextInputFormat",
        "output_format": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
        "serde_info": {
          "serialization_library": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
          "parameters": {
            "field.delim": ",",
            "skip.header.line.count": "1"
          }
        }
      },
      "partition_keys": [
        {"name": "year", "type": "int"},
        {"name": "month", "type": "int"},
        {"name": "day", "type": "int"}
      ]
    },
    {
      "name": "trips_raw",
      "storage_descriptor": {
        "location": "s3://bus-mvp-data-lake/raw/trips/",
        "input_format": "org.apache.hadoop.mapred.TextInputFormat",
        "output_format": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
        "serde_info": {
          "serialization_library": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
          "parameters": {
            "field.delim": ",",
            "skip.header.line.count": "1"
          }
        }
      },
      "partition_keys": [
        {"name": "year", "type": "int"},
        {"name": "month", "type": "int"},
        {"name": "day", "type": "int"}
      ]
    },
    {
      "name": "tickets_raw",
      "storage_descriptor": {
        "location": "s3://bus-mvp-data-lake/raw/tickets/",
        "input_format": "org.apache.hadoop.mapred.TextInputFormat",
        "output_format": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
        "serde_info": {
          "serialization_library": "org.openx.data.jsonserde.JsonSerDe"
        }
      },
      "partition_keys": [
        {"name": "year", "type": "int"},
        {"name": "month", "type": "int"},
        {"name": "day", "type": "int"}
      ]
    }
  ]
}
```

## Estrategia de Particionado

### Por Fecha (año/mes/día)
- **Ventajas**: 
  - Optimiza consultas por rango de fechas
  - Facilita el lifecycle management de datos
  - Permite processing incremental
  
- **Desventajas**:
  - Puede crear muchas particiones pequeñas
  - Requiere maintenance periódico

### Consideraciones Adicionales
- **Compresión**: Usar GZIP o Snappy para reducir costos de storage
- **Formato**: Considerar Parquet para mejor performance en consultas analíticas
- **Lifecycle**: Configurar políticas para mover datos antiguos a storage class más económico

## Variables de Configuración

### Variables Genéricas (provider-agnostic)
```bash
# Almacenamiento de objetos
OBJECT_STORE_BUCKET=bus-mvp-data-lake
OBJECT_STORE_REGION=us-east-1

# Catálogo de datos
CATALOG_DATABASE=bus_mvp_catalog
DATA_LOCATION_PREFIX=raw/

# Motor de consulta
QUERY_ENGINE_WORKGROUP=bus-mvp-analytics
QUERY_OUTPUT_PATH=s3://bus-mvp-data-lake/results/query-outputs/
QUERY_RESULT_RETENTION_DAYS=30
```

### Variables específicas por proveedor

#### AWS
```bash
AWS_GLUE_CATALOG_DATABASE=bus_mvp_catalog
AWS_ATHENA_WORKGROUP=bus-mvp-analytics
AWS_S3_BUCKET=bus-mvp-data-lake
```

#### Google Cloud
```bash
GCP_PROJECT_ID=bus-mvp-project
GCP_DATASET_ID=bus_mvp_catalog
GCP_BUCKET=bus-mvp-data-lake
```

#### Azure
```bash
AZURE_STORAGE_ACCOUNT=busmvpdatalake
AZURE_CONTAINER=raw-data
AZURE_SYNAPSE_WORKSPACE=bus-mvp-analytics
```

## Automation y Maintenance

### Scheduled Jobs
1. **Partition Discovery**: Ejecutar diariamente para detectar nuevas particiones
2. **Statistics Update**: Actualizar estadísticas de tablas semanalmente
3. **Data Cleanup**: Eliminar particiones antiguas según política de retención

### Monitoring
- Alertas por fallos en ingesta
- Métricas de volumen de datos por tabla
- Performance de consultas
- Costos de storage y compute

## TODO - Para completar según proveedor elegido

- [ ] Configurar catálogo específico (Glue/Data Catalog/etc.)
- [ ] Crear scripts de creación de tablas
- [ ] Implementar discovery automático de particiones
- [ ] Configurar lifecycle policies para storage
- [ ] Crear scripts de maintenance y monitoring
- [ ] Definir políticas de acceso y seguridad
- [ ] Configurar encryption en storage y catálogo
- [ ] Crear dashboards de monitoring

## Notas de Implementación

- **Consistencia**: Usar naming conventions consistentes entre microservicios
- **Schema Evolution**: Planificar para cambios en esquemas de datos
- **Performance**: Considerar columnar formats (Parquet) para analytics workloads
- **Cost Optimization**: Usar tiered storage para datos históricos
- **Security**: Implementar encryption at rest y in transit
