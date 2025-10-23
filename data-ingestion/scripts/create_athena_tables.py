#!/usr/bin/env python3
"""
Script para crear tablas en Athena con el esquema correcto (con skip.header.line.count)
"""

import boto3
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde la raíz del proyecto
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class AthenaTablesFix:
    def __init__(self):
        self.athena = boto3.client('athena', region_name='us-east-1')
        self.database = os.getenv('GLUE_DATABASE', 'bus_mvp_db')
        self.output_location = os.getenv('ATHENA_OUTPUT_LOCATION', 's3://bus-mvp-datalake-1/athena-results/')
        self.bucket = os.getenv('S3_BUCKET', 'bus-mvp-datalake-1')
        
    def execute_ddl(self, query, description=""):
        """Ejecuta una consulta DDL en Athena"""
        print(f"\n🔧 {description}")
        print("-" * 60)
        
        try:
            response = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': self.database},
                ResultConfiguration={'OutputLocation': self.output_location}
            )
            
            query_execution_id = response['QueryExecutionId']
            
            # Esperar a que termine
            while True:
                query_status = self.athena.get_query_execution(QueryExecutionId=query_execution_id)
                status = query_status['QueryExecution']['Status']['State']
                
                if status == 'SUCCEEDED':
                    print("✅ Ejecutado exitosamente")
                    return True
                elif status in ['FAILED', 'CANCELLED']:
                    reason = query_status['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                    print(f"❌ Falló: {reason}")
                    return False
                else:
                    time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def create_tables(self):
        """Crea las tablas con el esquema correcto"""
        print("="*60)
        print("🚀 CREANDO TABLAS EN ATHENA CON ESQUEMA CORRECTO")
        print("="*60)
        
        # Eliminar tablas existentes primero
        self.execute_ddl("DROP TABLE IF EXISTS passengers_csv", "Eliminando tabla passengers_csv anterior")
        self.execute_ddl("DROP TABLE IF EXISTS trips_csv", "Eliminando tabla trips_csv anterior")
        self.execute_ddl("DROP TABLE IF EXISTS tickets_csv", "Eliminando tabla tickets_csv anterior")
        
        # Tabla de Passengers
        self.execute_ddl(f"""
            CREATE EXTERNAL TABLE IF NOT EXISTS passengers_csv (
                full_name STRING,
                phone STRING,
                passenger_id STRING,
                document_number STRING,
                registration_date STRING,
                email STRING,
                document_type STRING,
                date_of_birth STRING,
                status STRING,
                ingestion_timestamp STRING
            )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
            LOCATION 's3://{self.bucket}/raw/passengers_csv/'
            TBLPROPERTIES ('skip.header.line.count'='1')
        """, "Creando tabla: passengers_csv")
        
        # Tabla de Trips
        self.execute_ddl(f"""
            CREATE EXTERNAL TABLE IF NOT EXISTS trips_csv (
                tripId STRING,
                routeId STRING,
                departureDateTime STRING,
                arrivalDateTime STRING,
                busCapacity INT,
                availableSeats INT,
                finalPrice DOUBLE,
                status STRING,
                driverName STRING,
                busPlate STRING,
                createdAt STRING,
                updatedAt STRING,
                ingestion_timestamp STRING
            )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
            LOCATION 's3://{self.bucket}/raw/trips_csv/'
            TBLPROPERTIES ('skip.header.line.count'='1')
        """, "Creando tabla: trips_csv")
        
        # Tabla de Tickets
        self.execute_ddl(f"""
            CREATE EXTERNAL TABLE IF NOT EXISTS tickets_csv (
                ticket_id STRING,
                passenger_id STRING,
                trip_id STRING,
                seat_number STRING,
                total_price DOUBLE,
                currency STRING,
                booking_status STRING,
                ingestion_timestamp STRING
            )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
            LOCATION 's3://{self.bucket}/raw/tickets_csv/'
            TBLPROPERTIES ('skip.header.line.count'='1')
        """, "Creando tabla: tickets_csv")
        
        print("\n" + "="*60)
        print("✅ TABLAS CREADAS EXITOSAMENTE")
        print("="*60)
        print("\nAhora puedes consultar:")
        print("  - SELECT * FROM passengers_csv LIMIT 5")
        print("  - SELECT * FROM trips_csv LIMIT 5")
        print("  - SELECT * FROM tickets_csv LIMIT 5")

def main():
    tables = AthenaTablesFix()
    tables.create_tables()

if __name__ == '__main__':
    main()
