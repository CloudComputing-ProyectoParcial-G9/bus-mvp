#!/usr/bin/env python3
"""
Script de Auto-Sincronización para Bus MVP
Ejecuta automáticamente:
1. Ingesta de datos desde las APIs
2. Actualización de crawlers en Glue
3. Actualización del catálogo

Se ejecuta en loop continuo con intervalo configurable
"""

import boto3
import time
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


class AutoSync:
    def __init__(self, interval_minutes=60):
        """
        Args:
            interval_minutes: Intervalo en minutos entre sincronizaciones
        """
        self.interval_minutes = interval_minutes
        self.interval_seconds = interval_minutes * 60
        self.glue = boto3.client('glue', region_name='us-east-1')
        self.database_name = 'bus_mvp_db'
        self.crawlers = ['passengers-crawler', 'trips-crawler', 'tickets-crawler']
        self.project_root = Path(__file__).parent.parent

    def log(self, message, level='INFO'):
        """Log con timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {
            'INFO': '📋',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'SYNC': '🔄'
        }.get(level, '📋')
        print(f'[{timestamp}] {prefix} {message}', flush=True)

    def run_ingestion(self):
        """Ejecuta la ingesta de datos usando docker-compose"""
        self.log('Iniciando ingesta de datos...', 'SYNC')

        services = ['passengers-ingestion', 'trips-ingestion', 'tickets-ingestion']
        success = True

        try:
            for service in services:
                self.log(f'Ejecutando {service}...', 'INFO')
                result = subprocess.run(
                    ['docker', 'compose', 'up', service, '--build'],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutos timeout
                )

                if result.returncode == 0:
                    self.log(f'{service} completado', 'SUCCESS')
                else:
                    self.log(f'{service} falló: {result.stderr}', 'ERROR')
                    success = False

            return success
        except subprocess.TimeoutExpired:
            self.log('Timeout en ingesta de datos', 'ERROR')
            return False
        except Exception as e:
            self.log(f'Error en ingesta: {e}', 'ERROR')
            return False

    def start_crawler(self, crawler_name):
        """Inicia un crawler si no está corriendo"""
        try:
            # Verificar estado
            response = self.glue.get_crawler(Name=crawler_name)
            state = response['Crawler']['State']

            if state == 'RUNNING':
                self.log(f'Crawler {crawler_name} ya está corriendo', 'INFO')
                return True

            # Iniciar crawler
            self.glue.start_crawler(Name=crawler_name)
            self.log(f'Crawler {crawler_name} iniciado', 'SUCCESS')
            return True

        except self.glue.exceptions.EntityNotFoundException:
            self.log(f'Crawler {crawler_name} no existe, creándolo...', 'WARNING')
            # Aquí podrías llamar a setup_glue.py si el crawler no existe
            return False
        except Exception as e:
            self.log(f'Error iniciando crawler {crawler_name}: {e}', 'ERROR')
            return False

    def wait_for_crawlers(self, timeout=600):
        """Espera a que todos los crawlers terminen"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            all_ready = True

            for crawler_name in self.crawlers:
                try:
                    response = self.glue.get_crawler(Name=crawler_name)
                    state = response['Crawler']['State']

                    if state in ['RUNNING', 'STOPPING']:
                        all_ready = False

                except Exception:
                    pass

            if all_ready:
                self.log('Todos los crawlers completados', 'SUCCESS')
                return True

            time.sleep(10)

        self.log('Timeout esperando crawlers', 'WARNING')
        return False

    def run_crawlers(self):
        """Ejecuta todos los crawlers"""
        self.log('Iniciando crawlers...', 'SYNC')

        success = True
        for crawler_name in self.crawlers:
            if not self.start_crawler(crawler_name):
                success = False

        if success:
            # Esperar a que terminen
            self.wait_for_crawlers()

        return success

    def get_table_count(self):
        """Obtiene el número de tablas en el catálogo"""
        try:
            response = self.glue.get_tables(DatabaseName=self.database_name)
            return len(response.get('TableList', []))
        except Exception:
            return 0

    def run_sync_cycle(self):
        """Ejecuta un ciclo completo de sincronización"""
        self.log('=' * 70, 'INFO')
        self.log('INICIANDO CICLO DE SINCRONIZACIÓN', 'SYNC')
        self.log('=' * 70, 'INFO')

        start_time = time.time()

        # 1. Ejecutar ingesta
        if self.run_ingestion():
            self.log('Ingesta completada exitosamente', 'SUCCESS')
        else:
            self.log('Ingesta completada con errores', 'WARNING')

        # Esperar un poco antes de ejecutar crawlers
        time.sleep(5)

        # 2. Ejecutar crawlers
        if self.run_crawlers():
            self.log('Crawlers completados exitosamente', 'SUCCESS')
        else:
            self.log('Crawlers completados con errores', 'WARNING')

        # 3. Verificar resultados
        table_count = self.get_table_count()
        self.log(f'Tablas en catálogo: {table_count}', 'INFO')

        elapsed = time.time() - start_time
        self.log(f'Ciclo completado en {elapsed:.1f} segundos', 'SUCCESS')
        self.log('=' * 70, 'INFO')

    def run_forever(self):
        """Ejecuta sincronización en loop infinito"""
        self.log('🚀 Auto-Sync iniciado', 'SUCCESS')
        self.log(f'⏱️  Intervalo: {self.interval_minutes} minutos', 'INFO')
        self.log(f'🗄️  Database: {self.database_name}', 'INFO')
        self.log(f'🕷️  Crawlers: {", ".join(self.crawlers)}', 'INFO')
        self.log('', 'INFO')
        self.log('Presiona Ctrl+C para detener', 'INFO')
        self.log('', 'INFO')

        cycle_number = 0

        try:
            while True:
                cycle_number += 1
                self.log(f'Ciclo #{cycle_number}', 'INFO')

                self.run_sync_cycle()

                # Calcular próxima ejecución
                next_run = datetime.now().timestamp() + self.interval_seconds
                next_run_str = datetime.fromtimestamp(next_run).strftime('%Y-%m-%d %H:%M:%S')

                self.log(f'Próxima sincronización: {next_run_str}', 'INFO')
                self.log(f'Esperando {self.interval_minutes} minutos...', 'INFO')
                self.log('', 'INFO')

                time.sleep(self.interval_seconds)

        except KeyboardInterrupt:
            self.log('', 'INFO')
            self.log('Auto-Sync detenido por el usuario', 'WARNING')
            sys.exit(0)
        except Exception as e:
            self.log(f'Error fatal: {e}', 'ERROR')
            sys.exit(1)


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Auto-sincronización de datos Bus MVP')
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Intervalo en minutos entre sincronizaciones (default: 60)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Ejecutar solo una vez y salir'
    )

    args = parser.parse_args()

    sync = AutoSync(interval_minutes=args.interval)

    if args.once:
        # Ejecutar solo una vez
        sync.run_sync_cycle()
    else:
        # Ejecutar en loop infinito
        sync.run_forever()


if __name__ == '__main__':
    main()
