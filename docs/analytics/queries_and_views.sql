-- ================================
-- CONSULTAS Y VISTAS DE EJEMPLO
-- Bus MVP - Analytics Layer
-- ================================

-- Este archivo contiene ejemplos de consultas SQL y vistas
-- para ser ejecutadas en un motor de consulta serverless
-- (AWS Athena, Google BigQuery, Azure Synapse, etc.)

-- ================================
-- CONSULTAS DE EJEMPLO (≥4)
-- ================================

-- CONSULTA 1: Ingresos por ruta y fecha
-- Calcula los ingresos totales agrupados por ruta y fecha
SELECT 
    t.route_code,
    t.origin_city,
    t.destination_city,
    DATE(t.departure_time) as travel_date,
    COUNT(tk.ticket_id) as total_tickets,
    SUM(tk.total_price) as total_revenue,
    AVG(tk.total_price) as avg_ticket_price,
    t.base_price,
    (SUM(tk.total_price) - (COUNT(tk.ticket_id) * t.base_price)) as price_variance
FROM trips_raw t
JOIN tickets_raw tk ON t.trip_id = tk.trip_id
WHERE t.year >= 2024 
    AND t.status = 'completed'
    AND tk.booking_status = 'confirmed'
GROUP BY 
    t.route_code, 
    t.origin_city, 
    t.destination_city,
    DATE(t.departure_time),
    t.base_price
ORDER BY total_revenue DESC, travel_date DESC;

-- CONSULTA 2: Top rutas por número de boletos vendidos
-- Identifica las rutas más populares por volumen de ventas
SELECT 
    t.route_code,
    CONCAT(t.origin_city, ' → ', t.destination_city) as route_description,
    COUNT(DISTINCT t.trip_id) as total_trips,
    COUNT(tk.ticket_id) as total_tickets_sold,
    SUM(tk.total_price) as total_revenue,
    AVG(t.bus_capacity) as avg_bus_capacity,
    ROUND(COUNT(tk.ticket_id) * 100.0 / (COUNT(DISTINCT t.trip_id) * AVG(t.bus_capacity)), 2) as occupancy_rate_percent,
    AVG(tk.total_price) as avg_ticket_price
FROM trips_raw t
LEFT JOIN tickets_raw tk ON t.trip_id = tk.trip_id 
    AND tk.booking_status = 'confirmed'
WHERE t.year = 2024 
    AND t.month >= 1
GROUP BY 
    t.route_code, 
    t.origin_city, 
    t.destination_city
HAVING COUNT(tk.ticket_id) > 0
ORDER BY total_tickets_sold DESC
LIMIT 20;

-- CONSULTA 3: Análisis de ocupación por día de la semana
-- Muestra patrones de demanda según día de la semana
SELECT 
    EXTRACT(dow FROM t.departure_time) as day_of_week,
    CASE EXTRACT(dow FROM t.departure_time)
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
    END as day_name,
    COUNT(DISTINCT t.trip_id) as total_trips,
    COUNT(tk.ticket_id) as tickets_sold,
    SUM(t.bus_capacity) as total_capacity,
    ROUND(COUNT(tk.ticket_id) * 100.0 / SUM(t.bus_capacity), 2) as avg_occupancy_rate,
    SUM(tk.total_price) as daily_revenue,
    AVG(tk.total_price) as avg_ticket_price
FROM trips_raw t
LEFT JOIN tickets_raw tk ON t.trip_id = tk.trip_id 
    AND tk.booking_status = 'confirmed'
WHERE t.year = 2024 
    AND t.status = 'completed'
    AND DATE(t.departure_time) >= DATE_SUB(CURRENT_DATE, INTERVAL 90 DAY)
GROUP BY 
    EXTRACT(dow FROM t.departure_time)
ORDER BY day_of_week;

-- CONSULTA 4: Análisis de pasajeros frecuentes y segmentación
-- Identifica patrones de comportamiento de pasajeros
SELECT 
    p.passenger_id,
    p.full_name,
    p.email,
    COUNT(tk.ticket_id) as total_trips,
    SUM(tk.total_price) as total_spent,
    AVG(tk.total_price) as avg_ticket_price,
    MIN(tk.purchase_date) as first_purchase,
    MAX(tk.purchase_date) as last_purchase,
    DATE_DIFF('day', MIN(tk.purchase_date), MAX(tk.purchase_date)) as customer_lifetime_days,
    COUNT(DISTINCT DATE(tk.purchase_date)) as active_days,
    COUNT(DISTINCT t.route_code) as routes_used,
    CASE 
        WHEN COUNT(tk.ticket_id) >= 20 THEN 'VIP'
        WHEN COUNT(tk.ticket_id) >= 10 THEN 'Frequent'
        WHEN COUNT(tk.ticket_id) >= 5 THEN 'Regular'
        ELSE 'Occasional'
    END as customer_segment
FROM passengers_raw p
JOIN tickets_raw tk ON p.passenger_id = tk.passenger_id
JOIN trips_raw t ON tk.trip_id = t.trip_id
WHERE p.status = 'active'
    AND tk.booking_status = 'confirmed'
    AND p.year = 2024
GROUP BY 
    p.passenger_id, 
    p.full_name, 
    p.email
HAVING COUNT(tk.ticket_id) >= 3
ORDER BY total_spent DESC;

-- ================================
-- VISTAS ANALÍTICAS (≥2)
-- ================================

-- VISTA 1: Dashboard de KPIs diarios
-- Métricas clave agregadas por día para dashboards
CREATE VIEW daily_kpis AS
SELECT 
    DATE(t.departure_time) as report_date,
    t.year,
    t.month,
    t.day,
    -- Métricas de viajes
    COUNT(DISTINCT t.trip_id) as total_trips,
    COUNT(DISTINCT t.route_code) as active_routes,
    SUM(t.bus_capacity) as total_capacity,
    
    -- Métricas de ventas
    COUNT(tk.ticket_id) as tickets_sold,
    COUNT(CASE WHEN tk.booking_status = 'confirmed' THEN 1 END) as confirmed_tickets,
    COUNT(CASE WHEN tk.booking_status = 'cancelled' THEN 1 END) as cancelled_tickets,
    
    -- Métricas financieras
    SUM(CASE WHEN tk.booking_status = 'confirmed' THEN tk.total_price ELSE 0 END) as daily_revenue,
    AVG(CASE WHEN tk.booking_status = 'confirmed' THEN tk.total_price END) as avg_ticket_price,
    SUM(CASE WHEN tk.booking_status = 'confirmed' THEN tk.total_price ELSE 0 END) / NULLIF(COUNT(DISTINCT t.trip_id), 0) as revenue_per_trip,
    
    -- Métricas de ocupación
    ROUND(COUNT(tk.ticket_id) * 100.0 / NULLIF(SUM(t.bus_capacity), 0), 2) as occupancy_rate,
    
    -- Métricas de pasajeros
    COUNT(DISTINCT tk.passenger_id) as unique_passengers,
    COUNT(DISTINCT p.passenger_id) as new_passengers_registered
    
FROM trips_raw t
LEFT JOIN tickets_raw tk ON t.trip_id = tk.trip_id
LEFT JOIN passengers_raw p ON tk.passenger_id = p.passenger_id 
    AND DATE(p.registration_date) = DATE(t.departure_time)
WHERE t.status IN ('completed', 'in_progress')
GROUP BY 
    DATE(t.departure_time),
    t.year,
    t.month, 
    t.day
ORDER BY report_date DESC;

-- VISTA 2: Ranking de rutas por performance
-- Vista consolidada del rendimiento de rutas para análisis de negocio
CREATE VIEW route_performance_ranking AS
SELECT 
    t.route_code,
    CONCAT(t.origin_city, ' → ', t.destination_city) as route_name,
    t.origin_city,
    t.destination_city,
    
    -- Métricas de operación
    COUNT(DISTINCT t.trip_id) as total_trips,
    COUNT(DISTINCT DATE(t.departure_time)) as operating_days,
    AVG(t.bus_capacity) as avg_capacity,
    
    -- Métricas de ventas
    COUNT(tk.ticket_id) as total_tickets,
    COUNT(CASE WHEN tk.booking_status = 'confirmed' THEN 1 END) as confirmed_tickets,
    ROUND(COUNT(CASE WHEN tk.booking_status = 'confirmed' THEN 1 END) * 100.0 / NULLIF(COUNT(tk.ticket_id), 0), 2) as confirmation_rate,
    
    -- Métricas financieras
    SUM(CASE WHEN tk.booking_status = 'confirmed' THEN tk.total_price ELSE 0 END) as total_revenue,
    AVG(CASE WHEN tk.booking_status = 'confirmed' THEN tk.total_price END) as avg_price,
    AVG(t.base_price) as avg_base_price,
    
    -- Métricas de eficiencia
    ROUND(COUNT(CASE WHEN tk.booking_status = 'confirmed' THEN 1 END) * 100.0 / 
          NULLIF(COUNT(DISTINCT t.trip_id) * AVG(t.bus_capacity), 0), 2) as avg_occupancy_rate,
    
    -- Métricas de popularidad
    COUNT(DISTINCT tk.passenger_id) as unique_passengers,
    ROUND(COUNT(tk.ticket_id) * 1.0 / NULLIF(COUNT(DISTINCT t.trip_id), 0), 2) as avg_tickets_per_trip,
    
    -- Ranking y scoring
    ROW_NUMBER() OVER (ORDER BY SUM(CASE WHEN tk.booking_status = 'confirmed' THEN tk.total_price ELSE 0 END) DESC) as revenue_rank,
    ROW_NUMBER() OVER (ORDER BY COUNT(CASE WHEN tk.booking_status = 'confirmed' THEN 1 END) DESC) as volume_rank,
    ROW_NUMBER() OVER (ORDER BY 
        ROUND(COUNT(CASE WHEN tk.booking_status = 'confirmed' THEN 1 END) * 100.0 / 
              NULLIF(COUNT(DISTINCT t.trip_id) * AVG(t.bus_capacity), 0), 2) DESC) as occupancy_rank
    
FROM trips_raw t
LEFT JOIN tickets_raw tk ON t.trip_id = tk.trip_id
WHERE t.year = 2024
    AND t.status IN ('completed', 'in_progress')
GROUP BY 
    t.route_code,
    t.origin_city,
    t.destination_city
HAVING COUNT(DISTINCT t.trip_id) >= 5  -- Filtrar rutas con al menos 5 viajes
ORDER BY total_revenue DESC;

-- ================================
-- CONSULTAS DE MANTENIMIENTO
-- ================================

-- Consulta para verificar calidad de datos
SELECT 
    'passengers_raw' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT passenger_id) as unique_ids,
    COUNT(*) - COUNT(passenger_id) as null_ids,
    MIN(year) as min_year,
    MAX(year) as max_year
FROM passengers_raw
UNION ALL
SELECT 
    'trips_raw' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT trip_id) as unique_ids,
    COUNT(*) - COUNT(trip_id) as null_ids,
    MIN(year) as min_year,
    MAX(year) as max_year
FROM trips_raw
UNION ALL
SELECT 
    'tickets_raw' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT ticket_id) as unique_ids,
    COUNT(*) - COUNT(ticket_id) as null_ids,
    MIN(year) as min_year,
    MAX(year) as max_year
FROM tickets_raw;

-- Consulta para monitorear particiones activas
SELECT 
    table_name,
    year,
    month,
    COUNT(*) as record_count,
    MAX(day) as last_day_with_data
FROM (
    SELECT 'passengers_raw' as table_name, year, month, day FROM passengers_raw
    UNION ALL
    SELECT 'trips_raw' as table_name, year, month, day FROM trips_raw
    UNION ALL
    SELECT 'tickets_raw' as table_name, year, month, day FROM tickets_raw
)
GROUP BY table_name, year, month
ORDER BY table_name, year DESC, month DESC;

-- ================================
-- NOTAS DE USO
-- ================================

/*
CONFIGURACIÓN REQUERIDA:

1. Variables de entorno del motor de consulta:
   - QUERY_OUTPUT_PATH: Ubicación para resultados de consulta
   - CATALOG_DATABASE: Nombre de la base de datos del catálogo
   - WORKGROUP: Grupo de trabajo del motor de consulta

2. Optimizaciones recomendadas:
   - Usar LIMIT en consultas exploratorias
   - Filtrar por particiones (year, month, day) para mejor performance
   - Considerar materializar vistas frecuentemente usadas

3. Consideraciones de costos:
   - Las consultas escanean datos según filtros de partición
   - Usar columnar formats (Parquet) para reducir scan costs
   - Implementar lifecycle policies para datos históricos

4. Monitoreo:
   - Ejecutar consultas de calidad de datos regularmente
   - Alertar sobre inconsistencias en foreign keys
   - Monitorear performance y optimizar índices según uso

TODO:
- [ ] Adaptar sintaxis SQL según motor elegido (Athena/BigQuery/Synapse)
- [ ] Configurar alertas automatizadas sobre anomalías en datos
- [ ] Crear dashboards usando herramientas de BI
- [ ] Implementar data quality checks automatizados
- [ ] Optimizar consultas según patrones de acceso reales
*/
