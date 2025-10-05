# 🚀 Bus MVP - Data Science Pipeline - Resumen del Proyecto

## ✅ Cumplimiento de Requisitos

### Requisitos Obligatorios

| # | Requisito | Estado | Evidencia |
|---|-----------|--------|-----------|
| 1 | **MV Ingesta** | ✅ Completado | `AWS_EC2_DEPLOYMENT.md` - Guía completa de creación de EC2 |
| 2 | **Bucket S3** | ✅ Completado | `scripts/setup_s3.py` - Script automatizado + estructura `/raw/`, `/processed/`, `/athena-results/` |
| 3 | **3 Contenedores Docker** | ✅ Completado | `passengers-ingestion/`, `trips-ingestion/`, `tickets-ingestion/` |
| 4 | **Estrategia Pull 100%** | ✅ Completado | Cada contenedor extrae todos los registros vía API REST |
| 5 | **Archivos CSV/JSON** | ✅ Completado | Cada ingesta genera ambos formatos con timestamp |
| 6 | **Catálogo AWS Glue** | ✅ Completado | `scripts/setup_glue.py` - Database + 3 crawlers automáticos |
| 7 | **Diagrama ER** | ✅ Completado | `docs/er-diagrams/data_catalog_er.md` - Diagrama detallado con relaciones |
| 8 | **4+ Consultas SQL** | ✅ Completado | `docs/analytics/queries_and_views.sql` - 6 consultas complejas |
| 9 | **2+ Vistas** | ✅ Completado | `docs/analytics/queries_and_views.sql` - 4 vistas materializadas |
| 10 | **Repositorio GitHub** | ✅ Completado | https://github.com/CloudComputing-ProyectoParcial-G9/bus-mvp |

---

## 🎁 Features Adicionales (Valor Agregado)

| Feature | Descripción | Archivos |
|---------|-------------|----------|
| **Analytics API REST** | Servicio Python/Flask para consultas en tiempo real | `analytics-service/app.py` |
| **8 Endpoints REST** | top-passengers, popular-routes, daily-sales, occupancy-rate, etc. | `analytics-service/README.md` |
| **Automatización Completa** | Scripts de setup para S3, Glue, y deployment | `scripts/` |
| **Docker Compose** | Orquestación simplificada de todos los servicios | `docker-compose.yml` |
| **Quick Start Script** | Script bash interactivo para setup rápido | `quick_start.sh` |
| **Documentación Exhaustiva** | Guías paso a paso con troubleshooting | `README.md`, `IMPLEMENTATION_GUIDE.md` |
| **Múltiples Formatos** | CSV + JSON para máxima compatibilidad | Cada contenedor de ingesta |
| **Seguridad IAM** | Soporte para IAM Roles en lugar de credenciales | `AWS_EC2_DEPLOYMENT.md` |

---

## 📊 Arquitectura Implementada

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CAPA DE ORIGEN                                  │
│  ms-passengers (MySQL)  │  ms-trips (PostgreSQL)  │  ms-tickets (Mongo) │
└────────────┬──────────────────────┬──────────────────────┬──────────────┘
             │                      │                       │
             │ HTTP REST GET        │ HTTP REST GET         │ HTTP REST GET
             │                      │                       │
┌────────────▼──────────────────────▼───────────────────────▼─────────────┐
│                        CAPA DE INGESTA (ETL)                             │
│  Contenedor 1          │  Contenedor 2           │  Contenedor 3         │
│  passengers-ingestion  │  trips-ingestion        │  tickets-ingestion    │
│  - Extract (API)       │  - Extract (API)        │  - Extract (API)      │
│  - Transform (Pandas)  │  - Transform (Pandas)   │  - Transform (Pandas) │
│  - Load (S3 CSV+JSON)  │  - Load (S3 CSV+JSON)   │  - Load (S3 CSV+JSON) │
└────────────┬──────────────────────┬───────────────────────┬─────────────┘
             │                      │                       │
             └──────────────────────┼───────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     CAPA DE ALMACENAMIENTO                               │
│                  AWS S3 Data Lake (bus-mvp-datalake)                     │
│  raw/passengers/*.{csv,json}                                             │
│  raw/trips/*.{csv,json}                                                  │
│  raw/tickets/*.{csv,json}                                                │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     │ AWS Glue Crawlers
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      CAPA DE CATÁLOGO                                    │
│                  AWS Glue Data Catalog (bus_mvp_db)                      │
│  passengers (table) │ trips (table) │ tickets (table)                    │
│  - Schema auto-detected                                                  │
│  - Metadata indexed                                                      │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     │ SQL Queries
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      CAPA DE ANALYTICS                                   │
│                         AWS Athena                                       │
│  - 6 Consultas SQL complejas                                             │
│  - 4 Vistas materializadas                                               │
│  - JOINs entre tablas                                                    │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     │ Boto3 SDK
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        CAPA DE API                                       │
│                Analytics API (Python/Flask)                              │
│  /api/analytics/top-passengers                                           │
│  /api/analytics/popular-routes                                           │
│  /api/analytics/daily-sales                                              │
│  /api/analytics/occupancy-rate                                           │
│  ... + 4 endpoints más                                                   │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     │ HTTP REST
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      CAPA DE PRESENTACIÓN                                │
│                  Frontend Web (React + TypeScript)                       │
│                    AnalyticsSection.tsx                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
data-ingestion/
├── README.md                          # Documentación principal
├── IMPLEMENTATION_GUIDE.md            # Guía de implementación completa
├── AWS_EC2_DEPLOYMENT.md              # Guía de deployment en AWS
├── docker-compose.yml                 # Orquestación de servicios
├── quick_start.sh                     # Script de inicio rápido
├── .env.example                       # Template de variables de entorno
├── .gitignore                         # Archivos excluidos de git
│
├── passengers-ingestion/              # Contenedor 1
│   ├── Dockerfile                     # Imagen Docker
│   ├── ingest.py                      # Script de ingesta
│   └── requirements.txt               # Dependencias Python
│
├── trips-ingestion/                   # Contenedor 2
│   ├── Dockerfile
│   ├── ingest.py
│   └── requirements.txt
│
├── tickets-ingestion/                 # Contenedor 3
│   ├── Dockerfile
│   ├── ingest.py
│   └── requirements.txt
│
├── analytics-service/                 # API REST
│   ├── Dockerfile
│   ├── app.py                         # Servidor Flask
│   ├── requirements.txt
│   └── README.md
│
└── scripts/                           # Scripts de automatización
    ├── setup_s3.py                    # Crear bucket S3
    ├── setup_glue.py                  # Configurar Glue Catalog
    └── requirements.txt

../docs/analytics/
├── queries_and_views.sql              # Consultas y vistas SQL
└── catalog_design.md                  # Diseño del catálogo

../docs/er-diagrams/
└── data_catalog_er.md                 # Diagrama ER completo
```

---

## 🔧 Tecnologías Utilizadas

### Lenguajes
- **Python 3.11**: Contenedores de ingesta y Analytics API
- **SQL**: Consultas en AWS Athena
- **Bash**: Scripts de automatización

### Frameworks y Librerías
- **Flask**: API REST para analytics
- **Pandas**: Transformación de datos
- **Boto3**: SDK de AWS para Python
- **Requests**: Cliente HTTP para APIs

### AWS Services
- **EC2**: Máquina virtual de ingesta
- **S3**: Data Lake
- **Glue**: Data Catalog y Crawlers
- **Athena**: Query engine SQL
- **IAM**: Gestión de permisos

### DevOps
- **Docker**: Contenedorización
- **Docker Compose**: Orquestación
- **Git**: Control de versiones

---

## 📊 Datos Procesados

### Fuentes de Datos

| Microservicio | Base de Datos | Puerto | Formato API | Contenedor |
|---------------|---------------|--------|-------------|------------|
| ms-passengers | MySQL/PostgreSQL | 3001 | JSON REST | passengers-ingestion |
| ms-trips | PostgreSQL | 3002 | JSON REST | trips-ingestion |
| ms-tickets | MongoDB | 3003 | JSON REST | tickets-ingestion |

### Salidas Generadas

Cada ejecución genera:
- ✅ 1 archivo CSV por servicio (timestamped)
- ✅ 1 archivo JSON por servicio (timestamped)
- ✅ Metadatos de ingesta (timestamp, count)
- ✅ Logs de ejecución

Ejemplo:
```
s3://bus-mvp-datalake/raw/passengers/passengers_20251005_143022.csv
s3://bus-mvp-datalake/raw/passengers/passengers_20251005_143022.json
s3://bus-mvp-datalake/raw/trips/trips_20251005_143025.csv
s3://bus-mvp-datalake/raw/trips/trips_20251005_143025.json
s3://bus-mvp-datalake/raw/tickets/tickets_20251005_143028.csv
s3://bus-mvp-datalake/raw/tickets/tickets_20251005_143028.json
```

---

## 🎯 Consultas SQL Implementadas

### 1. Top Pasajeros (Query + View)
```sql
SELECT * FROM top_passengers
WHERE customer_tier = 'VIP'
ORDER BY total_spent DESC;
```

### 2. Rutas Populares (Query + View)
```sql
SELECT * FROM popular_routes
WHERE route_popularity = 'Muy Popular'
ORDER BY total_revenue DESC;
```

### 3. Ventas Diarias (Query + View)
```sql
SELECT * FROM daily_sales_summary
WHERE sale_date >= CURRENT_DATE - INTERVAL '30' DAY
ORDER BY sale_date DESC;
```

### 4. Performance de Viajes (Query + View)
```sql
SELECT * FROM trip_performance
WHERE performance_rating IN ('Excelente', 'Bueno')
ORDER BY occupancy_percent DESC;
```

### 5. Pasajeros Frecuentes por Ruta
```sql
SELECT p.name, tr.origin, tr.destination, COUNT(*) as trips
FROM passengers p
JOIN tickets t ON p.passenger_id = t.passenger_id
JOIN trips tr ON t.trip_id = tr.trip_id
GROUP BY p.passenger_id, tr.origin, tr.destination
HAVING COUNT(*) >= 2;
```

### 6. Análisis de Revenue por Ruta
```sql
SELECT origin, destination, SUM(price) as revenue
FROM trips tr
JOIN tickets t ON tr.trip_id = t.trip_id
GROUP BY origin, destination
ORDER BY revenue DESC;
```

---

## 🚀 Comandos Rápidos

### Setup Inicial
```bash
# Clonar repositorio
git clone https://github.com/CloudComputing-ProyectoParcial-G9/bus-mvp.git
cd bus-mvp/data-ingestion

# Configurar entorno
cp .env.example .env
nano .env  # Editar credenciales

# Setup automatizado
chmod +x quick_start.sh
./quick_start.sh
```

### Ejecutar Ingesta
```bash
# Todas las ingestas
docker-compose up

# Ingesta individual
docker-compose up passengers-ingestion
docker-compose up trips-ingestion
docker-compose up tickets-ingestion
```

### Verificar Resultados
```bash
# Ver archivos en S3
aws s3 ls s3://bus-mvp-datalake/raw/ --recursive

# Listar tablas en Glue
aws glue get-tables --database-name bus_mvp_db

# Health check de Analytics API
curl http://localhost:5000/health
```

### Consultas Analytics
```bash
# Top passengers
curl http://localhost:5000/api/analytics/top-passengers?limit=10

# Popular routes
curl http://localhost:5000/api/analytics/popular-routes

# Daily sales
curl http://localhost:5000/api/analytics/daily-sales?days=30
```

---

## 📈 Métricas del Proyecto

### Código
- **Archivos Python**: 6
- **Archivos Dockerfile**: 4
- **Scripts Bash**: 1
- **Archivos de Configuración**: 4
- **Líneas de Código**: ~2,500
- **Archivos de Documentación**: 7

### Funcionalidad
- **Contenedores Docker**: 4 (3 ingesta + 1 API)
- **Endpoints REST**: 8
- **Consultas SQL**: 6
- **Vistas SQL**: 4
- **Scripts de Automatización**: 2
- **Servicios AWS**: 4 (EC2, S3, Glue, Athena)

### Documentación
- **Páginas de Documentación**: 7
- **Guías de Deployment**: 2
- **Diagramas**: 2 (Arquitectura + ER)
- **READMEs**: 3

---

## ✅ Checklist Final

### Infraestructura
- [x] Bucket S3 creado con estructura de carpetas
- [x] Instancia EC2 configurada (opcional)
- [x] Security Groups configurados
- [x] IAM Roles/Usuarios con permisos correctos

### Código
- [x] 3 contenedores de ingesta implementados
- [x] Docker Compose configurado
- [x] Analytics API implementada
- [x] Scripts de automatización creados

### AWS Services
- [x] S3 bucket con data
- [x] Glue database creada
- [x] 3 Glue crawlers configurados
- [x] Tablas catalogadas en Glue
- [x] Consultas probadas en Athena
- [x] Vistas creadas y verificadas

### Documentación
- [x] README principal
- [x] Guía de implementación
- [x] Guía de deployment AWS
- [x] Diagrama ER
- [x] Consultas SQL documentadas
- [x] API endpoints documentados

### Testing
- [x] Ingesta de passengers verificada
- [x] Ingesta de trips verificada
- [x] Ingesta de tickets verificada
- [x] Archivos CSV generados
- [x] Archivos JSON generados
- [x] Crawlers ejecutados exitosamente
- [x] Consultas SQL funcionando
- [x] Vistas creadas
- [x] API endpoints funcionando

---

## 🎓 Conclusión

Este proyecto implementa un **pipeline completo de Data Science** que cumple con todos los requisitos especificados y añade valor adicional mediante:

1. **Automatización**: Scripts para setup completo
2. **API REST**: Acceso programático a analytics
3. **Documentación**: Guías detalladas paso a paso
4. **Escalabilidad**: Arquitectura preparada para producción
5. **Seguridad**: Uso de IAM roles y best practices

El proyecto está listo para:
- ✅ Deployment en producción
- ✅ Integración con frontend
- ✅ Escalamiento horizontal
- ✅ Monitoreo y logging
- ✅ Automatización con CI/CD

---

## 📚 Links Útiles

- **Repositorio**: https://github.com/CloudComputing-ProyectoParcial-G9/bus-mvp
- **AWS Console**: https://console.aws.amazon.com/
- **AWS Glue**: https://console.aws.amazon.com/glue/
- **AWS Athena**: https://console.aws.amazon.com/athena/
- **AWS S3**: https://console.aws.amazon.com/s3/

---

**Desarrollado para el Proyecto Parcial de Cloud Computing**  
**Grupo 9 - 2025**
