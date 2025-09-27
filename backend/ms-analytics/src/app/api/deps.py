"""
FastAPI dependencies for dependency injection
"""

from typing import Union
from fastapi import Depends, HTTPException, status
import structlog

from app.core.config import settings
from app.services.athena_service import AthenaService
from app.services.mock_service import MockAnalyticsService
from app.queries.query_builder import QueryBuilder

logger = structlog.get_logger(__name__)


def get_analytics_service() -> Union[AthenaService, MockAnalyticsService]:
    """
    Dependency that returns the appropriate analytics service
    based on the current environment configuration
    """
    if settings.is_aws_environment:
        logger.info("Using AWS Athena service")
        return AthenaService()
    else:
        logger.info("Using mock analytics service")
        return MockAnalyticsService()


def get_query_builder() -> QueryBuilder:
    """Dependency that returns a query builder instance"""
    return QueryBuilder()


async def verify_aws_credentials():
    """
    Dependency to verify AWS credentials are properly configured
    Only used when in AWS environment
    """
    if settings.is_aws_environment:
        if not settings.aws_access_key_id and not settings.aws_profile:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AWS credentials not configured"
            )


async def verify_custom_query_permission():
    """
    Dependency to verify permission for custom queries
    In production, this would check JWT tokens or API keys
    """
    # For now, just check if we're in AWS environment
    # In production, add proper authentication here
    if settings.is_aws_environment:
        # Add authentication logic here
        pass
    
    return True
