package com.busmvp.mstickets.service;

public class TicketNotFoundException extends RuntimeException {
    public TicketNotFoundException(String ticketId) {
        super("Ticket not found: " + ticketId);
    }
}
