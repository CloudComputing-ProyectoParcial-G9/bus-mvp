-- Route Performance Analysis
-- Comprehensive performance metrics for each route

WITH route_metrics AS (
    SELECT 
        t.route_code,
        CASE 
            WHEN t.route_code = 'RT001' THEN 'Madrid - Barcelona Express'
            WHEN t.route_code = 'RT002' THEN 'Sevilla - Valencia Direct'
            WHEN t.route_code = 'RT003' THEN 'Bilbao - Zaragoza Route'
            WHEN t.route_code = 'RT004' THEN 'Barcelona - Madrid Night'
            WHEN t.route_code = 'RT005' THEN 'Valencia - Sevilla Express'
            WHEN t.route_code = 'RT006' THEN 'Zaragoza - Bilbao Direct'
            ELSE CONCAT('Route ', t.route_code)
        END as route_name,
        t.origin_city,
        t.destination_city,
        COUNT(DISTINCT t.trip_id) as total_trips,
        
        -- Revenue metrics
        SUM(COALESCE(tk.total_price, 0)) as total_revenue,
        AVG(COALESCE(tk.total_price, 0)) as avg_ticket_price,
        
        -- Occupancy metrics
        SUM(t.bus_capacity) as total_capacity,
        COUNT(tk.ticket_id) as tickets_sold,
        ROUND(
            CASE 
                WHEN SUM(t.bus_capacity) > 0 
                THEN (COUNT(tk.ticket_id) * 100.0 / SUM(t.bus_capacity))
                ELSE 0 
            END, 1
        ) as average_occupancy,
        
        -- On-time performance (mock calculation)
        ROUND(85 + (RAND() * 15), 1) as on_time_performance,
        
        -- Cancellation rate (mock calculation)
        ROUND(RAND() * 8, 1) as cancellation_rate
        
    FROM {catalog_database}.trips_raw t
    LEFT JOIN {catalog_database}.tickets_raw tk ON t.trip_id = tk.trip_id 
        AND tk.booking_status = 'confirmed'
    WHERE 1=1
        AND t.year >= {year_from}
        {route_filter}
        {date_filter}
    GROUP BY 
        t.route_code, 
        t.origin_city, 
        t.destination_city
)
SELECT 
    route_code,
    route_name,
    origin_city,
    destination_city,
    total_trips,
    -- Include metrics based on requested metrics
    CASE WHEN '{metrics}' LIKE '%revenue%' THEN total_revenue ELSE NULL END as total_revenue,
    CASE WHEN '{metrics}' LIKE '%occupancy%' THEN average_occupancy ELSE NULL END as average_occupancy,
    CASE WHEN '{metrics}' LIKE '%on_time%' THEN on_time_performance ELSE NULL END as on_time_performance,
    CASE WHEN '{metrics}' LIKE '%cancellation%' THEN cancellation_rate ELSE NULL END as cancellation_rate,
    -- Calculate overall performance score
    ROUND((
        COALESCE(average_occupancy, 50) + 
        COALESCE(on_time_performance, 80) - 
        COALESCE(cancellation_rate, 5)
    ) / 2, 1) as performance_score
FROM route_metrics
ORDER BY performance_score DESC
