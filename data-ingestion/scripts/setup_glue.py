#!/usr/bin/env python3
"""
Script para configurar AWS Glue Catalog
Crea database, crawlers y ejecuta el proceso de catalogación
"""

import boto3
import sys
import time
import os
from datetime import datetime
from pathlib import Path

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    # Buscar el archivo .env en la raíz del proyecto
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f'✅ Variables de entorno cargadas desde: {env_path}')
    else:
        print(f'⚠️  No se encontró archivo .env en: {env_path}')
except ImportError:
    print('⚠️  python-dotenv no instalado. Usando variables de entorno del sistema.')
    pass

class GlueSetup:
    def __init__(self, region='us-east-1'):
        self.glue = boto3.client('glue', region_name=region)
        self.sts = boto3.client('sts', region_name=region)
        self.database_name = 'bus_mvp_db'
        self.bucket_name = 'bus-mvp-datalake-1'
        
        # Obtener Account ID automáticamente
        account_id = self._get_account_id()
        
        # Para AWS Academy Lab, usa: arn:aws:iam::ACCOUNT_ID:role/LabRole
        # Para cuenta AWS normal, usa: arn:aws:iam::ACCOUNT_ID:role/AWSGlueServiceRole
        self.role_arn = f'arn:aws:iam::{account_id}:role/LabRole'
        print(f'🔑 Using IAM Role: {self.role_arn}')
    
    def _get_account_id(self):
        """Obtiene el Account ID de AWS automáticamente"""
        try:
            # Intenta obtenerlo desde variable de entorno
            account_id = os.getenv('AWS_ACCOUNT_ID')
            if account_id:
                print(f'✅ Account ID obtenido desde variable de entorno: {account_id}')
                return account_id
            
            # Si no existe, lo obtiene usando AWS STS
            identity = self.sts.get_caller_identity()
            account_id = identity['Account']
            print(f'✅ Account ID obtenido desde AWS STS: {account_id}')
            return account_id
        except Exception as e:
            print(f'❌ Error obteniendo Account ID: {e}')
            print('💡 Tip: Define la variable de entorno AWS_ACCOUNT_ID o verifica tus credenciales AWS')
            sys.exit(1)
        
    def create_database(self):
        """Crea la database en Glue Catalog"""
        try:
            self.glue.create_database(
                DatabaseInput={
                    'Name': self.database_name,
                    'Description': 'Database para analytics de Bus MVP',
                    'LocationUri': f's3://{self.bucket_name}/raw/'
                }
            )
            print(f'✅ Database {self.database_name} creada exitosamente')
        except self.glue.exceptions.AlreadyExistsException:
            print(f'⚠️  Database {self.database_name} ya existe')
        except Exception as e:
            print(f'❌ Error creando database: {e}')
            sys.exit(1)
    
    def create_crawler(self, name, path, table_prefix=''):
        """Crea un crawler para una tabla específica"""
        try:
            self.glue.create_crawler(
                Name=name,
                Role=self.role_arn,
                DatabaseName=self.database_name,
                Description=f'Crawler for {name}',
                Targets={
                    'S3Targets': [
                        {
                            'Path': f's3://{self.bucket_name}/raw/{path}/'
                        }
                    ]
                },
                TablePrefix=table_prefix,
                SchemaChangePolicy={
                    'UpdateBehavior': 'UPDATE_IN_DATABASE',
                    'DeleteBehavior': 'LOG'
                },
                RecrawlPolicy={
                    'RecrawlBehavior': 'CRAWL_EVERYTHING'
                }
            )
            print(f'✅ Crawler {name} creado exitosamente')
        except self.glue.exceptions.AlreadyExistsException:
            print(f'⚠️  Crawler {name} ya existe')
        except Exception as e:
            print(f'❌ Error creando crawler {name}: {e}')
    
    def start_crawler(self, name):
        """Inicia un crawler"""
        try:
            self.glue.start_crawler(Name=name)
            print(f'🚀 Crawler {name} iniciado')
        except Exception as e:
            print(f'❌ Error iniciando crawler {name}: {e}')
    
    def wait_for_crawler(self, name):
        """Espera a que un crawler termine"""
        print(f'⏳ Esperando que crawler {name} termine...')
        while True:
            response = self.glue.get_crawler(Name=name)
            state = response['Crawler']['State']
            
            if state == 'READY':
                print(f'✅ Crawler {name} completado')
                break
            elif state == 'RUNNING':
                print(f'⏳ Crawler {name} aún corriendo...')
                time.sleep(10)
            else:
                print(f'⚠️  Crawler {name} en estado: {state}')
                time.sleep(10)
    
    def setup_all(self):
        """Ejecuta el setup completo"""
        print('=' * 60)
        print('🚀 AWS GLUE CATALOG SETUP')
        print('=' * 60)
        print(f'🕐 Started at: {datetime.now().isoformat()}')
        print('=' * 60)
        
        # Crear database
        print('\n📊 Step 1: Creating database...')
        self.create_database()
        
        # Crear crawlers
        print('\n🕷️  Step 2: Creating crawlers...')
        crawlers = [
            ('passengers-crawler', 'passengers'),
            ('trips-crawler', 'trips'),
            ('tickets-crawler', 'tickets')
        ]
        
        for crawler_name, path in crawlers:
            self.create_crawler(crawler_name, path)
        
        # Iniciar crawlers
        print('\n🚀 Step 3: Starting crawlers...')
        for crawler_name, _ in crawlers:
            self.start_crawler(crawler_name)
        
        # Esperar a que terminen
        print('\n⏳ Step 4: Waiting for crawlers to complete...')
        for crawler_name, _ in crawlers:
            self.wait_for_crawler(crawler_name)
        
        print('\n' + '=' * 60)
        print('✅ GLUE CATALOG SETUP COMPLETED')
        print(f'🕐 Finished at: {datetime.now().isoformat()}')
        print('=' * 60)
        
        # Listar tablas creadas
        self.list_tables()
    
    def list_tables(self):
        """Lista las tablas en el catálogo"""
        print('\n📋 Tables in catalog:')
        try:
            response = self.glue.get_tables(DatabaseName=self.database_name)
            for table in response['TableList']:
                print(f"  - {table['Name']} ({table.get('StorageDescriptor', {}).get('Location', 'N/A')})")
        except Exception as e:
            print(f'❌ Error listing tables: {e}')

def main():
    """Main function"""
    # Verificar argumentos
    if len(sys.argv) > 1:
        region = sys.argv[1]
    else:
        region = 'us-east-1'
    
    print(f'🌎 Region: {region}')
    
    # Ejecutar setup
    setup = GlueSetup(region=region)
    setup.setup_all()

if __name__ == '__main__':
    main()
