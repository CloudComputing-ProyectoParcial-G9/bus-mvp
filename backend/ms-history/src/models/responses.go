package models

import "time"

// PassengerHistoryResponse representa el historial completo de un pasajero
type PassengerHistoryResponse struct {
	Passenger     *Passenger              `json:"passenger"`
	RecentTickets []Ticket               `json:"recent_tickets"`
	Statistics    *PassengerStatistics   `json:"statistics"`
	TravelHistory []TripWithRoute        `json:"travel_history"`
}

// PassengerStatistics contiene estadísticas calculadas del pasajero
type PassengerStatistics struct {
	TotalTrips        int     `json:"total_trips"`
	TotalSpent        float64 `json:"total_spent"`
	FavoriteRoute     string  `json:"favorite_route"`
	FavoriteDestination string `json:"favorite_destination"`
	AverageSpentPerTrip float64 `json:"average_spent_per_trip"`
	LastTripDate      *time.Time `json:"last_trip_date"`
	FirstTripDate     *time.Time `json:"first_trip_date"`
}

// DashboardSummaryResponse contiene métricas del dashboard
type DashboardSummaryResponse struct {
	TotalPassengers   int                    `json:"total_passengers"`
	TotalTrips        int                    `json:"total_trips"`
	TotalTickets      int                    `json:"total_tickets"`
	TotalRevenue      float64               `json:"total_revenue"`
	ActiveRoutes      int                    `json:"active_routes"`
	PopularRoutes     []RoutePopularity     `json:"popular_routes"`
	RecentActivity    []RecentActivity      `json:"recent_activity"`
	MonthlyStats      *MonthlyStatistics    `json:"monthly_stats"`
	LastUpdated       time.Time             `json:"last_updated"`
}

// RoutePopularity representa la popularidad de una ruta
type RoutePopularity struct {
	RouteCode       string  `json:"route_code"`
	OriginCity      string  `json:"origin_city"`
	DestinationCity string  `json:"destination_city"`
	TotalTickets    int     `json:"total_tickets"`
	TotalRevenue    float64 `json:"total_revenue"`
	AveragePrice    float64 `json:"average_price"`
}

// RecentActivity representa actividad reciente del sistema
type RecentActivity struct {
	Type        string    `json:"type"` // "ticket_purchase", "new_passenger", "trip_completed"
	Description string    `json:"description"`
	Timestamp   time.Time `json:"timestamp"`
	EntityID    string    `json:"entity_id"`
}

// MonthlyStatistics contiene estadísticas mensuales
type MonthlyStatistics struct {
	CurrentMonth    MonthData `json:"current_month"`
	PreviousMonth   MonthData `json:"previous_month"`
	GrowthRate      float64   `json:"growth_rate"`
}

// MonthData representa datos de un mes específico
type MonthData struct {
	Month       string  `json:"month"`
	Passengers  int     `json:"passengers"`
	Trips       int     `json:"trips"`
	Tickets     int     `json:"tickets"`
	Revenue     float64 `json:"revenue"`
}

// TripHistoryResponse representa el historial de un viaje
type TripHistoryResponse struct {
	Trip          *TripWithRoute     `json:"trip"`
	Tickets       []TicketWithPassenger `json:"tickets"`
	Statistics    *TripStatistics    `json:"statistics"`
}

// TicketWithPassenger representa un ticket con datos del pasajero
type TicketWithPassenger struct {
	Ticket    Ticket    `json:"ticket"`
	Passenger Passenger `json:"passenger"`
}

// TripStatistics contiene estadísticas de un viaje
type TripStatistics struct {
	OccupancyRate     float64 `json:"occupancy_rate"`
	TotalRevenue      float64 `json:"total_revenue"`
	PassengerCount    int     `json:"passenger_count"`
	AverageAge        float64 `json:"average_age"`
	GenderDistribution map[string]int `json:"gender_distribution"`
}

// RouteAnalyticsResponse contiene análisis de rutas
type RouteAnalyticsResponse struct {
	Route         Route             `json:"route"`
	Popularity    RoutePopularity   `json:"popularity"`
	TrendData     []TrendPoint      `json:"trend_data"`
	Recommendations []string        `json:"recommendations"`
}

// TrendPoint representa un punto en el tiempo para tendencias
type TrendPoint struct {
	Date         time.Time `json:"date"`
	TicketCount  int       `json:"ticket_count"`
	Revenue      float64   `json:"revenue"`
	OccupancyRate float64  `json:"occupancy_rate"`
}

// HealthCheckResponse representa el estado de salud del servicio
type HealthCheckResponse struct {
	Status       string                    `json:"status"`
	Timestamp    time.Time                `json:"timestamp"`
	Version      string                   `json:"version"`
	Dependencies map[string]ServiceHealth `json:"dependencies"`
}

// ServiceHealth representa el estado de un servicio dependiente
type ServiceHealth struct {
	Status       string        `json:"status"`
	ResponseTime time.Duration `json:"response_time"`
	LastChecked  time.Time     `json:"last_checked"`
	Error        string        `json:"error,omitempty"`
}

// PopularRouteResponse representa una ruta popular con sus estadísticas
// @Description Popular route with statistics
type PopularRouteResponse struct {
	RouteID         string  `json:"route_id" example:"RT_001"`
	RouteCode       string  `json:"route_code" example:"LIM-ARQ"`
	OriginCity      string  `json:"origin_city" example:"Lima"`
	DestinationCity string  `json:"destination_city" example:"Arequipa"`
	Distance        float64 `json:"distance_km" example:"1010.5"`
	TotalTickets    int     `json:"total_tickets" example:"45"`
	TotalRevenue    float64 `json:"total_revenue" example:"2250.00"`
	AveragePrice    float64 `json:"average_price" example:"50.00"`
	OccupancyRate   float64 `json:"occupancy_rate" example:"75.5"`
	Rank            int     `json:"rank" example:"1"`
	Trend           string  `json:"trend" example:"up"` // up, down, stable
}

// PopularRoutesResponse contiene la lista de rutas populares
// @Description Response with list of popular routes
type PopularRoutesResponse struct {
	PopularRoutes       []PopularRouteResponse `json:"popular_routes"`
	Period              string                 `json:"period" example:"2025-10"`
	TotalRoutesAnalyzed int                    `json:"total_routes_analyzed" example:"6"`
	GeneratedAt         time.Time              `json:"generated_at" example:"2025-10-04T16:30:00Z"`
}

// RouteStatsResponse contiene estadísticas detalladas de una ruta específica
// @Description Detailed statistics for a specific route
type RouteStatsResponse struct {
	RouteID         string           `json:"route_id" example:"RT_001"`
	RouteCode       string           `json:"route_code" example:"LIM-ARQ"`
	OriginCity      string           `json:"origin_city" example:"Lima"`
	DestinationCity string           `json:"destination_city" example:"Arequipa"`
	Distance        float64          `json:"distance_km" example:"1010.5"`
	Statistics      RouteStatistics  `json:"statistics"`
	PopularityRank  int              `json:"popularity_rank" example:"1"`
	Trend           RouteTrend       `json:"trend"`
	RecentTrips     []TripSummary    `json:"recent_trips"`
}

// RouteStatistics contiene estadísticas agregadas de una ruta
// @Description Aggregated statistics for a route
type RouteStatistics struct {
	TotalTrips       int     `json:"total_trips" example:"15"`
	TotalTicketsSold int     `json:"total_tickets_sold" example:"45"`
	TotalRevenue     float64 `json:"total_revenue" example:"2250.00"`
	AveragePrice     float64 `json:"average_ticket_price" example:"50.00"`
	OccupancyRate    float64 `json:"occupancy_rate" example:"75.5"`
	PeakDemandDay    string  `json:"peak_demand_day" example:"Friday"`
}

// RouteTrend representa la tendencia de una ruta
// @Description Trend information for a route
type RouteTrend struct {
	CurrentMonth  int     `json:"current_month" example:"45"`
	PreviousMonth int     `json:"previous_month" example:"38"`
	GrowthRate    float64 `json:"growth_rate" example:"18.4"`
	Direction     string  `json:"direction" example:"up"` // up, down, stable
}

// TripSummary representa un resumen de un viaje
// @Description Summary of a trip
type TripSummary struct {
	TripID          string    `json:"trip_id" example:"TRP_20251004_LIM_ARQ_01"`
	DepartureDate   time.Time `json:"departure_date" example:"2025-10-05T08:00:00Z"`
	TicketsSold     int       `json:"tickets_sold" example:"35"`
	SeatsAvailable  int       `json:"seats_available" example:"5"`
	Status          string    `json:"status" example:"scheduled"`
}