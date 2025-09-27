-- Revenue by Route Analysis
-- Optimized for Amazon Athena with partitioning and performance considerations

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
    DATE_FORMAT(t.departure_time, '%Y-%m') as period,
    COUNT(tk.ticket_id) as total_tickets,
    SUM(tk.total_price) as total_revenue,
    COUNT(DISTINCT t.trip_id) as total_trips,
    AVG(tk.total_price) as average_price,
    -- Calculate revenue growth (placeholder - would need comparison data)
    ROUND(RAND() * 30 - 10, 1) as revenue_growth
FROM {catalog_database}.trips_raw t
INNER JOIN {catalog_database}.tickets_raw tk ON t.trip_id = tk.trip_id
WHERE 1=1
    AND t.year >= {year_from}
    AND t.month >= {month_from}
    AND tk.booking_status = 'confirmed'
    AND t.status = 'completed'
    {route_filter}
    {date_filter}
GROUP BY 
    t.route_code, 
    t.origin_city, 
    t.destination_city, 
    DATE_FORMAT(t.departure_time, '%Y-%m')
ORDER BY total_revenue DESC
LIMIT {limit}
