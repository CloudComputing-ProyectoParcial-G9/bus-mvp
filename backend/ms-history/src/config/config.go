package config

import (
	"os"
	"strconv"
	"time"
)

type Config struct {
	Port                string
	Environment         string
	LogLevel           string
	
	// Microservices URLs
	PassengersURL      string
	TripsURL           string
	TicketsURL         string
	
	// HTTP Client Settings
	HTTPTimeout        time.Duration
	MaxRetries         int
	RetryDelay         time.Duration
	
	// Cache Settings
	RedisURL           string
	CacheTTL           time.Duration
	EnableCache        bool
	
	// Circuit Breaker Settings
	CircuitBreakerTimeout time.Duration
	CircuitBreakerMaxRequests uint32
}

func LoadConfig() *Config {
	return &Config{
		Port:                getEnv("MS_HISTORY_PORT", "8004"),
		Environment:         getEnv("NODE_ENV", "development"),
		LogLevel:           getEnv("LOG_LEVEL", "info"),
		
		PassengersURL:      getEnv("MS_PASSENGERS_URL", "http://localhost:8001"),
		TripsURL:           getEnv("MS_TRIPS_URL", "http://localhost:8002"),
		TicketsURL:         getEnv("MS_TICKETS_URL", "http://localhost:8003"),
		
		HTTPTimeout:        getEnvDuration("HTTP_TIMEOUT_MS", 5000) * time.Millisecond,
		MaxRetries:         getEnvInt("MAX_RETRIES", 3),
		RetryDelay:         getEnvDuration("RETRY_DELAY_MS", 1000) * time.Millisecond,
		
		RedisURL:           getEnv("REDIS_URL", "redis://localhost:6379"),
		CacheTTL:           getEnvDuration("CACHE_TTL_SECONDS", 300) * time.Second,
		EnableCache:        getEnvBool("ENABLE_CACHE", false),
		
		CircuitBreakerTimeout: time.Second * 30,
		CircuitBreakerMaxRequests: 3,
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getEnvDuration(key string, defaultValue int64) time.Duration {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.ParseInt(value, 10, 64); err == nil {
			return time.Duration(intValue)
		}
	}
	return time.Duration(defaultValue)
}

func getEnvBool(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if boolValue, err := strconv.ParseBool(value); err == nil {
			return boolValue
		}
	}
	return defaultValue
}