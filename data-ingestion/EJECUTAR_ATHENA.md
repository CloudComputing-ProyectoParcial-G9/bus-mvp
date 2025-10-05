# 🚀 EJECUCIÓN RÁPIDA - Scripts de Athena

## ✅ Scripts Listos para Ejecutar

Ya tengo **3 scripts Python** que ejecutan automáticamente las consultas y vistas en Athena, guardando los resultados en `s3://bus-mvp-datalake/athena-results/`.

---

## 📋 Pasos para Ejecutar

### Opción 1: Menu Interactivo PowerShell (RECOMENDADO)

```powershell
cd data-ingestion
.\run_complete_setup.ps1
```

**En el menú, selecciona:**
- **Opción 5**: Ejecutar 4 Consultas SQL en Athena ⭐
- **Opción 6**: Crear 2 Vistas en Athena ⭐
- **Opción 7**: Ejecutar TODO (hace todo automáticamente) 🎯

---

### Opción 2: Ejecutar Scripts Individuales

#### 1️⃣ Primero: Crear tablas en Athena (una sola vez)

```powershell
cd data-ingestion
python scripts/create_athena_tables.py
```

**Esto crea:**
- Tabla `passengers` desde CSV
- Tabla `trips` desde CSV
- Tabla `tickets` desde CSV

#### 2️⃣ Segundo: Ejecutar 4 Consultas SQL (REQUISITO)

```powershell
python scripts/run_athena_queries.py
```

**Esto ejecuta automáticamente:**
- ✅ Consulta 1: Historial de Compras por Pasajero (JOIN passengers + tickets)
- ✅ Consulta 2: Análisis de Ingresos por Viaje (JOIN trips + tickets)
- ✅ Consulta 3: Resumen Completo de Transacciones (JOIN TRIPLE)
- ✅ Consulta 4: Tendencias de Ventas por Ruta

**Resultados:**
- 📦 Archivos CSV guardados en: `s3://bus-mvp-datalake/athena-results/`
- 📄 Reporte local: `scripts/athena_queries_execution_TIMESTAMP.txt`
- 📊 Preview de resultados en consola

#### 3️⃣ Tercero: Crear 2 Vistas (REQUISITO)

```powershell
python scripts/create_athena_views.py
```

**Esto crea automáticamente:**
- ✅ Vista 1: `passenger_sales_summary`
- ✅ Vista 2: `trip_occupancy_revenue`

**Resultados:**
- 🔍 Vistas creadas y verificadas
- 📄 Reporte local: `scripts/athena_views_creation_TIMESTAMP.txt`

---

## 📸 Evidencias Generadas Automáticamente

### Al ejecutar `run_athena_queries.py`:

1. **Output en consola** (capturar screenshot):
```
╔══════════════════════════════════════════════════════════════════╗
║        BUS MVP - EJECUCIÓN DE CONSULTAS SQL EN ATHENA           ║
║  Requisito: 4 consultas SQL que unen varias tablas              ║
║  Destino: s3://bus-mvp-datalake/athena-results/                 ║
╚══════════════════════════════════════════════════════════════════╝

======================================================================
📊 CONSULTA 1: Historial de Compras por Pasajero
======================================================================
✅ Query ejecutada exitosamente en 3.45 segundos
📁 Resultados guardados en: s3://bus-mvp-datalake/athena-results/abc123.csv

📊 RESULTADOS:
passenger_id | full_name | email | total_tickets | total_spent
...
```

2. **Archivo de reporte**: `athena_queries_execution_TIMESTAMP.txt`
   - Contiene Execution IDs
   - Ubicación de archivos en S3
   - Timestamps de ejecución
   - Evidencia completa

3. **Archivos en S3**: `s3://bus-mvp-datalake/athena-results/`
   - CSVs con resultados de cada query

### Al ejecutar `create_athena_views.py`:

1. **Output en consola** (capturar screenshot):
```
╔══════════════════════════════════════════════════════════════════╗
║          BUS MVP - CREACIÓN DE VISTAS EN ATHENA                 ║
║  Requisito: 2 vistas que simplifican consultas analíticas      ║
╚══════════════════════════════════════════════════════════════════╝

======================================================================
🔧 CREANDO VISTA: passenger_sales_summary
======================================================================
✅ Vista creada exitosamente en 2.10 segundos
✅ Vista verificada - 10 filas retornadas
...
```

2. **Archivo de reporte**: `athena_views_creation_TIMESTAMP.txt`

---

## 🔍 Verificación de Resultados

### Ver archivos en S3:

```powershell
aws s3 ls s3://bus-mvp-datalake/athena-results/ --recursive
```

### Descargar resultados como evidencia:

```powershell
# Crear carpeta de evidencias
mkdir evidencias

# Descargar todos los CSVs
aws s3 cp s3://bus-mvp-datalake/athena-results/ ./evidencias/ --recursive --exclude "*" --include "*.csv"
```

### Verificar vistas en Athena Console:

1. Ir a: https://console.aws.amazon.com/athena/
2. Seleccionar database: `bus_mvp_db`
3. Ejecutar:

```sql
SHOW VIEWS;
-- Debe mostrar: passenger_sales_summary, trip_occupancy_revenue

SELECT * FROM passenger_sales_summary LIMIT 10;
SELECT * FROM trip_occupancy_revenue LIMIT 10;
```

---

## ✅ Checklist de Entrega

Después de ejecutar los scripts, tendrás:

### Para Consultas SQL:
- [x] ✅ 4 consultas ejecutadas automáticamente
- [x] ✅ Resultados en S3 (`athena-results/`)
- [x] ✅ Screenshot del output del script
- [x] ✅ Archivo de reporte local
- [x] ✅ Execution IDs documentados

### Para Vistas:
- [x] ✅ 2 vistas creadas (`passenger_sales_summary`, `trip_occupancy_revenue`)
- [x] ✅ Vistas verificadas con SELECT
- [x] ✅ Screenshot del output del script
- [x] ✅ Archivo de reporte local

---

## 🆘 Solución Rápida de Problemas

### Error: "Database does not exist"
```powershell
# Ejecutar primero el setup de Glue
python scripts/setup_complete_glue.py
```

### Error: "Table does not exist"
```powershell
# Crear tablas primero
python scripts/create_athena_tables.py
```

### Error: "No module named boto3"
```powershell
pip install boto3 python-dotenv
```

### Error: "Access Denied"
```powershell
# Verificar credenciales AWS en .env
# Renovar credenciales de AWS Academy si expiraron
```

---

## 🎯 Ejemplo de Ejecución Completa

```powershell
# 1. Ir a la carpeta
cd C:\Users\luisf\CS\cloudcomputing\bus-mvp\data-ingestion

# 2. Ejecutar setup completo (si no lo has hecho)
python scripts/setup_complete_glue.py

# 3. Crear tablas
python scripts/create_athena_tables.py

# 4. Ejecutar 4 consultas SQL ⭐
python scripts/run_athena_queries.py
# ✅ Capturar screenshot del output
# ✅ Guardar archivo athena_queries_execution_*.txt

# 5. Crear 2 vistas ⭐
python scripts/create_athena_views.py
# ✅ Capturar screenshot del output
# ✅ Guardar archivo athena_views_creation_*.txt

# 6. Descargar resultados de S3
aws s3 ls s3://bus-mvp-datalake/athena-results/
aws s3 cp s3://bus-mvp-datalake/athena-results/ ./evidencias/ --recursive
```

---

## 📦 Archivos Generados

Después de ejecutar todo, tendrás:

```
data-ingestion/
├── scripts/
│   ├── athena_queries_execution_20251005_143025.txt  📄 Evidencia queries
│   └── athena_views_creation_20251005_143530.txt     📄 Evidencia vistas
│
└── evidencias/                                         📁 (crear esta carpeta)
    ├── abc123-query1.csv                              📊 Resultados query 1
    ├── def456-query2.csv                              📊 Resultados query 2
    ├── ghi789-query3.csv                              📊 Resultados query 3
    └── jkl012-query4.csv                              📊 Resultados query 4
```

---

## 🎉 ¡Listo!

Con estos scripts, cumples automáticamente los requisitos:
- ✅ **4 consultas SQL** ejecutadas y guardadas en S3
- ✅ **2 vistas** creadas en Athena
- ✅ **Evidencia completa** generada automáticamente

**Todo guardado en:** `s3://bus-mvp-datalake/athena-results/` ✨
