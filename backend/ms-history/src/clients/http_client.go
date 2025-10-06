package clients

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/sony/gobreaker"
	"ms-history/src/config"
)

type HTTPClient struct {
	client      *http.Client
	breaker     *gobreaker.CircuitBreaker
	maxRetries  int
	retryDelay  time.Duration
	baseURL     string
}

func NewHTTPClient(baseURL string, cfg *config.Config, serviceName string) *HTTPClient {
	// Configurar circuit breaker
	breakerSettings := gobreaker.Settings{
		Name:        serviceName,
		MaxRequests: cfg.CircuitBreakerMaxRequests,
		Interval:    time.Second * 60,
		Timeout:     cfg.CircuitBreakerTimeout,
		ReadyToTrip: func(counts gobreaker.Counts) bool {
			return counts.ConsecutiveFailures > 3
		},
		OnStateChange: func(name string, from gobreaker.State, to gobreaker.State) {
			fmt.Printf("Circuit breaker %s changed from %s to %s\n", name, from, to)
		},
	}

	return &HTTPClient{
		client: &http.Client{
			Timeout: cfg.HTTPTimeout,
		},
		breaker:    gobreaker.NewCircuitBreaker(breakerSettings),
		maxRetries: cfg.MaxRetries,
		retryDelay: cfg.RetryDelay,
		baseURL:    baseURL,
	}
}

func (c *HTTPClient) Get(ctx context.Context, endpoint string) ([]byte, error) {
	url := c.baseURL + endpoint
	
	result, err := c.breaker.Execute(func() (interface{}, error) {
		return c.doRequestWithRetry(ctx, "GET", url, nil)
	})
	
	if err != nil {
		return nil, err
	}
	
	return result.([]byte), nil
}

func (c *HTTPClient) GetJSON(ctx context.Context, endpoint string, target interface{}) error {
	data, err := c.Get(ctx, endpoint)
	if err != nil {
		return err
	}
	
	return json.Unmarshal(data, target)
}

func (c *HTTPClient) doRequestWithRetry(ctx context.Context, method, url string, body io.Reader) ([]byte, error) {
	var lastErr error
	
	for attempt := 0; attempt <= c.maxRetries; attempt++ {
		req, err := http.NewRequestWithContext(ctx, method, url, body)
		if err != nil {
			return nil, err
		}
		
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("User-Agent", "ms-history/1.0")
		req.Header.Set("X-Internal-Call", "true") // Identificar como llamada interna
		
		resp, err := c.client.Do(req)
		if err != nil {
			lastErr = err
			if attempt < c.maxRetries {
				time.Sleep(c.calculateBackoff(attempt))
				continue
			}
			break
		}
		
		defer resp.Body.Close()
		
		if resp.StatusCode >= 200 && resp.StatusCode < 300 {
			return io.ReadAll(resp.Body)
		}
		
		if resp.StatusCode >= 500 && attempt < c.maxRetries {
			lastErr = fmt.Errorf("server error: %d", resp.StatusCode)
			time.Sleep(c.calculateBackoff(attempt))
			continue
		}
		
		bodyBytes, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("HTTP %d: %s", resp.StatusCode, string(bodyBytes))
	}
	
	return nil, lastErr
}

func (c *HTTPClient) calculateBackoff(attempt int) time.Duration {
	// Exponential backoff with jitter
	backoff := time.Duration(attempt+1) * c.retryDelay
	if backoff > time.Second*10 {
		backoff = time.Second * 10
	}
	return backoff
}

func (c *HTTPClient) HealthCheck(ctx context.Context) (time.Duration, error) {
	start := time.Now()
	
	_, err := c.Get(ctx, "/health")
	duration := time.Since(start)
	
	return duration, err
}