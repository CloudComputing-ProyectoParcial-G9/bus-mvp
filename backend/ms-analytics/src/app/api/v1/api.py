"""
Main API router combining all endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, analytics, custom_query

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(custom_query.router, prefix="/query", tags=["custom-queries"])
