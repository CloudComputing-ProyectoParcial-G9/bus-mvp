package clients

import (
	"context"
	"fmt"

	"ms-history/src/config"
	"ms-history/src/models"
)

type PassengersClient struct {
	*HTTPClient
}

func NewPassengersClient(cfg *config.Config) *PassengersClient {
	return &PassengersClient{
		HTTPClient: NewHTTPClient(cfg.PassengersURL, cfg, "passengers-service"),
	}
}

func (c *PassengersClient) GetPassenger(ctx context.Context, passengerID string) (*models.Passenger, error) {
	var passenger models.Passenger
	err := c.GetJSON(ctx, fmt.Sprintf("/passengers/%s", passengerID), &passenger)
	if err != nil {
		return nil, fmt.Errorf("failed to get passenger %s: %w", passengerID, err)
	}
	return &passenger, nil
}

func (c *PassengersClient) ListPassengers(ctx context.Context, page, limit int) ([]models.Passenger, error) {
	var passengers []models.Passenger
	endpoint := fmt.Sprintf("/passengers?page=%d&limit=%d", page, limit)
	err := c.GetJSON(ctx, endpoint, &passengers)
	if err != nil {
		return nil, fmt.Errorf("failed to list passengers: %w", err)
	}
	return passengers, nil
}

func (c *PassengersClient) GetPassengerStats(ctx context.Context) (map[string]interface{}, error) {
	var stats map[string]interface{}
	err := c.GetJSON(ctx, "/passengers?page=1&limit=1", &stats)
	if err != nil {
		return nil, fmt.Errorf("failed to get passenger stats: %w", err)
	}
	
	// Simular estadísticas básicas
	passengers, _ := c.ListPassengers(ctx, 1, 1000)
	return map[string]interface{}{
		"total_passengers": len(passengers),
		"active_passengers": len(passengers), // Simplificado
	}, nil
}