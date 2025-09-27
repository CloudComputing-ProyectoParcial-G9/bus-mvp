"""
Request models for analytics endpoints
"""

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, validator


class DateRangeRequest(BaseModel):
    """Base model for date range requests"""
    date_from: Optional[date] = Field(None, description="Start date for analysis")
    date_to: Optional[date] = Field(None, description="End date for analysis")
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        if v and values.get('date_from') and v < values['date_from']:
            raise ValueError('date_to must be greater than or equal to date_from')
        return v


class RevenueByRouteRequest(DateRangeRequest):
    """Request model for revenue by route analysis"""
    route_codes: Optional[List[str]] = Field(None, description="Specific route codes to analyze")
    limit: int = Field(100, description="Maximum number of results", ge=1, le=1000)
    group_by: str = Field("route", description="Grouping criteria: route, day, month")


class OccupancyTrendsRequest(DateRangeRequest):
    """Request model for occupancy trends analysis"""
    group_by: str = Field("day_of_week", description="Grouping: day_of_week, hour, month")
    route_codes: Optional[List[str]] = Field(None, description="Specific route codes to analyze")


class CustomerSegmentationRequest(BaseModel):
    """Request model for customer segmentation analysis"""
    segment_criteria: str = Field("frequency", description="Segmentation criteria: frequency, value, recency")
    limit: int = Field(100, description="Maximum number of segments", ge=1, le=500)


class RoutePerformanceRequest(DateRangeRequest):
    """Request model for route performance analysis"""
    metrics: List[str] = Field(
        ["revenue", "occupancy", "on_time"], 
        description="Metrics to include: revenue, occupancy, on_time, cancellation_rate"
    )
    route_codes: Optional[List[str]] = Field(None, description="Specific route codes to analyze")


class CustomQueryRequest(BaseModel):
    """Request model for custom SQL queries"""
    sql_query: str = Field(..., description="Custom SQL query", min_length=10)
    max_results: int = Field(1000, description="Maximum results to return", ge=1, le=10000)
    timeout_seconds: int = Field(300, description="Query timeout in seconds", ge=30, le=600)
    
    @validator('sql_query')
    def validate_sql_query(cls, v):
        # Basic SQL injection prevention
        forbidden_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 'TRUNCATE']
        upper_query = v.upper()
        for keyword in forbidden_keywords:
            if keyword in upper_query:
                raise ValueError(f'SQL query contains forbidden keyword: {keyword}')
        return v
