package routes

import (
	"github.com/gin-gonic/gin"
	"ms-history/src/handlers"
	"ms-history/src/middleware"
)

func SetupRoutes(r *gin.Engine, historyHandler *handlers.HistoryHandler) {
	// Middleware global
	r.Use(middleware.CORSMiddleware())
	r.Use(middleware.LoggingMiddleware())
	r.Use(gin.Recovery())

	// Health check básico
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "healthy",
			"service": "ms-history",
		})
	})

	// API v1
	v1 := r.Group("/api/v1")
	{
		// Dashboard endpoints
		v1.GET("/dashboard", historyHandler.GetDashboard)
		
		// History endpoints
		history := v1.Group("/history")
		{
			history.GET("/passengers/:passenger_id", historyHandler.GetPassengerHistory)
		}
		
		// System health
		v1.GET("/health", historyHandler.GetSystemHealth)
	}
}