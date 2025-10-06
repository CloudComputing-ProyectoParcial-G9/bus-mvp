import requests
import pandas as pd
import boto3
from datetime import datetime
import os
import json
import sys

class TripIngestion:
    """
    Contenedor de ingesta para el microservicio de Viajes
    Extrae el 100% de los registros y los carga a S3
    """
    
    def __init__(self):
        self.api_url = os.getenv('TRIPS_API_URL', 'http://host.docker.internal:3002/api')
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv('S3_BUCKET', 'bus-mvp-datalake')
        
    def extract_trips(self):
        """Extrae el 100% de viajes desde la API con paginación"""
        all_trips = []
        page = 1
        page_size = 100
        
        try:
            while True:
                print(f'🔍 Fetching trips page {page} from {self.api_url}/trips...')
                params = {
                    'page': page,
                    'limit': page_size
                }
                response = requests.get(f'{self.api_url}/trips', params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, dict) and 'data' in data:
                    trips = data['data']
                    has_more = data.get('hasMore', False) or data.get('pagination', {}).get('hasNextPage', False)
                elif isinstance(data, list):
                    trips = data
                    has_more = len(trips) == page_size
                else:
                    trips = [data]
                    has_more = False
                
                if not trips:
                    break
                    
                all_trips.extend(trips)
                print(f'✅ Retrieved {len(trips)} trips from page {page} (total: {len(all_trips)})')
                
                if not has_more or len(trips) < page_size:
                    break
                    
                page += 1
                
            print(f'✅ Total trips retrieved: {len(all_trips)}')
            return all_trips
        except requests.exceptions.RequestException as e:
            print(f'❌ Error fetching trips: {e}')
            sys.exit(1)
    
    def transform_to_dataframe(self, data):
        """Transforma datos a DataFrame de pandas"""
        if not data:
            print('⚠️  No data to transform')
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        df['ingestion_timestamp'] = datetime.now().isoformat()
        
        # Convert date fields if present
        date_columns = ['departure_time', 'arrival_time', 'created_at', 'updated_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        print(f'🔄 Transformed {len(df)} records to DataFrame')
        print(f'📊 Columns: {list(df.columns)}')
        return df
    
    def load_to_s3(self, df):
        """Carga datos a S3 en formatos CSV y JSON"""
        if df.empty:
            print('⚠️  Empty DataFrame, skipping S3 upload')
            return None, None
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Upload CSV to trips_csv folder
            csv_key = f'raw/trips_csv/trips_{timestamp}.csv'
            csv_buffer = df.to_csv(index=False, date_format='%Y-%m-%d %H:%M:%S')
            self.s3_client.put_object(
                Bucket=self.bucket_name, 
                Key=csv_key, 
                Body=csv_buffer,
                ContentType='text/csv'
            )
            print(f'✅ Uploaded CSV: s3://{self.bucket_name}/{csv_key}')
            
            # Upload JSON to trips_json folder
            json_key = f'raw/trips_json/trips_{timestamp}.json'
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
        print('🚀 TRIPS INGESTION PIPELINE')
        print('=' * 60)
        print(f'📍 API URL: {self.api_url}')
        print(f'📦 S3 Bucket: {self.bucket_name}')
        print(f'🕐 Started at: {datetime.now().isoformat()}')
        print('=' * 60)
        
        # Extract
        data = self.extract_trips()
        
        # Transform
        df = self.transform_to_dataframe(data)
        
        # Load
        csv_key, json_key = self.load_to_s3(df)
        
        print('=' * 60)
        print('✅ TRIPS INGESTION COMPLETED')
        print(f'📊 Total records ingested: {len(df)}')
        print(f'🕐 Finished at: {datetime.now().isoformat()}')
        print('=' * 60)

if __name__ == '__main__':
    ingestion = TripIngestion()
    ingestion.run()
