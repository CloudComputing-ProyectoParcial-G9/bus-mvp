# 🧪 Guía de Pruebas - Bus MVP Data Pipeline

Esta guía te ayudará a probar cada componente del pipeline de datos paso a paso.

## 📋 Pre-requisitos

Antes de comenzar las pruebas:

- [ ] Microservicios corriendo (ms-passengers, ms-trips, ms-tickets)
- [ ] Docker y Docker Compose instalados
- [ ] AWS CLI configurado con credenciales
- [ ] Archivo `.env` configurado

## 🧪 Test Suite

### Test 1: Verificar Conectividad a Microservicios

```bash
# Test ms-passengers
curl http://localhost:3001/api/passengers
# Esperado: Lista de pasajeros en JSON

# Test ms-trips
curl http://localhost:3002/api/trips
# Esperado: Lista de viajes en JSON

# Test ms-tickets
curl http://localhost:3003/api/tickets
# Esperado: Lista de tickets en JSON
```

**✅ Criterio de Éxito**: Cada endpoint retorna datos en formato JSON

---

### Test 2: Verificar Variables de Entorno

```bash
cd data-ingestion

# Verificar que .env existe y tiene las credenciales
cat .env | grep -v "^#" | grep -v "^$"

# Verificar credenciales AWS
aws sts get-caller-identity
# Esperado: Tu Account ID y ARN
```

**✅ Criterio de Éxito**: 
- Archivo .env existe
- Credenciales AWS válidas
- Account ID visible

---

### Test 3: Build de Contenedores

```bash
# Build de todos los contenedores
docker-compose build

# Verificar imágenes creadas
docker images | grep -E "passengers-ingestion|trips-ingestion|tickets-ingestion|analytics"

# Esperado: 4 imágenes listadas
```

**✅ Criterio de Éxito**: 
- Build sin errores
- 4 imágenes Docker creadas

---

### Test 4: Ingesta de Pasajeros

```bash
# Ejecutar solo ingesta de pasajeros
docker-compose up passengers-ingestion

# Verificar logs (en otro terminal)
docker-compose logs passengers-ingestion

# Verificar archivo en S3
aws s3 ls s3://bus-mvp-datalake/raw/passengers/
```

**✅ Criterio de Éxito**:
- ✅ Logs muestran "PASSENGERS INGESTION COMPLETED"
- ✅ Archivos .csv y .json en S3
- ✅ Sin errores en logs

**Ejemplo de Output Esperado**:
```
============================================================
🚀 PASSENGERS INGESTION PIPELINE
============================================================
📍 API URL: http://host.docker.internal:3001/api
📦 S3 Bucket: bus-mvp-datalake
🕐 Started at: 2025-10-05T14:30:22
============================================================
🔍 Fetching passengers from http://host.docker.internal:3001/api/passengers...
✅ Retrieved 150 passengers
🔄 Transformed 150 records to DataFrame
📊 Columns: ['passenger_id', 'name', 'email', 'phone', 'dni', 'created_at', 'ingestion_timestamp']
✅ Uploaded CSV: s3://bus-mvp-datalake/raw/passengers/passengers_20251005_143022.csv
✅ Uploaded JSON: s3://bus-mvp-datalake/raw/passengers/passengers_20251005_143022.json
============================================================
✅ PASSENGERS INGESTION COMPLETED
📊 Total records ingested: 150
🕐 Finished at: 2025-10-05T14:30:25
============================================================
```

---

### Test 5: Ingesta de Viajes

```bash
# Ejecutar ingesta de viajes
docker-compose up trips-ingestion

# Verificar archivo en S3
aws s3 ls s3://bus-mvp-datalake/raw/trips/
```

**✅ Criterio de Éxito**:
- ✅ Logs muestran "TRIPS INGESTION COMPLETED"
- ✅ Archivos .csv y .json en S3

---

### Test 6: Ingesta de Tickets

```bash
# Ejecutar ingesta de tickets
docker-compose up tickets-ingestion

# Verificar archivo en S3
aws s3 ls s3://bus-mvp-datalake/raw/tickets/
```

**✅ Criterio de Éxito**:
- ✅ Logs muestran "TICKETS INGESTION COMPLETED"
- ✅ Archivos .csv y .json en S3

---

### Test 7: Verificar Datos en S3

```bash
# Listar todos los archivos
aws s3 ls s3://bus-mvp-datalake/raw/ --recursive

# Contar archivos
aws s3 ls s3://bus-mvp-datalake/raw/ --recursive | wc -l
# Esperado: Mínimo 6 archivos (3 CSV + 3 JSON)

# Descargar y ver un archivo CSV
aws s3 cp s3://bus-mvp-datalake/raw/passengers/passengers_*.csv - | head -n 5

# Descargar y ver un archivo JSON
aws s3 cp s3://bus-mvp-datalake/raw/passengers/passengers_*.json - | head -n 20
```

**✅ Criterio de Éxito**:
- ✅ Mínimo 6 archivos en S3
- ✅ Archivos tienen contenido válido
- ✅ CSV tiene headers
- ✅ JSON es válido

---

### Test 8: Setup de AWS Glue

```bash
# Actualizar Account ID en el script
YOUR_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Your Account ID: $YOUR_ACCOUNT_ID"

# Editar script (reemplazar YOUR_ACCOUNT_ID)
nano scripts/setup_glue.py

# Ejecutar setup
python3 scripts/setup_glue.py

# Verificar database creada
aws glue get-database --name bus_mvp_db

# Verificar crawlers
aws glue list-crawlers | grep "Name"
```

**✅ Criterio de Éxito**:
- ✅ Database "bus_mvp_db" creada
- ✅ 3 crawlers creados
- ✅ Crawlers en estado READY

**Ejemplo de Output**:
```
============================================================
🚀 AWS GLUE CATALOG SETUP
============================================================
🕐 Started at: 2025-10-05T14:35:00
============================================================

📊 Step 1: Creating database...
✅ Database bus_mvp_db creada exitosamente

🕷️  Step 2: Creating crawlers...
✅ Crawler passengers-crawler creado exitosamente
✅ Crawler trips-crawler creado exitosamente
✅ Crawler tickets-crawler creado exitosamente

🚀 Step 3: Starting crawlers...
🚀 Crawler passengers-crawler iniciado
🚀 Crawler trips-crawler iniciado
🚀 Crawler tickets-crawler iniciado

⏳ Step 4: Waiting for crawlers to complete...
⏳ Esperando que crawler passengers-crawler termine...
✅ Crawler passengers-crawler completado
...
```

---

### Test 9: Verificar Tablas en Glue

```bash
# Listar todas las tablas
aws glue get-tables --database-name bus_mvp_db

# Ver schema de una tabla
aws glue get-table --database-name bus_mvp_db --name passengers

# Contar tablas
aws glue get-tables --database-name bus_mvp_db --query 'TableList[*].Name' --output text | wc -w
# Esperado: 3
```

**✅ Criterio de Éxito**:
- ✅ 3 tablas creadas (passengers, trips, tickets)
- ✅ Cada tabla tiene schema detectado
- ✅ Location apunta a S3

---

### Test 10: Consultas en Athena

```bash
# Opción 1: Desde AWS Console
# 1. Ir a AWS Athena Console
# 2. Seleccionar database: bus_mvp_db
# 3. Configurar output: s3://bus-mvp-datalake/athena-results/
# 4. Ejecutar query de prueba:

SELECT COUNT(*) as total_passengers FROM passengers;

# Opción 2: Desde AWS CLI
aws athena start-query-execution \
    --query-string "SELECT COUNT(*) FROM passengers" \
    --query-execution-context Database=bus_mvp_db \
    --result-configuration OutputLocation=s3://bus-mvp-datalake/athena-results/
```

**✅ Criterio de Éxito**:
- ✅ Query se ejecuta sin errores
- ✅ Retorna número de registros
- ✅ Resultados en S3

---

### Test 11: Crear Vistas en Athena

```bash
# En Athena Console, ejecutar:

CREATE OR REPLACE VIEW top_passengers AS
SELECT 
    p.passenger_id,
    p.name,
    COUNT(t.ticket_id) as total_tickets
FROM passengers p
LEFT JOIN tickets t ON p.passenger_id = t.passenger_id
GROUP BY p.passenger_id, p.name;

# Verificar vista
SELECT * FROM top_passengers LIMIT 10;
```

**✅ Criterio de Éxito**:
- ✅ Vista creada sin errores
- ✅ Query retorna datos

---

### Test 12: Analytics API

```bash
# Iniciar servicio
docker-compose up -d analytics-service

# Esperar 5 segundos
sleep 5

# Health check
curl http://localhost:5000/health
# Esperado: {"status": "healthy", ...}

# Test endpoint top-passengers
curl http://localhost:5000/api/analytics/top-passengers?limit=5

# Test endpoint popular-routes
curl http://localhost:5000/api/analytics/popular-routes

# Test endpoint summary
curl http://localhost:5000/api/analytics/summary
```

**✅ Criterio de Éxito**:
- ✅ Health check retorna 200
- ✅ Endpoints retornan JSON
- ✅ Datos son correctos

---

### Test 13: Consultas SQL Complejas

Ejecutar en Athena Console:

```sql
-- Query 1: Pasajeros con más tickets
SELECT 
    p.name,
    COUNT(t.ticket_id) as total_tickets,
    SUM(t.price) as total_spent
FROM passengers p
INNER JOIN tickets t ON p.passenger_id = t.passenger_id
GROUP BY p.passenger_id, p.name
ORDER BY total_tickets DESC
LIMIT 10;

-- Query 2: Rutas más populares
SELECT 
    tr.origin,
    tr.destination,
    COUNT(DISTINCT tr.trip_id) as total_trips,
    COUNT(t.ticket_id) as tickets_sold
FROM trips tr
LEFT JOIN tickets t ON tr.trip_id = t.trip_id
GROUP BY tr.origin, tr.destination
ORDER BY total_trips DESC;

-- Query 3: Revenue por fecha
SELECT 
    DATE(t.purchase_date) as sale_date,
    SUM(t.price) as daily_revenue
FROM tickets t
GROUP BY DATE(t.purchase_date)
ORDER BY sale_date DESC
LIMIT 30;
```

**✅ Criterio de Éxito**:
- ✅ Todas las queries ejecutan sin errores
- ✅ JOINs funcionan correctamente
- ✅ Resultados son lógicos

---

### Test 14: Prueba End-to-End

```bash
# 1. Limpiar datos anteriores (opcional)
aws s3 rm s3://bus-mvp-datalake/raw/ --recursive

# 2. Ejecutar ingesta completa
docker-compose up passengers-ingestion trips-ingestion tickets-ingestion

# 3. Esperar a que terminen
# Verificar logs

# 4. Verificar archivos en S3
aws s3 ls s3://bus-mvp-datalake/raw/ --recursive

# 5. Re-ejecutar crawlers
python3 scripts/setup_glue.py

# 6. Consultar en Athena
# (Desde Console)

# 7. Probar Analytics API
curl http://localhost:5000/api/analytics/summary
```

**✅ Criterio de Éxito**:
- ✅ Pipeline completo funciona
- ✅ Datos fluyen correctamente
- ✅ API retorna datos actualizados

---

## 📊 Checklist de Validación Final

### Infraestructura
- [ ] Bucket S3 existe y es accesible
- [ ] Estructura de carpetas creada
- [ ] IAM permissions configurados

### Ingesta
- [ ] Contenedor passengers-ingestion funciona
- [ ] Contenedor trips-ingestion funciona
- [ ] Contenedor tickets-ingestion funciona
- [ ] Archivos CSV generados correctamente
- [ ] Archivos JSON generados correctamente

### AWS Glue
- [ ] Database bus_mvp_db existe
- [ ] 3 crawlers creados
- [ ] 3 tablas catalogadas
- [ ] Schemas detectados correctamente

### Athena
- [ ] 4+ consultas SQL ejecutadas
- [ ] 2+ vistas creadas
- [ ] JOINs entre tablas funcionan
- [ ] Resultados son correctos

### Analytics API
- [ ] Servicio corriendo en puerto 5000
- [ ] Health check pasa
- [ ] 8 endpoints funcionan
- [ ] Retorna datos de Athena

### Documentación
- [ ] README actualizado
- [ ] Diagrama ER completo
- [ ] Queries documentadas
- [ ] Guías de deployment listas

---

## 🐛 Troubleshooting Común

### ❌ Error: Cannot connect to Docker daemon
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
# Logout y login de nuevo
```

### ❌ Error: Access Denied S3
```bash
# Verificar credenciales
aws sts get-caller-identity

# Verificar permisos del bucket
aws s3api get-bucket-policy --bucket bus-mvp-datalake
```

### ❌ Error: No data in Athena
```bash
# Re-ejecutar crawlers
aws glue start-crawler --name passengers-crawler
aws glue start-crawler --name trips-crawler
aws glue start-crawler --name tickets-crawler

# Esperar a que terminen
aws glue get-crawler --name passengers-crawler
```

### ❌ Error: Analytics API no responde
```bash
# Verificar logs
docker-compose logs analytics-service

# Verificar que esté corriendo
docker ps | grep analytics

# Reiniciar servicio
docker-compose restart analytics-service
```

---

## 🎯 Métricas de Éxito

Un deployment exitoso debe cumplir:

- ✅ **100% de ingestas exitosas** (3/3)
- ✅ **100% de archivos en S3** (6/6 mínimo)
- ✅ **100% de tablas catalogadas** (3/3)
- ✅ **100% de consultas funcionando** (6/6)
- ✅ **100% de vistas creadas** (4/4)
- ✅ **100% de endpoints API** (8/8)
- ✅ **0 errores críticos**

---

**¡Felicidades!** 🎉 Si todos los tests pasan, tu pipeline de Data Science está completamente funcional.
