package com.busmvp.mstickets.service.dto;

public class TripResponse {
    private String tripId;
    private String routeId;
    private String finalPrice;
    private String currency;
    
    // Getters and setters
    public String getTripId() { return tripId; }
    public void setTripId(String tripId) { this.tripId = tripId; }
    public String getRouteId() { return routeId; }
    public void setRouteId(String routeId) { this.routeId = routeId; }
    public String getFinalPrice() { return finalPrice; }
    public void setFinalPrice(String finalPrice) { this.finalPrice = finalPrice; }
    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }
}
