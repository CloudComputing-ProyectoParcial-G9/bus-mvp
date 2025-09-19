#!/usr/bin/env python3
"""
Real-Time Data Ingestion Service
================================

Servicio principal para ingesta de datos en tiempo real del sistema Bus MVP.
Maneja GPS tracking, sensores IoT, y eventos del sistema en vivo.

TODO (@A): Implementar conectores específicos para fuentes de datos reales.

Autor: Bus MVP Analytics Team
Fecha: 2024-01-15
Versión: 1.0.0
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

import aiohttp
import structlog
from aiohttp import web
from decouple import config

# Importar módulos internos
from src.core.config import Settings
from src.core.logger import setup_logging
from src.ingestion.gps_tracker import GPSTracker
from src.ingestion.iot_sensors import IoTSensorManager
from src.ingestion.system_events import SystemEventCollector
from src.storage.cloud_uploader import CloudUploader
from src.monitoring.health_check import HealthChecker
from src.monitoring.metrics import MetricsCollector


class RealTimeIngestionService:
    """
    Servicio principal de ingesta de datos en tiempo real.
    
    Coordina múltiples fuentes de datos y el flujo hacia el almacenamiento.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = structlog.get_logger()
        self.is_running = False
        self.tasks: List[asyncio.Task] = []
        
        # Componentes principales
        self.gps_tracker = GPSTracker(settings)
        self.iot_manager = IoTSensorManager(settings)
        self.event_collector = SystemEventCollector(settings)
        self.cloud_uploader = CloudUploader(settings)
        self.health_checker = HealthChecker(settings)
        self.metrics = MetricsCollector(settings)
        
        # Servidor web para health checks
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        """Configurar rutas del servidor web."""
        self.app.router.add_get('/health', self.health_endpoint)
        self.app.router.add_get('/metrics', self.metrics_endpoint)
        self.app.router.add_get('/status', self.status_endpoint)
    
    async def health_endpoint(self, request: web.Request) -> web.Response:
        """Endpoint de health check."""
        try:
            health_status = await self.health_checker.check_all()
            status_code = 200 if health_status['healthy'] else 503
            
            return web.json_response(health_status, status=status_code)
        except Exception as e:
            self.logger.error("Error en health check", error=str(e))
            return web.json_response(
                {"healthy": False, "error": str(e)},
                status=503
            )
    
    async def metrics_endpoint(self, request: web.Request) -> web.Response:
        """Endpoint de métricas."""
        try:
            metrics_data = await self.metrics.get_all_metrics()
            return web.json_response(metrics_data)
        except Exception as e:
            self.logger.error("Error obteniendo métricas", error=str(e))
            return web.json_response({"error": str(e)}, status=500)
    
    async def status_endpoint(self, request: web.Request) -> web.Response:
        """Endpoint de status del servicio."""
        status = {
            "service": "real-time-ingestion",
            "version": "1.0.0",
            "status": "running" if self.is_running else "stopped",
            "uptime": str(datetime.now() - self.start_time) if hasattr(self, 'start_time') else None,
            "active_tasks": len([t for t in self.tasks if not t.done()]),
            "components": {
                "gps_tracker": self.gps_tracker.is_active(),
                "iot_manager": self.iot_manager.is_active(),
                "event_collector": self.event_collector.is_active(),
                "cloud_uploader": self.cloud_uploader.is_active()
            }
        }
        return web.json_response(status)
    
    async def start(self):
        """Iniciar el servicio de ingesta."""
        self.logger.info("Iniciando servicio de ingesta en tiempo real...")
        self.start_time = datetime.now()
        self.is_running = True
        
        try:
            # Inicializar componentes
            await self._initialize_components()
            
            # Iniciar tareas de ingesta
            await self._start_ingestion_tasks()
            
            # Iniciar servidor web
            await self._start_web_server()
            
            self.logger.info("Servicio iniciado correctamente")
            
            # Mantener el servicio corriendo
            await self._wait_for_shutdown()
            
        except Exception as e:
            self.logger.error("Error al iniciar servicio", error=str(e))
            raise
    
    async def _initialize_components(self):
        """Inicializar todos los componentes."""
        self.logger.info("Inicializando componentes...")
        
        # Inicializar en orden de dependencias
        await self.cloud_uploader.initialize()
        await self.metrics.initialize()
        await self.health_checker.initialize()
        
        await self.gps_tracker.initialize()
        await self.iot_manager.initialize()
        await self.event_collector.initialize()
        
        self.logger.info("Componentes inicializados correctamente")
    
    async def _start_ingestion_tasks(self):
        """Iniciar tareas de ingesta en paralelo."""
        self.logger.info("Iniciando tareas de ingesta...")
        
        # Crear tareas asíncronas para cada componente
        tasks_config = [
            ("gps_ingestion", self.gps_tracker.start_ingestion()),
            ("iot_ingestion", self.iot_manager.start_ingestion()),
            ("events_ingestion", self.event_collector.start_ingestion()),
            ("data_upload", self.cloud_uploader.start_upload_worker()),
            ("metrics_collection", self.metrics.start_collection()),
        ]
        
        for task_name, coro in tasks_config:
            task = asyncio.create_task(coro, name=task_name)
            self.tasks.append(task)
            self.logger.info(f"Tarea iniciada: {task_name}")
    
    async def _start_web_server(self):
        """Iniciar servidor web para endpoints."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(
            runner, 
            host='0.0.0.0', 
            port=self.settings.health_check_port
        )
        await site.start()
        
        self.logger.info(
            f"Servidor web iniciado en puerto {self.settings.health_check_port}"
        )
    
    async def _wait_for_shutdown(self):
        """Esperar señal de cierre."""
        try:
            # Configurar handlers de señales
            loop = asyncio.get_running_loop()
            
            def signal_handler(signum, frame):
                self.logger.info(f"Recibida señal {signum}, iniciando cierre...")
                loop.create_task(self.shutdown())
            
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            # Esperar hasta que se cancelen todas las tareas
            while self.is_running and any(not t.done() for t in self.tasks):
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            self.logger.info("Servicio cancelado")
    
    async def shutdown(self):
        """Cerrar el servicio gracefully."""
        self.logger.info("Iniciando cierre del servicio...")
        self.is_running = False
        
        try:
            # Cancelar tareas activas
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            
            # Esperar a que terminen las tareas
            if self.tasks:
                await asyncio.gather(*self.tasks, return_exceptions=True)
            
            # Cerrar componentes
            await self._shutdown_components()
            
            self.logger.info("Servicio cerrado correctamente")
            
        except Exception as e:
            self.logger.error("Error durante el cierre", error=str(e))
    
    async def _shutdown_components(self):
        """Cerrar todos los componentes."""
        components = [
            self.gps_tracker,
            self.iot_manager,
            self.event_collector,
            self.cloud_uploader,
            self.metrics,
            self.health_checker
        ]
        
        for component in components:
            try:
                await component.shutdown()
            except Exception as e:
                self.logger.error(
                    f"Error cerrando componente {component.__class__.__name__}",
                    error=str(e)
                )


async def main():
    """Función principal del servicio."""
    try:
        # Configurar logging
        setup_logging()
        logger = structlog.get_logger()
        
        logger.info("=== Bus MVP Real-Time Data Ingestion ===")
        logger.info("Iniciando servicio...")
        
        # Cargar configuración
        settings = Settings()
        logger.info("Configuración cargada", environment=settings.environment)
        
        # Crear y ejecutar servicio
        service = RealTimeIngestionService(settings)
        await service.start()
        
    except KeyboardInterrupt:
        logger.info("Servicio interrumpido por usuario")
    except Exception as e:
        logger.error("Error fatal en servicio", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    # TODO (@A): Implementar configuración específica para producción
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServicio detenido por usuario")
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)
