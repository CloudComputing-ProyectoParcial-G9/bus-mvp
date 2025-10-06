from typing import List, Dict
from loguru import logger
from src.services.athena_service import AthenaService
from src.models.responses import (
    DashboardSummaryResponse, SummaryMetrics, SummaryTrends,
    PassengerAnalyticsResponse, TopCustomer,
    RevenueAnalyticsResponse, RouteRevenue, RevenueTrend, DailyRevenue,
    OccupancyAnalyticsResponse, OccupancyByRoute,
    TripAnalyticsResponse
)
from src.core.exceptions import DataNotFoundException

class AnalyticsService:
    """
    Servicio de lógica de negocio para analytics
    Usa AthenaService para queries y transforma datos
    """
    
    def __init__(self, athena_service: AthenaService):
        self.athena = athena_service
    
    async def get_dashboard_summary(self) -> DashboardSummaryResponse:
        """
        Obtiene resumen general del dashboard
        
        Returns:
            DashboardSummaryResponse con métricas principales
        """
        logger.info("Getting dashboard summary")
        
        # Query para métricas principales
        query = """
        SELECT 
            COUNT(DISTINCT p.passenger_id) as total_passengers,
            COUNT(DISTINCT CASE 
                WHEN tr.status = 'active' OR tr.status = 'scheduled' THEN tr.tripId 
            END) as active_trips,
            COUNT(t.ticket_id) as tickets_sold,
            COALESCE(SUM(CASE 
                WHEN t.booking_status = 'confirmed' THEN t.total_price 
                ELSE 0 
            END), 0) as total_revenue,
            COALESCE(AVG((tr.busCapacity - tr.availableSeats) * 100.0 / NULLIF(tr.busCapacity, 0)), 0) as avg_occupancy,
            COALESCE(
                COUNT(CASE WHEN t.booking_status = 'cancelled' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(t.ticket_id), 0), 
                0
            ) as cancellation_rate
        FROM tickets_csv t
        LEFT JOIN passengers_csv p ON t.passenger_id = p.passenger_id
        LEFT JOIN trips_csv tr ON t.trip_id = tr.tripId
        """
        
        results = await self.athena.execute_query(query)
        
        if not results:
            raise DataNotFoundException("No summary data available")
        
        row = results[0]
        
        summary = SummaryMetrics(
            total_passengers=int(row.get('total_passengers', 0)),
            active_trips=int(row.get('active_trips', 0)),
            tickets_sold=int(row.get('tickets_sold', 0)),
            total_revenue=float(row.get('total_revenue', 0)),
            average_occupancy=float(row.get('avg_occupancy', 0)),
            cancellation_rate=float(row.get('cancellation_rate', 0))
        )
        
        return DashboardSummaryResponse(
            summary=summary,
            trends=SummaryTrends()  # Podría calcularse comparando con período anterior
        )
    
    async def get_passenger_analytics(self) -> PassengerAnalyticsResponse:
        """
        Analítica de pasajeros usando vista passenger_sales_summary
        
        Returns:
            PassengerAnalyticsResponse con segmentación y top customers
        """
        logger.info("Getting passenger analytics")
        
        # Query usando vista creada
        query = """
        SELECT 
            passenger_id,
            full_name,
            total_revenue,
            total_tickets_purchased,
            customer_segment
        FROM passenger_sales_summary
        WHERE total_revenue IS NOT NULL
        ORDER BY total_revenue DESC
        LIMIT 100
        """
        
        results = await self.athena.execute_query(query)
        
        if not results:
            raise DataNotFoundException("No passenger data available")
        
        # Contar segmentos
        segments = {}
        top_customers = []
        active_passengers = 0
        
        for row in results:
            segment = row['customer_segment']
            segments[segment] = segments.get(segment, 0) + 1
            
            # Top 10 customers
            if len(top_customers) < 10:
                top_customers.append(TopCustomer(
                    passenger_id=row['passenger_id'],
                    full_name=row['full_name'],
                    total_spent=float(row['total_revenue']) if row['total_revenue'] else 0,
                    tickets_purchased=int(row['total_tickets_purchased']) if row['total_tickets_purchased'] else 0,
                    segment=segment
                ))
            
            # Pasajeros activos (con al menos 1 ticket)
            if int(row['total_tickets_purchased'] or 0) > 0:
                active_passengers += 1
        
        return PassengerAnalyticsResponse(
            total_passengers=len(results),
            active_passengers=active_passengers,
            passenger_segments=segments,
            top_customers=top_customers
        )
    
    async def get_revenue_analytics(self) -> RevenueAnalyticsResponse:
        """
        Analítica de ingresos por ruta y status
        
        Returns:
            RevenueAnalyticsResponse
        """
        logger.info("Getting revenue analytics")
        
        query = """
        SELECT 
            tr.routeId as route_id,
            COALESCE(SUM(CASE WHEN t.booking_status = 'confirmed' THEN t.total_price ELSE 0 END), 0) as confirmed_revenue,
            COALESCE(SUM(CASE WHEN t.booking_status = 'cancelled' THEN t.total_price ELSE 0 END), 0) as cancelled_revenue,
            COUNT(DISTINCT tr.tripId) as trips_count
        FROM trips_csv tr
        LEFT JOIN tickets_csv t ON tr.tripId = t.trip_id
        GROUP BY tr.routeId
        ORDER BY confirmed_revenue DESC
        """
        
        results = await self.athena.execute_query(query)
        
        if not results:
            raise DataNotFoundException("No revenue data available")
        
        total_confirmed = 0
        total_cancelled = 0
        routes = []
        
        for row in results:
            confirmed = float(row.get('confirmed_revenue', 0))
            cancelled = float(row.get('cancelled_revenue', 0))
            trips = int(row.get('trips_count', 0))
            
            total_confirmed += confirmed
            total_cancelled += cancelled
            
            routes.append(RouteRevenue(
                route_id=row['route_id'],
                total_revenue=confirmed,
                trips_count=trips,
                avg_revenue_per_trip=confirmed / trips if trips > 0 else 0
            ))
        
        return RevenueAnalyticsResponse(
            total_revenue=total_confirmed + total_cancelled,
            confirmed_revenue=total_confirmed,
            cancelled_revenue=total_cancelled,
            by_route=routes
        )
    
    async def get_occupancy_analytics(self) -> OccupancyAnalyticsResponse:
        """
        Analítica de ocupación usando vista trip_occupancy_revenue
        
        Returns:
            OccupancyAnalyticsResponse
        """
        logger.info("Getting occupancy analytics")
        
        query = """
        SELECT 
            route_id,
            bus_capacity,
            seats_sold,
            occupancy_percentage,
            occupancy_level
        FROM trip_occupancy_revenue
        """
        
        results = await self.athena.execute_query(query)
        
        if not results:
            raise DataNotFoundException("No occupancy data available")
        
        total_capacity = 0
        total_seats_sold = 0
        occupancy_levels = {}
        by_route = []
        
        for row in results:
            capacity = int(row.get('bus_capacity', 0))
            seats = int(row.get('seats_sold', 0))
            occupancy_pct = float(row.get('occupancy_percentage', 0))
            level = row.get('occupancy_level', 'Unknown')
            
            total_capacity += capacity
            total_seats_sold += seats
            occupancy_levels[level] = occupancy_levels.get(level, 0) + 1
            
            by_route.append(OccupancyByRoute(
                route_id=row['route_id'],
                avg_occupancy=occupancy_pct,
                trips_count=1  # Cada fila es un trip
            ))
        
        avg_occupancy = (total_seats_sold * 100.0 / total_capacity) if total_capacity > 0 else 0
        
        return OccupancyAnalyticsResponse(
            average_occupancy=avg_occupancy,
            total_capacity=total_capacity,
            total_seats_sold=total_seats_sold,
            by_level=occupancy_levels,
            by_route=by_route
        )
    
    async def get_trip_analytics(self) -> TripAnalyticsResponse:
        """
        Analítica de viajes con breakdown de ocupación
        
        Returns:
            TripAnalyticsResponse
        """
        logger.info("Getting trip analytics")
        
        query = """
        SELECT 
            COUNT(*) as total_trips,
            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_trips,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_trips,
            COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_trips
        FROM trips_csv
        """
        
        results = await self.athena.execute_query(query)
        
        if not results:
            raise DataNotFoundException("No trip data available")
        
        row = results[0]
        
        # Obtener breakdown de ocupación desde la vista
        occupancy_query = """
        SELECT occupancy_level, COUNT(*) as count
        FROM trip_occupancy_revenue
        GROUP BY occupancy_level
        """
        
        occupancy_results = await self.athena.execute_query(occupancy_query)
        occupancy_breakdown = {r['occupancy_level']: int(r['count']) for r in occupancy_results}
        
        return TripAnalyticsResponse(
            total_trips=int(row.get('total_trips', 0)),
            active_trips=int(row.get('active_trips', 0)),
            completed_trips=int(row.get('completed_trips', 0)),
            cancelled_trips=int(row.get('cancelled_trips', 0)),
            occupancy_breakdown=occupancy_breakdown
        )
