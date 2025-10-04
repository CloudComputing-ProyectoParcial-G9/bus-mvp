package handlers

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"ms-history/src/services"
)

type HistoryHandler struct {
	aggregationService *services.AggregationService
}

func NewHistoryHandler(aggregationService *services.AggregationService) *HistoryHandler {
	return &HistoryHandler{
		aggregationService: aggregationService,
	}
}

// GetPassengerHistory obtiene el historial completo de un pasajero
// @Summary Get passenger history
// @Description Get complete passenger travel history with statistics and recent tickets
// @Tags History
// @Accept json
// @Produce json
// @Param passenger_id path string true "Passenger ID"
// @Success 200 {object} models.PassengerHistoryResponse "Passenger history retrieved successfully"
// @Failure 400 {object} ErrorResponse "Invalid passenger ID"
// @Failure 404 {object} ErrorResponse "Passenger not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /api/v1/history/passengers/{passenger_id} [get]
func (h *HistoryHandler) GetPassengerHistory(c *gin.Context) {
	passengerID := c.Param("passenger_id")
	
	if passengerID == "" {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "Bad Request",
			Message: "passenger_id is required",
		})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	history, err := h.aggregationService.GetPassengerHistory(ctx, passengerID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "Internal Server Error",
			Message: "Failed to retrieve passenger history: " + err.Error(),
		})
		return
	}

	if history.Passenger == nil {
		c.JSON(http.StatusNotFound, ErrorResponse{
			Error:   "Not Found",
			Message: "Passenger not found",
		})
		return
	}

	c.JSON(http.StatusOK, history)
}

// GetDashboard obtiene resumen del dashboard con estadísticas generales
// @Summary Get dashboard summary
// @Description Get general statistics summary for dashboard including passengers, trips, tickets, and revenue
// @Tags Dashboard
// @Accept json
// @Produce json
// @Success 200 {object} models.DashboardSummaryResponse "Dashboard data retrieved successfully"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /api/v1/dashboard [get]
func (h *HistoryHandler) GetDashboard(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 15*time.Second)
	defer cancel()

	dashboard, err := h.aggregationService.GetDashboardSummary(ctx)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "Internal Server Error",
			Message: "Failed to retrieve dashboard data: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, dashboard)
}

// GetSystemHealth verifica el estado de todos los microservicios
// @Summary Get system health
// @Description Check health status of all microservices (passengers, trips, tickets)
// @Tags Health
// @Accept json
// @Produce json
// @Success 200 {object} SystemHealthResponse "System health status"
// @Router /api/v1/health [get]
func (h *HistoryHandler) GetSystemHealth(c *gin.Context) {
	// TODO: Implementar verificación de salud de los servicios
	health := SystemHealthResponse{
		Status:    "healthy",
		Timestamp: time.Now(),
		Services: map[string]ServiceHealth{
			"ms-passengers": {Status: "healthy", LastCheck: time.Now()},
			"ms-trips":      {Status: "healthy", LastCheck: time.Now()},
			"ms-tickets":    {Status: "healthy", LastCheck: time.Now()},
		},
	}

	c.JSON(http.StatusOK, health)
}

// Estructuras de respuesta de error y salud del sistema

// ErrorResponse representa un error en la API
// @Description Error response structure
type ErrorResponse struct {
	Error   string `json:"error" example:"Bad Request"`
	Message string `json:"message" example:"passenger_id is required"`
}

// SystemHealthResponse representa el estado del sistema
// @Description System health response structure
type SystemHealthResponse struct {
	Status    string                     `json:"status" example:"healthy"`
	Timestamp time.Time                  `json:"timestamp" example:"2025-10-04T12:00:00Z"`
	Services  map[string]ServiceHealth   `json:"services"`
}

// ServiceHealth representa el estado de un servicio
// @Description Individual service health status
type ServiceHealth struct {
	Status    string    `json:"status" example:"healthy"`
	LastCheck time.Time `json:"last_check" example:"2025-10-04T12:00:00Z"`
}