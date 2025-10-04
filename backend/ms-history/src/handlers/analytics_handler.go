package handlers

import (
	"context"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"ms-history/src/services"
)

type AnalyticsHandler struct {
	aggregationService *services.AggregationService
}

func NewAnalyticsHandler(aggregationService *services.AggregationService) *AnalyticsHandler {
	return &AnalyticsHandler{
		aggregationService: aggregationService,
	}
}

// GetPopularRoutes obtiene las rutas más populares
// @Summary Get popular routes
// @Description Get list of most popular routes ranked by ticket sales
// @Tags Analytics
// @Accept json
// @Produce json
// @Param limit query int false "Number of routes to return (default 10)" default(10)
// @Param period query string false "Time period (month, week, all)" default(month)
// @Success 200 {object} models.PopularRoutesResponse "Popular routes retrieved successfully"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /api/v1/analytics/popular-routes [get]
func (h *AnalyticsHandler) GetPopularRoutes(c *gin.Context) {
	// Parse limit parameter
	limit := 10
	if limitParam := c.Query("limit"); limitParam != "" {
		if l, err := strconv.Atoi(limitParam); err == nil && l > 0 && l <= 100 {
			limit = l
		}
	}

	// Parse period parameter
	period := c.DefaultQuery("period", "month")

	ctx, cancel := context.WithTimeout(c.Request.Context(), 15*time.Second)
	defer cancel()

	popularRoutes, err := h.aggregationService.GetPopularRoutes(ctx, limit, period)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "Internal Server Error",
			Message: "Failed to retrieve popular routes: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, popularRoutes)
}

// GetRouteStatistics obtiene estadísticas detalladas de una ruta
// @Summary Get route statistics by ID
// @Description Get detailed statistics for a specific route including trips, tickets, and trends
// @Tags Analytics
// @Accept json
// @Produce json
// @Param route_id path string true "Route ID"
// @Success 200 {object} models.RouteStatsResponse "Route statistics retrieved successfully"
// @Failure 400 {object} ErrorResponse "Invalid route ID"
// @Failure 404 {object} ErrorResponse "Route not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /api/v1/analytics/routes/{route_id}/stats [get]
func (h *AnalyticsHandler) GetRouteStats(c *gin.Context) {
	routeID := c.Param("route_id")

	if routeID == "" {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "Bad Request",
			Message: "route_id is required",
		})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 15*time.Second)
	defer cancel()

	stats, err := h.aggregationService.GetRouteStatistics(ctx, routeID)
	if err != nil {
		// Check if it's a not found error
		if isNotFoundError(err) {
			c.JSON(http.StatusNotFound, ErrorResponse{
				Error:   "Not Found",
				Message: "Route not found",
			})
			return
		}

		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "Internal Server Error",
			Message: "Failed to retrieve route statistics: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, stats)
}
