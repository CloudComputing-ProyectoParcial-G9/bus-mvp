from fastapi import APIRouter, Depends
from src.models.responses import HealthCheckResponse
from src.config import get_settings, Settings
from src.services.athena_service import AthenaService

router = APIRouter(tags=["Health"])

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Verifica el estado del servicio y la conexión con Athena"
)
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Endpoint de health check
    
    Returns:
        HealthCheckResponse con estado del servicio
    """
    # Test Athena connection
    athena = AthenaService(settings)
    athena_ok = await athena.test_connection()
    
    return HealthCheckResponse(
        status="healthy" if athena_ok else "degraded",
        service="ms-analytics",
        version=settings.app_version,
        athena_connection=athena_ok
    )
