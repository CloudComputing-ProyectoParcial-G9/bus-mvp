package com.busmvp.mstickets.service;

public class PassengerNotFoundException extends RuntimeException {
    public PassengerNotFoundException(String passengerId) {
        super("Passenger not found: " + passengerId);
    }
}
