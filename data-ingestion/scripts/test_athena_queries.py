#!/usr/bin/env python3
"""
Script para ejecutar consultas de ejemplo en Amazon Athena
"""

import boto3
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde la raíz del proyecto
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class AthenaQueries:
    def __init__(self):
        self.athena = boto3.client('athena', region_name='us-east-1')
        self.database = os.getenv('GLUE_DATABASE', 'bus_mvp_db')
        self.output_location = os.getenv('ATHENA_OUTPUT_LOCATION', 's3://bus-mvp-datalake-1/athena-results/')
        
    def execute_query(self, query, description=""):
        """Ejecuta una consulta en Athena y espera los resultados"""
        print(f"\n{'='*60}")
        print(f"🔍 {description}")
        print(f"{'='*60}")
        print(f"Query: {query[:100]}...")
        
        try:
            # Iniciar ejecución
            response = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': self.database},
                ResultConfiguration={'OutputLocation': self.output_location}
            )
            
            query_execution_id = response['QueryExecutionId']
            print(f"Query ID: {query_execution_id}")
            
            # Esperar a que termine
            while True:
                query_status = self.athena.get_query_execution(QueryExecutionId=query_execution_id)
                status = query_status['QueryExecution']['Status']['State']
                
                if status == 'SUCCEEDED':
                    print("✅ Query ejecutada exitosamente")
                    break
                elif status in ['FAILED', 'CANCELLED']:
                    reason = query_status['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                    print(f"❌ Query falló: {reason}")
                    return None
                else:
                    print(f"⏳ Estado: {status}...")
                    time.sleep(2)
            
            # Obtener resultados
            results = self.athena.get_query_results(QueryExecutionId=query_execution_id)
            
            # Mostrar resultados
            rows = results['ResultSet']['Rows']
            print(f"\n📊 Resultados ({len(rows)-1} filas):")
            print("-" * 60)
            
            # Encabezados
            headers = [col['VarCharValue'] for col in rows[0]['Data']]
            print(" | ".join(headers))
            print("-" * 60)
            
            # Datos (máximo 10 filas)
            for row in rows[1:11]:
                values = [col.get('VarCharValue', 'NULL') for col in row['Data']]
                print(" | ".join(values))
            
            if len(rows) > 11:
                print(f"... y {len(rows)-11} filas más")
            
            return results
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def run_example_queries(self):
        """Ejecuta un conjunto de consultas de ejemplo"""
        print("\n" + "="*60)
        print("🚀 ATHENA - CONSULTAS DE EJEMPLO")
        print("="*60)
        print(f"Database: {self.database}")
        print(f"Output: {self.output_location}")
        
        # Consulta 1: Contar pasajeros
        self.execute_query(
            "SELECT COUNT(*) as total_passengers FROM passengers_csv",
            "Total de Pasajeros"
        )

        # Consulta 2: Contar viajes
        self.execute_query(
            "SELECT COUNT(*) as total_trips FROM trips_csv",
            "Total de Viajes"
        )

        # Consulta 3: Contar tickets
        self.execute_query(
            "SELECT COUNT(*) as total_tickets FROM tickets_csv",
            "Total de Tickets"
        )

        # Consulta 4: Primeros 5 pasajeros
        self.execute_query(
            """
            SELECT passenger_id, full_name, email, phone
            FROM passengers_csv
            LIMIT 5
            """,
            "Primeros 5 Pasajeros"
        )

        # Consulta 5: Viajes con información
        self.execute_query(
            """
            SELECT tripid, routeid, departuredatetime, finalprice, status
            FROM trips_csv
            LIMIT 5
            """,
            "Primeros 5 Viajes"
        )

        # Consulta 6: Tickets con detalles
        self.execute_query(
            """
            SELECT ticket_id, passenger_id, trip_id, total_price, seat_number
            FROM tickets_csv
            LIMIT 5
            """,
            "Primeros 5 Tickets"
        )

        # Consulta 7: Análisis - Tickets por viaje (TOP 5)
        self.execute_query(
            """
            SELECT trip_id, COUNT(*) as total_tickets
            FROM tickets_csv
            GROUP BY trip_id
            ORDER BY total_tickets DESC
            LIMIT 5
            """,
            "Top 5 Viajes con Más Tickets Vendidos"
        )

        # Consulta 8: Análisis - Ingresos totales
        self.execute_query(
            """
            SELECT
                SUM(total_price) as total_revenue,
                AVG(total_price) as avg_ticket_price,
                COUNT(*) as total_tickets
            FROM tickets_csv
            """,
            "Análisis de Ingresos"
        )
        
        print("\n" + "="*60)
        print("✅ CONSULTAS COMPLETADAS")
        print("="*60)

def main():
    """Función principal"""
    queries = AthenaQueries()
    queries.run_example_queries()

if __name__ == '__main__':
    main()
