package main

import (
	"log"
	"fmt"

	"github.com/gin-gonic/gin"
	"ms-history/src/clients"
	"ms-history/src/config"
	"ms-history/src/handlers"
	"ms-history/src/routes"
	"ms-history/src/services"
)

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