-- ============================================================================
-- CONSULTAS SQL PARA AWS ATHENA - Bus MVP Analytics
-- ============================================================================
-- Base de Datos: bus_mvp_db
-- Propósito: 4 consultas SQL que unen múltiples tablas para análisis
-- ============================================================================

-- ============================================================================
-- CONSULTA 1: Historial de Compras por Pasajero
-- ============================================================================
-- Descripción: Obtiene el historial completo de compras de cada pasajero
--              mostrando detalles del ticket y del viaje asociado
-- Tablas: passengers, tickets
-- ============================================================================

SELECT 
    p.passenger_id,
    p.full_name,
    p.email,
    p.phone,
    COUNT(t.ticket_id) as total_tickets,
    SUM(t.total_price) as total_spent,
    AVG(t.total_price) as avg_ticket_price,
    MIN(t.purchase_date) as first_purchase,
    MAX(t.purchase_date) as last_purchase,
    COUNT(CASE WHEN t.booking_status = 'confirmed' THEN 1 END) as confirmed_tickets,
    COUNT(CASE WHEN t.booking_status = 'cancelled' THEN 1 END) as cancelled_tickets
FROM passengers p
JOIN tickets t ON p.passenger_id = t.passenger_id
GROUP BY 
    p.passenger_id,
    p.full_name,
    p.email,
    p.phone
ORDER BY total_spent DESC
LIMIT 100;

-- Ejemplo de Uso en Athena Console:
-- 1. Abrir AWS Athena Console
-- 2. Seleccionar Database: bus_mvp_db
-- 3. Copiar y ejecutar esta query
-- 4. Capturar screenshot de resultados


-- ============================================================================
-- CONSULTA 2: Análisis de Ingresos por Viaje
-- ============================================================================
-- Descripción: Calcula los ingresos totales, ocupación y rentabilidad
--              de cada viaje basado en los tickets vendidos
-- Tablas: trips, tickets
-- ============================================================================

SELECT 
    tr.trip_id,
    tr.route_id,
    tr.departure_time,
    tr.arrival_time,
    tr.bus_capacity,
    tr.available_seats,
    tr.driver_name,
    tr.bus_plate,
    tr.status as trip_status,
    COUNT(ti.ticket_id) as tickets_sold,
    (tr.bus_capacity - tr.available_seats) as seats_occupied,
    ROUND(((tr.bus_capacity - tr.available_seats) * 100.0 / tr.bus_capacity), 2) as occupancy_percentage,
    SUM(ti.total_price) as total_revenue,
    AVG(ti.total_price) as avg_ticket_price,
    MIN(ti.total_price) as min_ticket_price,
    MAX(ti.total_price) as max_ticket_price,
    COUNT(CASE WHEN ti.booking_status = 'cancelled' THEN 1 END) as cancelled_count
FROM trips tr
LEFT JOIN tickets ti ON tr.trip_id = ti.trip_id
GROUP BY 
    tr.trip_id,
    tr.route_id,
    tr.departure_time,
    tr.arrival_time,
    tr.bus_capacity,
    tr.available_seats,
    tr.driver_name,
    tr.bus_plate,
    tr.status
HAVING COUNT(ti.ticket_id) > 0
ORDER BY total_revenue DESC
LIMIT 100;

-- Caso de Uso: Identificar los viajes más rentables y optimizar rutas


-- ============================================================================
-- CONSULTA 3: Resumen Completo de Transacciones (JOIN Triple)
-- ============================================================================
-- Descripción: Une las tres tablas principales para obtener información
--              completa de cada ticket: quién compró, qué viaje, cuándo
-- Tablas: passengers, tickets, trips
-- ============================================================================

SELECT 
    -- Información del Pasajero
    p.passenger_id,
    p.full_name,
    p.email,
    p.document_type,
    p.document_number,
    
    -- Información del Ticket
    t.ticket_id,
    t.seat_number,
    t.total_price,
    t.currency,
    t.booking_status,
    t.purchase_date,
    
    -- Información del Viaje
    tr.trip_id,
    tr.route_id,
    tr.departure_time,
    tr.arrival_time,
    tr.driver_name,
    tr.bus_plate,
    tr.status as trip_status,
    
    -- Métricas Calculadas
    CAST(tr.departure_time AS DATE) as travel_date,
    DATE_DIFF('day', t.purchase_date, tr.departure_time) as days_before_trip,
    CASE 
        WHEN DATE_DIFF('day', t.purchase_date, tr.departure_time) <= 1 THEN 'Last Minute'
        WHEN DATE_DIFF('day', t.purchase_date, tr.departure_time) <= 7 THEN 'Week Before'
        WHEN DATE_DIFF('day', t.purchase_date, tr.departure_time) <= 30 THEN 'Month Before'
        ELSE 'Early Bird'
    END as purchase_timing
    
FROM passengers p
JOIN tickets t ON p.passenger_id = t.passenger_id
JOIN trips tr ON t.trip_id = tr.trip_id
WHERE t.booking_status != 'cancelled'
ORDER BY t.purchase_date DESC
LIMIT 1000;

-- Caso de Uso: Análisis de comportamiento de compra y planificación de viajes


-- ============================================================================
-- CONSULTA 4: Tendencias de Ventas y Ocupación por Período
-- ============================================================================
-- Descripción: Análisis temporal de ventas, ocupación y rentabilidad
--              agrupado por fecha con métricas de rendimiento
-- Tablas: trips, tickets, passengers (opcional)
-- ============================================================================

SELECT 
    CAST(tr.departure_time AS DATE) as travel_date,
    DATE_FORMAT(tr.departure_time, '%Y-%m') as year_month,
    EXTRACT(DOW FROM tr.departure_time) as day_of_week,
    CASE EXTRACT(DOW FROM tr.departure_time)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as weekday_name,
    
    -- Métricas de Viajes
    COUNT(DISTINCT tr.trip_id) as total_trips,
    COUNT(DISTINCT tr.route_id) as unique_routes,
    
    -- Métricas de Tickets
    COUNT(ti.ticket_id) as total_tickets_sold,
    COUNT(DISTINCT ti.passenger_id) as unique_passengers,
    
    -- Métricas Financieras
    SUM(ti.total_price) as total_revenue,
    AVG(ti.total_price) as avg_ticket_price,
    
    -- Métricas de Ocupación
    SUM(tr.bus_capacity) as total_capacity,
    SUM(tr.bus_capacity - tr.available_seats) as total_seats_sold,
    ROUND(AVG((tr.bus_capacity - tr.available_seats) * 100.0 / tr.bus_capacity), 2) as avg_occupancy_rate,
    
    -- Métricas de Estado
    COUNT(CASE WHEN ti.booking_status = 'confirmed' THEN 1 END) as confirmed_tickets,
    COUNT(CASE WHEN ti.booking_status = 'cancelled' THEN 1 END) as cancelled_tickets,
    ROUND(COUNT(CASE WHEN ti.booking_status = 'cancelled' THEN 1 END) * 100.0 / COUNT(ti.ticket_id), 2) as cancellation_rate

FROM trips tr
LEFT JOIN tickets ti ON tr.trip_id = ti.trip_id
WHERE tr.departure_time >= DATE_ADD('day', -90, CURRENT_DATE)  -- Últimos 90 días
GROUP BY 
    CAST(tr.departure_time AS DATE),
    DATE_FORMAT(tr.departure_time, '%Y-%m'),
    EXTRACT(DOW FROM tr.departure_time)
ORDER BY travel_date DESC;

-- Caso de Uso: Identificar patrones de demanda, días con mayor ocupación,
--              y tendencias de ventas para optimización de rutas y precios


-- ============================================================================
-- CONSULTAS ADICIONALES (BONUS)
-- ============================================================================

-- CONSULTA 5: Top 10 Rutas Más Rentables
-- ============================================================================
SELECT 
    tr.route_id,
    COUNT(DISTINCT tr.trip_id) as total_trips,
    COUNT(ti.ticket_id) as tickets_sold,
    SUM(ti.total_price) as total_revenue,
    AVG(ti.total_price) as avg_price,
    ROUND(AVG((tr.bus_capacity - tr.available_seats) * 100.0 / tr.bus_capacity), 2) as avg_occupancy
FROM trips tr
JOIN tickets ti ON tr.trip_id = ti.trip_id
WHERE ti.booking_status = 'confirmed'
GROUP BY tr.route_id
ORDER BY total_revenue DESC
LIMIT 10;


-- CONSULTA 6: Pasajeros Más Frecuentes (Programa de Lealtad)
-- ============================================================================
SELECT 
    p.passenger_id,
    p.full_name,
    p.email,
    COUNT(DISTINCT t.trip_id) as trips_taken,
    COUNT(t.ticket_id) as total_tickets,
    SUM(t.total_price) as lifetime_value,
    MIN(t.purchase_date) as first_purchase,
    MAX(t.purchase_date) as last_purchase,
    DATE_DIFF('day', MIN(t.purchase_date), MAX(t.purchase_date)) as customer_tenure_days
FROM passengers p
JOIN tickets t ON p.passenger_id = t.passenger_id
WHERE t.booking_status != 'cancelled'
GROUP BY p.passenger_id, p.full_name, p.email
HAVING COUNT(t.ticket_id) >= 3
ORDER BY lifetime_value DESC
LIMIT 50;


-- ============================================================================
-- INSTRUCCIONES DE EJECUCIÓN
-- ============================================================================
-- 1. Acceder a AWS Athena Console: https://console.aws.amazon.com/athena/
-- 2. Seleccionar Database: bus_mvp_db
-- 3. Verificar que las tablas existen:
--    - SHOW TABLES;
--    - DESCRIBE passengers;
--    - DESCRIBE trips;
--    - DESCRIBE tickets;
-- 4. Ejecutar cada consulta individualmente
-- 5. Guardar resultados como CSV para evidencia
-- 6. Capturar screenshots de cada consulta ejecutada
--
-- NOTA: Ajustar nombres de columnas según el esquema real detectado por Glue Crawlers
-- ============================================================================
