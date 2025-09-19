#!/usr/bin/env python3
"""
External APIs Collector Service
==============================

Servicio especializado en recolección de datos desde APIs externas.
Maneja web scraping, APIs de terceros, y normalización de datos externos.

TODO (@A): Implementar conectores específicos para APIs reales.

Autor: Bus MVP Analytics Team
Fecha: 2024-01-15
Versión: 1.0.0
"""

import asyncio
import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import aiohttp
import requests
import schedule
from flask import Flask, jsonify
from decouple import config

# Importar módulos internos
from src.core.config import Settings
from src.core.logger import setup_logging
from src.collectors.weather_api import WeatherAPICollector
from src.collectors.traffic_api import TrafficAPICollector
from src.collectors.news_scraper import NewsScraperCollector
from src.collectors.fuel_prices import FuelPriceCollector
from src.storage.cloud_uploader import CloudUploader
from src.monitoring.health_check import HealthChecker
from src.monitoring.metrics import MetricsCollector
from src.utils.rate_limiter import RateLimiter


class ExternalAPIsService:
    """
    Servicio principal de recolección de APIs externas.
    
    Coordina la recolección de datos desde múltiples fuentes externas
    con manejo de rate limiting y normalización de datos.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
        # Componentes principales
        self.weather_collector = WeatherAPICollector(settings)
        self.traffic_collector = TrafficAPICollector(settings)
        self.news_scraper = NewsScraperCollector(settings)
        self.fuel_collector = FuelPriceCollector(settings)
        self.cloud_uploader = CloudUploader(settings)
        self.health_checker = HealthChecker(settings)
        self.metrics = MetricsCollector(settings)
        self.rate_limiter = RateLimiter(settings)
        
        # Flask app para health checks
        self.app = Flask(__name__)
        self._setup_routes()
        
        # Sesión HTTP reutilizable
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Bus MVP Data Collector 1.0.0',
            'Accept': 'application/json, text/html, */*',
            'Connection': 'keep-alive'
        })
        
        # Contadores para métricas
        self.api_calls_made = 0
        self.api_calls_failed = 0
        self.data_points_collected = 0
        self.last_collection_time = None
    
    def _setup_routes(self):
        """Configurar rutas del servidor Flask."""
        
        @self.app.route('/health')
        def health():
            """Endpoint de health check."""
            try:
                health_status = self.health_checker.check_all()
                
                # Añadir checks específicos de APIs
                api_status = self._check_api_endpoints()
                health_status['apis'] = api_status
                
                overall_healthy = (
                    health_status['healthy'] and 
                    all(api['accessible'] for api in api_status.values())
                )
                
                status_code = 200 if overall_healthy else 503
                return jsonify(health_status), status_code
                
            except Exception as e:
                self.logger.error(f"Error en health check: {e}")
                return jsonify({"healthy": False, "error": str(e)}), 503
        
        @self.app.route('/metrics')
        def metrics():
            """Endpoint de métricas."""
            try:
                metrics_data = {
                    "api_calls_made": self.api_calls_made,
                    "api_calls_failed": self.api_calls_failed,
                    "success_rate": (
                        (self.api_calls_made - self.api_calls_failed) / self.api_calls_made
                        if self.api_calls_made > 0 else 0
                    ),
                    "data_points_collected": self.data_points_collected,
                    "last_collection_time": self.last_collection_time,
                    "rate_limit_status": self.rate_limiter.get_status(),
                    "uptime": str(datetime.now() - self.start_time) if hasattr(self, 'start_time') else None,
                    "collectors": {
                        "weather": self.weather_collector.get_metrics(),
                        "traffic": self.traffic_collector.get_metrics(),
                        "news": self.news_scraper.get_metrics(),
                        "fuel": self.fuel_collector.get_metrics()
                    }
                }
                return jsonify(metrics_data)
            except Exception as e:
                self.logger.error(f"Error obteniendo métricas: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/status')
        def status():
            """Endpoint de status del servicio."""
            status_data = {
                "service": "external-apis-collector",
                "version": "1.0.0",
                "status": "running" if self.is_running else "stopped",
                "components": {
                    "weather_collector": self.weather_collector.is_active(),
                    "traffic_collector": self.traffic_collector.is_active(),
                    "news_scraper": self.news_scraper.is_active(),
                    "fuel_collector": self.fuel_collector.is_active(),
                    "cloud_uploader": self.cloud_uploader.is_active()
                },
                "scheduled_jobs": len(schedule.jobs),
                "collection_stats": {
                    "total_calls": self.api_calls_made,
                    "failed_calls": self.api_calls_failed,
                    "data_points": self.data_points_collected,
                    "last_run": self.last_collection_time
                },
                "rate_limits": self.rate_limiter.get_all_limits()
            }
            return jsonify(status_data)
        
        @self.app.route('/collectors/<collector_name>/trigger')
        def trigger_collector(collector_name):
            """Endpoint para disparar manualmente un collector."""
            try:
                if collector_name == 'weather':
                    result = self._collect_weather_data()
                elif collector_name == 'traffic':
                    result = self._collect_traffic_data()
                elif collector_name == 'news':
                    result = self._collect_news_data()
                elif collector_name == 'fuel':
                    result = self._collect_fuel_data()
                else:
                    return jsonify({"error": "Collector no encontrado"}), 404
                
                return jsonify({"message": f"Collector {collector_name} ejecutado", "result": result})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def start(self):
        """Iniciar el servicio de recolección de APIs externas."""
        self.logger.info("Iniciando servicio de recolección de APIs externas...")
        self.start_time = datetime.now()
        self.is_running = True
        
        try:
            # Inicializar componentes
            self._initialize_components()
            
            # Configurar tareas programadas
            self._setup_scheduled_jobs()
            
            # Iniciar servidor web en hilo separado
            self._start_web_server()
            
            self.logger.info("Servicio iniciado correctamente")
            
            # Loop principal
            self._run_main_loop()
            
        except Exception as e:
            self.logger.error(f"Error al iniciar servicio: {e}")
            raise
    
    def _initialize_components(self):
        """Inicializar todos los componentes."""
        self.logger.info("Inicializando componentes...")
        
        components = [
            self.cloud_uploader,
            self.metrics,
            self.health_checker,
            self.rate_limiter,
            self.weather_collector,
            self.traffic_collector,
            self.news_scraper,
            self.fuel_collector
        ]
        
        for component in components:
            try:
                component.initialize()
                self.logger.info(f"Componente inicializado: {component.__class__.__name__}")
            except Exception as e:
                self.logger.error(f"Error inicializando {component.__class__.__name__}: {e}")
                raise
    
    def _setup_scheduled_jobs(self):
        """Configurar trabajos programados."""
        self.logger.info("Configurando trabajos programados...")
        
        # Datos meteorológicos cada 30 minutos
        schedule.every(30).minutes.do(self._collect_weather_data)
        
        # Datos de tráfico cada 15 minutos
        schedule.every(15).minutes.do(self._collect_traffic_data)
        
        # Noticias relacionadas cada 2 horas
        schedule.every(2).hours.do(self._collect_news_data)
        
        # Precios de combustible cada 6 horas
        schedule.every(6).hours.do(self._collect_fuel_data)
        
        # Limpieza de cache diaria
        schedule.every().day.at("02:00").do(self._cleanup_cache)
        
        # Rotación de logs diaria
        schedule.every().day.at("03:00").do(self._rotate_logs)
        
        self.logger.info(f"Configurados {len(schedule.jobs)} trabajos programados")
    
    def _start_web_server(self):
        """Iniciar servidor web en hilo separado."""
        import threading
        
        def run_server():
            self.app.run(
                host='0.0.0.0',
                port=self.settings.health_check_port,
                debug=False,
                use_reloader=False
            )
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        self.logger.info(f"Servidor web iniciado en puerto {self.settings.health_check_port}")
    
    def _run_main_loop(self):
        """Loop principal del servicio."""
        self.logger.info("Iniciando loop principal...")
        
        try:
            while self.is_running:
                # Ejecutar trabajos programados
                schedule.run_pending()
                
                # Procesar cola de requests pendientes
                self._process_pending_requests()
                
                # Actualizar métricas
                self._update_metrics()
                
                # Verificar rate limits
                self._check_rate_limits()
                
                # Dormir brevemente
                time.sleep(30)
                
        except KeyboardInterrupt:
            self.logger.info("Recibida señal de interrupción")
            self.shutdown()
        except Exception as e:
            self.logger.error(f"Error en loop principal: {e}")
            raise
    
    def _collect_weather_data(self):
        """Recolectar datos meteorológicos."""
        self.logger.info("Recolectando datos meteorológicos...")
        
        try:
            # Verificar rate limit
            if not self.rate_limiter.can_make_request('weather_api'):
                self.logger.warning("Rate limit alcanzado para Weather API")
                return
            
            # Recolectar datos
            weather_data = self.weather_collector.collect_current_weather()
            
            if weather_data:
                # Subir a cloud storage
                self.cloud_uploader.upload_data(weather_data, 'weather')
                
                self.api_calls_made += 1
                self.data_points_collected += len(weather_data.get('locations', []))
                self.rate_limiter.record_request('weather_api')
                
                self.logger.info(f"Datos meteorológicos recolectados: {len(weather_data.get('locations', []))} ubicaciones")
            else:
                self.api_calls_failed += 1
                self.logger.error("Error recolectando datos meteorológicos")
            
            self.last_collection_time = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Error en recolección meteorológica: {e}")
            self.api_calls_failed += 1
    
    def _collect_traffic_data(self):
        """Recolectar datos de tráfico."""
        self.logger.info("Recolectando datos de tráfico...")
        
        try:
            if not self.rate_limiter.can_make_request('traffic_api'):
                self.logger.warning("Rate limit alcanzado para Traffic API")
                return
            
            traffic_data = self.traffic_collector.collect_traffic_conditions()
            
            if traffic_data:
                self.cloud_uploader.upload_data(traffic_data, 'traffic')
                self.api_calls_made += 1
                self.data_points_collected += len(traffic_data.get('routes', []))
                self.rate_limiter.record_request('traffic_api')
                
                self.logger.info(f"Datos de tráfico recolectados: {len(traffic_data.get('routes', []))} rutas")
            else:
                self.api_calls_failed += 1
                
        except Exception as e:
            self.logger.error(f"Error en recolección de tráfico: {e}")
            self.api_calls_failed += 1
    
    def _collect_news_data(self):
        """Recolectar noticias relacionadas."""
        self.logger.info("Recolectando noticias relacionadas...")
        
        try:
            # No hay rate limit típicamente para scraping (con precaución)
            news_data = self.news_scraper.collect_transport_news()
            
            if news_data:
                self.cloud_uploader.upload_data(news_data, 'news')
                self.api_calls_made += 1
                self.data_points_collected += len(news_data.get('articles', []))
                
                self.logger.info(f"Noticias recolectadas: {len(news_data.get('articles', []))} artículos")
            else:
                self.api_calls_failed += 1
                
        except Exception as e:
            self.logger.error(f"Error en recolección de noticias: {e}")
            self.api_calls_failed += 1
    
    def _collect_fuel_data(self):
        """Recolectar precios de combustible."""
        self.logger.info("Recolectando precios de combustible...")
        
        try:
            if not self.rate_limiter.can_make_request('fuel_api'):
                self.logger.warning("Rate limit alcanzado para Fuel API")
                return
            
            fuel_data = self.fuel_collector.collect_fuel_prices()
            
            if fuel_data:
                self.cloud_uploader.upload_data(fuel_data, 'fuel')
                self.api_calls_made += 1
                self.data_points_collected += len(fuel_data.get('stations', []))
                self.rate_limiter.record_request('fuel_api')
                
                self.logger.info(f"Precios de combustible recolectados: {len(fuel_data.get('stations', []))} estaciones")
            else:
                self.api_calls_failed += 1
                
        except Exception as e:
            self.logger.error(f"Error en recolección de combustible: {e}")
            self.api_calls_failed += 1
    
    def _check_api_endpoints(self) -> Dict[str, Any]:
        """Verificar accesibilidad de endpoints API."""
        api_status = {}
        
        # Lista de APIs a verificar
        apis_to_check = [
            ('weather_api', self.weather_collector.get_health_endpoint()),
            ('traffic_api', self.traffic_collector.get_health_endpoint()),
            ('fuel_api', self.fuel_collector.get_health_endpoint())
        ]
        
        for api_name, endpoint in apis_to_check:
            try:
                if endpoint:
                    response = self.session.get(endpoint, timeout=5)
                    api_status[api_name] = {
                        'accessible': response.status_code == 200,
                        'response_time': response.elapsed.total_seconds(),
                        'status_code': response.status_code
                    }
                else:
                    api_status[api_name] = {
                        'accessible': False,
                        'error': 'No health endpoint configured'
                    }
            except Exception as e:
                api_status[api_name] = {
                    'accessible': False,
                    'error': str(e)
                }
        
        return api_status
    
    def _process_pending_requests(self):
        """Procesar requests pendientes en cola."""
        # TODO (@A): Implementar cola de requests pendientes
        pass
    
    def _update_metrics(self):
        """Actualizar métricas del servicio."""
        self.metrics.update_metric('api_calls_made', self.api_calls_made)
        self.metrics.update_metric('api_calls_failed', self.api_calls_failed)
        self.metrics.update_metric('data_points_collected', self.data_points_collected)
    
    def _check_rate_limits(self):
        """Verificar y manejar rate limits."""
        # Revisar límites y ajustar frecuencia si es necesario
        for api_name in ['weather_api', 'traffic_api', 'fuel_api']:
            if self.rate_limiter.is_near_limit(api_name):
                self.logger.warning(f"Acercándose al rate limit para {api_name}")
    
    def _cleanup_cache(self):
        """Limpiar archivos de cache."""
        self.logger.info("Limpiando cache...")
        
        try:
            # Limpiar cache de cada collector
            for collector in [self.weather_collector, self.traffic_collector, 
                             self.news_scraper, self.fuel_collector]:
                collector.cleanup_cache()
                
            self.logger.info("Cache limpiado correctamente")
        except Exception as e:
            self.logger.error(f"Error limpiando cache: {e}")
    
    def _rotate_logs(self):
        """Rotar archivos de log."""
        self.logger.info("Rotando logs...")
        # TODO (@A): Implementar rotación de logs
        pass
    
    def shutdown(self):
        """Cerrar el servicio gracefully."""
        self.logger.info("Iniciando cierre del servicio...")
        self.is_running = False
        
        try:
            # Cerrar sesión HTTP
            self.session.close()
            
            # Cerrar componentes
            components = [
                self.weather_collector,
                self.traffic_collector,
                self.news_scraper,
                self.fuel_collector,
                self.cloud_uploader,
                self.metrics,
                self.health_checker,
                self.rate_limiter
            ]
            
            for component in components:
                try:
                    component.shutdown()
                except Exception as e:
                    self.logger.error(f"Error cerrando {component.__class__.__name__}: {e}")
            
            # Limpiar trabajos programados
            schedule.clear()
            
            self.logger.info("Servicio cerrado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error durante el cierre: {e}")


def main():
    """Función principal del servicio."""
    try:
        # Configurar logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("=== Bus MVP External APIs Collector ===")
        logger.info("Iniciando servicio...")
        
        # Cargar configuración
        settings = Settings()
        logger.info(f"Configuración cargada: {settings.environment}")
        
        # Crear y ejecutar servicio
        service = ExternalAPIsService(settings)
        service.start()
        
    except KeyboardInterrupt:
        logger.info("Servicio interrumpido por usuario")
    except Exception as e:
        logger.error(f"Error fatal en servicio: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # TODO (@A): Implementar configuración específica para producción
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nServicio detenido por usuario")
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)
