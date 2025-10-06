package com.busmvp.mstickets.service;

import com.busmvp.mstickets.model.Ticket;
import com.busmvp.mstickets.repository.TicketRepository;
import com.busmvp.mstickets.service.dto.CreateTicketRequest;
import com.busmvp.mstickets.service.dto.TicketDto;
import com.busmvp.mstickets.service.dto.TripResponse;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.time.Instant;
import java.util.UUID;
import java.util.List;
import java.util.stream.Collectors;
import java.util.Optional;

@Service
public class TicketService {

    private final TicketRepository ticketRepository;

    public TicketService(TicketRepository ticketRepository) {
        this.ticketRepository = ticketRepository;
    }

    public TicketDto createTicket(CreateTicketRequest req) {
        // TODO: Re-enable integration checks once other services are properly configured
        // For now, skip validation to allow ticket creation during development

        // Basic integration checks: validate passenger and trip exist (DISABLED FOR NOW)
        boolean enableIntegrationChecks = Boolean.parseBoolean(System.getenv().getOrDefault("ENABLE_INTEGRATION_CHECKS", "false"));

        String tripsUrl = System.getenv().getOrDefault("MS_TRIPS_URL", "http://ms-trips:8002");
        RestTemplate rt = new RestTemplate();
        TripResponse trip = null;
        double tripPrice = 0.0;
        String currency = "PEN";

        if (enableIntegrationChecks) {
            String passengersUrl = System.getenv().getOrDefault("MS_PASSENGERS_URL", "http://ms-passengers:8001");
            try {
                rt.getForEntity(passengersUrl + "/api/passengers/" + req.getPassenger_id(), String.class);
            } catch (RestClientException ex) {
                throw new PassengerNotFoundException(req.getPassenger_id());
            }
        }

        // Always try to get trip price, even if integration checks are disabled
        try {
            trip = rt.getForObject(tripsUrl + "/api/v1/trips/" + req.getTrip_id(), TripResponse.class);
            if (trip != null && trip.getFinalPrice() != null && !trip.getFinalPrice().isEmpty()) {
                tripPrice = Double.parseDouble(trip.getFinalPrice());
                if (trip.getCurrency() != null && !trip.getCurrency().isEmpty()) {
                    currency = trip.getCurrency();
                }
            }
        } catch (Exception ex) {
            // If we can't get trip price, log it but continue with 0.0
            System.err.println("Warning: Could not fetch trip price for " + req.getTrip_id() + ": " + ex.getMessage());
            if (enableIntegrationChecks) {
                throw new TripNotFoundException(req.getTrip_id());
            }
        }

        String ticketId = "ticket_" + UUID.randomUUID().toString();
        Instant now = Instant.now();
        
        Ticket t = new Ticket();
        t.setTicket_id(ticketId);
        t.setPassenger_id(req.getPassenger_id());
        t.setTrip_id(req.getTrip_id());
        t.setSeat_number(req.getSeat_number() == null ? "" : req.getSeat_number());
        t.setBooking_status("confirmed");
        t.setCreated_at(now);
        t.setPurchase_date(now);
        t.setTotal_price(tripPrice);
        t.setCurrency(currency);
        t.setPayment_method("");
        t.setBooking_reference("");

    ticketRepository.save(t);

        TicketDto dto = new TicketDto();
        dto.setTicket_id(ticketId);
        dto.setPassenger_id(req.getPassenger_id());
        dto.setTrip_id(req.getTrip_id());
        dto.setSeat_number(req.getSeat_number());
        dto.setBooking_status("confirmed");
        dto.setTotal_price(tripPrice);
        dto.setCurrency(currency);
        return dto;
    }

    // List tickets using Spring Data Pageable for better performance
    public List<TicketDto> listTickets(int page, int limit) {
        int p = Math.max(0, page - 1);
        org.springframework.data.domain.PageRequest pr = org.springframework.data.domain.PageRequest.of(p, Math.max(1, limit));
        org.springframework.data.domain.Page<Ticket> pg = ticketRepository.findAll(pr);
        return pg.getContent().stream().map(this::toDto).collect(Collectors.toList());
    }

    public TicketDto getTicketById(String ticketId) {
        Optional<Ticket> t = ticketRepository.findById(ticketId);
        if (t.isEmpty()) throw new TicketNotFoundException(ticketId);
        return toDto(t.get());
    }

    public TicketDto updateTicket(String ticketId, TicketDto update) {
        Ticket existing = ticketRepository.findById(ticketId).orElseThrow(() -> new TicketNotFoundException(ticketId));
        if (update.getSeat_number() != null) existing.setSeat_number(update.getSeat_number());
        if (update.getBooking_status() != null) existing.setBooking_status(update.getBooking_status());
        if (update.getTotal_price() != null) existing.setTotal_price(update.getTotal_price());
        ticketRepository.save(existing);
        return toDto(existing);
    }

    public TicketDto cancelTicket(String ticketId) {
        Ticket existing = ticketRepository.findById(ticketId).orElseThrow(() -> new TicketNotFoundException(ticketId));
        existing.setBooking_status("cancelled");
        ticketRepository.save(existing);
        return toDto(existing);
    }

    public List<TicketDto> getTicketsByPassenger(String passengerId) {
        List<Ticket> list = ticketRepository.findByPassengerId(passengerId);
        return list.stream().map(this::toDto).collect(Collectors.toList());
    }
    
    public List<TicketDto> getTicketsByTrip(String tripId) {
        List<Ticket> list = ticketRepository.findByTripId(tripId);
        return list.stream().map(this::toDto).collect(Collectors.toList());
    }

    private TicketDto toDto(Ticket t){
        TicketDto dto = new TicketDto();
        dto.setTicket_id(t.getTicket_id());
        dto.setPassenger_id(t.getPassenger_id());
        dto.setTrip_id(t.getTrip_id());
        dto.setSeat_number(t.getSeat_number());
        dto.setBooking_status(t.getBooking_status());
        dto.setTotal_price(t.getTotal_price());
        dto.setCurrency(t.getCurrency());
        return dto;
    }
}
