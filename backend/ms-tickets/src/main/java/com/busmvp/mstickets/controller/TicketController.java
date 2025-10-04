package com.busmvp.mstickets.controller;

import com.busmvp.mstickets.service.TicketService;
import com.busmvp.mstickets.service.dto.CreateTicketRequest;
import com.busmvp.mstickets.service.dto.TicketDto;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
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
@Tag(name = "Tickets", description = "Operaciones de gestión de boletos")
public class TicketController {

    private final TicketService ticketService;

    public TicketController(TicketService ticketService) {
        this.ticketService = ticketService;
    }

    @GetMapping("/health")
    @Operation(summary = "Health Check", description = "Verifica el estado del servicio")
    @ApiResponse(responseCode = "200", description = "Servicio saludable")
    public ResponseEntity<?> health() {
        return ResponseEntity.ok(Map.of("status", "healthy", "timestamp", Instant.now().toString()));
    }

    @PostMapping
    @Operation(summary = "Crear ticket", description = "Crea un nuevo ticket de compra para un pasajero en un viaje específico")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "Ticket creado exitosamente",
                content = @Content(mediaType = "application/json", schema = @Schema(implementation = TicketDto.class))),
        @ApiResponse(responseCode = "400", description = "Datos de entrada inválidos", content = @Content),
        @ApiResponse(responseCode = "404", description = "Pasajero o viaje no encontrado", content = @Content),
        @ApiResponse(responseCode = "409", description = "No hay asientos disponibles", content = @Content)
    })
    public ResponseEntity<?> create(@Valid @RequestBody CreateTicketRequest req) {
        TicketDto dto = ticketService.createTicket(req);
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of("message", "Ticket purchased successfully", "data", dto));
    }

    @GetMapping
    @Operation(summary = "Listar tickets", description = "Obtiene una lista paginada de todos los tickets")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Lista de tickets obtenida exitosamente")
    })
    public ResponseEntity<?> list(
            @Parameter(description = "Número de página (por defecto: 1)") @RequestParam(name = "page", defaultValue = "1") int page,
            @Parameter(description = "Límite de resultados por página (por defecto: 20)") @RequestParam(name = "limit", defaultValue = "20") int limit) {
        List<TicketDto> list = ticketService.listTickets(page, limit);
        return ResponseEntity.ok(Map.of("data", list, "page", page, "limit", limit));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener ticket por ID", description = "Obtiene los detalles de un ticket específico")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Ticket encontrado",
                content = @Content(mediaType = "application/json", schema = @Schema(implementation = TicketDto.class))),
        @ApiResponse(responseCode = "404", description = "Ticket no encontrado", content = @Content)
    })
    public ResponseEntity<?> getById(@Parameter(description = "ID del ticket") @PathVariable("id") String id) {
        TicketDto dto = ticketService.getTicketById(id);
        return ResponseEntity.ok(Map.of("data", dto));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Actualizar ticket", description = "Actualiza la información de un ticket existente")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Ticket actualizado exitosamente",
                content = @Content(mediaType = "application/json", schema = @Schema(implementation = TicketDto.class))),
        @ApiResponse(responseCode = "404", description = "Ticket no encontrado", content = @Content)
    })
    public ResponseEntity<?> update(
            @Parameter(description = "ID del ticket") @PathVariable("id") String id, 
            @RequestBody TicketDto update) {
        TicketDto dto = ticketService.updateTicket(id, update);
        return ResponseEntity.ok(Map.of("message", "Ticket updated", "data", dto));
    }

    @PostMapping("/{id}/cancel")
    @Operation(summary = "Cancelar ticket", description = "Cancela un ticket existente y libera el asiento")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Ticket cancelado exitosamente",
                content = @Content(mediaType = "application/json", schema = @Schema(implementation = TicketDto.class))),
        @ApiResponse(responseCode = "404", description = "Ticket no encontrado", content = @Content)
    })
    public ResponseEntity<?> cancel(@Parameter(description = "ID del ticket") @PathVariable("id") String id) {
        TicketDto dto = ticketService.cancelTicket(id);
        return ResponseEntity.ok(Map.of("message", "Ticket cancelled", "data", dto));
    }

    @GetMapping("/passenger/{passenger_id}/history")
    @Operation(summary = "Historial de tickets por pasajero", description = "Obtiene todos los tickets de un pasajero específico")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Historial obtenido exitosamente")
    })
    public ResponseEntity<?> history(@Parameter(description = "ID del pasajero") @PathVariable("passenger_id") String passengerId) {
        List<TicketDto> list = ticketService.getTicketsByPassenger(passengerId);
        return ResponseEntity.ok(Map.of("data", list));
    }
}
