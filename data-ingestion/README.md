# Data Ingestion Pipeline - Bus MVP

Pipeline de ingesta de datos para extracción desde microservicios hacia AWS S3.

## ⚡ Inicio Rápido

**Ejecuta todo el proceso con un solo comando:**

```powershell
# Windows
.\setup_aws_academy.ps1  # Primera vez
.\run_all.ps1            # Ejecuta TODO

# Linux/Mac
./setup_aws_academy.sh   # Primera vez
./run_all.sh             # Ejecuta TODO
```

📖 **Guía completa**: [RUN_ALL_GUIDE.md](./RUN_ALL_GUIDE.md)



## 📋 Descripción## 📋 Arquitectura



Este módulo extrae datos de los microservicios de Bus MVP y los carga a AWS S3 para análisis con Athena.```

Microservicios (MySQL, PostgreSQL, MongoDB)

## 🏗️ Arquitectura    ↓

Contenedores de Ingesta (Python)

```    ↓

Microservicios → Ingestion Services → S3 → Glue Catalog → Athena → Analytics APIAWS S3 Bucket (Data Lake)

```    ↓

AWS Glue Catalog

### Componentes:    ↓

AWS Athena (Consultas SQL)

1. **Servicios de Ingesta**: Extraen datos de los microservicios y los cargan a S3```

   - `passengers-ingestion/`: Extrae datos de pasajeros

   - `trips-ingestion/`: Extrae datos de viajes## 🏗️ Estructura del Proyecto

   - `tickets-ingestion/`: Extrae datos de tickets

```

2. **AWS S3**: Data Lake para almacenar datos en formato CSV y JSONdata-ingestion/

   - `raw/passengers_csv/`: Datos de pasajeros en CSV├── passengers-ingestion/     # Ingesta desde ms-passengers (Python/Flask)

   - `raw/trips_csv/`: Datos de viajes en CSV├── trips-ingestion/          # Ingesta desde ms-trips (Node.js/PostgreSQL)

   - `raw/tickets_csv/`: Datos de tickets en CSV├── tickets-ingestion/        # Ingesta desde ms-tickets (Java/MongoDB)

├── analytics-service/        # API REST para consultas analíticas

3. **AWS Glue**: Catálogo de datos├── docker-compose.yml        # Orquestación de contenedores

   - Database: `bus_mvp_db`├── .env.example             # Variables de entorno

   - Tablas: `passengers`, `trips`, `tickets`└── scripts/                 # Scripts de utilidad

```

4. **AWS Athena**: Motor de consultas SQL sobre S3

## 🔧 Prerequisitos

5. **Analytics Service**: API REST para consultas analíticas

1. **AWS Account** con permisos para:

## 🚀 Quick Start   - S3

   - Glue

### Prerequisitos   - Athena

   - EC2 (opcional para MV)

- Docker & Docker Compose   

- AWS CLI   📚 **Para AWS Academy Lab**: Ver [AWS_ACADEMY_SETUP.md](./AWS_ACADEMY_SETUP.md)

- Python 3.8+

- Cuenta AWS Academy Lab (con credenciales temporales)2. **Docker & Docker Compose** instalado



### Paso 1: Configurar credenciales de AWS3. **Microservicios corriendo**:

   - ms-passengers: http://localhost:3001

**Windows:**   - ms-trips: http://localhost:3002

```powershell   - ms-tickets: http://localhost:3003

.\setup_aws_academy.ps1

```## 🚀 Quick Start



**Linux/Mac:**### 1. Configurar variables de entorno

```bash

./setup_aws_academy.sh```bash

```cp .env.example .env

# Editar .env con tus credenciales AWS

Este script:```

- ✅ Solicita tus credenciales de AWS Academy

- ✅ Las guarda en `.env`**Para AWS Academy Lab**: Las credenciales incluyen `AWS_SESSION_TOKEN` (ver [AWS_ACADEMY_SETUP.md](./AWS_ACADEMY_SETUP.md))

- ✅ Valida que funcionen correctamente

- ✅ Obtiene automáticamente tu Account ID### 2. Crear bucket S3



### Paso 2: Crear infraestructura en AWS```bash

aws s3 mb s3://bus-mvp-datalake-1 --region us-east-1

```bash

# Instalar dependencias Python# Crear estructura de carpetas

pip install -r scripts/requirements.txtaws s3api put-object --bucket bus-mvp-datalake-1 --key raw/passengers/

aws s3api put-object --bucket bus-mvp-datalake-1 --key raw/trips/

# Crear bucket S3aws s3api put-object --bucket bus-mvp-datalake-1 --key raw/tickets/

python scripts/setup_s3.pyaws s3api put-object --bucket bus-mvp-datalake-1 --key athena-results/

```

# Crear base de datos y tablas en Glue/Athena

python scripts/setup_glue.py### 3. Ejecutar ingesta

python scripts/create_athena_tables.py

``````bash

# Construir contenedores

### Paso 3: Ejecutar ingesta de datosdocker-compose build



```bash# Ejecutar ingesta de todos los microservicios

# Iniciar servicios de ingestadocker-compose up

docker-compose up

# O ejecutar individualmente

# Los datos se cargarán automáticamente a S3docker-compose up passengers-ingestion

```docker-compose up trips-ingestion

docker-compose up tickets-ingestion

### Paso 4: Verificar datos en Athena```



```bash### 4. Verificar datos en S3

# Ejecutar consultas de prueba

python scripts/test_athena_queries.py```bash

aws s3 ls s3://bus-mvp-datalake-1/raw/ --recursive

# Ver estado de crawlers```

python scripts/check_crawlers.py

```## 📊 AWS Glue Setup



## 📊 Estructura de Datos### Crear Database



### Tabla: passengers```bash

```sqlaws glue create-database \

- full_name: STRING    --database-input '{"Name": "bus_mvp_db", "Description": "Bus MVP Analytics Database"}'

- phone: STRING```

- passenger_id: STRING

- document_number: STRING### Crear Crawlers

- registration_date: STRING

- email: STRING```bash

- document_type: STRING# Passengers Crawler

- date_of_birth: STRINGaws glue create-crawler \

- status: STRING    --name passengers-crawler \

- ingestion_timestamp: STRING    --role AWSGlueServiceRole \

```    --database-name bus_mvp_db \

    --targets '{"S3Targets": [{"Path": "s3://bus-mvp-datalake-1/raw/passengers/"}]}'

### Tabla: trips

```sql# Trips Crawler

- tripId: STRINGaws glue create-crawler \

- routeId: STRING    --name trips-crawler \

- departureDateTime: STRING    --role AWSGlueServiceRole \

- arrivalDateTime: STRING    --database-name bus_mvp_db \

- busCapacity: INT    --targets '{"S3Targets": [{"Path": "s3://bus-mvp-datalake-1/raw/trips/"}]}'

- availableSeats: INT

- finalPrice: DOUBLE# Tickets Crawler

- status: STRINGaws glue create-crawler \

- driverName: STRING    --name tickets-crawler \

- busPlate: STRING    --role AWSGlueServiceRole \

- createdAt: STRING    --database-name bus_mvp_db \

- updatedAt: STRING    --targets '{"S3Targets": [{"Path": "s3://bus-mvp-datalake-1/raw/tickets/"}]}'

- ingestion_timestamp: STRING```

```

### Ejecutar Crawlers

### Tabla: tickets

```sql```bash

- ticket_id: STRINGaws glue start-crawler --name passengers-crawler

- passenger_id: STRINGaws glue start-crawler --name trips-crawler

- trip_id: STRINGaws glue start-crawler --name tickets-crawler

- seat_number: STRING```

- total_price: DOUBLE

- currency: STRING## 🔍 AWS Athena Queries

- booking_status: STRING

- ingestion_timestamp: STRINGLas consultas SQL están en: `docs/analytics/queries_and_views.sql`

```

## 📈 Analytics API

## 🔍 Consultas de Ejemplo

```bash

```sql# Iniciar servicio de analytics

-- Total de pasajeroscd analytics-service

SELECT COUNT(*) as total_passengers FROM passengers;docker build -t analytics-api .

docker run -p 5000:5000 analytics-api

-- Ingresos totales```

SELECT SUM(total_price) as total_revenue FROM tickets;

Endpoints disponibles:

-- Top viajes con más tickets- `GET /api/analytics/top-passengers`

SELECT trip_id, COUNT(*) as total_tickets - `GET /api/analytics/popular-routes`

FROM tickets - `GET /api/analytics/daily-sales`

GROUP BY trip_id - `GET /api/analytics/occupancy-rate`

ORDER BY total_tickets DESC 

LIMIT 5;## 🔄 Automatización (Opcional)

```

### Cronjob para ingesta periódica

## 🔧 Scripts Disponibles

```bash

### `/scripts/`# Ejecutar ingesta cada hora

0 * * * * cd /path/to/data-ingestion && docker-compose up

- **setup_s3.py**: Crea el bucket S3 y la estructura de carpetas```

- **setup_glue.py**: Crea la base de datos en Glue y los crawlers

- **create_athena_tables.py**: Crea las tablas en Athena con esquema correcto## 📝 Notas

- **test_athena_queries.py**: Ejecuta consultas de prueba

- **check_crawlers.py**: Verifica el estado de los crawlers- Los archivos se generan en formato CSV y JSON

- Cada ejecución crea un nuevo archivo con timestamp

## 🌐 Analytics API- Los crawlers de Glue detectan automáticamente el esquema



Una vez que los datos estén en Athena, puedes iniciar el servicio de Analytics:## 🐛 Troubleshooting



```bash### Error: No se puede conectar a microservicios

docker-compose up analytics-service- Verificar que los servicios estén corriendo

```- Verificar URLs en variables de entorno



Endpoints disponibles:### Error: Access Denied S3

- `GET /` - Información del servicio- Verificar credenciales AWS en .env

- `GET /api/analytics/summary` - Resumen general- Verificar IAM role/user tiene permisos S3

- `POST /api/analytics/custom-query` - Query personalizada

### Error: Glue Crawler falla

## ⚙️ Configuración- Verificar que el bucket S3 tenga datos

- Verificar formato de archivos (CSV/JSON)

Las variables de entorno se configuran en `.env`:

## 📚 Referencias

```properties

# AWS Credentials- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)

AWS_ACCESS_KEY_ID=...- [AWS Athena Documentation](https://docs.aws.amazon.com/athena/)

AWS_SECRET_ACCESS_KEY=...- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

AWS_SESSION_TOKEN=...
AWS_DEFAULT_REGION=us-east-1
AWS_ACCOUNT_ID=...

# S3 Configuration
S3_BUCKET=bus-mvp-datalake

# Microservices URLs
PASSENGERS_API_URL=http://host.docker.internal:8001/api/v1
TRIPS_API_URL=http://host.docker.internal:8002/api/v1
TICKETS_API_URL=http://host.docker.internal:8003

# Glue Configuration
GLUE_DATABASE=bus_mvp_db

# Athena Configuration
ATHENA_OUTPUT_LOCATION=s3://bus-mvp-datalake-1/athena-results/
```

## ⚠️ Importante

- Las credenciales de AWS Academy **expiran en 4 horas**
- Debes ejecutar `setup_aws_academy.ps1` nuevamente cuando expiren
- Los datos en S3 persisten entre sesiones

## 📝 Notas Técnicas

### Separación de archivos CSV y JSON

Los archivos CSV y JSON se almacenan en carpetas separadas para evitar conflictos:
- CSV: `raw/passengers_csv/`, `raw/trips_csv/`, `raw/tickets_csv/`
- JSON: `raw/passengers_json/`, `raw/trips_json/`, `raw/tickets_json/`

Las tablas de Athena solo leen de las carpetas `_csv` para garantizar datos limpios.

### Actualización de datos

Para actualizar los datos:
1. Ejecuta `docker-compose up` nuevamente
2. Los nuevos archivos se crearán con timestamp
3. Athena leerá automáticamente todos los archivos CSV en el directorio

## 🆘 Troubleshooting

**Error: "Unable to locate credentials"**
- Solución: Ejecuta `setup_aws_academy.ps1` para configurar credenciales

**Error: "Bucket already exists"**
- Solución: El bucket ya fue creado. Continúa con el siguiente paso.

**Error: "Query timeout"**
- Solución: Athena puede tardar en la primera consulta. Intenta nuevamente.

**Datos incorrectos en Athena**
- Solución: Verifica que las tablas apunten a carpetas `_csv` y no mezclen con JSON

## 📚 Documentación Adicional

- [AWS Academy Setup](./QUICKSTART_AWS_ACADEMY.md)
- [Guía de Implementación](./IMPLEMENTATION_GUIDE.md)
- [Guía de Testing](./TESTING_GUIDE.md)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es parte del curso de Cloud Computing - UTEC.
