"""
MS Analytics - FastAPI Application
Bus MVP Analytics Microservice using AWS Athena
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import structlog

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging

# Setup structured logging
setup_logging()
logger = structlog.get_logger()

# Create FastAPI application
app = FastAPI(
    title="MS Analytics - Bus MVP",
    description="Microservicio de análisis de datos usando AWS Athena",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(
        "MS Analytics starting up",
        environment=settings.environment,
        aws_region=settings.aws_region,
        port=settings.port
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("MS Analytics shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
