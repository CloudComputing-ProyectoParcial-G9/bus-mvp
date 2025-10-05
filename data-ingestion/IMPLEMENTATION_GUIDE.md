# Manual de Implementación Completo
# Pipeline de Data Science - Bus MVP

## 📚 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura](#arquitectura)
3. [Prerequisitos](#prerequisitos)
4. [Instalación Local](#instalación-local)
5. [Despliegue en AWS](#despliegue-en-aws)
6. [Configuración de AWS Glue](#configuración-de-aws-glue)
7. [Consultas SQL en Athena](#consultas-sql-en-athena)
8. [Analytics API](#analytics-api)
9. [Integración con Frontend](#integración-con-frontend)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Visión General

Este proyecto implementa un pipeline completo de data science para el sistema Bus MVP, siguiendo las siguientes especificaciones:

### ✅ Requisitos Cumplidos

- ✅ **MV Ingesta**: Máquina virtual EC2 para procesamiento de datos
- ✅ **Bucket S3**: Almacenamiento de datos en formato data lake
- ✅ **3 Contenedores Docker**: Ingesta desde 3 microservicios diferentes
- ✅ **Estrategia Pull 100%**: Extracción completa de registros
- ✅ **Múltiples formatos**: CSV y JSON para cada dataset
- ✅ **AWS Glue Catalog**: Catálogo de datos con crawlers automáticos
- ✅ **Diagrama ER**: Documentación de relaciones entre tablas
- ✅ **4+ Consultas SQL**: Queries complejas con joins en Athena
- ✅ **2+ Vistas**: Vistas materializadas para analytics
- ✅ **Repositorio GitHub**: Código fuente público

### 🎁 Features Adicionales

- 🚀 **Analytics API REST**: Servicio Python/Flask para consultas
- 📊 **Múltiples endpoints**: Top passengers, popular routes, daily sales, etc.
- 🔄 **Automatización**: Scripts de setup y configuración
- 📝 **Documentación completa**: READMEs, guías de deployment
- 🐳 **Docker Compose**: Orquestación simplificada
- 🔐 **IAM Roles**: Seguridad mediante roles en lugar de credenciales

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                      MICROSERVICIOS                              │
├─────────────────────────────────────────────────────────────────┤
│  ms-passengers    │    ms-trips      │    ms-tickets            │
│  (MySQL/Flask)    │  (PostgreSQL/    │  (MongoDB/Java)          │
│                   │   Node.js)       │                          │
│  Port: 3001       │  Port: 3002      │  Port: 3003              │
└──────┬────────────┴────────┬─────────┴──────────┬───────────────┘
       │                     │                     │
       │ HTTP GET /api       │ HTTP GET /api       │ HTTP GET /api
       │                     │                     │
┌──────▼─────────────────────▼─────────────────────▼───────────────┐
│              CONTENEDORES DE INGESTA (Python)                    │
├──────────────────────────────────────────────────────────────────┤
│  passengers-     │   trips-          │   tickets-               │
│  ingestion       │   ingestion       │   ingestion              │
│                  │                   │                          │
│  - Extract       │   - Extract       │   - Extract              │
│  - Transform     │   - Transform     │   - Transform            │
│  - Load to S3    │   - Load to S3    │   - Load to S3           │
└──────┬───────────┴───────┬───────────┴──────────┬───────────────┘
       │                   │                       │
       │ CSV + JSON        │ CSV + JSON            │ CSV + JSON
       │                   │                       │
       ▼                   ▼                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    AWS S3 BUCKET (Data Lake)                     │
├──────────────────────────────────────────────────────────────────┤
│  s3://bus-mvp-datalake/                                          │
│  ├── raw/                                                        │
│  │   ├── passengers/*.csv, *.json                               │
│  │   ├── trips/*.csv, *.json                                    │
│  │   └── tickets/*.csv, *.json                                  │
│  ├── processed/                                                  │
│  └── athena-results/                                             │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       │ Crawlers
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                   AWS GLUE DATA CATALOG                          │
├──────────────────────────────────────────────────────────────────┤
│  Database: bus_mvp_db                                            │
│  ├── passengers (table)                                          │
│  ├── trips (table)                                               │
│  └── tickets (table)                                             │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       │ SQL Queries
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                       AWS ATHENA                                 │
├──────────────────────────────────────────────────────────────────┤
│  - SQL Queries (4+)                                              │
│  - Views (4+)                                                    │
│  - Analytics                                                     │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       │ API Calls
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    ANALYTICS API (Python/Flask)                  │
├──────────────────────────────────────────────────────────────────┤
│  Port: 5000                                                      │
│  Endpoints:                                                      │
│  - GET /api/analytics/top-passengers                             │
│  - GET /api/analytics/popular-routes                             │
│  - GET /api/analytics/daily-sales                                │
│  - GET /api/analytics/occupancy-rate                             │
│  - POST /api/analytics/custom-query                              │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       │ HTTP REST
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                            │
│                   AnalyticsSection.tsx                           │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisitos

### Software Requerido

- **Docker**: v20.10+
- **Docker Compose**: v2.0+
- **Python**: 3.8+
- **AWS CLI**: v2.0+
- **Git**: cualquier versión reciente

### Cuentas Necesarias

- **AWS Account** con permisos para:
  - EC2
  - S3
  - Glue
  - Athena
  - IAM

### Conocimientos

- Básico de Docker
- Básico de AWS
- SQL
- Python (opcional)

---

## 🚀 Instalación Local

### 1. Clonar Repositorio

```bash
git clone https://github.com/CloudComputing-ProyectoParcial-G9/bus-mvp.git
cd bus-mvp/data-ingestion
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
nano .env
```

Editar:
```env
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET=bus-mvp-datalake
PASSENGERS_API_URL=http://localhost:3001/api
TRIPS_API_URL=http://localhost:3002/api
TICKETS_API_URL=http://localhost:3003/api
```

### 3. Iniciar Microservicios

Asegúrate de que tus microservicios estén corriendo:

```bash
# En directorios separados
cd ../backend/ms-passengers && docker-compose up -d
cd ../backend/ms-trips && docker-compose up -d
cd ../backend/ms-tickets && docker-compose up -d
```

### 4. Crear Bucket S3

```bash
# Instalar dependencias
pip3 install -r scripts/requirements.txt

# Ejecutar script
python3 scripts/setup_s3.py
```

### 5. Build y Ejecutar Ingesta

```bash
# Build
docker-compose build

# Ejecutar todos los contenedores
docker-compose up

# O ejecutar individualmente
docker-compose up passengers-ingestion
docker-compose up trips-ingestion
docker-compose up tickets-ingestion
```

### 6. Verificar Datos en S3

```bash
aws s3 ls s3://bus-mvp-datalake/raw/ --recursive
```

---

## ☁️ Despliegue en AWS

Consulta el archivo [AWS_EC2_DEPLOYMENT.md](./AWS_EC2_DEPLOYMENT.md) para instrucciones detalladas.

### Resumen Rápido

```bash
# 1. Lanzar instancia EC2
aws ec2 run-instances \
    --image-id ami-0c7217cdde317cfec \
    --instance-type t3.medium \
    --key-name your-key

# 2. Conectar vía SSH
ssh -i "your-key.pem" ubuntu@<PUBLIC_IP>

# 3. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Clonar repo y ejecutar
git clone https://github.com/CloudComputing-ProyectoParcial-G9/bus-mvp.git
cd bus-mvp/data-ingestion
chmod +x quick_start.sh
./quick_start.sh
```

---

## 📊 Configuración de AWS Glue

### 1. Actualizar Account ID

```bash
# Obtener tu Account ID
aws sts get-caller-identity --query Account --output text

# Editar script
nano scripts/setup_glue.py
# Reemplazar YOUR_ACCOUNT_ID con tu Account ID
```

### 2. Ejecutar Setup

```bash
python3 scripts/setup_glue.py
```

### 3. Verificar Tablas

```bash
aws glue get-tables --database-name bus_mvp_db
```

---

## 🔍 Consultas SQL en Athena

### Acceder a Athena

1. AWS Console → Athena
2. Seleccionar database: `bus_mvp_db`
3. Configurar resultado: `s3://bus-mvp-datalake/athena-results/`

### Consultas Principales

Ver archivo completo: [docs/analytics/queries_and_views.sql](../docs/analytics/queries_and_views.sql)

#### Consulta 1: Top Pasajeros
```sql
SELECT * FROM top_passengers LIMIT 10;
```

#### Consulta 2: Rutas Populares
```sql
SELECT * FROM popular_routes ORDER BY total_trips DESC;
```

#### Consulta 3: Ventas Diarias
```sql
SELECT * FROM daily_sales_summary ORDER BY sale_date DESC LIMIT 30;
```

#### Consulta 4: Performance de Viajes
```sql
SELECT * FROM trip_performance WHERE performance_rating = 'Excelente';
```

---

## 🎯 Analytics API

### Iniciar Servicio

```bash
docker-compose up -d analytics-service
```

### Endpoints Disponibles

```bash
# Health check
curl http://localhost:5000/health

# Top passengers
curl http://localhost:5000/api/analytics/top-passengers?limit=10

# Popular routes
curl http://localhost:5000/api/analytics/popular-routes

# Daily sales
curl http://localhost:5000/api/analytics/daily-sales?days=30

# Occupancy rate
curl http://localhost:5000/api/analytics/occupancy-rate

# Custom query
curl -X POST http://localhost:5000/api/analytics/custom-query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT COUNT(*) as total FROM passengers"}'
```

---

## 🎨 Integración con Frontend

### Actualizar AnalyticsSection.tsx

```typescript
// En frontend/web-portal/src/services/api.ts
const ANALYTICS_API = 'http://localhost:5000/api/analytics';

export const analyticsService = {
  getTopPassengers: () => axios.get(`${ANALYTICS_API}/top-passengers`),
  getPopularRoutes: () => axios.get(`${ANALYTICS_API}/popular-routes`),
  getDailySales: () => axios.get(`${ANALYTICS_API}/daily-sales`),
  getOccupancyRate: () => axios.get(`${ANALYTICS_API}/occupancy-rate`),
};
```

```typescript
// En AnalyticsSection.tsx
const fetchAnalytics = async () => {
  const data = await analyticsService.getTopPassengers();
  setAnalytics(data);
};
```

---

## 🐛 Troubleshooting

### Error: No puede conectar a microservicios

```bash
# Verificar que estén corriendo
docker ps

# Verificar URLs
cat .env | grep API_URL

# Probar conexión
curl http://localhost:3001/api/passengers
```

### Error: Access Denied S3

```bash
# Verificar credenciales
aws sts get-caller-identity

# Verificar permisos
aws s3 ls s3://bus-mvp-datalake/
```

### Error: Glue Crawler falla

```bash
# Verificar datos en S3
aws s3 ls s3://bus-mvp-datalake/raw/passengers/

# Verificar logs del crawler
aws glue get-crawler --name passengers-crawler
```

### Error: Athena query falla

```bash
# Verificar que las tablas existan
aws glue get-table --database-name bus_mvp_db --name passengers

# Verificar formato de archivos
aws s3 cp s3://bus-mvp-datalake/raw/passengers/passengers_*.csv - | head
```

---

## 📚 Recursos Adicionales

- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)
- [AWS Athena Documentation](https://docs.aws.amazon.com/athena/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

## 📝 Checklist de Implementación

- [ ] Instancia EC2 creada y configurada
- [ ] Docker y Docker Compose instalados
- [ ] Credenciales AWS configuradas
- [ ] Bucket S3 creado con estructura de carpetas
- [ ] Microservicios corriendo
- [ ] Contenedores de ingesta ejecutados exitosamente
- [ ] Datos verificados en S3 (CSV y JSON)
- [ ] AWS Glue database creada
- [ ] Crawlers ejecutados y tablas catalogadas
- [ ] Consultas SQL probadas en Athena
- [ ] Vistas creadas y verificadas
- [ ] Analytics API corriendo
- [ ] Endpoints de API probados
- [ ] Integración con frontend (opcional)
- [ ] Documentación revisada
- [ ] Repositorio GitHub actualizado

---

## 🎓 Conclusión

Este proyecto cumple con todos los requisitos especificados:

1. ✅ MV Ingesta creada en EC2
2. ✅ Bucket S3 con data lake
3. ✅ 3 contenedores Docker para ingesta
4. ✅ Estrategia pull 100%
5. ✅ Archivos CSV y JSON generados
6. ✅ AWS Glue Catalog configurado
7. ✅ Diagrama ER documentado
8. ✅ 6 consultas SQL + 4 vistas en Athena
9. ✅ Repositorio GitHub público

Además, incluye features adicionales como Analytics API REST, automatización completa, y documentación exhaustiva.
