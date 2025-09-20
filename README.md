# Bus MVP - Sistema de Gestión de Autobuses

## Resumen del Proyecto

Este MVP (Minimum Viable Product) implementa un sistema distribuido para la gestión de servicios de autobuses, diseñado como un proyecto de Cloud Computing que demuestra la implementación de microservicios, ingesta de datos y análisis en la nube.

## Objetivos del MVP

- Demostrar arquitectura de microservicios escalable
- Implementar ingesta y análisis de datos en tiempo real
- Crear una aplicación web moderna que consuma múltiples servicios
- Configurar infraestructura reproducible con Docker y CI/CD

## Requisitos del Curso - Checklist de Cumplimiento

### Microservicios
- [ ] 5 microservicios dockerizados
- [ ] 3 MS con DB, 3 lenguajes distintos, 3 DB (2 SQL + 1 NoSQL)
- [ ] 1 MS sin DB que consuma a otros (agregador)
- [ ] 1 MS analítico (mock local + documentación nube)

### Frontend
- [ ] Frontend consume los 5 MS (≥2 endpoints por MS)

### Data Science / Ingesta
- [ ] 3 contenedores de ingesta → almacenamiento de objetos
- [ ] Catálogo de datos documentado
- [ ] ≥4 consultas SQL + ≥2 vistas (archivo .sql)

### Infraestructura
- [ ] Swagger/OpenAPI en los 5 MS
- [ ] Docker Compose + Load Balancer
- [ ] Evidencia para exposición/informe

## División del Equipo y Ownership

- **@B1** – Backend Developer 1 (ms-passengers, ms-history) Joel
- **@B2** – Backend Developer 2 (ms-trips, ms-tickets) Leonardo
- **@A** – Analytics & Data Science (data-ingestion/, ms-analytics, docs/analytics/) Luis
- **@F** – Frontend Developer (frontend/web-portal) Karolay
- **@DevOps** – Project Manager (infra/) Nayeli

## Arquitectura de Microservicios

### Backend Services
1. **ms-passengers** - Gestión de pasajeros (con DB)
2. **ms-trips** - Gestión de viajes y rutas (con DB)  
3. **ms-tickets** - Gestión de boletos y reservas (con DB)
4. **ms-history** - Agregador de historial (sin DB, consume otros MS)
5. **ms-analytics** - Servicio analítico (consultas sobre datos almacenados)

### Base de Datos
- **2 Bases SQL**: Para `ms-passengers`, `ms-trips` o `ms-tickets` (motores a definir)
- **1 Base NoSQL**: Para uno de los microservicios con DB (motor a definir)

### Frontend
- **web-portal**: SPA que consume los 5 microservicios (framework a definir)

### Data Ingestion
- **3 contenedores de ingesta**: Extraen datos de las 3 DB y los depositan en almacenamiento de objetos

## Inicio Rápido (Entorno Local)

### Prerequisitos
- Docker y Docker Compose
- Git

### Pasos

1. **Configurar variables de entorno**:
```bash
cp infra/.env.example infra/.env
# Editar infra/.env con las configuraciones apropiadas
```

2. **Levantar servicios**:
```bash
cd infra
docker compose up -d --build
```

3. **Verificar servicios**:

**Microservicios (Swagger/OpenAPI):**
- ms-passengers: http://localhost:8001/docs
- ms-trips: http://localhost:8002/docs
- ms-tickets: http://localhost:8003/docs
- ms-history: http://localhost:8004/docs
- ms-analytics: http://localhost:8010/docs

**Load Balancer:**
- lb: http://localhost:8088/

**Frontend:**
- Seguir instrucciones específicas en `frontend/web-portal/README.md`
- Instalar dependencias según el framework elegido
- Ejecutar servidor de desarrollo (típicamente en puerto 5173)

## Estructura del Proyecto

```
bus-mvp/
├── README.md
├── docs/
│   ├── arquitectura.drawio              # Diagrama de arquitectura
│   ├── er-diagrams/
│   │   ├── sql_db1.er.md               # ER para primera DB SQL
│   │   └── sql_db2.er.md               # ER para segunda DB SQL
│   └── analytics/
│       ├── catalog_design.md           # Diseño del catálogo de datos
│       └── queries_and_views.sql       # Consultas y vistas de ejemplo
├── infra/
│   ├── docker-compose.yml             # Orquestación de servicios
│   ├── .env.example                   # Variables de entorno template
│   └── lb/
│       └── default.conf               # Configuración del load balancer
├── frontend/
│   └── web-portal/                     # SPA (framework a definir)
├── backend/
│   ├── ms-passengers/                  # Microservicio de pasajeros
│   ├── ms-trips/                       # Microservicio de viajes
│   ├── ms-tickets/                     # Microservicio de boletos
│   ├── ms-history/                     # Microservicio agregador
│   └── ms-analytics/                   # Microservicio analítico
├── data-ingestion/
│   ├── ingest_sql_db1/                # Ingesta desde primera DB SQL
│   ├── ingest_sql_db2/                # Ingesta desde segunda DB SQL
│   └── ingest_nosql/                  # Ingesta desde DB NoSQL
└── .github/
    ├── workflows/                      # CI/CD pipelines
    ├── PULL_REQUEST_TEMPLATE.md
    └── ISSUE_TEMPLATE/
        ├── bug.md
        └── feature.md
```

## Definition of Done

### Microservicio listo
- [ ] OpenAPI actualizado y accesible
- [ ] Endpoints responden localmente (mock si es necesario)
- [ ] Variables de entorno documentadas
- [ ] Ejemplo de request/response disponible

### MS con Base de Datos
- [ ] Esquema de DB documentado
- [ ] Seed de datos reproducible
- [ ] Conexión a DB configurada

### Ingesta
- [ ] Script ejecutable localmente
- [ ] Conexión a destino de almacenamiento configurada
- [ ] Logging de filas exportadas implementado

### Analítico
- [ ] Endpoints devuelven mock local
- [ ] Documentación clara para ejecución en nube
- [ ] Variables de nube documentadas

### Frontend
- [ ] Consume al menos 2 endpoints por cada MS
- [ ] Interfaz básica funcional
- [ ] Manejo de errores implementado

### CI/CD
- [ ] Pipeline básico configurado
- [ ] Linting y build automatizados
- [ ] Tests unitarios (cuando aplique)

## Tecnologías a Definir

Este proyecto está diseñado para ser agnóstico de tecnologías específicas. Cada equipo debe elegir:

### Backend
- **Lenguajes**: 3 diferentes para los MS con DB (ej: Node.js, Python, Java/Go)
- **Frameworks**: Express, FastAPI, Spring Boot, etc.
- **Bases de Datos**: 2 SQL (MySQL, PostgreSQL) + 1 NoSQL (MongoDB, Redis)

### Frontend
- **Framework**: React, Vue, Angular, Svelte, etc.
- **Estado**: Redux, Vuex, Context API, etc.

### Cloud Provider
- **AWS**: S3, Glue, Athena
- **GCP**: Cloud Storage, Data Catalog, BigQuery
- **Azure**: Blob Storage, Data Factory, Synapse

## Contribución

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guidelines de desarrollo.

## Seguridad

Ver [SECURITY.md](SECURITY.md) para políticas de seguridad.

## Licencia

[Especificar licencia]