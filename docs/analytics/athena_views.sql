-- ============================================================================
-- VISTAS EN AWS ATHENA - Bus MVP Analytics
-- ============================================================================
-- Base de Datos: bus_mvp_db
-- Propósito: Crear 2 vistas para simplificar consultas analíticas recurrentes
-- ============================================================================

-- ============================================================================
-- VISTA 1: passenger_sales_summary
-- ============================================================================
-- Descripción: Vista consolidada del historial de compras y comportamiento
--              de cada pasajero con métricas de valor del cliente
-- 
-- Uso: Programa de fidelización, segmentación de clientes, análisis RFM
-- ============================================================================

CREATE OR REPLACE VIEW passenger_sales_summary AS
SELECT 
    -- Identificación del Pasajero
    p.passenger_id,
    p.full_name,
    p.email,
    p.phone,
    p.document_type,
    p.document_number,
    p.registration_date,
    p.status as passenger_status,
    
    -- Métricas de Compra
    COUNT(t.ticket_id) as total_tickets_purchased,
    COUNT(DISTINCT t.trip_id) as total_trips_taken,
    COUNT(CASE WHEN t.booking_status = 'confirmed' THEN 1 END) as confirmed_tickets,
    COUNT(CASE WHEN t.booking_status = 'cancelled' THEN 1 END) as cancelled_tickets,
    COUNT(CASE WHEN t.booking_status = 'reserved' THEN 1 END) as reserved_tickets,
    
    -- Métricas Financieras
    SUM(CASE WHEN t.booking_status != 'cancelled' THEN t.total_price ELSE 0 END) as total_revenue,
    SUM(CASE WHEN t.booking_status = 'cancelled' THEN t.total_price ELSE 0 END) as cancelled_revenue,
    AVG(CASE WHEN t.booking_status != 'cancelled' THEN t.total_price END) as avg_ticket_price,
    MIN(CASE WHEN t.booking_status != 'cancelled' THEN t.total_price END) as min_ticket_price,
    MAX(CASE WHEN t.booking_status != 'cancelled' THEN t.total_price END) as max_ticket_price,
    
    -- Métricas Temporales (RFM Analysis)
    MIN(t.purchase_date) as first_purchase_date,
    MAX(t.purchase_date) as last_purchase_date,
    DATE_DIFF('day', MIN(t.purchase_date), MAX(t.purchase_date)) as customer_lifetime_days,
    DATE_DIFF('day', MAX(t.purchase_date), CURRENT_DATE) as days_since_last_purchase,
    
    -- Frecuencia de Compra
    CASE 
        WHEN COUNT(t.ticket_id) >= 10 THEN 'VIP'
        WHEN COUNT(t.ticket_id) >= 5 THEN 'Frequent'
        WHEN COUNT(t.ticket_id) >= 2 THEN 'Regular'
        ELSE 'Occasional'
    END as customer_segment,
    
    -- Estado de Actividad
    CASE 
        WHEN DATE_DIFF('day', MAX(t.purchase_date), CURRENT_DATE) <= 30 THEN 'Active'
        WHEN DATE_DIFF('day', MAX(t.purchase_date), CURRENT_DATE) <= 90 THEN 'At Risk'
        WHEN DATE_DIFF('day', MAX(t.purchase_date), CURRENT_DATE) <= 180 THEN 'Inactive'
        ELSE 'Churned'
    END as activity_status,
    
    -- Tasa de Cancelación
    ROUND(
        COUNT(CASE WHEN t.booking_status = 'cancelled' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(t.ticket_id), 0), 
        2
    ) as cancellation_rate_percentage

FROM passengers p
LEFT JOIN tickets t ON p.passenger_id = t.passenger_id
GROUP BY 
    p.passenger_id,
    p.full_name,
    p.email,
    p.phone,
    p.document_type,
    p.document_number,
    p.registration_date,
    p.status;

-- ============================================================================
-- Ejemplos de Uso de la Vista: passenger_sales_summary
-- ============================================================================

-- Ejemplo 1: Top 20 clientes por valor total
-- SELECT * FROM passenger_sales_summary 
-- ORDER BY total_revenue DESC 
-- LIMIT 20;

-- Ejemplo 2: Clientes VIP activos para programa de lealtad
-- SELECT * FROM passenger_sales_summary 
-- WHERE customer_segment = 'VIP' AND activity_status = 'Active';

-- Ejemplo 3: Clientes en riesgo de abandono
-- SELECT * FROM passenger_sales_summary 
-- WHERE activity_status = 'At Risk' AND total_revenue > 1000;

-- Ejemplo 4: Análisis de cancelaciones
-- SELECT customer_segment, AVG(cancellation_rate_percentage) as avg_cancellation
-- FROM passenger_sales_summary
-- GROUP BY customer_segment;


-- ============================================================================
-- VISTA 2: trip_occupancy_revenue
-- ============================================================================
-- Descripción: Vista de rendimiento de viajes con métricas de ocupación,
--              ingresos, y eficiencia operativa para análisis de rutas
-- 
-- Uso: Optimización de rutas, planificación de capacidad, análisis de rentabilidad
-- ============================================================================

CREATE OR REPLACE VIEW trip_occupancy_revenue AS
SELECT 
    -- Información del Viaje
    tr.trip_id,
    tr.route_id,
    tr.departure_time,
    tr.arrival_time,
    CAST(tr.departure_time AS DATE) as departure_date,
    DATE_FORMAT(tr.departure_time, '%Y-%m') as year_month,
    EXTRACT(DOW FROM tr.departure_time) as day_of_week_number,
    CASE EXTRACT(DOW FROM tr.departure_time)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_of_week_name,
    EXTRACT(HOUR FROM tr.departure_time) as departure_hour,
    tr.status as trip_status,
    tr.driver_name,
    tr.bus_plate,
    
    -- Capacidad y Ocupación
    tr.bus_capacity,
    tr.available_seats,
    (tr.bus_capacity - tr.available_seats) as seats_sold,
    COUNT(ti.ticket_id) as tickets_count,
    
    -- Porcentaje de Ocupación
    ROUND(
        (tr.bus_capacity - tr.available_seats) * 100.0 / 
        NULLIF(tr.bus_capacity, 0), 
        2
    ) as occupancy_percentage,
    
    -- Clasificación de Ocupación
    CASE 
        WHEN (tr.bus_capacity - tr.available_seats) * 100.0 / NULLIF(tr.bus_capacity, 0) >= 90 THEN 'Full'
        WHEN (tr.bus_capacity - tr.available_seats) * 100.0 / NULLIF(tr.bus_capacity, 0) >= 70 THEN 'High'
        WHEN (tr.bus_capacity - tr.available_seats) * 100.0 / NULLIF(tr.bus_capacity, 0) >= 50 THEN 'Medium'
        WHEN (tr.bus_capacity - tr.available_seats) * 100.0 / NULLIF(tr.bus_capacity, 0) >= 30 THEN 'Low'
        ELSE 'Very Low'
    END as occupancy_level,
    
    -- Métricas Financieras
    SUM(CASE WHEN ti.booking_status != 'cancelled' THEN ti.total_price ELSE 0 END) as total_revenue,
    SUM(CASE WHEN ti.booking_status = 'cancelled' THEN ti.total_price ELSE 0 END) as lost_revenue,
    AVG(CASE WHEN ti.booking_status != 'cancelled' THEN ti.total_price END) as avg_ticket_price,
    MIN(CASE WHEN ti.booking_status != 'cancelled' THEN ti.total_price END) as min_ticket_price,
    MAX(CASE WHEN ti.booking_status != 'cancelled' THEN ti.total_price END) as max_ticket_price,
    
    -- Ingresos por Asiento
    ROUND(
        SUM(CASE WHEN ti.booking_status != 'cancelled' THEN ti.total_price ELSE 0 END) / 
        NULLIF(tr.bus_capacity, 0),
        2
    ) as revenue_per_seat,
    
    -- Utilización de Capacidad (Revenue per Available Seat)
    ROUND(
        SUM(CASE WHEN ti.booking_status != 'cancelled' THEN ti.total_price ELSE 0 END) / 
        NULLIF((tr.bus_capacity - tr.available_seats), 0),
        2
    ) as revenue_per_sold_seat,
    
    -- Métricas de Tickets
    COUNT(CASE WHEN ti.booking_status = 'confirmed' THEN 1 END) as confirmed_tickets,
    COUNT(CASE WHEN ti.booking_status = 'cancelled' THEN 1 END) as cancelled_tickets,
    COUNT(CASE WHEN ti.booking_status = 'reserved' THEN 1 END) as reserved_tickets,
    
    -- Tasa de Cancelación
    ROUND(
        COUNT(CASE WHEN ti.booking_status = 'cancelled' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(ti.ticket_id), 0),
        2
    ) as cancellation_rate,
    
    -- Pasajeros Únicos
    COUNT(DISTINCT ti.passenger_id) as unique_passengers,
    
    -- Clasificación de Rentabilidad
    CASE 
        WHEN SUM(CASE WHEN ti.booking_status != 'cancelled' THEN ti.total_price ELSE 0 END) >= 10000 THEN 'High Revenue'
        WHEN SUM(CASE WHEN ti.booking_status != 'cancelled' THEN ti.total_price ELSE 0 END) >= 5000 THEN 'Medium Revenue'
        WHEN SUM(CASE WHEN ti.booking_status != 'cancelled' THEN ti.total_price ELSE 0 END) >= 2000 THEN 'Low Revenue'
        ELSE 'Very Low Revenue'
    END as revenue_category,
    
    -- Eficiencia (Ingresos vs Capacidad)
    CASE 
        WHEN (tr.bus_capacity - tr.available_seats) * 100.0 / NULLIF(tr.bus_capacity, 0) >= 80 
         AND SUM(CASE WHEN ti.booking_status != 'cancelled' THEN ti.total_price ELSE 0 END) >= 5000 
        THEN 'Optimal'
        WHEN (tr.bus_capacity - tr.available_seats) * 100.0 / NULLIF(tr.bus_capacity, 0) >= 60 
        THEN 'Good'
        WHEN (tr.bus_capacity - tr.available_seats) * 100.0 / NULLIF(tr.bus_capacity, 0) >= 40 
        THEN 'Fair'
        ELSE 'Poor'
    END as trip_efficiency

FROM trips tr
LEFT JOIN tickets ti ON tr.trip_id = ti.trip_id
GROUP BY 
    tr.trip_id,
    tr.route_id,
    tr.departure_time,
    tr.arrival_time,
    tr.status,
    tr.driver_name,
    tr.bus_plate,
    tr.bus_capacity,
    tr.available_seats;

-- ============================================================================
-- Ejemplos de Uso de la Vista: trip_occupancy_revenue
-- ============================================================================

-- Ejemplo 1: Viajes con ocupación completa (>=90%)
-- SELECT * FROM trip_occupancy_revenue 
-- WHERE occupancy_level = 'Full'
-- ORDER BY departure_date DESC;

-- Ejemplo 2: Rutas más rentables del último mes
-- SELECT route_id, COUNT(*) as trips, SUM(total_revenue) as revenue
-- FROM trip_occupancy_revenue 
-- WHERE departure_date >= DATE_ADD('month', -1, CURRENT_DATE)
-- GROUP BY route_id
-- ORDER BY revenue DESC;

-- Ejemplo 3: Análisis de ocupación por día de la semana
-- SELECT day_of_week_name, 
--        AVG(occupancy_percentage) as avg_occupancy,
--        AVG(total_revenue) as avg_revenue
-- FROM trip_occupancy_revenue
-- GROUP BY day_of_week_name, day_of_week_number
-- ORDER BY day_of_week_number;

-- Ejemplo 4: Viajes con baja ocupación para optimización
-- SELECT * FROM trip_occupancy_revenue 
-- WHERE occupancy_level IN ('Low', 'Very Low')
-- AND trip_status = 'completed'
-- ORDER BY total_revenue ASC;

-- Ejemplo 5: Mejores horarios de salida
-- SELECT departure_hour, 
--        COUNT(*) as trip_count,
--        AVG(occupancy_percentage) as avg_occupancy,
--        SUM(total_revenue) as total_revenue
-- FROM trip_occupancy_revenue
-- GROUP BY departure_hour
-- ORDER BY avg_occupancy DESC;


-- ============================================================================
-- INSTRUCCIONES DE CREACIÓN DE VISTAS
-- ============================================================================
-- 1. Acceder a AWS Athena Console: https://console.aws.amazon.com/athena/
-- 2. Seleccionar Database: bus_mvp_db
-- 3. Verificar que las tablas base existen:
--    SHOW TABLES;
-- 4. Ejecutar el comando CREATE VIEW para cada vista
-- 5. Verificar creación exitosa:
--    SHOW VIEWS;
-- 6. Probar las vistas con queries de ejemplo
-- 7. Capturar screenshots de:
--    - Comando CREATE VIEW ejecutado
--    - Listado de vistas con SHOW VIEWS
--    - Resultados de queries de ejemplo sobre las vistas
--
-- NOTA: Si una vista ya existe, usar CREATE OR REPLACE VIEW
--       Las vistas se actualizan automáticamente cuando cambian los datos base
-- ============================================================================

-- ============================================================================
-- VENTAJAS DE USAR ESTAS VISTAS
-- ============================================================================
-- 1. Simplicidad: Queries complejas pre-calculadas y reutilizables
-- 2. Consistencia: Métricas calculadas de forma uniforme
-- 3. Performance: Athena optimiza la ejecución de vistas
-- 4. Mantenibilidad: Cambios en lógica de negocio centralizados
-- 5. Seguridad: Control de acceso granular por vista
-- 6. Documentación: Lógica de negocio auto-documentada
-- ============================================================================
