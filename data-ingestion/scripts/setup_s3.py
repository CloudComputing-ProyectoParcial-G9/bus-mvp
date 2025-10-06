#!/usr/bin/env python3
"""
Script para crear bucket S3 con la estructura necesaria
"""

import boto3
import sys
from datetime import datetime
from pathlib import Path

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    # Buscar el archivo .env en el directorio padre (data-ingestion/)
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f'✅ Variables de entorno cargadas desde: {env_path}')
    else:
        print(f'⚠️  No se encontró archivo .env en: {env_path}')
except ImportError:
    print('⚠️  python-dotenv no instalado. Usando variables de entorno del sistema.')
    pass

class S3Setup:
    def __init__(self, region='us-east-1'):
        self.s3 = boto3.client('s3', region_name=region)
        self.bucket_name = 'bus-mvp-datalake-1'
        self.region = region
    
    def create_bucket(self):
        """Crea el bucket S3"""
        try:
            if self.region == 'us-east-1':
                self.s3.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            print(f'✅ Bucket {self.bucket_name} creado exitosamente')
        except self.s3.exceptions.BucketAlreadyOwnedByYou:
            print(f'⚠️  Bucket {self.bucket_name} ya existe y es tuyo')
        except self.s3.exceptions.BucketAlreadyExists:
            print(f'❌ Bucket {self.bucket_name} ya existe (pertenece a otra cuenta)')
            sys.exit(1)
        except Exception as e:
            print(f'❌ Error creando bucket: {e}')
            sys.exit(1)
    
    def create_folder_structure(self):
        """Crea la estructura de carpetas"""
        folders = [
            'raw/passengers_csv/',
            'raw/passengers_json/',
            'raw/trips_csv/',
            'raw/trips_json/',
            'raw/tickets_csv/',
            'raw/tickets_json/',
            'processed/passengers/',
            'processed/trips/',
            'processed/tickets/',
            'athena-results/'
        ]
        
        print('\n📁 Creating folder structure...')
        for folder in folders:
            try:
                self.s3.put_object(
                    Bucket=self.bucket_name,
                    Key=folder,
                    Body=b''
                )
                print(f'  ✅ {folder}')
            except Exception as e:
                print(f'  ❌ Error creating {folder}: {e}')
    
    def enable_versioning(self):
        """Habilita versionamiento en el bucket"""
        try:
            self.s3.put_bucket_versioning(
                Bucket=self.bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            print(f'✅ Versioning habilitado en {self.bucket_name}')
        except Exception as e:
            print(f'❌ Error habilitando versioning: {e}')
    
    def setup_lifecycle_policy(self):
        """Configura política de lifecycle"""
        lifecycle_policy = {
            'Rules': [
                {
                    'Id': 'delete-old-data',
                    'Status': 'Enabled',
                    'Prefix': 'raw/',
                    'Expiration': {
                        'Days': 90
                    }
                },
                {
                    'Id': 'transition-to-ia',
                    'Status': 'Enabled',
                    'Prefix': 'raw/',
                    'Transitions': [
                        {
                            'Days': 30,
                            'StorageClass': 'STANDARD_IA'
                        }
                    ]
                }
            ]
        }
        
        try:
            self.s3.put_bucket_lifecycle_configuration(
                Bucket=self.bucket_name,
                LifecycleConfiguration=lifecycle_policy
            )
            print(f'✅ Lifecycle policy configurada')
        except Exception as e:
            print(f'⚠️  Error configurando lifecycle: {e}')
    
    def list_bucket_contents(self):
        """Lista el contenido del bucket"""
        print('\n📋 Bucket contents:')
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Delimiter='/'
            )
            
            if 'CommonPrefixes' in response:
                for prefix in response['CommonPrefixes']:
                    print(f"  📁 {prefix['Prefix']}")
        except Exception as e:
            print(f'❌ Error listing bucket: {e}')
    
    def setup_all(self):
        """Ejecuta el setup completo"""
        print('=' * 60)
        print('🚀 AWS S3 BUCKET SETUP')
        print('=' * 60)
        print(f'🪣 Bucket: {self.bucket_name}')
        print(f'🌎 Region: {self.region}')
        print(f'🕐 Started at: {datetime.now().isoformat()}')
        print('=' * 60)
        
        # Crear bucket
        print('\n📦 Step 1: Creating bucket...')
        self.create_bucket()
        
        # Crear estructura de carpetas
        print('\n📁 Step 2: Creating folder structure...')
        self.create_folder_structure()
        
        # Habilitar versionamiento
        print('\n🔄 Step 3: Enabling versioning...')
        self.enable_versioning()
        
        # Configurar lifecycle
        print('\n⏰ Step 4: Setting up lifecycle policy...')
        self.setup_lifecycle_policy()
        
        # Listar contenido
        self.list_bucket_contents()
        
        print('\n' + '=' * 60)
        print('✅ S3 BUCKET SETUP COMPLETED')
        print(f'🕐 Finished at: {datetime.now().isoformat()}')
        print('=' * 60)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        region = sys.argv[1]
    else:
        region = 'us-east-1'
    
    print(f'🌎 Using region: {region}')
    
    setup = S3Setup(region=region)
    setup.setup_all()

if __name__ == '__main__':
    main()
