from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from src.config import get_settings, Settings
from src.services.athena_service import AthenaService
from src.services.analytics_service import AnalyticsService
from src.models.responses import (
    DashboardSummaryResponse,
    PassengerAnalyticsResponse,
    RevenueAnalyticsResponse,
    OccupancyAnalyticsResponse,
    TripAnalyticsResponse
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_analytics_service(settings: Settings = Depends(get_settings)) -> AnalyticsService:
    """Dependency para obtener AnalyticsService"""
    athena = AthenaService(settings)
    return AnalyticsService(athena)

# ============================================================================
# Dashboard Summary Endpoint
# ============================================================================

@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Dashboard Summary",
    description="Obtiene resumen ejecutivo con métricas principales del negocio"
)
async def get_dashboard_summary(
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    **Resumen del Dashboard**
    
    Retorna métricas clave:
    - Total de pasajeros registrados
    - Viajes activos
    - Tickets vendidos
    - Ingresos totales
    - Ocupación promedio
    - Tasa de cancelación
    
    **Uso:**
    ```
    GET /api/v1/analytics/summary
    ```
    """
    try:
        return await service.get_dashboard_summary()
    except Exception as e:
        logger.error(f"Error in dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Passenger Analytics Endpoint
# ============================================================================

@router.get(
    "/passengers",
    response_model=PassengerAnalyticsResponse,
    summary="Passenger Analytics",
    description="Análisis detallado de pasajeros con segmentación y top customers"
)
async def get_passenger_analytics(
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    **Analítica de Pasajeros**
    
    Incluye:
    - Segmentación de pasajeros (VIP, Frequent, Regular, Occasional)
    - Top 10 clientes por gasto total
    - Pasajeros activos vs totales
    
    **Segmentos:**
    - **VIP**: >10 tickets o >$500 gastados
    - **Frequent**: 6-10 tickets o $301-$500
    - **Regular**: 3-5 tickets o $101-$300
    - **Occasional**: 1-2 tickets o <$100
    
    **Uso:**
    ```
    GET /api/v1/analytics/passengers
    ```
    """
    try:
        return await service.get_passenger_analytics()
    except Exception as e:
        logger.error(f"Error in passenger analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Revenue Analytics Endpoint
# ============================================================================

@router.get(
    "/revenue",
    response_model=RevenueAnalyticsResponse,
    summary="Revenue Analytics",
    description="Análisis de ingresos por ruta y estado de tickets"
)
async def get_revenue_analytics(
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    **Analítica de Ingresos**
    
    Métricas:
    - Ingresos totales (confirmados + cancelados)
    - Desglose por estado (confirmed vs cancelled)
    - Ingresos por ruta
    - Promedio de ingresos por viaje
    
    **Uso:**
    ```
    GET /api/v1/analytics/revenue
    ```
    """
    try:
        return await service.get_revenue_analytics()
    except Exception as e:
        logger.error(f"Error in revenue analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Occupancy Analytics Endpoint
# ============================================================================

@router.get(
    "/occupancy",
    response_model=OccupancyAnalyticsResponse,
    summary="Occupancy Analytics",
    description="Análisis de ocupación de buses por ruta y nivel"
)
async def get_occupancy_analytics(
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    **Analítica de Ocupación**
    
    Incluye:
    - Ocupación promedio general (%)
    - Capacidad total vs asientos vendidos
    - Distribución por nivel de ocupación
    - Ocupación por ruta
    
    **Niveles de Ocupación:**
    - **Full**: >90%
    - **High**: 70-90%
    - **Medium**: 50-70%
    - **Low**: 30-50%
    - **Very Low**: <30%
    
    **Uso:**
    ```
    GET /api/v1/analytics/occupancy
    ```
    """
    try:
        return await service.get_occupancy_analytics()
    except Exception as e:
        logger.error(f"Error in occupancy analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Trip Analytics Endpoint
# ============================================================================

@router.get(
    "/trips",
    response_model=TripAnalyticsResponse,
    summary="Trip Analytics",
    description="Análisis de viajes por estado y ocupación"
)
async def get_trip_analytics(
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    **Analítica de Viajes**
    
    Estadísticas:
    - Total de viajes
    - Viajes por estado (activos, completados, cancelados)
    - Distribución por nivel de ocupación
    
    **Uso:**
    ```
    GET /api/v1/analytics/trips
    ```
    """
    try:
        return await service.get_trip_analytics()
    except Exception as e:
        logger.error(f"Error in trip analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
