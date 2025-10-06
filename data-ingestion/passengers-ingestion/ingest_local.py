import requests
import pandas as pd
import os
from datetime import datetime
import json
import sys

class PassengerIngestion:
    """
    Contenedor de ingesta para el microservicio de Pasajeros
    Extrae el 100% de los registros y los guarda localmente
    """
    
    def __init__(self):
        self.api_url = os.getenv('PASSENGERS_API_URL', 'http://host.docker.internal:8001/api/v1')
        self.output_dir = '/app/output'
        os.makedirs(self.output_dir, exist_ok=True)
        
    def extract_passengers(self):
        """Extrae el 100% de pasajeros desde la API con paginación"""
        all_passengers = []
        page = 1
        page_size = 100
        
        try:
            while True:
                print(f'🔍 Fetching passengers page {page} from {self.api_url}/passengers...')
                params = {
                    'page': page,
                    'limit': page_size
                }
                response = requests.get(f'{self.api_url}/passengers', params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, dict) and 'data' in data:
                    passengers = data['data']
                    has_more = data.get('hasMore', False) or data.get('pagination', {}).get('hasNextPage', False)
                elif isinstance(data, list):
                    passengers = data
                    has_more = len(passengers) == page_size
                else:
                    passengers = [data]
                    has_more = False
                
                if not passengers:
                    break
                    
                all_passengers.extend(passengers)
                print(f'✅ Retrieved {len(passengers)} passengers from page {page} (total: {len(all_passengers)})')
                
                if not has_more or len(passengers) < page_size:
                    break
                    
                page += 1
                
        except requests.exceptions.RequestException as e:
            print(f'❌ Error fetching passengers: {e}')
            sys.exit(1)
            
        print(f'✅ Total passengers retrieved: {len(all_passengers)}')
        return all_passengers
    
    def transform_to_dataframe(self, data):
        """Transforma datos a DataFrame de pandas"""
        if not data:
            print('⚠️  No data to transform')
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        df['ingestion_timestamp'] = datetime.now().isoformat()
        
        # Convert date fields if present
        date_columns = ['registration_date', 'date_of_birth', 'created_at', 'updated_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        print(f'🔄 Transformed {len(df)} records to DataFrame')
        print(f'📊 Columns: {list(df.columns)}')
        return df
    
    def save_locally(self, df):
        """Guarda datos localmente en formatos CSV y JSON"""
        if df.empty:
            print('⚠️  Empty DataFrame, skipping save')
            return None, None
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Save CSV
            csv_path = f'{self.output_dir}/passengers_{timestamp}.csv'
            df.to_csv(csv_path, index=False, date_format='%Y-%m-%d %H:%M:%S')
            print(f'✅ Saved CSV: {csv_path}')
            
            # Save JSON
            json_path = f'{self.output_dir}/passengers_{timestamp}.json'
            df.to_json(json_path, orient='records', date_format='iso', indent=2)
            print(f'✅ Saved JSON: {json_path}')
            
            return csv_path, json_path
            
        except Exception as e:
            print(f'❌ Error saving files: {e}')
            sys.exit(1)
    
    def run(self):
        """Ejecuta el pipeline completo de ingesta"""
        print('=' * 60)
        print('🚀 PASSENGERS INGESTION PIPELINE (LOCAL)')
        print('=' * 60)
        print(f'📍 API URL: {self.api_url}')
        print(f'📁 Output Directory: {self.output_dir}')
        print(f'🕐 Started at: {datetime.now().isoformat()}')
        print('=' * 60)
        
        # Extract
        data = self.extract_passengers()
        
        # Transform
        df = self.transform_to_dataframe(data)
        
        # Save locally
        csv_path, json_path = self.save_locally(df)
        
        print('=' * 60)
        print('✅ PASSENGERS INGESTION COMPLETED')
        print(f'📊 Total records ingested: {len(df)}')
        print(f'🕐 Finished at: {datetime.now().isoformat()}')
        print('=' * 60)

if __name__ == '__main__':
    ingestion = PassengerIngestion()
    ingestion.run()
