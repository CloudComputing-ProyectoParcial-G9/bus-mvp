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
// @Description Get complete passenger travel history with statistics
// @Tags History
// @Accept json
// @Produce json
// @Param passenger_id path string true "Passenger ID"
// @Success 200 {object} models.PassengerHistoryResponse
// @Failure 400 {object} ErrorResponse
// @Failure 404 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
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
// @Description Get general statistics summary for dashboard
// @Tags Dashboard
// @Accept json
// @Produce json
// @Success 200 {object} models.DashboardSummaryResponse
// @Failure 500 {object} ErrorResponse
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
// @Description Check health status of all microservices
// @Tags Health
// @Accept json
// @Produce json
// @Success 200 {object} SystemHealthResponse
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
type ErrorResponse struct {
	Error   string `json:"error"`
	Message string `json:"message"`
}

type SystemHealthResponse struct {
	Status    string                     `json:"status"`
	Timestamp time.Time                  `json:"timestamp"`
	Services  map[string]ServiceHealth   `json:"services"`
}

type ServiceHealth struct {
	Status    string    `json:"status"`
	LastCheck time.Time `json:"last_check"`
}