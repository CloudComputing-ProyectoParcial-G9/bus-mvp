"""
Analytics API - Bus MVP
Servicio REST para consultas analíticas usando AWS Athena
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import boto3
import time
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# AWS Configuration
athena = boto3.client('athena')
DATABASE = os.getenv('GLUE_DATABASE', 'bus_mvp_db')
OUTPUT_LOCATION = os.getenv('ATHENA_OUTPUT_LOCATION', 's3://bus-mvp-datalake/athena-results/')

def execute_query(query, timeout=30):
    """
    Ejecuta una query en Athena y retorna los resultados
    """
    try:
        # Iniciar ejecución de la query
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': DATABASE},
            ResultConfiguration={'OutputLocation': OUTPUT_LOCATION}
        )
        
        query_id = response['QueryExecutionId']
        
        # Esperar a que la query termine
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                return {'error': 'Query timeout'}
            
            status = athena.get_query_execution(QueryExecutionId=query_id)
            state = status['QueryExecution']['Status']['State']
            
            if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
            
            time.sleep(1)
        
        if state == 'SUCCEEDED':
            # Obtener resultados
            results = athena.get_query_results(QueryExecutionId=query_id)
            
            # Parsear resultados
            columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
            rows = []
            
            for row in results['ResultSet']['Rows'][1:]:  # Skip header row
                row_data = {}
                for i, col in enumerate(columns):
                    value = row['Data'][i].get('VarCharValue', None)
                    row_data[col] = value
                rows.append(row_data)
            
            return {
                'success': True,
                'data': rows,
                'count': len(rows),
                'columns': columns
            }
        else:
            error_msg = status['QueryExecution']['Status'].get('StateChangeReason', 'Query failed')
            return {
                'success': False,
                'error': error_msg
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def home():
    """Endpoint de bienvenida"""
    return jsonify({
        'service': 'Bus MVP Analytics API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'GET /api/analytics/top-passengers': 'Top pasajeros con más tickets',
            'GET /api/analytics/popular-routes': 'Rutas más populares',
            'GET /api/analytics/daily-sales': 'Ventas diarias',
            'GET /api/analytics/occupancy-rate': 'Tasa de ocupación',
            'GET /api/analytics/revenue-by-route': 'Ingresos por ruta',
            'GET /api/analytics/customer-tiers': 'Distribución de clientes por tier',
            'POST /api/analytics/custom-query': 'Ejecutar query personalizada'
        }
    })

@app.route('/api/analytics/top-passengers', methods=['GET'])
def top_passengers():
    """Top pasajeros con más tickets comprados"""
    limit = request.args.get('limit', 10)
    
    query = f"""
    SELECT * FROM top_passengers
    LIMIT {limit}
    """
    
    result = execute_query(query)
    return jsonify(result)

@app.route('/api/analytics/popular-routes', methods=['GET'])
def popular_routes():
    """Rutas más populares"""
    limit = request.args.get('limit', 10)
    
    query = f"""
    SELECT * FROM popular_routes
    ORDER BY total_trips DESC
    LIMIT {limit}
    """
    
    result = execute_query(query)
    return jsonify(result)

@app.route('/api/analytics/daily-sales', methods=['GET'])
def daily_sales():
    """Ventas diarias"""
    days = request.args.get('days', 30)
    
    query = f"""
    SELECT * FROM daily_sales_summary
    ORDER BY sale_date DESC
    LIMIT {days}
    """
    
    result = execute_query(query)
    return jsonify(result)

@app.route('/api/analytics/occupancy-rate', methods=['GET'])
def occupancy_rate():
    """Tasa de ocupación promedio"""
    query = """
    SELECT 
        AVG(occupancy_percent) as avg_occupancy_rate,
        MIN(occupancy_percent) as min_occupancy_rate,
        MAX(occupancy_percent) as max_occupancy_rate,
        COUNT(*) as total_trips
    FROM trip_performance
    WHERE occupancy_percent IS NOT NULL
    """
    
    result = execute_query(query)
    return jsonify(result)

@app.route('/api/analytics/revenue-by-route', methods=['GET'])
def revenue_by_route():
    """Ingresos totales por ruta"""
    query = """
    SELECT 
        origin,
        destination,
        route_name,
        total_revenue,
        total_trips,
        tickets_sold,
        avg_ticket_price
    FROM popular_routes
    ORDER BY total_revenue DESC
    LIMIT 20
    """
    
    result = execute_query(query)
    return jsonify(result)

@app.route('/api/analytics/customer-tiers', methods=['GET'])
def customer_tiers():
    """Distribución de clientes por tier"""
    query = """
    SELECT 
        customer_tier,
        COUNT(*) as customer_count,
        SUM(total_tickets) as total_tickets,
        SUM(total_spent) as total_revenue
    FROM top_passengers
    GROUP BY customer_tier
    ORDER BY 
        CASE customer_tier
            WHEN 'VIP' THEN 1
            WHEN 'Frecuente' THEN 2
            WHEN 'Regular' THEN 3
            WHEN 'Ocasional' THEN 4
        END
    """
    
    result = execute_query(query)
    return jsonify(result)

@app.route('/api/analytics/trip-performance', methods=['GET'])
def trip_performance():
    """Performance de viajes"""
    rating = request.args.get('rating', None)
    limit = request.args.get('limit', 50)
    
    if rating:
        query = f"""
        SELECT * FROM trip_performance
        WHERE performance_rating = '{rating}'
        ORDER BY occupancy_percent DESC
        LIMIT {limit}
        """
    else:
        query = f"""
        SELECT * FROM trip_performance
        ORDER BY occupancy_percent DESC
        LIMIT {limit}
        """
    
    result = execute_query(query)
    return jsonify(result)

@app.route('/api/analytics/summary', methods=['GET'])
def summary():
    """Resumen general de analytics"""
    query = """
    SELECT 
        (SELECT COUNT(*) FROM passengers) as total_passengers,
        (SELECT COUNT(*) FROM trips) as total_trips,
        (SELECT COUNT(*) FROM tickets) as total_tickets,
        (SELECT SUM(price) FROM tickets) as total_revenue,
        (SELECT AVG(occupancy_percent) FROM trip_performance) as avg_occupancy_rate
    """
    
    result = execute_query(query)
    return jsonify(result)

@app.route('/api/analytics/custom-query', methods=['POST'])
def custom_query():
    """Ejecutar query personalizada"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({
            'success': False,
            'error': 'Query is required'
        }), 400
    
    query = data['query']
    
    # Validación básica de seguridad
    forbidden_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']
    if any(keyword in query.upper() for keyword in forbidden_keywords):
        return jsonify({
            'success': False,
            'error': 'Query contains forbidden keywords'
        }), 400
    
    result = execute_query(query)
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'analytics-api'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print('=' * 60)
    print('🚀 Analytics API Server Starting')
    print('=' * 60)
    print(f'📊 Database: {DATABASE}')
    print(f'📍 Output Location: {OUTPUT_LOCATION}')
    print(f'🌐 Port: {port}')
    print('=' * 60)
    
    app.run(host='0.0.0.0', port=port, debug=True)
