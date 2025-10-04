package models

import (
	"encoding/json"
	"time"
)

// FlexibleDate is a type that can unmarshal from multiple date formats
type FlexibleDate struct {
	time.Time
}

// UnmarshalJSON implements custom unmarshaling for FlexibleDate
func (fd *FlexibleDate) UnmarshalJSON(b []byte) error {
	var s string
	if err := json.Unmarshal(b, &s); err != nil {
		return err
	}
	
	if s == "" || s == "null" {
		return nil
	}
	
	// Try multiple date formats
	formats := []string{
		"2006-01-02T15:04:05Z07:00", // RFC3339
		"2006-01-02T15:04:05Z",      // RFC3339 without timezone
		"2006-01-02",                // Date only
		"2006-01-02 15:04:05",       // Datetime without T
	}
	
	var parseErr error
	for _, format := range formats {
		t, err := time.Parse(format, s)
		if err == nil {
			fd.Time = t
			return nil
		}
		parseErr = err
	}
	
	return parseErr
}

// Passenger representa los datos de un pasajero
type Passenger struct {
	PassengerID    string       `json:"passenger_id"`
	FullName       string       `json:"full_name"`
	Email          string       `json:"email"`
	Phone          string       `json:"phone"`
	DocumentType   string       `json:"document_type"`
	DocumentNumber string       `json:"document_number"`
	DateOfBirth    FlexibleDate `json:"date_of_birth"`
	Status         string       `json:"status"`
	CreatedAt      *time.Time   `json:"created_at"`
}

// Trip representa los datos de un viaje
type Trip struct {
	TripID            string    `json:"trip_id"`
	RouteID           string    `json:"route_id"`
	DepartureDateTime time.Time `json:"departure_datetime"`
	ArrivalDateTime   time.Time `json:"arrival_datetime"`
	BusCapacity       int       `json:"bus_capacity"`
	AvailableSeats    int       `json:"available_seats"`
	PricePerSeat      float64   `json:"price_per_seat"`
	Status            string    `json:"status"`
	DriverName        string    `json:"driver_name"`
	BusLicensePlate   string    `json:"bus_license_plate"`
}

// Route representa los datos de una ruta
type Route struct {
	RouteID         string  `json:"route_id"`
	RouteCode       string  `json:"route_code"`
	OriginCity      string  `json:"origin_city"`
	DestinationCity string  `json:"destination_city"`
	Distance        float64 `json:"distance"`
	EstimatedDuration int   `json:"estimated_duration"`
	Status          string  `json:"status"`
}

// Ticket representa los datos de un boleto
type Ticket struct {
	TicketID         string    `json:"ticket_id"`
	PassengerID      string    `json:"passenger_id"`
	TripID           string    `json:"trip_id"`
	SeatNumber       string    `json:"seat_number"`
	PurchaseDate     time.Time `json:"purchase_date"`
	TotalPrice       float64   `json:"total_price"`
	Currency         string    `json:"currency"`
	PaymentMethod    string    `json:"payment_method"`
	BookingStatus    string    `json:"booking_status"`
	BookingReference string    `json:"booking_reference"`
}

// TripWithRoute representa un viaje con información de ruta
type TripWithRoute struct {
	Trip  Trip  `json:"trip"`
	Route Route `json:"route"`
}