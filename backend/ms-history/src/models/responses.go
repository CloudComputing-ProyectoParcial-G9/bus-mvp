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