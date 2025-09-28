"""
Custom query endpoint for advanced SQL queries
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Union, List, Dict, Any
import time
import structlog

from app.core.config import settings
from app.models.requests import CustomQueryRequest
from app.models.responses import CustomQueryResponse
from app.api.deps import get_analytics_service, get_query_builder, verify_custom_query_permission
from app.services.athena_service import AthenaService
from app.services.mock_service import MockAnalyticsService
from app.queries.query_builder import QueryBuilder

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/custom", response_model=CustomQueryResponse)
async def execute_custom_query(
    request: CustomQueryRequest,
    analytics_service: Union[AthenaService, MockAnalyticsService] = Depends(get_analytics_service),
    query_builder: QueryBuilder = Depends(get_query_builder),
    _: bool = Depends(verify_custom_query_permission)
) -> CustomQueryResponse:
    """
    Execute a custom SQL query against the analytics data
    
    **Security Note**: This endpoint validates queries to prevent harmful operations
    and is only available in AWS environment with proper authentication.
    """
    try:
        start_time = time.time()
        
        # Validate query for security
        if not query_builder.validate_custom_query(request.sql_query):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid SQL query. Query must be SELECT-only and reference allowed tables."
            )
        
        # Log custom query execution (for audit)
        logger.info(
            "Executing custom query",
            query_preview=request.sql_query[:100],
            max_results=request.max_results,
            timeout_seconds=request.timeout_seconds
        )
        
        # If using AWS Athena
        if settings.is_aws_environment and isinstance(analytics_service, AthenaService):
            execution_id, raw_results = await analytics_service.execute_query(
                request.sql_query,
                request.max_results
            )
            
            # Extract column names from first result if any
            columns = list(raw_results[0].keys()) if raw_results else []
            
            logger.info(
                "Custom query executed successfully",
                execution_id=execution_id,
                result_count=len(raw_results),
                columns=columns
            )
            
        else:
            # Mock service for local development
            if settings.is_local_environment:
                logger.warning("Custom queries not fully supported in local mode")
                # Return sample data for local testing
                raw_results = [
                    {"query_result": "Sample result for custom query"},
                    {"note": "This is mock data for local development"}
                ]
                columns = ["query_result", "note"]
                execution_id = "mock-custom-query"
            else:
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Custom queries are only available in AWS environment"
                )
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return CustomQueryResponse(
            data=raw_results,
            columns=columns,
            row_count=len(raw_results),
            execution_time_ms=execution_time,
            query_cost_estimate=None  # Could add AWS cost estimation here
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Custom query execution failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )


@router.get("/tables")
async def list_available_tables(
    analytics_service: Union[AthenaService, MockAnalyticsService] = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    List available tables in the data catalog for custom queries
    """
    try:
        if settings.is_aws_environment and isinstance(analytics_service, AthenaService):
            # In a real implementation, this would query Glue catalog
            # For now, return static table information
            tables = [
                {
                    "name": f"{settings.aws_glue_table_prefix}trips_raw",
                    "description": "Raw trip data with routes and schedules",
                    "columns": ["trip_id", "route_code", "origin_city", "destination_city", "departure_time", "bus_capacity"]
                },
                {
                    "name": f"{settings.aws_glue_table_prefix}tickets_raw", 
                    "description": "Raw ticket booking data",
                    "columns": ["ticket_id", "trip_id", "passenger_id", "booking_date", "total_price", "booking_status"]
                },
                {
                    "name": f"{settings.aws_glue_table_prefix}passengers_raw",
                    "description": "Passenger information",
                    "columns": ["passenger_id", "email", "first_name", "last_name", "registration_date"]
                }
            ]
        else:
            # Mock tables for local development
            tables = [
                {
                    "name": "mock_trips",
                    "description": "Mock trip data for local development",
                    "columns": ["trip_id", "route_code", "origin_city", "destination_city"]
                },
                {
                    "name": "mock_tickets",
                    "description": "Mock ticket data for local development", 
                    "columns": ["ticket_id", "trip_id", "price", "status"]
                }
            ]
        
        return {
            "database": settings.aws_glue_catalog_database,
            "tables": tables,
            "total_tables": len(tables)
        }
        
    except Exception as e:
        logger.error("Failed to list tables", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list available tables: {str(e)}"
        )
