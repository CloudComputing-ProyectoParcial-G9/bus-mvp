package com.busmvp.mstickets.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;

@Document(collection = "tickets")
public class Ticket {

    @Id
    private String ticket_id;
    private String passenger_id;
    private String trip_id;
    private String seat_number;
    private String booking_status;
    private double total_price;
    private String currency;
    private Instant created_at;

    // getters and setters
    public String getTicket_id() { return ticket_id; }
    public void setTicket_id(String ticket_id) { this.ticket_id = ticket_id; }
    public String getPassenger_id() { return passenger_id; }
    public void setPassenger_id(String passenger_id) { this.passenger_id = passenger_id; }
    public String getTrip_id() { return trip_id; }
    public void setTrip_id(String trip_id) { this.trip_id = trip_id; }
    public String getSeat_number() { return seat_number; }
    public void setSeat_number(String seat_number) { this.seat_number = seat_number; }
    public String getBooking_status() { return booking_status; }
    public void setBooking_status(String booking_status) { this.booking_status = booking_status; }
    public double getTotal_price() { return total_price; }
    public void setTotal_price(double total_price) { this.total_price = total_price; }
    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }
    public Instant getCreated_at() { return created_at; }
    public void setCreated_at(Instant created_at) { this.created_at = created_at; }
}
