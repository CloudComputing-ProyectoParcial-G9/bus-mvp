package services

import (
	"context"
	"fmt"
	"sort"
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
	var tickets []models.Ticket
	var errs []error
	var mu sync.Mutex

	wg.Add(4)

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

	// Obtener todos los tickets para calcular revenue real
	go func() {
		defer wg.Done()
		t, err := s.ticketsClient.ListTickets(ctx, 1, 1000)
		if err != nil {
			mu.Lock()
			errs = append(errs, err)
			mu.Unlock()
			return
		}
		tickets = t
	}()

	wg.Wait()

	// Calcular revenue real desde los trips
	totalRevenue := s.calculateTotalRevenue(ctx, tickets)

	// Calcular rutas populares (top 5)
	popularRoutes := s.calculatePopularRoutes(ctx, tickets, 5)

	// Calcular actividad reciente (últimas 5 actividades)
	recentActivity := s.calculateRecentActivity(ctx, tickets, 5)

	// Calcular estadísticas mensuales
	totalPassengers := s.getIntValue(passengerStats, "total_passengers", 0)
	totalTrips := s.getIntValue(tripStats, "total_trips", 0)
	monthlyStats := s.calculateMonthlyStats(ctx, tickets, totalPassengers, totalTrips)

	// Construir respuesta con fallbacks para datos faltantes
	dashboard := &models.DashboardSummaryResponse{
		TotalPassengers: totalPassengers,
		TotalTrips:      totalTrips,
		TotalTickets:    s.getIntValue(ticketStats, "total_tickets", 0),
		TotalRevenue:    totalRevenue,
		ActiveRoutes:    s.getIntValue(tripStats, "active_routes", 0),
		PopularRoutes:   popularRoutes,
		RecentActivity:  recentActivity,
		MonthlyStats:    monthlyStats,
		LastUpdated:     time.Now(),
	}

	return dashboard, nil
}

// calculateTotalRevenue calcula el revenue total obteniendo los precios desde los trips
func (s *AggregationService) calculateTotalRevenue(ctx context.Context, tickets []models.Ticket) float64 {
	if len(tickets) == 0 {
		return 0.0
	}

	var totalRevenue float64
	var mu sync.Mutex
	var wg sync.WaitGroup

	// Limitar concurrencia
	sem := make(chan struct{}, 10)

	for _, ticket := range tickets {
		if ticket.BookingStatus != "confirmed" {
			continue
		}

		wg.Add(1)
		go func(tripID string) {
			defer wg.Done()
			sem <- struct{}{}
			defer func() { <-sem }()

			trip, err := s.tripsClient.GetTrip(ctx, tripID)
			if err != nil {
				// Si no podemos obtener el trip, continuamos
				return
			}

			// Convertir finalPrice string a float64
			var price float64
			if trip.FinalPrice != "" {
				fmt.Sscanf(trip.FinalPrice, "%f", &price)
			}

			mu.Lock()
			totalRevenue += price
			mu.Unlock()
		}(ticket.TripID)
	}

	wg.Wait()
	return totalRevenue
}

// calculatePopularRoutes calcula las rutas más populares basadas en tickets y revenue
func (s *AggregationService) calculatePopularRoutes(ctx context.Context, tickets []models.Ticket, limit int) []models.RoutePopularity {
	if len(tickets) == 0 {
		return []models.RoutePopularity{}
	}

	// Mapa para contar tickets por ruta
	type routeStats struct {
		tripIDs  []string
		tickets  int
		revenue  float64
		routeInfo *models.Route
	}
	
	routeMap := make(map[string]*routeStats)
	var mu sync.Mutex
	var wg sync.WaitGroup
	sem := make(chan struct{}, 10)

	// Obtener información de cada trip y agrupar por ruta
	for _, ticket := range tickets {
		if ticket.BookingStatus != "confirmed" {
			continue
		}

		wg.Add(1)
		go func(tripID string) {
			defer wg.Done()
			sem <- struct{}{}
			defer func() { <-sem }()

			trip, err := s.tripsClient.GetTrip(ctx, tripID)
			if err != nil {
				return
			}

			route, err := s.tripsClient.GetRoute(ctx, trip.RouteID)
			if err != nil {
				return
			}

			var price float64
			if trip.FinalPrice != "" {
				fmt.Sscanf(trip.FinalPrice, "%f", &price)
			}

			mu.Lock()
			if _, exists := routeMap[trip.RouteID]; !exists {
				routeMap[trip.RouteID] = &routeStats{
					tripIDs:  []string{},
					routeInfo: route,
				}
			}
			routeMap[trip.RouteID].tickets++
			routeMap[trip.RouteID].revenue += price
			routeMap[trip.RouteID].tripIDs = append(routeMap[trip.RouteID].tripIDs, tripID)
			mu.Unlock()
		}(ticket.TripID)
	}

	wg.Wait()

	// Convertir a slice y ordenar por número de tickets
	popularRoutes := []models.RoutePopularity{}
	for _, stats := range routeMap {
		if stats.routeInfo != nil {
			avgPrice := 0.0
			if stats.tickets > 0 {
				avgPrice = stats.revenue / float64(stats.tickets)
			}
			
			popularRoutes = append(popularRoutes, models.RoutePopularity{
				RouteCode:       stats.routeInfo.RouteCode,
				OriginCity:      stats.routeInfo.OriginCity,
				DestinationCity: stats.routeInfo.DestinationCity,
				TotalTickets:    stats.tickets,
				TotalRevenue:    stats.revenue,
				AveragePrice:    avgPrice,
			})
		}
	}

	// Ordenar por total de tickets (descendente)
	sort.Slice(popularRoutes, func(i, j int) bool {
		return popularRoutes[i].TotalTickets > popularRoutes[j].TotalTickets
	})

	// Limitar resultados
	if limit > 0 && len(popularRoutes) > limit {
		popularRoutes = popularRoutes[:limit]
	}

	return popularRoutes
}

// calculateRecentActivity genera actividad reciente del sistema
func (s *AggregationService) calculateRecentActivity(ctx context.Context, tickets []models.Ticket, limit int) []models.RecentActivity {
	activities := []models.RecentActivity{}

	// Agregar actividad de tickets recientes (últimos N tickets)
	recentTickets := tickets
	if len(recentTickets) > limit {
		recentTickets = recentTickets[len(recentTickets)-limit:]
	}

	for _, ticket := range recentTickets {
		if ticket.BookingStatus == "confirmed" {
			activities = append(activities, models.RecentActivity{
				Type:        "ticket_purchase",
				Description: fmt.Sprintf("Ticket purchased for trip %s", ticket.TripID),
				Timestamp:   time.Now(), // En producción, usar ticket.CreatedAt si existe
				EntityID:    ticket.TicketID,
			})
		}
	}

	// Ordenar por timestamp (más reciente primero)
	sort.Slice(activities, func(i, j int) bool {
		return activities[i].Timestamp.After(activities[j].Timestamp)
	})

	if len(activities) > limit {
		activities = activities[:limit]
	}

	return activities
}

// calculateMonthlyStats calcula estadísticas del mes actual
func (s *AggregationService) calculateMonthlyStats(ctx context.Context, tickets []models.Ticket, totalPassengers int, totalTrips int) *models.MonthlyStatistics {
	now := time.Now()
	currentMonth := now.Format("2006-01")
	
	// Calcular revenue del mes actual
	currentRevenue := 0.0
	currentTickets := 0
	
	for _, ticket := range tickets {
		if ticket.BookingStatus == "confirmed" {
			currentTickets++
			// En producción, filtrar por fecha del ticket
			// Por ahora contamos todos los tickets
		}
	}
	
	// Calcular revenue para tickets del mes actual
	currentRevenue = s.calculateTotalRevenue(ctx, tickets)

	return &models.MonthlyStatistics{
		CurrentMonth: models.MonthData{
			Month:      currentMonth,
			Passengers: totalPassengers,
			Trips:      totalTrips,
			Tickets:    currentTickets,
			Revenue:    currentRevenue,
		},
		PreviousMonth: models.MonthData{
			Month:      "", // TODO: Implementar histórico
			Passengers: 0,
			Trips:      0,
			Tickets:    0,
			Revenue:    0,
		},
		GrowthRate: 0.0, // TODO: Calcular cuando haya datos del mes anterior
	}
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
// GetPopularRoutes obtiene las rutas más populares basado en ventas de tickets
func (s *AggregationService) GetPopularRoutes(ctx context.Context, limit int, period string) (*models.PopularRoutesResponse, error) {
var wg sync.WaitGroup
var tickets []models.Ticket
var trips []models.Trip
var routes []models.Route
var errs []error
var mu sync.Mutex

wg.Add(3)

// Obtener todos los tickets
go func() {
defer wg.Done()
t, err := s.ticketsClient.ListTickets(ctx, 1, 10000)
if err != nil {
mu.Lock()
errs = append(errs, err)
mu.Unlock()
return
}
tickets = t
}()

// Obtener todos los trips
go func() {
defer wg.Done()
t, err := s.tripsClient.ListTrips(ctx, 1, 10000)
if err != nil {
mu.Lock()
errs = append(errs, err)
mu.Unlock()
return
}
trips = t
}()

// Obtener todas las rutas
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

if len(errs) > 0 {
return nil, fmt.Errorf("failed to fetch data: %w", errs[0])
}

// Crear mapa de trips por ID para búsqueda rápida
tripMap := make(map[string]*models.Trip)
for i := range trips {
tripMap[trips[i].TripID] = &trips[i]
}

// Crear mapa de routes por ID
routeMap := make(map[string]*models.Route)
for i := range routes {
routeMap[routes[i].RouteID] = &routes[i]
}

// Agrupar tickets por route_id
routeStats := make(map[string]*routeStatsData)

for _, ticket := range tickets {
if ticket.BookingStatus != "confirmed" {
continue
}

trip, exists := tripMap[ticket.TripID]
if !exists || trip == nil {
continue
}

route, exists := routeMap[trip.RouteID]
if !exists || route == nil {
continue
}

if _, exists := routeStats[trip.RouteID]; !exists {
routeStats[trip.RouteID] = &routeStatsData{
RouteID:         route.RouteID,
RouteCode:       route.RouteCode,
OriginCity:      route.OriginCity,
DestinationCity: route.DestinationCity,
Distance:        route.Distance,
TotalTickets:    0,
TotalRevenue:    0,
TotalSeats:      0,
OccupiedSeats:   0,
}
}

routeStats[trip.RouteID].TotalTickets++
routeStats[trip.RouteID].TotalRevenue += ticket.TotalPrice
routeStats[trip.RouteID].TotalSeats += trip.BusCapacity
routeStats[trip.RouteID].OccupiedSeats += 1
}

// Convertir a slice y ordenar por total de tickets (popularidad)
popularRoutes := make([]models.PopularRouteResponse, 0, len(routeStats))
for _, stats := range routeStats {
avgPrice := 0.0
if stats.TotalTickets > 0 {
avgPrice = stats.TotalRevenue / float64(stats.TotalTickets)
}

occupancyRate := 0.0
if stats.TotalSeats > 0 {
occupancyRate = (float64(stats.OccupiedSeats) / float64(stats.TotalSeats)) * 100
}

popularRoutes = append(popularRoutes, models.PopularRouteResponse{
RouteID:         stats.RouteID,
RouteCode:       stats.RouteCode,
OriginCity:      stats.OriginCity,
DestinationCity: stats.DestinationCity,
Distance:        stats.Distance,
TotalTickets:    stats.TotalTickets,
TotalRevenue:    stats.TotalRevenue,
AveragePrice:    avgPrice,
OccupancyRate:   occupancyRate,
Trend:           "stable", // Por ahora, simplificado
})
}

// Ordenar por total de tickets descendente
sort.Slice(popularRoutes, func(i, j int) bool {
return popularRoutes[i].TotalTickets > popularRoutes[j].TotalTickets
})

// Asignar ranking
for i := range popularRoutes {
popularRoutes[i].Rank = i + 1
}

// Limitar resultados
if limit > 0 && len(popularRoutes) > limit {
popularRoutes = popularRoutes[:limit]
}

return &models.PopularRoutesResponse{
PopularRoutes:       popularRoutes,
Period:              period,
TotalRoutesAnalyzed: len(routes),
GeneratedAt:         time.Now(),
}, nil
}

// GetRouteStatistics obtiene estadísticas detalladas de una ruta específica
func (s *AggregationService) GetRouteStatistics(ctx context.Context, routeID string) (*models.RouteStatsResponse, error) {
var wg sync.WaitGroup
var route *models.Route
var tickets []models.Ticket
var trips []models.Trip
var errs []error
var mu sync.Mutex

wg.Add(3)

// Obtener información de la ruta
go func() {
defer wg.Done()
r, err := s.tripsClient.GetRoute(ctx, routeID)
if err != nil {
mu.Lock()
errs = append(errs, err)
mu.Unlock()
return
}
route = r
}()

// Obtener todos los tickets
go func() {
defer wg.Done()
t, err := s.ticketsClient.ListTickets(ctx, 1, 10000)
if err != nil {
mu.Lock()
errs = append(errs, err)
mu.Unlock()
return
}
tickets = t
}()

// Obtener todos los trips
go func() {
defer wg.Done()
t, err := s.tripsClient.ListTrips(ctx, 1, 10000)
if err != nil {
mu.Lock()
errs = append(errs, err)
mu.Unlock()
return
}
trips = t
}()

wg.Wait()

if len(errs) > 0 {
return nil, fmt.Errorf("failed to fetch route data: %w", errs[0])
}

if route == nil {
return nil, fmt.Errorf("route not found")
}

// Filtrar trips de esta ruta
routeTrips := []models.Trip{}
tripMap := make(map[string]*models.Trip)
for i := range trips {
if trips[i].RouteID == routeID {
routeTrips = append(routeTrips, trips[i])
tripMap[trips[i].TripID] = &trips[i]
}
}

// Calcular estadísticas
stats := models.RouteStatistics{
TotalTrips: len(routeTrips),
}

totalSeats := 0
occupiedSeats := 0
recentTripsMap := make(map[string]*models.TripSummary)

for _, ticket := range tickets {
if ticket.BookingStatus != "confirmed" {
continue
}

trip, exists := tripMap[ticket.TripID]
if !exists {
continue
}

stats.TotalTicketsSold++
stats.TotalRevenue += ticket.TotalPrice

totalSeats += trip.BusCapacity
occupiedSeats++

// Agregar a recent trips
if _, exists := recentTripsMap[trip.TripID]; !exists {
recentTripsMap[trip.TripID] = &models.TripSummary{
TripID:         trip.TripID,
DepartureDate:  trip.DepartureDateTime,
TicketsSold:    0,
SeatsAvailable: trip.AvailableSeats,
Status:         trip.Status,
}
}
recentTripsMap[trip.TripID].TicketsSold++
}

// Calcular promedios
if stats.TotalTicketsSold > 0 {
stats.AveragePrice = stats.TotalRevenue / float64(stats.TotalTicketsSold)
}

if totalSeats > 0 {
stats.OccupancyRate = (float64(occupiedSeats) / float64(totalSeats)) * 100
}

// Simplificado: peak demand (podría mejorarse con análisis real)
stats.PeakDemandDay = "N/A"

// Convertir recent trips a slice
recentTrips := make([]models.TripSummary, 0, len(recentTripsMap))
for _, trip := range recentTripsMap {
recentTrips = append(recentTrips, *trip)
}

// Ordenar por fecha descendente
sort.Slice(recentTrips, func(i, j int) bool {
return recentTrips[i].DepartureDate.After(recentTrips[j].DepartureDate)
})

// Limitar a últimos 5 viajes
if len(recentTrips) > 5 {
recentTrips = recentTrips[:5]
}

// Calcular tendencia (simplificado)
trend := models.RouteTrend{
CurrentMonth:  stats.TotalTicketsSold,
PreviousMonth: 0, // Simplificado
GrowthRate:    0,
Direction:     "stable",
}

// Calcular ranking (necesitaríamos comparar con todas las rutas)
popularityRank := 0

return &models.RouteStatsResponse{
RouteID:         route.RouteID,
RouteCode:       route.RouteCode,
OriginCity:      route.OriginCity,
DestinationCity: route.DestinationCity,
Distance:        route.Distance,
Statistics:      stats,
PopularityRank:  popularityRank,
Trend:           trend,
RecentTrips:     recentTrips,
}, nil
}

// routeStatsData estructura auxiliar para calcular estadísticas
type routeStatsData struct {
RouteID         string
RouteCode       string
OriginCity      string
DestinationCity string
Distance        float64
TotalTickets    int
TotalRevenue    float64
TotalSeats      int
OccupiedSeats   int
}
