package com.busmvp.mstickets.service;

public class NoSeatsException extends RuntimeException {
    public NoSeatsException(String message) { super(message); }
}
