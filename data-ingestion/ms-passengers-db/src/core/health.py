"""
Health Check Server for MS-Passengers Database Ingestion
FastAPI-based health check endpoint
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import Settings
from utils.logger import get_logger


class HealthCheckServer:
    """Health check HTTP server"""
    
    def __init__(
        self, 
        port: int,
        db_manager,
        ingestion_service
    ):
        self.port = port
        self.db_manager = db_manager
        self.ingestion_service = ingestion_service
        self.logger = get_logger(self.__class__.__name__)
        
        # FastAPI app
        self.app = FastAPI(
            title="MS-Passengers DB Ingestion Health Check",
            description="Health monitoring for PostgreSQL data ingestion service",
            version="1.0.0"
        )
        
        # Setup routes
        self._setup_routes()
        
        # Server instance
        self._server = None
    
    def _setup_routes(self):
        """Setup health check routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Main health check endpoint"""
            try:
                health_data = await self._get_health_data()
                
                if health_data["status"] == "healthy":
                    return JSONResponse(
                        content=health_data,
                        status_code=status.HTTP_200_OK
                    )
                else:
                    return JSONResponse(
                        content=health_data,
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE
                    )
                    
            except Exception as e:
                self.logger.error(f"Health check failed: {str(e)}", exc_info=True)
                return JSONResponse(
                    content={
                        "status": "unhealthy",
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        
        @self.app.get("/health/ready")
        async def readiness_check():
            """Readiness probe"""
            try:
                # Check if all components are ready
                db_health = await self.db_manager.health_check()
                ingestion_status = await self.ingestion_service.get_status()
                
                ready = (
                    db_health["status"] == "healthy" and
                    ingestion_status["status"] in ["running", "idle"]
                )
                
                if ready:
                    return JSONResponse(
                        content={"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()},
                        status_code=status.HTTP_200_OK
                    )
                else:
                    return JSONResponse(
                        content={
                            "status": "not_ready",
                            "database": db_health,
                            "ingestion": ingestion_status,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        },
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE
                    )
                    
            except Exception as e:
                return JSONResponse(
                    content={
                        "status": "not_ready",
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        
        @self.app.get("/health/live")
        async def liveness_check():
            """Liveness probe"""
            return JSONResponse(
                content={"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()},
                status_code=status.HTTP_200_OK
            )
        
        @self.app.get("/metrics")
        async def metrics():
            """Basic metrics endpoint"""
            try:
                metrics_data = await self._get_metrics_data()
                return JSONResponse(content=metrics_data)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )
        
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "service": "ms-passengers-db-ingestion",
                "version": "1.0.0",
                "status": "running",
                "endpoints": {
                    "health": "/health",
                    "ready": "/health/ready",
                    "live": "/health/live",
                    "metrics": "/metrics"
                }
            }
    
    async def _get_health_data(self) -> Dict[str, Any]:
        """Collect comprehensive health data"""
        try:
            # Database health
            db_health = await self.db_manager.health_check()
            
            # Ingestion service status
            ingestion_status = await self.ingestion_service.get_status()
            
            # System health
            system_health = self._get_system_health()
            
            # Overall status
            overall_status = "healthy"
            if (db_health["status"] != "healthy" or 
                ingestion_status["status"] == "error" or
                system_health["status"] != "healthy"):
                overall_status = "unhealthy"
            
            return {
                "status": overall_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "ms-passengers-db-ingestion",
                "version": "1.0.0",
                "components": {
                    "database": db_health,
                    "ingestion": ingestion_status,
                    "system": system_health
                },
                "uptime_seconds": self.ingestion_service.get_uptime()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect health data: {str(e)}")
            raise
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get basic system health metrics"""
        try:
            import psutil
            import os
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                "status": "healthy",
                "memory": {
                    "total_bytes": memory.total,
                    "available_bytes": memory.available,
                    "used_percent": memory.percent
                },
                "disk": {
                    "total_bytes": disk.total,
                    "free_bytes": disk.free,
                    "used_percent": (disk.used / disk.total) * 100
                },
                "cpu": {
                    "usage_percent": cpu_percent
                },
                "process": {
                    "pid": os.getpid(),
                    "threads": psutil.Process().num_threads()
                }
            }
            
        except ImportError:
            # psutil not available, return basic info
            return {
                "status": "healthy",
                "note": "Limited system metrics (psutil not available)"
            }
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e)
            }
    
    async def _get_metrics_data(self) -> Dict[str, Any]:
        """Get basic metrics for monitoring"""
        try:
            ingestion_metrics = await self.ingestion_service.get_metrics()
            db_metrics = await self.db_manager.health_check()
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ingestion": ingestion_metrics,
                "database": {
                    "passenger_count": db_metrics.get("passenger_count", 0),
                    "active_connections": db_metrics.get("active_connections", 0),
                    "database_size_bytes": db_metrics.get("database_size_bytes", 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {str(e)}")
            raise
    
    async def start(self):
        """Start the health check server"""
        try:
            self.logger.info(f"Starting health check server on port {self.port}")
            
            config = uvicorn.Config(
                self.app,
                host="0.0.0.0",
                port=self.port,
                log_config=None,  # Disable uvicorn logging to use our logger
                access_log=False
            )
            
            server = uvicorn.Server(config)
            self._server = server
            
            await server.serve()
            
        except Exception as e:
            self.logger.error(f"Failed to start health check server: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the health check server"""
        if self._server:
            self.logger.info("Stopping health check server")
            self._server.should_exit = True
