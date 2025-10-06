from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings
from src.core.logging import setup_logging
from src.api.v1.endpoints import health, analytics

# Configurar logging
settings = get_settings()
logger = setup_logging(settings.log_level)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Bus MVP Analytics API
    
    Microservicio de analítica que consume datos de AWS Athena para generar
    insights de negocio sobre pasajeros, viajes, tickets e ingresos.
    
    ### Características principales:
    
    - **Dashboard Summary**: Métricas ejecutivas en tiempo real
    - **Passenger Analytics**: Segmentación y análisis de clientes
    - **Revenue Analytics**: Análisis de ingresos por ruta y estado
    - **Occupancy Analytics**: Niveles de ocupación de buses
    - **Trip Analytics**: Estadísticas de viajes
    
    ### Tecnología:
    
    - **Backend**: FastAPI + Python 3.11
    - **Data Source**: AWS Athena
    - **Storage**: AWS S3 (bus-mvp-datalake-1)
    - **Catalog**: AWS Glue Database
    
    ### Documentación:
    
    - **Swagger UI**: `/docs` (esta página)
    - **ReDoc**: `/redoc` (documentación alternativa)
    - **OpenAPI JSON**: `/openapi.json`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Bus MVP Team",
        "url": "https://github.com/yourusername/bus-mvp",
    },
    license_info={
        "name": "MIT",
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz con información del servicio
    """
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Athena Database: {settings.glue_database}")
    logger.info(f"S3 Output: {settings.athena_output_location}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.app_name}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
