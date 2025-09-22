package com.busmvp.mstickets.controller;

import com.busmvp.mstickets.service.TicketService;
import com.busmvp.mstickets.service.dto.CreateTicketRequest;
import com.busmvp.mstickets.service.dto.TicketDto;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.time.Instant;
import java.util.Map;
import java.util.List;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;

@RestController
@RequestMapping("/tickets")
public class TicketController {

    private final TicketService ticketService;

    public TicketController(TicketService ticketService) {
        this.ticketService = ticketService;
    }

    @GetMapping("/health")
    public ResponseEntity<?> health() {
        return ResponseEntity.ok(Map.of("status", "healthy", "timestamp", Instant.now().toString()));
    }

    @PostMapping
    public ResponseEntity<?> create(@Valid @RequestBody CreateTicketRequest req) {
        TicketDto dto = ticketService.createTicket(req);
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of("message", "Ticket purchased successfully", "data", dto));
    }

    @GetMapping
    public ResponseEntity<?> list(@RequestParam(name = "page", defaultValue = "1") int page,
                                  @RequestParam(name = "limit", defaultValue = "20") int limit) {
        List<TicketDto> list = ticketService.listTickets(page, limit);
        return ResponseEntity.ok(Map.of("data", list, "page", page, "limit", limit));
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getById(@PathVariable("id") String id) {
        TicketDto dto = ticketService.getTicketById(id);
        return ResponseEntity.ok(Map.of("data", dto));
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> update(@PathVariable("id") String id, @RequestBody TicketDto update) {
        TicketDto dto = ticketService.updateTicket(id, update);
        return ResponseEntity.ok(Map.of("message", "Ticket updated", "data", dto));
    }

    @PostMapping("/{id}/cancel")
    public ResponseEntity<?> cancel(@PathVariable("id") String id) {
        TicketDto dto = ticketService.cancelTicket(id);
        return ResponseEntity.ok(Map.of("message", "Ticket cancelled", "data", dto));
    }

    @GetMapping("/passenger/{passenger_id}/history")
    public ResponseEntity<?> history(@PathVariable("passenger_id") String passengerId) {
        List<TicketDto> list = ticketService.getTicketsByPassenger(passengerId);
        return ResponseEntity.ok(Map.of("data", list));
    }
}
