# 🎯 Bus MVP - Data Analytics Setup Complete

## ✅ Estado de Implementación

Todos los requisitos del proyecto de **Data Science: Analytics** están implementados:

| # | Requisito | Estado | Archivos |
|---|-----------|--------|----------|
| 1 | **MV ingesta** | ✅ Completo | `docker-compose.yml` |
| 2 | **Bucket S3** | ✅ Completo | Variable `S3_BUCKET` configurada |
| 3 | **3 Contenedores Docker (PULL 100%)** | ✅ Completo | `*-ingestion/ingest.py` (x3) |
| 4 | **Catálogo AWS Glue** | ✅ Preparado | `scripts/setup_complete_glue.py` |
| 5 | **Diagrama ER** | ✅ Completo | `docs/analytics/data_catalog_er.md` |
| 6 | **4 Consultas SQL** | ✅ Preparado | `docs/analytics/athena_queries.sql` |
| 7 | **2 Vistas Athena** | ✅ Preparado | `docs/analytics/athena_views.sql` |

---

## 🚀 Inicio Rápido

### Opción 1: Script Automatizado (RECOMENDADO)

```powershell
cd data-ingestion
.\run_complete_setup.ps1
```

El script ofrece menú interactivo para:
1. ✅ Verificar todos los requisitos
2. 🚀 Ejecutar ingesta de datos
3. ⚙️ Configurar AWS Glue automáticamente
4. 📊 Ver resumen de cumplimiento

### Opción 2: Paso a Paso Manual

#### 1. Configurar Credenciales AWS

```powershell
cd data-ingestion
cp .env.example .env
# Editar .env con credenciales de AWS Academy
```

#### 2. Ejecutar Ingesta de Datos

```powershell
# Terminal 1
docker-compose up passengers-ingestion

# Terminal 2
docker-compose up trips-ingestion

# Terminal 3
docker-compose up tickets-ingestion
```

#### 3. Configurar AWS Glue

```powershell
pip install boto3
python scripts/setup_complete_glue.py
```

#### 4. Ejecutar Consultas en Athena

1. Abrir [AWS Athena Console](https://console.aws.amazon.com/athena/)
2. Seleccionar Database: `bus_mvp_db`
3. Ejecutar queries de: `docs/analytics/athena_queries.sql`

#### 5. Crear Vistas en Athena

1. Ejecutar comandos CREATE VIEW de: `docs/analytics/athena_views.sql`
2. Verificar con: `SHOW VIEWS;`

---

## 📁 Estructura de Archivos Creados

```
bus-mvp/
├── data-ingestion/
│   ├── passengers-ingestion/
│   │   └── ingest.py          ✅ Ingesta 100% de pasajeros
│   ├── trips-ingestion/
│   │   └── ingest.py          ✅ Ingesta 100% de viajes
│   ├── tickets-ingestion/
│   │   └── ingest.py          ✅ Ingesta 100% de tickets
│   ├── scripts/
│   │   └── setup_complete_glue.py  ✅ Setup automatizado de Glue
│   ├── docker-compose.yml     ✅ 4 servicios de ingesta
│   └── run_complete_setup.ps1 ✅ Script de ejecución completa
│
├── docs/analytics/
│   ├── data_catalog_er.md     ✅ Diagrama Entidad-Relación completo
│   ├── athena_queries.sql     ✅ 4 consultas SQL preparadas
│   └── athena_views.sql       ✅ 2 vistas preparadas
│
└── GUIA_VERIFICACION_REQUISITOS.md  ✅ Guía paso a paso completa
```

---

## 🎓 Características Implementadas

### 1. **Contenedores de Ingesta** ✅

Cada contenedor implementa:
- ✅ Estrategia **PULL del 100%** (sin límites ni paginación)
- ✅ Extracción completa de datos vía API REST
- ✅ Transformación a DataFrame con pandas
- ✅ Generación de archivos **CSV y JSON**
- ✅ Carga a S3 en carpetas separadas (`*_csv/` y `*_json/`)
- ✅ Timestamp de ingesta en cada registro
- ✅ Logging detallado del proceso

### 2. **Catálogo de Datos AWS Glue** ✅

Script automatizado que:
- ✅ Crea database `bus_mvp_db`
- ✅ Crea 3 crawlers (uno por cada fuente de datos)
- ✅ Ejecuta los crawlers automáticamente
- ✅ Verifica creación exitosa de tablas
- ✅ Muestra estadísticas de ingesta

### 3. **Diagrama ER Completo** ✅

Documentación incluye:
- ✅ Diagrama textual ASCII con relaciones
- ✅ Descripción detallada de cada relación
- ✅ Cardinalidades (1:N, N:M)
- ✅ Claves primarias y foráneas
- ✅ Restricciones de integridad
- ✅ Índices recomendados
- ✅ Modelo físico en S3/Glue

**Relaciones:**
```
PASSENGERS (1) ──< TICKETS >── (N) TRIPS
                    │
           Tabla de Unión (N:M)
```

### 4. **Consultas SQL para Athena** ✅

4 consultas preparadas que demuestran:

1. **Historial de Compras por Pasajero**
   - JOIN: `passengers` + `tickets`
   - Métricas: Total gastado, tickets comprados, promedio
   - Segmentación por status

2. **Análisis de Ingresos por Viaje**
   - JOIN: `trips` + `tickets`
   - Métricas: Ocupación, ingresos, precio promedio
   - KPIs operacionales

3. **Resumen Completo de Transacciones** (JOIN Triple)
   - JOIN: `passengers` + `tickets` + `trips`
   - Vista 360° de cada transacción
   - Análisis de comportamiento de compra

4. **Tendencias de Ventas por Período**
   - JOIN: `trips` + `tickets`
   - Análisis temporal
   - Métricas por día de semana

### 5. **Vistas en Athena** ✅

2 vistas optimizadas:

1. **`passenger_sales_summary`**
   - Métricas de valor del cliente
   - Segmentación RFM (Recency, Frequency, Monetary)
   - Estado de actividad (Active, At Risk, Churned)
   - Análisis de cancelaciones

2. **`trip_occupancy_revenue`**
   - Análisis de ocupación por viaje
   - Clasificación de rentabilidad
   - Métricas de eficiencia operativa
   - Ingresos por asiento

---

## 📊 Datos Generados

### Estructura en S3

```
s3://bus-mvp-datalake/
├── raw/
│   ├── passengers_csv/
│   │   └── passengers_YYYYMMDD_HHMMSS.csv
│   ├── passengers_json/
│   │   └── passengers_YYYYMMDD_HHMMSS.json
│   ├── trips_csv/
│   │   └── trips_YYYYMMDD_HHMMSS.csv
│   ├── trips_json/
│   │   └── trips_YYYYMMDD_HHMMSS.json
│   ├── tickets_csv/
│   │   └── tickets_YYYYMMDD_HHMMSS.csv
│   └── tickets_json/
│       └── tickets_YYYYMMDD_HHMMSS.json
└── athena-results/
    └── (resultados de queries)
```

### Tablas en Glue Catalog

| Tabla | Origen | Formato | Particionada |
|-------|--------|---------|--------------|
| `passengers_csv` | S3 CSV | CSV | No |
| `trips_csv` | S3 CSV | CSV | No |
| `tickets_csv` | S3 CSV | CSV | No |

---

## 🔧 Requisitos Técnicos

### Software Necesario
- ✅ Docker Desktop
- ✅ Python 3.8+
- ✅ AWS CLI configurado
- ✅ PowerShell 5.1+ (Windows)

### Credenciales AWS
- ✅ AWS_ACCESS_KEY_ID
- ✅ AWS_SECRET_ACCESS_KEY
- ✅ AWS_SESSION_TOKEN (si usas AWS Academy)
- ✅ S3 Bucket creado
- ✅ Permisos de Glue

### Microservicios Corriendo
- ✅ ms-passengers (Puerto 8001)
- ✅ ms-trips (Puerto 8002)
- ✅ ms-tickets (Puerto 8003)

---

## 📸 Evidencias a Generar

Para completar la entrega, captura screenshots de:

### Docker & Ingesta
1. ✅ `docker-compose ps` mostrando 4 servicios
2. ✅ Logs de ingesta con mensajes de éxito
3. ✅ Comando `aws s3 ls` mostrando archivos en S3

### AWS Glue
4. ✅ Database `bus_mvp_db` en Glue Console
5. ✅ Lista de 3 crawlers creados
6. ✅ Estado "Ready" de los crawlers
7. ✅ Tablas creadas en el catálogo

### AWS Athena
8. ✅ Ejecución de Consulta 1 con resultados
9. ✅ Ejecución de Consulta 2 con resultados
10. ✅ Ejecución de Consulta 3 con resultados
11. ✅ Ejecución de Consulta 4 con resultados
12. ✅ Comando `CREATE VIEW` para vista 1
13. ✅ Comando `CREATE VIEW` para vista 2
14. ✅ `SHOW VIEWS;` mostrando las 2 vistas
15. ✅ Query sobre una de las vistas

### Documentación
16. ✅ Diagrama ER (exportado como imagen)
17. ✅ Archivo athena_queries.sql
18. ✅ Archivo athena_views.sql

---

## 🆘 Solución de Problemas Comunes

### Error: "Credenciales AWS inválidas"
```powershell
# Solución: Renovar credenciales de AWS Academy
1. Acceder a AWS Academy Learner Lab
2. Click en "AWS Details"
3. Copiar nuevas credenciales
4. Actualizar archivo .env
```

### Error: "Bucket S3 no existe"
```powershell
# Solución: Crear bucket
aws s3 mb s3://bus-mvp-datalake
```

### Error: "Crawlers no encuentran datos"
```powershell
# Solución: Verificar que la ingesta se completó
aws s3 ls s3://bus-mvp-datalake/raw/ --recursive

# Si no hay archivos, re-ejecutar ingesta
docker-compose up passengers-ingestion
```

### Error: "Permission denied en Glue"
```powershell
# Solución: Verificar IAM Role
# El role debe tener políticas:
# - AWSGlueServiceRole
# - AmazonS3FullAccess (o específico al bucket)
```

---

## 📚 Documentación Adicional

- 📖 [Guía de Verificación Completa](GUIA_VERIFICACION_REQUISITOS.md)
- 📖 [Diagrama ER Detallado](docs/analytics/data_catalog_er.md)
- 📖 [Consultas SQL](docs/analytics/athena_queries.sql)
- 📖 [Vistas Athena](docs/analytics/athena_views.sql)
- 📖 [Testing Guide](data-ingestion/TESTING_GUIDE.md)

---

## 🎉 Conclusión

Este proyecto implementa una **pipeline completa de Data Analytics** que:

1. ✅ Extrae datos de 3 microservicios con arquitectura REST
2. ✅ Transforma y limpia los datos con pandas
3. ✅ Carga a S3 Data Lake en formato CSV y JSON
4. ✅ Cataloga con AWS Glue para descubrimiento automático
5. ✅ Permite consultas SQL con AWS Athena
6. ✅ Provee vistas optimizadas para análisis recurrentes

**Resultado**: Sistema de analytics escalable y listo para producción.

---

## 👥 Equipo

**Grupo 9 - Cloud Computing**
- Proyecto: Bus MVP
- Componente: Data Analytics & Ingestion

---

## 📞 Contacto

Para dudas sobre el setup:
1. Revisar `GUIA_VERIFICACION_REQUISITOS.md`
2. Ejecutar `run_complete_setup.ps1` opción "1" para diagnóstico
3. Verificar logs en Docker: `docker-compose logs [servicio]`

---

**Última actualización**: Octubre 2025
**Versión**: 1.0.0
