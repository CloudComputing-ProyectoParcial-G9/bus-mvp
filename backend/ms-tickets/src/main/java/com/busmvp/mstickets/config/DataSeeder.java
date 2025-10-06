package com.busmvp.mstickets.config;

import com.busmvp.mstickets.model.Ticket;
import com.busmvp.mstickets.repository.TicketRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

@Component
public class DataSeeder implements CommandLineRunner {

    private final TicketRepository ticketRepository;
    private final Random random = new Random();

    public DataSeeder(TicketRepository ticketRepository) {
        this.ticketRepository = ticketRepository;
    }

    @Override
    public void run(String... args) throws Exception {
        // Check if database is already populated
        long count = ticketRepository.count();
        
        if (count > 0) {
            System.out.println("✓ Database already contains " + count + " tickets. Skipping seed.");
            return;
        }

        System.out.println("📦 Seeding database with sample tickets...");
        
        List<Ticket> tickets = generateSampleTickets();
        ticketRepository.saveAll(tickets);
        
        System.out.println("✓ Successfully seeded database with " + tickets.size() + " tickets");
        System.out.println("\nSample tickets:");
        for (int i = 0; i < Math.min(3, tickets.size()); i++) {
            Ticket t = tickets.get(i);
            System.out.println("  - " + t.getTicket_id() + ": Passenger " + t.getPassenger_id() + 
                             " | Trip " + t.getTrip_id() + " | Seat " + t.getSeat_number() + 
                             " | €" + String.format("%.2f", t.getTotal_price()));
        }
        System.out.println("  ... and " + (tickets.size() - 3) + " more");
    }

    private List<Ticket> generateSampleTickets() {
        List<Ticket> tickets = new ArrayList<>();
        
        String[] passengerIds = {"PASS001", "PASS002", "PASS003", "PASS004", "PASS005", 
                                "PASS006", "PASS007", "PASS008", "PASS009", "PASS010"};
        String[] tripIds = {"TRIP001", "TRIP002", "TRIP003", "TRIP004", "TRIP005"};
        String[] statuses = {"confirmed", "confirmed", "confirmed", "confirmed", "pending", "cancelled"};
        String[] seatPrefixes = {"A", "B", "C", "D"};
        
        for (int i = 1; i <= 10; i++) {
            Ticket ticket = new Ticket();
            
            // Sequential ticket IDs
            ticket.setTicket_id(String.format("TICKET%03d", i));
            
            // Use existing passenger IDs
            ticket.setPassenger_id(passengerIds[i - 1]);
            
            // Random trip ID
            ticket.setTrip_id(tripIds[random.nextInt(tripIds.length)]);
            
            // Generate seat number (1-30 + A/B/C/D)
            int seatNum = random.nextInt(30) + 1;
            String seatPrefix = seatPrefixes[random.nextInt(seatPrefixes.length)];
            ticket.setSeat_number(seatNum + seatPrefix);
            
            // Random price between 20 and 120 euros
            double price = 20 + (100 * random.nextDouble());
            ticket.setTotal_price(Math.round(price * 100.0) / 100.0);
            
            ticket.setCurrency("EUR");
            
            // Random status (mostly confirmed)
            ticket.setBooking_status(statuses[random.nextInt(statuses.length)]);
            
            // Random creation date within last 90 days
            int daysAgo = random.nextInt(90);
            ticket.setCreated_at(Instant.now().minus(daysAgo, ChronoUnit.DAYS));
            
            tickets.add(ticket);
        }
        
        return tickets;
    }
}
