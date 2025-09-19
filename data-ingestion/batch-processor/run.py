#!/usr/bin/env python3
"""
Batch Data Processor Service
===========================

Servicio especializado en procesamiento de datos por lotes del sistema Bus MVP.
Maneja archivos CSV, logs del sistema, y procesos ETL programados.

TODO (@A): Implementar conectores específicos para fuentes de datos reales.

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
from pathlib import Path
from typing import Dict, Any, List, Optional

import pandas as pd
import schedule
from flask import Flask, jsonify
from decouple import config

# Importar módulos internos
from src.core.config import Settings
from src.core.logger import setup_logging
from src.processors.csv_processor import CSVProcessor
from src.processors.log_processor import LogProcessor
from src.processors.database_etl import DatabaseETL
from src.storage.cloud_uploader import CloudUploader
from src.monitoring.health_check import HealthChecker
from src.monitoring.metrics import MetricsCollector
from src.utils.file_watcher import FileWatcher


class BatchProcessorService:
    """
    Servicio principal de procesamiento de datos por lotes.
    
    Coordina la ingesta y procesamiento de archivos, logs y datos históricos.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
        # Componentes principales
        self.csv_processor = CSVProcessor(settings)
        self.log_processor = LogProcessor(settings)
        self.database_etl = DatabaseETL(settings)
        self.cloud_uploader = CloudUploader(settings)
        self.health_checker = HealthChecker(settings)
        self.metrics = MetricsCollector(settings)
        self.file_watcher = FileWatcher(settings)
        
        # Flask app para health checks
        self.app = Flask(__name__)
        self._setup_routes()
        
        # Contadores para métricas
        self.processed_files = 0
        self.failed_files = 0
        self.last_processing_time = None
    
    def _setup_routes(self):
        """Configurar rutas del servidor Flask."""
        
        @self.app.route('/health')
        def health():
            """Endpoint de health check."""
            try:
                health_status = self.health_checker.check_all()
                status_code = 200 if health_status['healthy'] else 503
                return jsonify(health_status), status_code
            except Exception as e:
                self.logger.error(f"Error en health check: {e}")
                return jsonify({"healthy": False, "error": str(e)}), 503
        
        @self.app.route('/metrics')
        def metrics():
            """Endpoint de métricas."""
            try:
                metrics_data = {
                    "processed_files": self.processed_files,
                    "failed_files": self.failed_files,
                    "success_rate": (
                        self.processed_files / (self.processed_files + self.failed_files)
                        if (self.processed_files + self.failed_files) > 0 else 0
                    ),
                    "last_processing_time": self.last_processing_time,
                    "uptime": str(datetime.now() - self.start_time) if hasattr(self, 'start_time') else None
                }
                return jsonify(metrics_data)
            except Exception as e:
                self.logger.error(f"Error obteniendo métricas: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/status')
        def status():
            """Endpoint de status del servicio."""
            status_data = {
                "service": "batch-processor",
                "version": "1.0.0",
                "status": "running" if self.is_running else "stopped",
                "components": {
                    "csv_processor": self.csv_processor.is_active(),
                    "log_processor": self.log_processor.is_active(),
                    "database_etl": self.database_etl.is_active(),
                    "cloud_uploader": self.cloud_uploader.is_active(),
                    "file_watcher": self.file_watcher.is_active()
                },
                "scheduled_jobs": len(schedule.jobs),
                "processing_stats": {
                    "total_processed": self.processed_files,
                    "total_failed": self.failed_files,
                    "last_run": self.last_processing_time
                }
            }
            return jsonify(status_data)
    
    def start(self):
        """Iniciar el servicio de procesamiento por lotes."""
        self.logger.info("Iniciando servicio de procesamiento por lotes...")
        self.start_time = datetime.now()
        self.is_running = True
        
        try:
            # Inicializar componentes
            self._initialize_components()
            
            # Configurar tareas programadas
            self._setup_scheduled_jobs()
            
            # Iniciar file watcher
            self._start_file_watcher()
            
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
            self.csv_processor,
            self.log_processor,
            self.database_etl,
            self.file_watcher
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
        
        # Procesamiento diario de archivos CSV
        schedule.every().day.at("02:00").do(self._daily_csv_processing)
        
        # Procesamiento de logs cada hora
        schedule.every().hour.do(self._hourly_log_processing)
        
        # ETL de base de datos cada 6 horas
        schedule.every(6).hours.do(self._database_etl_job)
        
        # Limpieza de archivos temporales diaria
        schedule.every().day.at("03:00").do(self._cleanup_temp_files)
        
        # Backup de métricas cada 12 horas
        schedule.every(12).hours.do(self._backup_metrics)
        
        self.logger.info(f"Configurados {len(schedule.jobs)} trabajos programados")
    
    def _start_file_watcher(self):
        """Iniciar el observador de archivos."""
        self.logger.info("Iniciando file watcher...")
        
        # Configurar callbacks para diferentes tipos de archivos
        self.file_watcher.add_handler('*.csv', self._handle_new_csv_file)
        self.file_watcher.add_handler('*.log', self._handle_new_log_file)
        self.file_watcher.add_handler('*.json', self._handle_new_json_file)
        
        self.file_watcher.start()
    
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
                
                # Procesar cola de archivos pendientes
                self._process_pending_files()
                
                # Actualizar métricas
                self._update_metrics()
                
                # Dormir brevemente para no consumir CPU
                time.sleep(10)
                
        except KeyboardInterrupt:
            self.logger.info("Recibida señal de interrupción")
            self.shutdown()
        except Exception as e:
            self.logger.error(f"Error en loop principal: {e}")
            raise
    
    def _daily_csv_processing(self):
        """Procesamiento diario de archivos CSV."""
        self.logger.info("Iniciando procesamiento diario de CSV...")
        
        try:
            # Buscar archivos CSV en directorio de entrada
            csv_files = list(Path(self.settings.input_directory).glob("*.csv"))
            
            for csv_file in csv_files:
                self._process_csv_file(csv_file)
            
            self.logger.info(f"Procesamiento diario completado: {len(csv_files)} archivos")
            
        except Exception as e:
            self.logger.error(f"Error en procesamiento diario: {e}")
            self.failed_files += 1
    
    def _hourly_log_processing(self):
        """Procesamiento por hora de logs."""
        self.logger.info("Iniciando procesamiento de logs...")
        
        try:
            # Procesar logs de la última hora
            cutoff_time = datetime.now() - timedelta(hours=1)
            log_files = self._find_recent_log_files(cutoff_time)
            
            for log_file in log_files:
                self._process_log_file(log_file)
            
            self.logger.info(f"Procesamiento de logs completado: {len(log_files)} archivos")
            
        except Exception as e:
            self.logger.error(f"Error en procesamiento de logs: {e}")
            self.failed_files += 1
    
    def _database_etl_job(self):
        """Trabajo de ETL de base de datos."""
        self.logger.info("Iniciando ETL de base de datos...")
        
        try:
            # Ejecutar procesos ETL configurados
            etl_results = self.database_etl.run_all_jobs()
            
            # Subir resultados a cloud storage
            for result in etl_results:
                self.cloud_uploader.upload_data(result)
            
            self.logger.info("ETL de base de datos completado")
            
        except Exception as e:
            self.logger.error(f"Error en ETL de base de datos: {e}")
            self.failed_files += 1
    
    def _handle_new_csv_file(self, file_path: Path):
        """Manejar nuevo archivo CSV detectado."""
        self.logger.info(f"Nuevo archivo CSV detectado: {file_path}")
        self._process_csv_file(file_path)
    
    def _handle_new_log_file(self, file_path: Path):
        """Manejar nuevo archivo de log detectado."""
        self.logger.info(f"Nuevo archivo de log detectado: {file_path}")
        self._process_log_file(file_path)
    
    def _handle_new_json_file(self, file_path: Path):
        """Manejar nuevo archivo JSON detectado."""
        self.logger.info(f"Nuevo archivo JSON detectado: {file_path}")
        self._process_json_file(file_path)
    
    def _process_csv_file(self, file_path: Path):
        """Procesar archivo CSV."""
        try:
            start_time = time.time()
            
            # Procesar con el componente CSV
            result = self.csv_processor.process_file(file_path)
            
            if result['success']:
                # Subir a cloud storage
                self.cloud_uploader.upload_data(result['data'])
                
                # Mover archivo a procesados
                self._move_to_processed(file_path)
                
                self.processed_files += 1
                self.logger.info(f"Archivo CSV procesado exitosamente: {file_path}")
            else:
                self._move_to_failed(file_path)
                self.failed_files += 1
                self.logger.error(f"Error procesando CSV: {result['error']}")
            
            self.last_processing_time = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Error procesando archivo CSV {file_path}: {e}")
            self._move_to_failed(file_path)
            self.failed_files += 1
    
    def _process_log_file(self, file_path: Path):
        """Procesar archivo de log."""
        try:
            result = self.log_processor.process_file(file_path)
            
            if result['success']:
                self.cloud_uploader.upload_data(result['data'])
                self._move_to_processed(file_path)
                self.processed_files += 1
            else:
                self._move_to_failed(file_path)
                self.failed_files += 1
                
        except Exception as e:
            self.logger.error(f"Error procesando log {file_path}: {e}")
            self._move_to_failed(file_path)
            self.failed_files += 1
    
    def _process_json_file(self, file_path: Path):
        """Procesar archivo JSON."""
        # TODO (@A): Implementar procesamiento específico de JSON
        pass
    
    def _move_to_processed(self, file_path: Path):
        """Mover archivo a directorio de procesados."""
        processed_dir = Path(self.settings.processed_directory)
        processed_dir.mkdir(exist_ok=True)
        
        destination = processed_dir / file_path.name
        file_path.rename(destination)
    
    def _move_to_failed(self, file_path: Path):
        """Mover archivo a directorio de fallos."""
        failed_dir = Path(self.settings.failed_directory)
        failed_dir.mkdir(exist_ok=True)
        
        destination = failed_dir / file_path.name
        file_path.rename(destination)
    
    def _cleanup_temp_files(self):
        """Limpiar archivos temporales."""
        self.logger.info("Iniciando limpieza de archivos temporales...")
        
        temp_dir = Path(self.settings.temp_directory)
        if temp_dir.exists():
            # Eliminar archivos más antiguos que 24 horas
            cutoff_time = time.time() - (24 * 60 * 60)
            
            for temp_file in temp_dir.rglob("*"):
                if temp_file.is_file() and temp_file.stat().st_mtime < cutoff_time:
                    temp_file.unlink()
    
    def _backup_metrics(self):
        """Respaldar métricas."""
        self.logger.info("Respaldando métricas...")
        
        try:
            metrics_data = self.metrics.get_all_metrics()
            self.cloud_uploader.upload_metrics(metrics_data)
        except Exception as e:
            self.logger.error(f"Error respaldando métricas: {e}")
    
    def _process_pending_files(self):
        """Procesar archivos en cola pendiente."""
        # TODO (@A): Implementar cola de archivos pendientes
        pass
    
    def _update_metrics(self):
        """Actualizar métricas del servicio."""
        self.metrics.update_metric('processed_files', self.processed_files)
        self.metrics.update_metric('failed_files', self.failed_files)
    
    def _find_recent_log_files(self, cutoff_time: datetime) -> List[Path]:
        """Encontrar archivos de log recientes."""
        log_dir = Path(self.settings.log_directory)
        recent_files = []
        
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                if datetime.fromtimestamp(log_file.stat().st_mtime) > cutoff_time:
                    recent_files.append(log_file)
        
        return recent_files
    
    def shutdown(self):
        """Cerrar el servicio gracefully."""
        self.logger.info("Iniciando cierre del servicio...")
        self.is_running = False
        
        try:
            # Detener file watcher
            self.file_watcher.stop()
            
            # Cerrar componentes
            components = [
                self.csv_processor,
                self.log_processor,
                self.database_etl,
                self.cloud_uploader,
                self.metrics,
                self.health_checker
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
        
        logger.info("=== Bus MVP Batch Data Processor ===")
        logger.info("Iniciando servicio...")
        
        # Cargar configuración
        settings = Settings()
        logger.info(f"Configuración cargada: {settings.environment}")
        
        # Crear y ejecutar servicio
        service = BatchProcessorService(settings)
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
