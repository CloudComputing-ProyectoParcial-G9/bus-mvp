"""
Analytics endpoints for business intelligence queries
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Union
from datetime import date, datetime
import structlog

from app.core.config import settings
from app.models.requests import (
    RevenueByRouteRequest, 
    OccupancyTrendsRequest,
    CustomerSegmentationRequest,
    RoutePerformanceRequest
)
from app.models.responses import (
    RevenueByRouteResponse,
    RevenueByRouteData,
    OccupancyTrendsResponse,
    OccupancyTrendsData,
    CustomerSegmentationResponse,
    CustomerSegmentData,
    RoutePerformanceResponse,
    RoutePerformanceData
)
from app.api.deps import get_analytics_service, get_query_builder
from app.services.athena_service import AthenaService
from app.services.mock_service import MockAnalyticsService
from app.queries.query_builder import QueryBuilder

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/revenue-by-route", response_model=RevenueByRouteResponse)
async def get_revenue_by_route(
    date_from: Optional[date] = Query(None, description="Start date for analysis"),
    date_to: Optional[date] = Query(None, description="End date for analysis"),
    route_codes: Optional[str] = Query(None, description="Comma-separated route codes"),
    limit: int = Query(100, description="Maximum number of results", ge=1, le=1000),
    analytics_service: Union[AthenaService, MockAnalyticsService] = Depends(get_analytics_service),
    query_builder: QueryBuilder = Depends(get_query_builder)
) -> RevenueByRouteResponse:
    """
    Get revenue analysis by route and time period
    """
    try:
        # Parse route codes if provided
        route_codes_list = None
        if route_codes:
            route_codes_list = [code.strip() for code in route_codes.split(',')]
        
        # If using AWS Athena, build and execute query
        if settings.is_aws_environment and isinstance(analytics_service, AthenaService):
            sql_query = query_builder.build_revenue_query(
                year_from=date_from.year if date_from else None,
                route_codes=route_codes_list,
                date_from=date_from,
                date_to=date_to,
                limit=limit
            )
            
            execution_id, raw_results = await analytics_service.execute_query(sql_query, limit)
            
            # Transform results to response model
            data = [
                RevenueByRouteData(
                    route_code=row.get('route_code', ''),
                    route_name=row.get('route_name'),
                    origin_city=row.get('origin_city', ''),
                    destination_city=row.get('destination_city', ''),
                    period=row.get('period', ''),
                    total_revenue=float(row.get('total_revenue', 0)),
                    total_tickets=int(row.get('total_tickets', 0)),
                    total_trips=int(row.get('total_trips', 0)),
                    average_price=float(row.get('average_price', 0)),
                    revenue_growth=float(row.get('revenue_growth')) if row.get('revenue_growth') else None
                )
                for row in raw_results
            ]
            
            logger.info("Revenue analysis completed", execution_id=execution_id, result_count=len(data))
            
        else:
            # Using mock service
            _, raw_results = await analytics_service.execute_query("revenue analysis", limit)
            
            data = [
                RevenueByRouteData(**row)
                for row in raw_results[:limit]
            ]
        
        return RevenueByRouteResponse(
            data=data,
            total_records=len(data),
            query_cost_estimate=None  # Could add AWS cost estimation here
        )
        
    except Exception as e:
        logger.error("Revenue analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Revenue analysis failed: {str(e)}"
        )


@router.get("/occupancy-trends", response_model=OccupancyTrendsResponse)
async def get_occupancy_trends(
    date_from: Optional[date] = Query(None, description="Start date for analysis"),
    date_to: Optional[date] = Query(None, description="End date for analysis"),
    route_codes: Optional[str] = Query(None, description="Comma-separated route codes"),
    group_by: str = Query("day_of_week", description="Grouping: day_of_week, hour, month"),
    analytics_service: Union[AthenaService, MockAnalyticsService] = Depends(get_analytics_service),
    query_builder: QueryBuilder = Depends(get_query_builder)
) -> OccupancyTrendsResponse:
    """
    Get occupancy trends analysis grouped by time periods
    """
    try:
        # Parse route codes if provided
        route_codes_list = None
        if route_codes:
            route_codes_list = [code.strip() for code in route_codes.split(',')]
        
        # If using AWS Athena, build and execute query
        if settings.is_aws_environment and isinstance(analytics_service, AthenaService):
            sql_query = query_builder.build_occupancy_query(
                year_from=date_from.year if date_from else None,
                route_codes=route_codes_list,
                date_from=date_from,
                date_to=date_to,
                group_by=group_by
            )
            
            execution_id, raw_results = await analytics_service.execute_query(sql_query)
            
            # Transform results to response model
            data = [
                OccupancyTrendsData(
                    period=str(row.get('period', '')),
                    period_label=row.get('period_label', ''),
                    total_trips=int(row.get('total_trips', 0)),
                    tickets_sold=int(row.get('tickets_sold', 0)),
                    total_capacity=int(row.get('total_capacity', 0)),
                    occupancy_rate=float(row.get('occupancy_rate', 0)),
                    average_occupancy=float(row.get('average_occupancy', 0))
                )
                for row in raw_results
            ]
            
            logger.info("Occupancy analysis completed", execution_id=execution_id, result_count=len(data))
            
        else:
            # Using mock service
            _, raw_results = await analytics_service.execute_query("occupancy analysis")
            
            data = [
                OccupancyTrendsData(**row)
                for row in raw_results
            ]
        
        # Calculate summary statistics
        summary = {
            "total_periods": len(data),
            "avg_occupancy_rate": sum(d.occupancy_rate for d in data) / len(data) if data else 0,
            "peak_period": max(data, key=lambda x: x.occupancy_rate).period_label if data else None,
            "low_period": min(data, key=lambda x: x.occupancy_rate).period_label if data else None
        }
        
        return OccupancyTrendsResponse(
            data=data,
            summary=summary
        )
        
    except Exception as e:
        logger.error("Occupancy analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Occupancy analysis failed: {str(e)}"
        )


@router.get("/customer-segmentation", response_model=CustomerSegmentationResponse)
async def get_customer_segmentation(
    segment_criteria: str = Query("frequency", description="Segmentation criteria: frequency, value, recency"),
    limit: int = Query(100, description="Maximum number of segments", ge=1, le=500),
    analytics_service: Union[AthenaService, MockAnalyticsService] = Depends(get_analytics_service),
    query_builder: QueryBuilder = Depends(get_query_builder)
) -> CustomerSegmentationResponse:
    """
    Get customer segmentation analysis based on various criteria
    """
    try:
        # Validate segment criteria
        valid_criteria = ["frequency", "value", "recency"]
        if segment_criteria not in valid_criteria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid segment_criteria. Must be one of: {valid_criteria}"
            )
        
        # If using AWS Athena, build and execute query
        if settings.is_aws_environment and isinstance(analytics_service, AthenaService):
            sql_query = query_builder.build_customer_segmentation_query(
                segment_criteria=segment_criteria,
                limit=limit
            )
            
            execution_id, raw_results = await analytics_service.execute_query(sql_query, limit)
            
            # Transform results to response model
            data = [
                CustomerSegmentData(
                    segment_id=str(row.get('segment_id', '')),
                    segment_name=row.get('segment_name', ''),
                    customer_count=int(row.get('customer_count', 0)),
                    average_trips=float(row.get('average_trips', 0)),
                    average_revenue=float(row.get('average_revenue', 0)),
                    total_revenue=float(row.get('total_revenue', 0)),
                    percentage=float(row.get('percentage', 0))
                )
                for row in raw_results
            ]
            
            logger.info("Customer segmentation completed", execution_id=execution_id, result_count=len(data))
            
        else:
            # Using mock service
            _, raw_results = await analytics_service.execute_query("customer segmentation", limit)
            
            data = [
                CustomerSegmentData(**row)
                for row in raw_results[:limit]
            ]
        
        return CustomerSegmentationResponse(
            data=data,
            segmentation_criteria=segment_criteria
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Customer segmentation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Customer segmentation failed: {str(e)}"
        )


@router.get("/route-performance", response_model=RoutePerformanceResponse)
async def get_route_performance(
    date_from: Optional[date] = Query(None, description="Start date for analysis"),
    date_to: Optional[date] = Query(None, description="End date for analysis"),
    route_codes: Optional[str] = Query(None, description="Comma-separated route codes"),
    metrics: str = Query("revenue,occupancy,on_time", description="Comma-separated metrics to include"),
    analytics_service: Union[AthenaService, MockAnalyticsService] = Depends(get_analytics_service),
    query_builder: QueryBuilder = Depends(get_query_builder)
) -> RoutePerformanceResponse:
    """
    Get route performance analysis with various metrics
    """
    try:
        # Parse metrics and route codes
        metrics_list = [metric.strip() for metric in metrics.split(',')]
        route_codes_list = None
        if route_codes:
            route_codes_list = [code.strip() for code in route_codes.split(',')]
        
        # Validate metrics
        valid_metrics = ["revenue", "occupancy", "on_time", "cancellation_rate"]
        invalid_metrics = [m for m in metrics_list if m not in valid_metrics]
        if invalid_metrics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid metrics: {invalid_metrics}. Valid metrics: {valid_metrics}"
            )
        
        # If using AWS Athena, build and execute query
        if settings.is_aws_environment and isinstance(analytics_service, AthenaService):
            sql_query = query_builder.build_route_performance_query(
                metrics=metrics_list,
                year_from=date_from.year if date_from else None,
                route_codes=route_codes_list,
                date_from=date_from,
                date_to=date_to
            )
            
            execution_id, raw_results = await analytics_service.execute_query(sql_query)
            
            # Transform results to response model
            data = [
                RoutePerformanceData(
                    route_code=row.get('route_code', ''),
                    route_name=row.get('route_name'),
                    origin_city=row.get('origin_city', ''),
                    destination_city=row.get('destination_city', ''),
                    total_revenue=float(row.get('total_revenue')) if row.get('total_revenue') is not None else None,
                    average_occupancy=float(row.get('average_occupancy')) if row.get('average_occupancy') is not None else None,
                    on_time_performance=float(row.get('on_time_performance')) if row.get('on_time_performance') is not None else None,
                    cancellation_rate=float(row.get('cancellation_rate')) if row.get('cancellation_rate') is not None else None,
                    total_trips=int(row.get('total_trips', 0)),
                    performance_score=float(row.get('performance_score')) if row.get('performance_score') is not None else None
                )
                for row in raw_results
            ]
            
            logger.info("Route performance analysis completed", execution_id=execution_id, result_count=len(data))
            
        else:
            # Using mock service
            _, raw_results = await analytics_service.execute_query("route performance")
            
            data = [
                RoutePerformanceData(**row)
                for row in raw_results
            ]
        
        return RoutePerformanceResponse(
            data=data,
            metrics_included=metrics_list
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Route performance analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route performance analysis failed: {str(e)}"
        )
