package services

import (
	"context"
	"sync"
	"time"

	"ms-history/src/clients"
	"ms-history/src/models"
)

type AggregationService struct {
	passengersClient *clients.PassengersClient
	tripsClient      *clients.TripsClient
	ticketsClient    *clients.TicketsClient
}

func NewAggregationService(
	passengersClient *clients.PassengersClient,
	tripsClient *clients.TripsClient,
	ticketsClient *clients.TicketsClient,
) *AggregationService {
	return &AggregationService{
		passengersClient: passengersClient,
		tripsClient:      tripsClient,
		ticketsClient:    ticketsClient,
	}
}

func (s *AggregationService) GetPassengerHistory(ctx context.Context, passengerID string) (*models.PassengerHistoryResponse, error) {
	var wg sync.WaitGroup
	var passenger *models.Passenger
	var tickets []models.Ticket
	var routes []models.Route
	var errs []error
	var mu sync.Mutex

	// Llamadas paralelas usando goroutines
	wg.Add(3)

	// Goroutine 1: Obtener datos del pasajero
	go func() {
		defer wg.Done()
		p, err := s.passengersClient.GetPassenger(ctx, passengerID)
		if err != nil {
			mu.Lock()
			errs = append(errs, err)
			mu.Unlock()
			return
		}
		passenger = p
	}()

	// Goroutine 2: Obtener historial de tickets
	go func() {
		defer wg.Done()
		t, err := s.ticketsClient.GetTicketsByPassenger(ctx, passengerID)
		if err != nil {
			mu.Lock()
			errs = append(errs, err)
			mu.Unlock()
			return
		}
		tickets = t
	}()

	// Goroutine 3: Obtener todas las rutas para referencia
	go func() {
		defer wg.Done()
		r, err := s.tripsClient.ListRoutes(ctx)
		if err != nil {
			mu.Lock()
			errs = append(errs, err)
			mu.Unlock()
			return
		}
		routes = r
	}()

	wg.Wait()

	// Verificar errores críticos
	if len(errs) > 0 && passenger == nil {
		return nil, errs[0]
	}

	// Obtener detalles de viajes para cada ticket (en paralelo)
	travelHistory := s.fetchTripDetailsParallel(ctx, tickets)

	// Calcular estadísticas
	stats := s.calculatePassengerStats(tickets, travelHistory, routes)

	// Limitar tickets recientes a los últimos 5
	recentTickets := tickets
	if len(recentTickets) > 5 {
		recentTickets = recentTickets[:5]
	}

	return &models.PassengerHistoryResponse{
		Passenger:     passenger,
		RecentTickets: recentTickets,
		Statistics:    stats,
		TravelHistory: travelHistory,
	}, nil
}

func (s *AggregationService) fetchTripDetailsParallel(ctx context.Context, tickets []models.Ticket) []models.TripWithRoute {
	if len(tickets) == 0 {
		return []models.TripWithRoute{}
	}

	type tripResult struct {
		index int
		trip  *models.Trip
		route *models.Route
		err   error
	}

	resultChan := make(chan tripResult, len(tickets))
	var wg sync.WaitGroup

	// Limitar concurrencia para evitar sobrecargar los servicios
	sem := make(chan struct{}, 5)

	for i, ticket := range tickets {
		wg.Add(1)
		go func(index int, tripID string) {
			defer wg.Done()
			sem <- struct{}{} // Acquire
			defer func() { <-sem }() // Release

			trip, err := s.tripsClient.GetTrip(ctx, tripID)
			if err != nil {
				resultChan <- tripResult{index: index, err: err}
				return
			}

			route, err := s.tripsClient.GetRoute(ctx, trip.RouteID)
			if err != nil {
				// Si no podemos obtener la ruta, continuamos sin ella
				resultChan <- tripResult{index: index, trip: trip, route: nil, err: nil}
				return
			}

			resultChan <- tripResult{index: index, trip: trip, route: route, err: nil}
		}(i, ticket.TripID)
	}

	wg.Wait()
	close(resultChan)

	// Recopilar resultados manteniendo el orden
	results := make([]models.TripWithRoute, 0, len(tickets))
	for result := range resultChan {
		if result.err == nil && result.trip != nil {
			tripWithRoute := models.TripWithRoute{
				Trip: *result.trip,
			}
			if result.route != nil {
				tripWithRoute.Route = *result.route
			}
			results = append(results, tripWithRoute)
		}
	}

	return results
}

func (s *AggregationService) calculatePassengerStats(tickets []models.Ticket, travelHistory []models.TripWithRoute, routes []models.Route) *models.PassengerStatistics {
	if len(tickets) == 0 {
		return &models.PassengerStatistics{
			TotalTrips:          0,
			TotalSpent:          0,
			FavoriteRoute:       "N/A",
			FavoriteDestination: "N/A",
			AverageSpentPerTrip: 0,
		}
	}

	// Calcular estadísticas básicas
	totalSpent := 0.0
	routeCount := make(map[string]int)
	destinationCount := make(map[string]int)
	var firstTrip, lastTrip *time.Time

	for _, ticket := range tickets {
		if ticket.BookingStatus == "confirmed" {
			totalSpent += ticket.TotalPrice

			// Encontrar fechas de primer y último viaje
			if firstTrip == nil || ticket.PurchaseDate.Before(*firstTrip) {
				firstTrip = &ticket.PurchaseDate
			}
			if lastTrip == nil || ticket.PurchaseDate.After(*lastTrip) {
				lastTrip = &ticket.PurchaseDate
			}
		}
	}

	// Analizar rutas y destinos favoritos
	for _, travel := range travelHistory {
		if travel.Route.RouteCode != "" {
			routeCount[travel.Route.RouteCode]++
			destinationCount[travel.Route.DestinationCity]++
		}
	}

	// Encontrar ruta y destino favoritos
	favoriteRoute := "N/A"
	favoriteDestination := "N/A"
	maxRouteCount := 0
	maxDestCount := 0

	for route, count := range routeCount {
		if count > maxRouteCount {
			maxRouteCount = count
			favoriteRoute = route
		}
	}

	for dest, count := range destinationCount {
		if count > maxDestCount {
			maxDestCount = count
			favoriteDestination = dest
		}
	}

	confirmedTrips := len(tickets) // Simplificado - asumimos todos confirmados
	averageSpent := 0.0
	if confirmedTrips > 0 {
		averageSpent = totalSpent / float64(confirmedTrips)
	}

	return &models.PassengerStatistics{
		TotalTrips:          confirmedTrips,
		TotalSpent:          totalSpent,
		FavoriteRoute:       favoriteRoute,
		FavoriteDestination: favoriteDestination,
		AverageSpentPerTrip: averageSpent,
		FirstTripDate:       firstTrip,
		LastTripDate:        lastTrip,
	}
}

func (s *AggregationService) GetDashboardSummary(ctx context.Context) (*models.DashboardSummaryResponse, error) {
	var wg sync.WaitGroup
	var passengerStats, tripStats, ticketStats map[string]interface{}
	var errs []error
	var mu sync.Mutex

	wg.Add(3)

	// Obtener estadísticas de cada servicio en paralelo
	go func() {
		defer wg.Done()
		stats, err := s.passengersClient.GetPassengerStats(ctx)
		if err != nil {
			mu.Lock()
			errs = append(errs, err)
			mu.Unlock()
			return
		}
		passengerStats = stats
	}()

	go func() {
		defer wg.Done()
		stats, err := s.tripsClient.GetTripsStats(ctx)
		if err != nil {
			mu.Lock()
			errs = append(errs, err)
			mu.Unlock()
			return
		}
		tripStats = stats
	}()

	go func() {
		defer wg.Done()
		stats, err := s.ticketsClient.GetTicketsStats(ctx)
		if err != nil {
			mu.Lock()
			errs = append(errs, err)
			mu.Unlock()
			return
		}
		ticketStats = stats
	}()

	wg.Wait()

	// Construir respuesta con fallbacks para datos faltantes
	dashboard := &models.DashboardSummaryResponse{
		TotalPassengers: s.getIntValue(passengerStats, "total_passengers", 0),
		TotalTrips:      s.getIntValue(tripStats, "total_trips", 0),
		TotalTickets:    s.getIntValue(ticketStats, "total_tickets", 0),
		TotalRevenue:    s.getFloatValue(ticketStats, "total_revenue", 0.0),
		ActiveRoutes:    s.getIntValue(tripStats, "active_routes", 0),
		PopularRoutes:   []models.RoutePopularity{}, // TODO: Implementar análisis de rutas populares
		RecentActivity:  []models.RecentActivity{},  // TODO: Implementar actividad reciente
		MonthlyStats:    &models.MonthlyStatistics{}, // TODO: Implementar estadísticas mensuales
		LastUpdated:     time.Now(),
	}

	return dashboard, nil
}

func (s *AggregationService) getIntValue(data map[string]interface{}, key string, defaultValue int) int {
	if data == nil {
		return defaultValue
	}
	if val, ok := data[key]; ok {
		if intVal, ok := val.(int); ok {
			return intVal
		}
		if floatVal, ok := val.(float64); ok {
			return int(floatVal)
		}
	}
	return defaultValue
}

func (s *AggregationService) getFloatValue(data map[string]interface{}, key string, defaultValue float64) float64 {
	if data == nil {
		return defaultValue
	}
	if val, ok := data[key]; ok {
		if floatVal, ok := val.(float64); ok {
			return floatVal
		}
		if intVal, ok := val.(int); ok {
			return float64(intVal)
		}
	}
	return defaultValue
}