-- Customer Segmentation Analysis
-- Segments customers based on travel frequency and spending patterns

WITH customer_metrics AS (
    SELECT 
        p.passenger_id,
        p.email,
        p.first_name,
        p.last_name,
        COUNT(tk.ticket_id) as trip_count,
        SUM(tk.total_price) as total_spent,
        AVG(tk.total_price) as avg_ticket_price,
        MAX(tk.booking_date) as last_booking_date,
        MIN(tk.booking_date) as first_booking_date,
        DATEDIFF(MAX(tk.booking_date), MIN(tk.booking_date)) as customer_lifetime_days
    FROM {catalog_database}.passengers_raw p
    INNER JOIN {catalog_database}.tickets_raw tk ON p.passenger_id = tk.passenger_id
    WHERE tk.booking_status = 'confirmed'
        AND tk.year >= {year_from}
        {date_filter}
    GROUP BY p.passenger_id, p.email, p.first_name, p.last_name
),
customer_segments AS (
    SELECT 
        passenger_id,
        email,
        first_name,
        last_name,
        trip_count,
        total_spent,
        avg_ticket_price,
        last_booking_date,
        customer_lifetime_days,
        CASE 
            -- Frequency-based segmentation
            WHEN trip_count >= 10 THEN 'Frequent Travelers'
            WHEN trip_count >= 5 THEN 'Regular Customers'
            WHEN trip_count >= 2 THEN 'Occasional Users'
            ELSE 'One-time Customers'
        END as frequency_segment,
        CASE 
            -- Value-based segmentation
            WHEN total_spent >= 500 THEN 'High Value'
            WHEN total_spent >= 200 THEN 'Medium Value'
            ELSE 'Low Value'
        END as value_segment,
        CASE 
            -- Recency-based segmentation
            WHEN DATEDIFF(CURRENT_DATE, last_booking_date) <= 30 THEN 'Recent'
            WHEN DATEDIFF(CURRENT_DATE, last_booking_date) <= 90 THEN 'Active'
            WHEN DATEDIFF(CURRENT_DATE, last_booking_date) <= 180 THEN 'At Risk'
            ELSE 'Inactive'
        END as recency_segment
    FROM customer_metrics
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) as segment_id,
    {segment_criteria}_segment as segment_name,
    COUNT(*) as customer_count,
    AVG(trip_count) as average_trips,
    AVG(total_spent) as average_revenue,
    SUM(total_spent) as total_revenue,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
FROM customer_segments
GROUP BY {segment_criteria}_segment
ORDER BY customer_count DESC
LIMIT {limit}
