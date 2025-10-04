package clients

import (
	"context"
	"fmt"

	"ms-history/src/config"
	"ms-history/src/models"
)

type TicketsClient struct {
	*HTTPClient
}

func NewTicketsClient(cfg *config.Config) *TicketsClient {
	return &TicketsClient{
		HTTPClient: NewHTTPClient(cfg.TicketsURL, cfg, "tickets-service"),
	}
}

func (c *TicketsClient) GetTicketsByPassenger(ctx context.Context, passengerID string) ([]models.Ticket, error) {
	var response struct {
		Data []models.Ticket `json:"data"`
	}
	endpoint := fmt.Sprintf("/tickets?passenger_id=%s", passengerID)
	err := c.GetJSON(ctx, endpoint, &response)
	if err != nil {
		return nil, fmt.Errorf("failed to get tickets for passenger %s: %w", passengerID, err)
	}
	return response.Data, nil
}

func (c *TicketsClient) GetTicketsByTrip(ctx context.Context, tripID string) ([]models.Ticket, error) {
	var response struct {
		Data []models.Ticket `json:"data"`
	}
	endpoint := fmt.Sprintf("/tickets?trip_id=%s", tripID)
	err := c.GetJSON(ctx, endpoint, &response)
	if err != nil {
		return nil, fmt.Errorf("failed to get tickets for trip %s: %w", tripID, err)
	}
	return response.Data, nil
}

func (c *TicketsClient) ListTickets(ctx context.Context, page, limit int) ([]models.Ticket, error) {
	var response struct {
		Data []models.Ticket `json:"data"`
	}
	endpoint := fmt.Sprintf("/tickets?page=%d&limit=%d", page, limit)
	err := c.GetJSON(ctx, endpoint, &response)
	if err != nil {
		return nil, fmt.Errorf("failed to list tickets: %w", err)
	}
	return response.Data, nil
}

func (c *TicketsClient) GetTicketsStats(ctx context.Context) (map[string]interface{}, error) {
	tickets, err := c.ListTickets(ctx, 1, 1000)
	if err != nil {
		return nil, fmt.Errorf("failed to get tickets stats: %w", err)
	}
	
	totalRevenue := 0.0
	confirmedTickets := 0
	
	for _, ticket := range tickets {
		if ticket.BookingStatus == "confirmed" {
			totalRevenue += ticket.TotalPrice
			confirmedTickets++
		}
	}
	
	return map[string]interface{}{
		"total_tickets":     len(tickets),
		"confirmed_tickets": confirmedTickets,
		"total_revenue":     totalRevenue,
		"average_price":     totalRevenue / float64(max(confirmedTickets, 1)),
	}, nil
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}