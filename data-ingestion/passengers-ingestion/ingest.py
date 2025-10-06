import requests
import pandas as pd
import boto3
from datetime import datetime
import os
import json
import sys

class PassengerIngestion:
    """
    Contenedor de ingesta para el microservicio de Pasajeros
    Extrae el 100% de los registros y los carga a S3
    """
    
    def __init__(self):
        self.api_url = os.getenv('PASSENGERS_API_URL', 'http://host.docker.internal:3001/api')
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv('S3_BUCKET', 'bus-mvp-datalake-1')
        
    def extract_passengers(self):
        """Extrae el 100% de pasajeros desde la API"""
        try:
            print(f'🔍 Fetching passengers from {self.api_url}/passengers...')
            response = requests.get(f'{self.api_url}/passengers', timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, dict) and 'data' in data:
                passengers = data['data']
            elif isinstance(data, list):
                passengers = data
            else:
                passengers = [data]
                
            print(f'✅ Retrieved {len(passengers)} passengers')
            return passengers
        except requests.exceptions.RequestException as e:
            print(f'❌ Error fetching passengers: {e}')
            sys.exit(1)
    
    def transform_to_dataframe(self, data):
        """Transforma datos a DataFrame de pandas"""
        if not data:
            print('⚠️  No data to transform')
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        df['ingestion_timestamp'] = datetime.now().isoformat()
        
        print(f'🔄 Transformed {len(df)} records to DataFrame')
        print(f'📊 Columns: {list(df.columns)}')
        return df
    
    def load_to_s3(self, df):
        """Carga datos a S3 en formatos CSV y JSON en carpetas separadas"""
        if df.empty:
            print('⚠️  Empty DataFrame, skipping S3 upload')
            return None, None
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Upload CSV to passengers_csv folder
            csv_key = f'raw/passengers_csv/passengers_{timestamp}.csv'
            csv_buffer = df.to_csv(index=False)
            self.s3_client.put_object(
                Bucket=self.bucket_name, 
                Key=csv_key, 
                Body=csv_buffer,
                ContentType='text/csv'
            )
            print(f'✅ Uploaded CSV: s3://{self.bucket_name}/{csv_key}')
            
            # Upload JSON to passengers_json folder
            json_key = f'raw/passengers_json/passengers_{timestamp}.json'
            json_buffer = df.to_json(orient='records', date_format='iso', indent=2)
            self.s3_client.put_object(
                Bucket=self.bucket_name, 
                Key=json_key, 
                Body=json_buffer,
                ContentType='application/json'
            )
            print(f'✅ Uploaded JSON: s3://{self.bucket_name}/{json_key}')
            
            return csv_key, json_key
            
        except Exception as e:
            print(f'❌ Error uploading to S3: {e}')
            sys.exit(1)
    
    def run(self):
        """Ejecuta el pipeline completo de ingesta"""
        print('=' * 60)
        print('🚀 PASSENGERS INGESTION PIPELINE')
        print('=' * 60)
        print(f'📍 API URL: {self.api_url}')
        print(f'📦 S3 Bucket: {self.bucket_name}')
        print(f'🕐 Started at: {datetime.now().isoformat()}')
        print('=' * 60)
        
        # Extract
        data = self.extract_passengers()
        
        # Transform
        df = self.transform_to_dataframe(data)
        
        # Load
        csv_key, json_key = self.load_to_s3(df)
        
        print('=' * 60)
        print('✅ PASSENGERS INGESTION COMPLETED')
        print(f'📊 Total records ingested: {len(df)}')
        print(f'🕐 Finished at: {datetime.now().isoformat()}')
        print('=' * 60)

if __name__ == '__main__':
    ingestion = PassengerIngestion()
    ingestion.run()
