# 🎯 Scripts de Athena - Ejecución Automática

## 📋 Scripts Disponibles

### 1. `create_athena_tables.py`
Crea las 3 tablas en Athena con el esquema correcto.

**Qué hace:**
- Crea tabla `passengers` desde CSV
- Crea tabla `trips` desde CSV  
- Crea tabla `tickets` desde CSV
- Configura `skip.header.line.count` para ignorar encabezados

**Uso:**
```powershell
cd data-ingestion
python scripts/create_athena_tables.py
```

---

### 2. `run_athena_queries.py` ⭐
**Ejecuta las 4 consultas SQL requeridas** y guarda resultados en S3.

**Qué hace:**
- ✅ **Consulta 1**: Historial de Compras por Pasajero (JOIN passengers + tickets)
- ✅ **Consulta 2**: Análisis de Ingresos por Viaje (JOIN trips + tickets)
- ✅ **Consulta 3**: Resumen Completo de Transacciones (JOIN TRIPLE: passengers + tickets + trips)
- ✅ **Consulta 4**: Tendencias de Ventas por Ruta (JOIN trips + tickets)
- 📦 Guarda resultados en `s3://bus-mvp-datalake-1/athena-results/`
- 📄 Genera reporte local con metadata de ejecución
- 📊 Muestra preview de resultados en consola

**Uso:**
```powershell
cd data-ingestion
python scripts/run_athena_queries.py
```

**Output esperado:**
```
╔══════════════════════════════════════════════════════════════════╗
║        BUS MVP - EJECUCIÓN DE CONSULTAS SQL EN ATHENA           ║
║  Requisito: 4 consultas SQL que unen varias tablas              ║
║  Destino: s3://bus-mvp-datalake-1/athena-results/                 ║
╚══════════════════════════════════════════════════════════════════╝

======================================================================
📊 CONSULTA 1: Historial de Compras por Pasajero
======================================================================
Descripción: Análisis del comportamiento de compra...
Query Execution ID: abc123...
✅ Query ejecutada exitosamente en 3.45 segundos
📁 Resultados guardados en: s3://bus-mvp-datalake-1/athena-results/abc123.csv

📊 RESULTADOS DE: Historial de Compras por Pasajero
Total de filas: 25
----------------------------------------------------------------------
passenger_id         | full_name           | email               ...
----------------------------------------------------------------------
...
```

---

### 3. `create_athena_views.py` ⭐
**Crea las 2 vistas requeridas** en Athena.

**Qué hace:**
- ✅ **Vista 1**: `passenger_sales_summary` - Métricas de clientes con segmentación
- ✅ **Vista 2**: `trip_occupancy_revenue` - Análisis de ocupación y rentabilidad
- 🔍 Verifica cada vista con SELECT
- 📄 Genera reporte local con metadata de creación

**Uso:**
```powershell
cd data-ingestion
python scripts/create_athena_views.py
```

**Output esperado:**
```
╔══════════════════════════════════════════════════════════════════╗
║          BUS MVP - CREACIÓN DE VISTAS EN ATHENA                 ║
║  Requisito: 2 vistas que simplifican consultas analíticas      ║
╚══════════════════════════════════════════════════════════════════╝

======================================================================
🔧 CREANDO VISTA: passenger_sales_summary
======================================================================
✅ Vista creada exitosamente en 2.10 segundos
🔍 Verificando vista: passenger_sales_summary
✅ Vista verificada - 10 filas retornadas en la muestra

======================================================================
🔧 CREANDO VISTA: trip_occupancy_revenue
======================================================================
✅ Vista creada exitosamente en 1.95 segundos
...
```

---

## 🚀 Ejecución Completa con Script PowerShell

### Método Recomendado: Menu Interactivo

```powershell
cd data-ingestion
.\run_complete_setup.ps1
```

**Opciones del menú:**
```
1. Verificar Requisitos (Check Only)
2. Ejecutar Ingesta de Datos
3. Configurar AWS Glue (Database + Crawlers)
4. Crear Tablas en Athena
5. Ejecutar 4 Consultas SQL en Athena         ⭐ NUEVO
6. Crear 2 Vistas en Athena                   ⭐ NUEVO
7. Ejecutar TODO (Ingesta + Glue + Athena)    ⭐ COMPLETO
8. Ver Resumen de Cumplimiento
9. Abrir Guía de Verificación
0. Salir
```

---

## 📊 Flujo Completo de Ejecución

### Paso a Paso Manual

```powershell
# 1. Ejecutar ingesta de datos
cd data-ingestion
docker-compose up passengers-ingestion
docker-compose up trips-ingestion
docker-compose up tickets-ingestion

# 2. Configurar Glue
python scripts/setup_complete_glue.py

# 3. Crear tablas en Athena
python scripts/create_athena_tables.py

# 4. Ejecutar 4 consultas SQL (REQUISITO)
python scripts/run_athena_queries.py

# 5. Crear 2 vistas (REQUISITO)
python scripts/create_athena_views.py
```

### Opción Automatizada (TODO EN UNO)

```powershell
cd data-ingestion
.\run_complete_setup.ps1
# Seleccionar opción 7 (Ejecutar TODO)
```

---

## 📁 Resultados en S3

Todos los resultados se guardan automáticamente en:

```
s3://bus-mvp-datalake-1/athena-results/
├── abc123-query1.csv                    # Consulta 1: Historial de Compras
├── abc123-query1.csv.metadata
├── def456-query2.csv                    # Consulta 2: Ingresos por Viaje
├── def456-query2.csv.metadata
├── ghi789-query3.csv                    # Consulta 3: JOIN Triple
├── ghi789-query3.csv.metadata
├── jkl012-query4.csv                    # Consulta 4: Tendencias por Ruta
└── jkl012-query4.csv.metadata
```

**Descargar resultados:**
```powershell
aws s3 ls s3://bus-mvp-datalake-1/athena-results/
aws s3 cp s3://bus-mvp-datalake-1/athena-results/ ./evidencias/ --recursive
```

---

## 📄 Reportes Generados Localmente

Los scripts generan archivos de evidencia en:

```
data-ingestion/scripts/
├── athena_queries_execution_20251005_143025.txt    # Reporte de queries
└── athena_views_creation_20251005_143530.txt       # Reporte de vistas
```

Estos archivos contienen:
- ✅ Execution IDs de cada query/vista
- ✅ Timestamps de ejecución
- ✅ Ubicación de resultados en S3
- ✅ Estadísticas de ejecución
- ✅ Evidencia completa para entrega

---

## 🔍 Verificación de Resultados

### Verificar que las queries se ejecutaron

```powershell
# Listar archivos en S3
aws s3 ls s3://bus-mvp-datalake-1/athena-results/ --recursive

# Ver query en Athena Console
# https://console.aws.amazon.com/athena/
```

### Verificar que las vistas existen

**En AWS Athena Console:**
```sql
SHOW VIEWS;
-- Debe mostrar: passenger_sales_summary, trip_occupancy_revenue

DESCRIBE passenger_sales_summary;
-- Muestra columnas de la vista

SELECT * FROM passenger_sales_summary LIMIT 10;
-- Consulta la vista
```

---

## 📸 Evidencias a Generar

### Para las 4 Consultas SQL:
1. ✅ Screenshot del output del script `run_athena_queries.py`
2. ✅ Screenshot de AWS Athena Console con historial de queries
3. ✅ Archivo local: `athena_queries_execution_*.txt`
4. ✅ (Opcional) Descargar CSVs desde S3

### Para las 2 Vistas:
1. ✅ Screenshot del output del script `create_athena_views.py`
2. ✅ Screenshot de `SHOW VIEWS;` en Athena Console
3. ✅ Screenshot de `SELECT * FROM passenger_sales_summary LIMIT 10;`
4. ✅ Archivo local: `athena_views_creation_*.txt`

---

## 🆘 Solución de Problemas

### Error: "No module named 'boto3'"
```powershell
pip install boto3 python-dotenv
```

### Error: "Database bus_mvp_db does not exist"
```powershell
# Ejecutar primero el setup de Glue
python scripts/setup_complete_glue.py
```

### Error: "Table passengers does not exist"
```powershell
# Crear tablas primero
python scripts/create_athena_tables.py
```

### Error: "Access Denied to S3"
```powershell
# Verificar credenciales AWS en .env
# Renovar credenciales de AWS Academy si expiraron
```

---

## ✅ Checklist de Cumplimiento

Después de ejecutar los scripts, verifica:

- [ ] ✅ 4 consultas SQL ejecutadas
  - [ ] Consulta 1: JOIN passengers + tickets
  - [ ] Consulta 2: JOIN trips + tickets
  - [ ] Consulta 3: JOIN TRIPLE (passengers + tickets + trips)
  - [ ] Consulta 4: Análisis agregado por ruta

- [ ] ✅ 2 vistas creadas
  - [ ] Vista 1: passenger_sales_summary
  - [ ] Vista 2: trip_occupancy_revenue

- [ ] ✅ Resultados en S3
  - [ ] Archivos CSV en athena-results/

- [ ] ✅ Evidencias generadas
  - [ ] Reportes locales .txt
  - [ ] Screenshots de ejecución

---

## 🎯 Resumen

**Scripts creados:**
1. ✅ `create_athena_tables.py` - Crea tablas
2. ✅ `run_athena_queries.py` - **4 Consultas SQL** ⭐
3. ✅ `create_athena_views.py` - **2 Vistas** ⭐
4. ✅ `run_complete_setup.ps1` - Menu interactivo completo

**Requisitos cumplidos:**
- ✅ 4 consultas SQL que unen múltiples tablas
- ✅ 2 vistas para análisis recurrentes
- ✅ Resultados guardados en S3 (`athena-results/`)
- ✅ Evidencia automática generada

**Todo listo para entrega!** 🎉
