"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict, Any
import structlog

from app.core.config import settings
from app.models.responses import HealthResponse
from app.api.deps import get_analytics_service
from app.utils.aws_helpers import AWSHealthChecker

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check(
    analytics_service=Depends(get_analytics_service)
) -> HealthResponse:
    """
    Health check endpoint that verifies service and dependencies status
    """
    services = {}
    overall_status = "healthy"
    
    try:
        # Check analytics service (AWS or Mock)
        service_health = await analytics_service.health_check()
        services["analytics"] = service_health["status"]
        
        if service_health["status"] != "healthy":
            overall_status = "degraded"
        
        # If using AWS, check individual services
        if settings.is_aws_environment:
            try:
                # Check AWS services
                s3_health = await AWSHealthChecker.check_s3_health()
                services["s3"] = s3_health["status"]
                
                glue_health = await AWSHealthChecker.check_glue_health()
                services["glue"] = glue_health["status"]
                
                athena_health = await AWSHealthChecker.check_athena_health()
                services["athena"] = athena_health["status"]
                
                # Determine overall status
                unhealthy_services = [status for status in services.values() if status == "unhealthy"]
                if unhealthy_services:
                    overall_status = "unhealthy"
                elif "degraded" in services.values():
                    overall_status = "degraded"
                    
            except Exception as e:
                logger.error("Error checking AWS services", error=str(e))
                services["aws"] = "unhealthy"
                overall_status = "unhealthy"
        
        logger.info("Health check completed", status=overall_status, services=services)
        
        return HealthResponse(
            status=overall_status,
            environment=settings.environment,
            services=services
        )
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return HealthResponse(
            status="unhealthy",
            environment=settings.environment,
            services={"error": str(e)}
        )


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Kubernetes readiness probe endpoint
    """
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment
    }


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes liveness probe endpoint
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "app": settings.app_name
    }
