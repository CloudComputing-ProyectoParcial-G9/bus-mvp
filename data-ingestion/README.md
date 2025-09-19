# Data Ingestion - Sistema de Ingesta de Datos

## Descripción
Conjunto de 3 contenedores especializados para la ingesta de datos del sistema Bus MVP, cada uno con un propósito específico dentro del pipeline de datos.

> **TODO (@A, @PM)**: Implementar lógica específica de ingesta según fuentes de datos reales.

## Requisitos del Proyecto
- ✅ **3 contenedores de ingesta dockerizados**
- ✅ **Diferentes tipos de fuentes de datos**
- ✅ **Integración con object storage**
- ✅ **Procesamiento y transformación de datos**

## Arquitectura de Ingesta

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   real-time-data    │    │   batch-processor   │    │   external-apis     │
│   (Contenedor 1)    │    │   (Contenedor 2)    │    │   (Contenedor 3)    │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ • IoT Sensores      │    │ • Archivos CSV      │    │ • APIs Externas     │
│ • GPS Tracking      │    │ • Logs del Sistema  │    │ • Web Scraping      │
│ • Eventos Tiempo    │    │ • Reportes Diarios  │    │ • Feeds RSS         │
│   Real              │    │ • Data Warehouse    │    │ • APIs de Clima     │
└─────────┬───────────┘    └─────────┬───────────┘    └─────────┬───────────┘
          │                          │                          │
          └──────────────────────────┼──────────────────────────┘
                                     │
                          ┌─────────┴───────────┐
                          │   Object Storage    │
                          │ (S3/GCS/Azure Blob) │
                          └─────────────────────┘
                                     │
                          ┌─────────┴───────────┐
                          │   Data Catalog      │
                          │  (ms-analytics)     │
                          └─────────────────────┘
```

## Estructura de Contenedores

### 1. Real-Time Data Ingestion (Contenedor 1)
**Propósito**: Ingesta de datos en tiempo real desde IoT, GPS, y eventos del sistema.

**Tecnologías sugeridas**:
- Python + asyncio/aiohttp
- Apache Kafka (opcional)
- Redis para buffer temporal
- WebSocket para datos streaming

**Fuentes de datos**:
- GPS tracking de autobuses
- Sensores IoT (temperatura, ocupación)
- Eventos de sistema en tiempo real
- Transacciones de boletos en vivo

### 2. Batch Data Processor (Contenedor 2)
**Propósito**: Procesamiento de archivos batch y ETL de sistemas legacy.

**Tecnologías sugeridas**:
- Python + Pandas/Apache Airflow
- Scheduled jobs (cron)
- File watchers
- Data validation

**Fuentes de datos**:
- Archivos CSV/Excel diarios
- Logs de sistema históricos
- Dumps de bases de datos
- Reportes financieros

### 3. External APIs Collector (Contenedor 3)
**Propósito**: Recolección de datos desde APIs externas y web scraping.

**Tecnologías sugeridas**:
- Python + requests/aiohttp
- BeautifulSoup para scraping
- API rate limiting
- Data normalization

**Fuentes de datos**:
- APIs de clima y tráfico
- Precios de combustible
- Información de rutas externas
- Datos demográficos

## Comandos de Desarrollo

```bash
# Desarrollo individual
cd data-ingestion/real-time-data
docker build -t bus-mvp-realtime-ingestion .
docker run bus-mvp-realtime-ingestion

cd ../batch-processor
docker build -t bus-mvp-batch-processor .
docker run bus-mvp-batch-processor

cd ../external-apis
docker build -t bus-mvp-external-collector .
docker run bus-mvp-external-collector

# Desarrollo completo
cd data-ingestion/
docker-compose up --build

# Con el sistema completo
cd ../infra/
docker-compose up --build
```

## Pipeline de Datos

### Flujo General
1. **Ingesta** → Cada contenedor recolecta datos de sus fuentes específicas
2. **Transformación** → Limpieza, validación y normalización de datos
3. **Storage** → Almacenamiento en object storage con estructura consistente
4. **Cataloging** → Registro en el data catalog para consultas analíticas
5. **Availability** → Datos disponibles para ms-analytics y consultas

### Formato de Datos Estándar
```json
{
  "metadata": {
    "source": "real-time-data|batch-processor|external-apis",
    "timestamp": "2024-01-15T10:30:00Z",
    "data_type": "gps_tracking|financial|weather|etc",
    "version": "1.0",
    "ingestion_id": "uuid",
    "quality_score": 0.95
  },
  "payload": {
    // Datos específicos según tipo
  },
  "schema": {
    "name": "gps_event_v1",
    "fields": [...],
    "validation_rules": [...]
  }
}
```

## Configuración de Variables

Cada contenedor tiene su propio `.env.example` con configuraciones específicas:

- **Object Storage**: Credenciales y configuración cloud
- **Data Sources**: URLs, API keys, conexiones
- **Processing**: Intervalos, batch sizes, timeouts
- **Quality**: Reglas de validación y limpieza
- **Monitoring**: Logs, métricas, alertas

## Monitoreo y Observabilidad

### Métricas Clave
- Volumen de datos ingestados por minuto/hora
- Latencia de procesamiento
- Tasa de errores y fallos
- Calidad de datos (completitud, precisión)
- Uso de recursos (CPU, memoria, red)

### Logs Estructurados
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "container": "real-time-data",
  "event": "data_ingested",
  "source": "gps_tracker_001",
  "records_count": 150,
  "processing_time_ms": 45,
  "quality_score": 0.98
}
```

## Integración con el Sistema

### Con Microservicios
- Los datos ingestados alimentan el data catalog
- ms-analytics consulta los datos para reportes
- ms-history puede usar datos históricos
- ms-trips puede usar datos de tráfico y clima

### Con Object Storage
- Estructura de carpetas consistente
- Particionado por fecha y tipo
- Compresión y optimización
- Backup y archivado automático

## Próximos Pasos

1. **Definir Fuentes** (@A, @PM): Identificar fuentes de datos reales específicas
2. **Implementar Contenedores** (@A): Desarrollar lógica de cada contenedor
3. **Configurar Storage** (@A): Setup de object storage y estructura
4. **Testing** (@A): Pruebas de integración y performance
5. **Monitoreo** (@PM): Implementar observabilidad y alertas
6. **Documentación** (@A): Completar documentación técnica

## Enlaces Útiles
- [Object Storage Config](../docs/analytics/catalog_design.md): Diseño del data catalog
- [Analytics Queries](../docs/analytics/queries_and_views.sql): Consultas sobre datos ingestados
- [Docker Compose](../infra/docker-compose.yml): Orquestación completa del sistema
