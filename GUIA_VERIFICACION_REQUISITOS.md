# 🎯 GUÍA DE VERIFICACIÓN DE REQUISITOS - Bus MVP Data Analytics

## 📋 Checklist de Cumplimiento

### ✅ Requisito 1: Máquina Virtual "MV ingesta"
**Estado**: ✅ **CUMPLIDO**

**Evidencia**:
- Servicios Docker en `data-ingestion/docker-compose.yml`
- 4 contenedores:
  - `passengers-ingestion`
  - `trips-ingestion`
  - `tickets-ingestion`
  - `analytics-service`

**Verificación**:
```powershell
cd data-ingestion
docker-compose ps
```

---

### ✅ Requisito 2: Bucket S3
**Estado**: ✅ **CUMPLIDO**

**Evidencia**:
- Variable `S3_BUCKET` configurada en docker-compose.yml
- Bucket: `bus-mvp-datalake` (o el que hayas configurado en .env)

**Verificación**:
```powershell
aws s3 ls s3://bus-mvp-datalake/raw/
```

Deberías ver:
```
PRE passengers_csv/
PRE passengers_json/
PRE tickets_csv/
PRE tickets_json/
PRE trips_csv/
PRE trips_json/
```

---

### ✅ Requisito 3: 3 Contenedores Docker con Estrategia PULL 100%
**Estado**: ✅ **CUMPLIDO**

**Evidencia**:
- `passengers-ingestion/ingest.py` - Extrae 100% de pasajeros
- `trips-ingestion/ingest.py` - Extrae 100% de viajes
- `tickets-ingestion/ingest.py` - Extrae 100% de tickets

**Características**:
- ✅ No hay límites de paginación
- ✅ Extrae todos los registros con `GET /api/{resource}`
- ✅ Genera archivos CSV **Y** JSON

**Verificación de Código**:
```python
# Todos los servicios usan:
response = requests.get(f'{self.api_url}/passengers')  # Sin limit ni offset
data = response.json()  # Todos los registros
```

**Ejecutar Ingesta**:
```powershell
cd data-ingestion

# Configurar credenciales AWS en .env
# Luego ejecutar:
docker-compose up passengers-ingestion
docker-compose up trips-ingestion
docker-compose up tickets-ingestion
```

**Verificar Logs**:
Los contenedores deben mostrar:
```
✅ Retrieved X passengers
✅ Uploaded CSV: s3://bus-mvp-datalake/raw/passengers_csv/...
✅ Uploaded JSON: s3://bus-mvp-datalake/raw/passengers_json/...
```

---

### ✅ Requisito 4: Catálogo de Datos en AWS Glue
**Estado**: ⚠️ **REQUIERE EJECUCIÓN**

**Archivos Creados**:
- ✅ `data-ingestion/scripts/setup_complete_glue.py` - Script automatizado

**Pasos para Cumplir**:

#### Opción A: Script Automatizado (RECOMENDADO)

```powershell
cd data-ingestion

# 1. Instalar dependencias
pip install boto3

# 2. Configurar credenciales AWS (si no están configuradas)
# Editar .env con:
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...
# AWS_SESSION_TOKEN=...

# 3. Ejecutar script
python scripts/setup_complete_glue.py
```

El script:
- ✅ Crea database `bus_mvp_db`
- ✅ Crea 3 crawlers (passengers, trips, tickets)
- ✅ Ejecuta los crawlers
- ✅ Verifica tablas creadas

#### Opción B: Manual desde AWS Console

1. **Acceder a Glue Console**:
   - https://console.aws.amazon.com/glue/

2. **Crear Database**:
   - Databases → Add database
   - Name: `bus_mvp_db`
   - Description: "Bus MVP Analytics Catalog"

3. **Crear Crawlers** (repetir 3 veces):

   **Crawler 1: Passengers**
   - Name: `passengers-csv-crawler`
   - Data source: `s3://bus-mvp-datalake/raw/passengers_csv/`
   - IAM role: `AWSGlueServiceRole-BusMVP` (crear si no existe)
   - Database: `bus_mvp_db`
   - Frequency: On demand

   **Crawler 2: Trips**
   - Name: `trips-csv-crawler`
   - Data source: `s3://bus-mvp-datalake/raw/trips_csv/`
   - IAM role: `AWSGlueServiceRole-BusMVP`
   - Database: `bus_mvp_db`

   **Crawler 3: Tickets**
   - Name: `tickets-csv-crawler`
   - Data source: `s3://bus-mvp-datalake/raw/tickets_csv/`
   - IAM role: `AWSGlueServiceRole-BusMVP`
   - Database: `bus_mvp_db`

4. **Ejecutar Crawlers**:
   - Seleccionar cada crawler → Run crawler
   - Esperar a que el estado sea "Ready"

5. **Verificar Tablas**:
   - Tables → Ver que existen 3 tablas:
     - `passengers_csv`
     - `trips_csv`
     - `tickets_csv`

**Evidencia Requerida**:
- ✅ Screenshot de Glue Database
- ✅ Screenshot de los 3 Crawlers
- ✅ Screenshot de las 3 Tablas creadas

---

### ✅ Requisito 5: Diagrama Entidad/Relación
**Estado**: ✅ **CUMPLIDO**

**Evidencia**:
- ✅ Archivo creado: `docs/analytics/data_catalog_er.md`

**Contenido del Diagrama**:
```
PASSENGERS (1) ──────< TICKETS >────── (N) TRIPS
     │                   │                   │
     │                   │                   │
  PK: passenger_id   PK: ticket_id      PK: trip_id
                     FK: passenger_id   
                     FK: trip_id
```

**Relaciones Documentadas**:
1. ✅ PASSENGERS → TICKETS (1:N)
2. ✅ TRIPS → TICKETS (1:N)
3. ✅ PASSENGERS ↔ TRIPS (N:M a través de TICKETS)

**Para Presentación**:
Puedes convertir el diagrama a imagen usando:
- https://www.drawio.com/ (importar el markdown)
- Lucidchart
- dbdiagram.io

**Evidencia Requerida**:
- ✅ Diagrama visual (PNG/PDF)
- ✅ Documento markdown con descripción de relaciones

---

### ⚠️ Requisito 6: 4 Consultas SQL en AWS Athena
**Estado**: ✅ **PREPARADO** - ⚠️ **REQUIERE EJECUCIÓN**

**Evidencia**:
- ✅ Archivo creado: `docs/analytics/athena_queries.sql`

**Consultas Preparadas**:
1. ✅ **Historial de Compras por Pasajero** (JOIN passengers + tickets)
2. ✅ **Análisis de Ingresos por Viaje** (JOIN trips + tickets)
3. ✅ **Resumen Completo de Transacciones** (JOIN triple: passengers + tickets + trips)
4. ✅ **Tendencias de Ventas por Período** (JOIN trips + tickets con análisis temporal)

**Pasos para Ejecutar**:

1. **Acceder a Athena Console**:
   - https://console.aws.amazon.com/athena/

2. **Configurar Output Location** (primera vez):
   - Settings → Manage
   - Query result location: `s3://bus-mvp-datalake/athena-results/`

3. **Seleccionar Database**:
   - En el panel izquierdo: Database → `bus_mvp_db`

4. **Verificar Tablas**:
   ```sql
   SHOW TABLES;
   ```
   Debes ver: `passengers_csv`, `trips_csv`, `tickets_csv`

5. **Ejecutar Consulta 1**:
   - Copiar consulta de `docs/analytics/athena_queries.sql`
   - Pegar en Query editor
   - Ejecutar (Run query)
   - Capturar screenshot de resultados

6. **Repetir para Consultas 2, 3 y 4**

**Evidencia Requerida**:
- ✅ 4 screenshots de consultas ejecutadas con resultados
- ✅ Archivo SQL con las 4 consultas
- ✅ (Opcional) Exportar resultados a CSV

---

### ⚠️ Requisito 7: 2 Vistas en AWS Athena
**Estado**: ✅ **PREPARADO** - ⚠️ **REQUIERE EJECUCIÓN**

**Evidencia**:
- ✅ Archivo creado: `docs/analytics/athena_views.sql`

**Vistas Preparadas**:
1. ✅ **`passenger_sales_summary`**
   - Métricas de valor del cliente
   - Segmentación RFM
   - Análisis de comportamiento

2. ✅ **`trip_occupancy_revenue`**
   - Análisis de ocupación por viaje
   - Métricas de rentabilidad
   - Optimización de rutas

**Pasos para Crear Vistas**:

1. **Acceder a Athena Console**

2. **Seleccionar Database**: `bus_mvp_db`

3. **Crear Vista 1**:
   ```sql
   -- Copiar el comando CREATE VIEW de docs/analytics/athena_views.sql
   -- Para passenger_sales_summary
   ```
   - Ejecutar
   - Verificar mensaje: "Query successful"

4. **Crear Vista 2**:
   ```sql
   -- Copiar el comando CREATE VIEW de docs/analytics/athena_views.sql
   -- Para trip_occupancy_revenue
   ```
   - Ejecutar
   - Verificar mensaje: "Query successful"

5. **Verificar Vistas Creadas**:
   ```sql
   SHOW VIEWS;
   ```
   Debes ver:
   - `passenger_sales_summary`
   - `trip_occupancy_revenue`

6. **Probar las Vistas**:
   ```sql
   SELECT * FROM passenger_sales_summary LIMIT 10;
   SELECT * FROM trip_occupancy_revenue LIMIT 10;
   ```

**Evidencia Requerida**:
- ✅ Screenshot de comando `CREATE VIEW` ejecutado
- ✅ Screenshot de `SHOW VIEWS` mostrando las 2 vistas
- ✅ Screenshot de resultados de queries sobre las vistas

---

## 🚀 PLAN DE EJECUCIÓN COMPLETO

### Fase 1: Preparación (5 minutos)

```powershell
# 1. Verificar microservicios corriendo
cd C:\Users\luisf\CS\cloudcomputing\bus-mvp
docker ps

# Deberías ver: ms-passengers, ms-trips, ms-tickets

# 2. Configurar credenciales AWS
cd data-ingestion
# Editar .env con credenciales de AWS Academy
```

### Fase 2: Ingesta de Datos (10 minutos)

```powershell
# Terminal 1: Passengers
docker-compose up passengers-ingestion

# Terminal 2: Trips
docker-compose up trips-ingestion

# Terminal 3: Tickets
docker-compose up tickets-ingestion

# Verificar datos en S3
aws s3 ls s3://bus-mvp-datalake/raw/ --recursive
```

### Fase 3: Configurar AWS Glue (15 minutos)

```powershell
# Opción Automatizada:
pip install boto3
python scripts/setup_complete_glue.py

# Opción Manual:
# Seguir pasos en AWS Glue Console (ver arriba)
```

### Fase 4: Ejecutar Consultas SQL (10 minutos)

1. Abrir Athena Console
2. Ejecutar 4 consultas de `docs/analytics/athena_queries.sql`
3. Capturar screenshots

### Fase 5: Crear Vistas (5 minutos)

1. En Athena Console
2. Ejecutar 2 comandos CREATE VIEW de `docs/analytics/athena_views.sql`
3. Verificar con SHOW VIEWS
4. Capturar screenshots

### Fase 6: Documentación (10 minutos)

1. Exportar diagrama ER a imagen
2. Organizar screenshots en carpeta `evidencias/`
3. Crear documento README con evidencias

---

## 📸 EVIDENCIAS A ENTREGAR

### Carpeta de Evidencias Sugerida:
```
evidencias/
├── 01-docker-compose-services.png
├── 02-s3-bucket-structure.png
├── 03-ingestion-logs-passengers.png
├── 04-ingestion-logs-trips.png
├── 05-ingestion-logs-tickets.png
├── 06-glue-database.png
├── 07-glue-crawlers.png
├── 08-glue-tables.png
├── 09-er-diagram.png
├── 10-athena-query-1.png
├── 11-athena-query-2.png
├── 12-athena-query-3.png
├── 13-athena-query-4.png
├── 14-athena-create-view-1.png
├── 15-athena-create-view-2.png
├── 16-athena-show-views.png
└── 17-athena-query-views.png
```

### Documentos a Entregar:
1. ✅ `docs/analytics/data_catalog_er.md` - Diagrama ER
2. ✅ `docs/analytics/athena_queries.sql` - 4 Consultas SQL
3. ✅ `docs/analytics/athena_views.sql` - 2 Vistas
4. ✅ Screenshots organizados
5. ✅ README explicando cada evidencia

---

## ✅ RESUMEN DE CUMPLIMIENTO FINAL

| # | Requisito | Estado | Evidencia |
|---|-----------|--------|-----------|
| 1 | MV ingesta | ✅ Cumplido | docker-compose.yml + logs |
| 2 | Bucket S3 | ✅ Cumplido | Variable S3_BUCKET + archivos |
| 3 | 3 Contenedores Docker | ✅ Cumplido | ingest.py (x3) + logs |
| 4 | Catálogo AWS Glue | ⚠️ Ejecutar | setup_complete_glue.py |
| 5 | Diagrama ER | ✅ Cumplido | data_catalog_er.md |
| 6 | 4 Consultas SQL | ⚠️ Ejecutar | athena_queries.sql |
| 7 | 2 Vistas Athena | ⚠️ Ejecutar | athena_views.sql |

**Estado Global**: 4/7 ✅ Completos | 3/7 ⚠️ Requieren Ejecución

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Problema: Crawlers no encuentran datos
**Solución**:
```powershell
# Verificar que los archivos existen en S3
aws s3 ls s3://bus-mvp-datalake/raw/passengers_csv/

# Re-ejecutar ingesta si no hay archivos
docker-compose up passengers-ingestion
```

### Problema: Athena no muestra tablas
**Solución**:
```sql
-- Verificar database seleccionada
SHOW DATABASES;

-- Cambiar a la database correcta
-- Luego: SHOW TABLES;
```

### Problema: Credenciales AWS expiradas
**Solución**:
1. Acceder a AWS Academy Learner Lab
2. Copiar nuevas credenciales
3. Actualizar archivo `.env`
4. Reiniciar contenedores: `docker-compose down && docker-compose up`

### Problema: Error de permisos en Glue
**Solución**:
- Verificar que el IAM Role tiene políticas:
  - `AWSGlueServiceRole`
  - Acceso a S3 bucket

---

## 📞 COMANDOS RÁPIDOS DE VERIFICACIÓN

```powershell
# Ver servicios corriendo
docker ps

# Ver logs de ingesta
docker-compose logs passengers-ingestion

# Listar archivos en S3
aws s3 ls s3://bus-mvp-datalake/raw/ --recursive

# Ver tablas en Glue (CLI)
aws glue get-tables --database-name bus_mvp_db

# Ejecutar query en Athena (CLI)
aws athena start-query-execution --query-string "SHOW TABLES" --result-configuration "OutputLocation=s3://bus-mvp-datalake/athena-results/" --query-execution-context "Database=bus_mvp_db"
```

---

## 🎓 CONCLUSIÓN

Tu proyecto **Bus MVP** tiene implementados correctamente:
- ✅ Arquitectura de ingesta con Docker
- ✅ Pipeline ETL completo (Extract, Transform, Load)
- ✅ Separación de datos CSV/JSON
- ✅ Estrategia PULL 100% sin paginación
- ✅ Documentación completa de esquema
- ✅ Consultas SQL analíticas preparadas
- ✅ Vistas para análisis recurrentes

**Solo falta ejecutar los pasos de AWS Glue y Athena para completar todos los requisitos.**

¡Buena suerte! 🚀
