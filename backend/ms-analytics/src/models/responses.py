from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

# ============================================================================
# Response Models - Dashboard Summary
# ============================================================================

class SummaryMetrics(BaseModel):
    """Métricas principales del dashboard"""
    total_passengers: int = Field(..., description="Total de pasajeros registrados")
    active_trips: int = Field(..., description="Viajes activos actualmente")
    tickets_sold: int = Field(..., description="Total de tickets vendidos")
    total_revenue: float = Field(..., description="Ingresos totales confirmados")
    average_occupancy: float = Field(..., description="Ocupación promedio de buses (%)")
    cancellation_rate: float = Field(..., description="Tasa de cancelación (%)")

class SummaryTrends(BaseModel):
    """Tendencias de crecimiento"""
    revenue_growth: float = Field(default=0.0, description="Crecimiento de ingresos (%)")
    passenger_growth: float = Field(default=0.0, description="Crecimiento de pasajeros (%)")

class DashboardSummaryResponse(BaseModel):
    """Response completo del dashboard principal"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    summary: SummaryMetrics
    trends: Optional[SummaryTrends] = None

# ============================================================================
# Response Models - Passengers Analytics
# ============================================================================

class TopCustomer(BaseModel):
    """Cliente top"""
    passenger_id: str
    full_name: str
    total_spent: float
    tickets_purchased: int
    segment: str

class PassengerAnalyticsResponse(BaseModel):
    """Analítica de pasajeros"""
    total_passengers: int
    active_passengers: int
    passenger_segments: Dict[str, int] = Field(
        description="Distribución por segmento: VIP, Frequent, Regular, Occasional"
    )
    top_customers: List[TopCustomer]

# ============================================================================
# Response Models - Revenue Analytics
# ============================================================================

class RouteRevenue(BaseModel):
    """Ingresos por ruta"""
    route_id: str
    total_revenue: float
    trips_count: int
    avg_revenue_per_trip: float

class DailyRevenue(BaseModel):
    """Ingresos diarios"""
    date: str
    revenue: float

class RevenueTrend(BaseModel):
    """Tendencia de ingresos"""
    daily: List[DailyRevenue]

class RevenueAnalyticsResponse(BaseModel):
    """Analítica de ingresos"""
    total_revenue: float
    confirmed_revenue: float
    cancelled_revenue: float
    by_route: List[RouteRevenue]
    trend: Optional[RevenueTrend] = None

# ============================================================================
# Response Models - Occupancy Analytics
# ============================================================================

class OccupancyByRoute(BaseModel):
    """Ocupación por ruta"""
    route_id: str
    avg_occupancy: float
    trips_count: int

class OccupancyAnalyticsResponse(BaseModel):
    """Analítica de ocupación"""
    average_occupancy: float
    total_capacity: int
    total_seats_sold: int
    by_level: Dict[str, int] = Field(
        description="Distribución: Full, High, Medium, Low, Very Low"
    )
    by_route: List[OccupancyByRoute]

# ============================================================================
# Response Models - Trips Analytics
# ============================================================================

class TripAnalyticsResponse(BaseModel):
    """Analítica de viajes"""
    total_trips: int
    active_trips: int
    completed_trips: int
    cancelled_trips: int
    occupancy_breakdown: Dict[str, int]

# ============================================================================
# Health Check
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str = "ms-analytics"
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    athena_connection: bool = True
