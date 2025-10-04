package clients

import (
	"context"
	"fmt"

	"ms-history/src/config"
	"ms-history/src/models"
)

type TripsClient struct {
	*HTTPClient
}

func NewTripsClient(cfg *config.Config) *TripsClient {
	return &TripsClient{
		HTTPClient: NewHTTPClient(cfg.TripsURL, cfg, "trips-service"),
	}
}

func (c *TripsClient) GetTrip(ctx context.Context, tripID string) (*models.Trip, error) {
	var trip models.Trip
	err := c.GetJSON(ctx, fmt.Sprintf("/api/v1/trips/%s", tripID), &trip)
	if err != nil {
		return nil, fmt.Errorf("failed to get trip %s: %w", tripID, err)
	}
	return &trip, nil
}

func (c *TripsClient) GetRoute(ctx context.Context, routeID string) (*models.Route, error) {
	var route models.Route
	err := c.GetJSON(ctx, fmt.Sprintf("/api/v1/routes/%s", routeID), &route)
	if err != nil {
		return nil, fmt.Errorf("failed to get route %s: %w", routeID, err)
	}
	return &route, nil
}

func (c *TripsClient) ListRoutes(ctx context.Context) ([]models.Route, error) {
	var response struct {
		Data []models.Route `json:"data"`
	}
	err := c.GetJSON(ctx, "/api/v1/routes", &response)
	if err != nil {
		return nil, fmt.Errorf("failed to list routes: %w", err)
	}
	return response.Data, nil
}

func (c *TripsClient) ListTrips(ctx context.Context, page, limit int) ([]models.Trip, error) {
	var response struct {
		Data []models.Trip `json:"data"`
	}
	endpoint := fmt.Sprintf("/api/v1/trips?page=%d&limit=%d", page, limit)
	err := c.GetJSON(ctx, endpoint, &response)
	if err != nil {
		return nil, fmt.Errorf("failed to list trips: %w", err)
	}
	return response.Data, nil
}

func (c *TripsClient) GetTripsByRoute(ctx context.Context, routeID string) ([]models.Trip, error) {
	var response struct {
		Data []models.Trip `json:"data"`
	}
	endpoint := fmt.Sprintf("/api/v1/trips?routeId=%s", routeID)
	err := c.GetJSON(ctx, endpoint, &response)
	if err != nil {
		return nil, fmt.Errorf("failed to get trips by route %s: %w", routeID, err)
	}
	return response.Data, nil
}

func (c *TripsClient) GetTripsStats(ctx context.Context) (map[string]interface{}, error) {
	trips, err := c.ListTrips(ctx, 1, 1000)
	if err != nil {
		return nil, fmt.Errorf("failed to get trips stats: %w", err)
	}
	
	routes, err := c.ListRoutes(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get routes for stats: %w", err)
	}
	
	return map[string]interface{}{
		"total_trips":    len(trips),
		"active_routes":  len(routes),
		"total_routes":   len(routes),
	}, nil
}