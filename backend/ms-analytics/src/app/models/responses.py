"""
Response models for analytics endpoints
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


class BaseAnalyticsResponse(BaseModel):
    """Base response model for analytics"""
    success: bool = Field(True, description="Request success status")
    message: str = Field("Success", description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status: healthy, degraded, unhealthy")
    environment: str = Field(..., description="Current environment")
    services: Dict[str, str] = Field(..., description="Status of dependent services")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RevenueByRouteData(BaseModel):
    """Revenue by route data model"""
    route_code: str = Field(..., description="Route identifier")
    route_name: Optional[str] = Field(None, description="Human-readable route name")
    origin_city: str = Field(..., description="Origin city")
    destination_city: str = Field(..., description="Destination city")
    period: str = Field(..., description="Time period (e.g., 2024-01, 2024-01-15)")
    total_revenue: float = Field(..., description="Total revenue in currency units")
    total_tickets: int = Field(..., description="Total number of tickets sold")
    total_trips: int = Field(..., description="Total number of trips")
    average_price: float = Field(..., description="Average ticket price")
    revenue_growth: Optional[float] = Field(None, description="Revenue growth percentage")


class RevenueByRouteResponse(BaseAnalyticsResponse):
    """Revenue by route response model"""
    data: List[RevenueByRouteData] = Field(..., description="Revenue analysis results")
    total_records: int = Field(..., description="Total number of records")
    query_cost_estimate: Optional[str] = Field(None, description="Estimated query cost")


class OccupancyTrendsData(BaseModel):
    """Occupancy trends data model"""
    period: str = Field(..., description="Time period identifier")
    period_label: str = Field(..., description="Human-readable period label")
    total_trips: int = Field(..., description="Total trips in period")
    tickets_sold: int = Field(..., description="Total tickets sold")
    total_capacity: int = Field(..., description="Total capacity available")
    occupancy_rate: float = Field(..., description="Occupancy rate percentage")
    average_occupancy: float = Field(..., description="Average occupancy per trip")


class OccupancyTrendsResponse(BaseAnalyticsResponse):
    """Occupancy trends response model"""
    data: List[OccupancyTrendsData] = Field(..., description="Occupancy trends results")
    summary: Dict[str, Any] = Field(..., description="Summary statistics")


class CustomerSegmentData(BaseModel):
    """Customer segmentation data model"""
    segment_id: str = Field(..., description="Segment identifier")
    segment_name: str = Field(..., description="Segment name")
    customer_count: int = Field(..., description="Number of customers in segment")
    average_trips: float = Field(..., description="Average trips per customer")
    average_revenue: float = Field(..., description="Average revenue per customer")
    total_revenue: float = Field(..., description="Total segment revenue")
    percentage: float = Field(..., description="Percentage of total customers")


class CustomerSegmentationResponse(BaseAnalyticsResponse):
    """Customer segmentation response model"""
    data: List[CustomerSegmentData] = Field(..., description="Customer segmentation results")
    segmentation_criteria: str = Field(..., description="Criteria used for segmentation")


class RoutePerformanceData(BaseModel):
    """Route performance data model"""
    route_code: str = Field(..., description="Route identifier")
    route_name: Optional[str] = Field(None, description="Route name")
    origin_city: str = Field(..., description="Origin city")
    destination_city: str = Field(..., description="Destination city")
    total_revenue: Optional[float] = Field(None, description="Total revenue")
    average_occupancy: Optional[float] = Field(None, description="Average occupancy rate")
    on_time_performance: Optional[float] = Field(None, description="On-time performance percentage")
    cancellation_rate: Optional[float] = Field(None, description="Cancellation rate percentage")
    total_trips: int = Field(..., description="Total number of trips")
    performance_score: Optional[float] = Field(None, description="Overall performance score")


class RoutePerformanceResponse(BaseAnalyticsResponse):
    """Route performance response model"""
    data: List[RoutePerformanceData] = Field(..., description="Route performance results")
    metrics_included: List[str] = Field(..., description="Metrics included in analysis")


class CustomQueryResponse(BaseAnalyticsResponse):
    """Custom query response model"""
    data: List[Dict[str, Any]] = Field(..., description="Query results")
    columns: List[str] = Field(..., description="Column names")
    row_count: int = Field(..., description="Number of rows returned")
    execution_time_ms: Optional[int] = Field(None, description="Query execution time in milliseconds")
    query_cost_estimate: Optional[str] = Field(None, description="Estimated query cost")
