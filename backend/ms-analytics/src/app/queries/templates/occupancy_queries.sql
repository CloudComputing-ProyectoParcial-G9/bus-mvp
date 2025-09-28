-- Occupancy Trends Analysis
-- Analyzes bus occupancy patterns by time periods

-- By Day of Week
SELECT 
    EXTRACT(dow FROM t.departure_time) as period,
    CASE EXTRACT(dow FROM t.departure_time)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as period_label,
    COUNT(DISTINCT t.trip_id) as total_trips,
    COUNT(tk.ticket_id) as tickets_sold,
    SUM(t.bus_capacity) as total_capacity,
    ROUND(
        CASE 
            WHEN SUM(t.bus_capacity) > 0 
            THEN (COUNT(tk.ticket_id) * 100.0 / SUM(t.bus_capacity))
            ELSE 0 
        END, 2
    ) as occupancy_rate,
    ROUND(
        CASE 
            WHEN COUNT(DISTINCT t.trip_id) > 0 
            THEN (COUNT(tk.ticket_id) * 1.0 / COUNT(DISTINCT t.trip_id))
            ELSE 0 
        END, 1
    ) as average_occupancy
FROM {catalog_database}.trips_raw t
LEFT JOIN {catalog_database}.tickets_raw tk ON t.trip_id = tk.trip_id 
    AND tk.booking_status = 'confirmed'
WHERE 1=1
    AND t.status = 'completed'
    AND t.year >= {year_from}
    {route_filter}
    {date_filter}
GROUP BY EXTRACT(dow FROM t.departure_time)
ORDER BY period
