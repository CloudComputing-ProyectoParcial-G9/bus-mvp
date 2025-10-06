"""
Script para Configuración Completa de AWS Glue
Crea Database, Crawlers, Tablas y ejecuta Crawlers

Requisitos:
- AWS CLI configurado con credenciales válidas
- Bucket S3 con datos cargados
- Permisos de AWS Glue
"""

import boto3
import time
import sys
from datetime import datetime

class GlueSetup:
    def __init__(self):
        self.glue_client = boto3.client('glue', region_name='us-east-1')

        self.s3_client = boto3.client('s3')
        
        # Configuración desde variables de entorno o valores por defecto
        import os
        self.bucket_name = os.getenv('S3_BUCKET', 'bus-mvp-datalake-1')
        self.database_name = os.getenv('GLUE_DATABASE', 'bus_mvp_db')
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        
        # IAM Role para Glue Crawlers (debe existir)
        self.glue_role_arn = os.getenv('GLUE_ROLE_ARN', 
            f'arn:aws:iam::{self.get_account_id()}:role/AWSGlueServiceRole-BusMVP')
    
    def get_account_id(self):
        """Obtiene el Account ID de AWS"""
        sts = boto3.client('sts')
        return sts.get_caller_identity()['Account']
    
    def print_banner(self, message):
        """Imprime un banner decorativo"""
        print('\n' + '=' * 70)
        print(f'  {message}')
        print('=' * 70 + '\n')
    
    def create_database(self):
        """Crea la base de datos en Glue Catalog"""
        self.print_banner('PASO 1: Creando Database en Glue Catalog')
        
        try:
            # Verificar si ya existe
            try:
                response = self.glue_client.get_database(Name=self.database_name)
                print(f'✅ Database "{self.database_name}" ya existe')
                print(f'   Descripción: {response["Database"].get("Description", "N/A")}')
                return True
            except self.glue_client.exceptions.EntityNotFoundException:
                pass
            
            # Crear database
            self.glue_client.create_database(
                DatabaseInput={
                    'Name': self.database_name,
                    'Description': 'Bus MVP Analytics - Data Catalog para Passengers, Trips y Tickets',
                    'LocationUri': f's3://{self.bucket_name}/raw/',
                    'Parameters': {
                        'project': 'bus-mvp',
                        'environment': 'production',
                        'created_by': 'glue_setup_script',
                        'created_at': datetime.now().isoformat()
                    }
                }
            )
            print(f'✅ Database "{self.database_name}" creada exitosamente')
            return True
            
        except Exception as e:
            print(f'❌ Error creando database: {e}')
            return False
    
    def create_crawler(self, name, s3_path, description, table_prefix=''):
        """Crea un Glue Crawler"""
        try:
            # Verificar si ya existe
            try:
                self.glue_client.get_crawler(Name=name)
                print(f'⚠️  Crawler "{name}" ya existe, actualizando...')
                
                self.glue_client.update_crawler(
                    Name=name,
                    Role=self.glue_role_arn,
                    DatabaseName=self.database_name,
                    Description=description,
                    Targets={
                        'S3Targets': [{'Path': s3_path}]
                    },
                    TablePrefix=table_prefix,
                    SchemaChangePolicy={
                        'UpdateBehavior': 'UPDATE_IN_DATABASE',
                        'DeleteBehavior': 'LOG'
                    },
                    RecrawlPolicy={'RecrawlBehavior': 'CRAWL_EVERYTHING'},
                    Configuration='{"Version":1.0,"CrawlerOutput":{"Partitions":{"AddOrUpdateBehavior":"InheritFromTable"}}}'
                )
                print(f'✅ Crawler "{name}" actualizado')
                return True
                
            except self.glue_client.exceptions.EntityNotFoundException:
                pass
            
            # Crear nuevo crawler
            self.glue_client.create_crawler(
                Name=name,
                Role=self.glue_role_arn,
                DatabaseName=self.database_name,
                Description=description,
                Targets={
                    'S3Targets': [{'Path': s3_path}]
                },
                TablePrefix=table_prefix,
                SchemaChangePolicy={
                    'UpdateBehavior': 'UPDATE_IN_DATABASE',
                    'DeleteBehavior': 'LOG'
                },
                RecrawlPolicy={
                    'RecrawlBehavior': 'CRAWL_EVERYTHING'
                },
                Configuration='{"Version":1.0,"CrawlerOutput":{"Partitions":{"AddOrUpdateBehavior":"InheritFromTable"}}}'
            )
            print(f'✅ Crawler "{name}" creado exitosamente')
            return True
            
        except Exception as e:
            print(f'❌ Error con crawler "{name}": {e}')
            return False
    
    def create_all_crawlers(self):
        """Crea los 3 crawlers necesarios para CSV"""
        self.print_banner('PASO 2: Creando Crawlers para CSV')
        
        crawlers = [
            {
                'name': 'passengers-csv-crawler',
                's3_path': f's3://{self.bucket_name}/raw/passengers_csv/',
                'description': 'Crawler for passengers CSV data',
                'table_prefix': ''
            },
            {
                'name': 'trips-csv-crawler',
                's3_path': f's3://{self.bucket_name}/raw/trips_csv/',
                'description': 'Crawler for trips CSV data',
                'table_prefix': ''
            },
            {
                'name': 'tickets-csv-crawler',
                's3_path': f's3://{self.bucket_name}/raw/tickets_csv/',
                'description': 'Crawler for tickets CSV data',
                'table_prefix': ''
            }
        ]
        
        results = []
        for crawler in crawlers:
            result = self.create_crawler(**crawler)
            results.append(result)
            time.sleep(1)  # Evitar throttling
        
        return all(results)
    
    def run_crawler(self, name):
        """Ejecuta un crawler"""
        try:
            # Verificar estado actual
            response = self.glue_client.get_crawler(Name=name)
            state = response['Crawler']['State']
            
            if state == 'RUNNING':
                print(f'⏳ Crawler "{name}" ya está en ejecución')
                return True
            
            # Iniciar crawler
            self.glue_client.start_crawler(Name=name)
            print(f'🚀 Crawler "{name}" iniciado')
            return True
            
        except Exception as e:
            print(f'❌ Error ejecutando crawler "{name}": {e}')
            return False
    
    def wait_for_crawler(self, name, timeout=300):
        """Espera a que un crawler termine"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.glue_client.get_crawler(Name=name)
                state = response['Crawler']['State']
                
                if state == 'READY':
                    print(f'✅ Crawler "{name}" completado')
                    
                    # Mostrar estadísticas
                    metrics = response['Crawler'].get('LastCrawl', {})
                    if metrics:
                        print(f'   Tablas creadas/actualizadas: {metrics.get("TablesCreated", 0) + metrics.get("TablesUpdated", 0)}')
                        print(f'   Estado: {metrics.get("Status", "N/A")}')
                    
                    return True
                elif state in ['STOPPING', 'RUNNING']:
                    print(f'⏳ Crawler "{name}" en ejecución... ({int(time.time() - start_time)}s)')
                    time.sleep(10)
                else:
                    print(f'⚠️  Crawler "{name}" en estado: {state}')
                    return False
                    
            except Exception as e:
                print(f'❌ Error verificando crawler "{name}": {e}')
                return False
        
        print(f'⏰ Timeout esperando crawler "{name}"')
        return False
    
    def run_all_crawlers(self, wait=True):
        """Ejecuta todos los crawlers"""
        self.print_banner('PASO 3: Ejecutando Crawlers')
        
        crawler_names = [
            'passengers-csv-crawler',
            'trips-csv-crawler',
            'tickets-csv-crawler'
        ]
        
        # Iniciar crawlers
        for name in crawler_names:
            self.run_crawler(name)
            time.sleep(2)
        
        # Esperar si se solicita
        if wait:
            print('\n⏳ Esperando a que los crawlers terminen...\n')
            for name in crawler_names:
                self.wait_for_crawler(name)
    
    def list_tables(self):
        """Lista las tablas creadas en el catálogo"""
        self.print_banner('PASO 4: Verificando Tablas Creadas')
        
        try:
            response = self.glue_client.get_tables(DatabaseName=self.database_name)
            tables = response.get('TableList', [])
            
            if not tables:
                print('⚠️  No se encontraron tablas en el catálogo')
                return []
            
            print(f'✅ Se encontraron {len(tables)} tabla(s):\n')
            
            for table in tables:
                print(f'📊 Tabla: {table["Name"]}')
                print(f'   Ubicación: {table.get("StorageDescriptor", {}).get("Location", "N/A")}')
                print(f'   Columnas: {len(table.get("StorageDescriptor", {}).get("Columns", []))}')
                print(f'   Formato: {table.get("StorageDescriptor", {}).get("InputFormat", "N/A")}')
                
                # Mostrar primeras 5 columnas
                columns = table.get('StorageDescriptor', {}).get('Columns', [])
                if columns:
                    print(f'   Primeras columnas:')
                    for col in columns[:5]:
                        print(f'     - {col["Name"]}: {col["Type"]}')
                print()
            
            return [t['Name'] for t in tables]
            
        except Exception as e:
            print(f'❌ Error listando tablas: {e}')
            return []
    
    def verify_s3_data(self):
        """Verifica que existan datos en S3"""
        self.print_banner('Verificando Datos en S3')
        
        paths = [
            'raw/passengers_csv/',
            'raw/trips_csv/',
            'raw/tickets_csv/'
        ]
        
        for path in paths:
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=path,
                    MaxKeys=10
                )
                
                count = response.get('KeyCount', 0)
                if count > 0:
                    print(f'✅ {path}: {count} archivo(s) encontrado(s)')
                    
                    # Mostrar primeros archivos
                    for obj in response.get('Contents', [])[:3]:
                        size_mb = obj['Size'] / (1024 * 1024)
                        print(f'   - {obj["Key"]} ({size_mb:.2f} MB)')
                else:
                    print(f'⚠️  {path}: No se encontraron archivos')
                    
            except Exception as e:
                print(f'❌ Error verificando {path}: {e}')
        
        print()
    
    def run_complete_setup(self):
        """Ejecuta el setup completo"""
        print('\n')
        print('╔' + '═' * 68 + '╗')
        print('║' + ' ' * 15 + 'AWS GLUE COMPLETE SETUP - BUS MVP' + ' ' * 20 + '║')
        print('╚' + '═' * 68 + '╝')
        print(f'\n📅 Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'🪣 Bucket S3: {self.bucket_name}')
        print(f'🗄️  Database: {self.database_name}')
        print(f'🌍 Region: {self.region}\n')
        
        # Verificar datos en S3
        self.verify_s3_data()
        
        # Paso 1: Crear database
        if not self.create_database():
            print('\n❌ Setup interrumpido: No se pudo crear la database')
            return False
        
        # Paso 2: Crear crawlers
        if not self.create_all_crawlers():
            print('\n❌ Setup interrumpido: No se pudieron crear los crawlers')
            return False
        
        # Paso 3: Ejecutar crawlers
        self.run_all_crawlers(wait=True)
        
        # Paso 4: Verificar tablas
        tables = self.list_tables()
        
        # Resumen final
        self.print_banner('RESUMEN DEL SETUP')
        print(f'✅ Database creada: {self.database_name}')
        print(f'✅ Crawlers creados: 3 (passengers, trips, tickets)')
        print(f'✅ Crawlers ejecutados: 3')
        print(f'✅ Tablas en catálogo: {len(tables)}')
        print('\n🎉 Setup completado exitosamente!\n')
        
        print('📋 PRÓXIMOS PASOS:')
        print('1. Verificar tablas en AWS Glue Console:')
        print(f'   https://console.aws.amazon.com/glue/home?region={self.region}#catalog:tab=databases')
        print('\n2. Ejecutar consultas SQL en AWS Athena Console:')
        print(f'   https://console.aws.amazon.com/athena/home?region={self.region}')
        print('\n3. Crear vistas usando: docs/analytics/athena_views.sql')
        print('4. Ejecutar consultas ejemplo: docs/analytics/athena_queries.sql\n')
        
        return True

def main():
    """Función principal"""
    try:
        setup = GlueSetup()
        success = setup.run_complete_setup()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print('\n\n⚠️  Setup interrumpido por el usuario')
        sys.exit(1)
    except Exception as e:
        print(f'\n\n❌ Error inesperado: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
