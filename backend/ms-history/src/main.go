package main

import (
	"log"
	"fmt"

	"github.com/gin-gonic/gin"
	"ms-history/src/clients"
	"ms-history/src/config"
	_ "ms-history/src/docs"
	"ms-history/src/handlers"
	"ms-history/src/routes"
	"ms-history/src/services"
)

// @title Bus MVP - History Service API
// @version 1.0
// @description API de agregación para historial de pasajeros del sistema Bus MVP. Consolida datos de passengers, trips y tickets.
// @contact.name Bus MVP Team
// @contact.email dev@busmvp.com
// @license.name MIT
// @license.url https://opensource.org/licenses/MIT
// @host localhost:8004
// @BasePath /
// @schemes http
// @securityDefinitions.apikey ApiKeyAuth
// @in header
// @name Authorization

func main() {
	// Cargar configuración
	cfg := config.LoadConfig()

	// Configurar modo de Gin (production/debug)
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	// Inicializar clientes HTTP
	passengersClient := clients.NewPassengersClient(cfg)
	tripsClient := clients.NewTripsClient(cfg)
	ticketsClient := clients.NewTicketsClient(cfg)

	// Inicializar servicios
	aggregationService := services.NewAggregationService(
		passengersClient,
		tripsClient,
		ticketsClient,
	)

	// Inicializar handlers
	historyHandler := handlers.NewHistoryHandler(aggregationService)

	// Configurar router
	router := gin.New()
	routes.SetupRoutes(router, historyHandler)

	// Log de inicio
	log.Printf("🚌 MS-History starting on port %s", cfg.Port)
	log.Printf("📊 Environment: %s", cfg.Environment)
	log.Printf("🔗 Passengers Service: %s", cfg.PassengersURL)
	log.Printf("🚐 Trips Service: %s", cfg.TripsURL)
	log.Printf("🎫 Tickets Service: %s", cfg.TicketsURL)

	// Iniciar servidor
	serverAddr := fmt.Sprintf(":%s", cfg.Port)
	if err := router.Run(serverAddr); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}