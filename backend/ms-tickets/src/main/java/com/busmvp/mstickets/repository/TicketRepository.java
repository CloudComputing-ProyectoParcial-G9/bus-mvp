package com.busmvp.mstickets.repository;

import com.busmvp.mstickets.model.Ticket;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import java.util.List;

public interface TicketRepository extends MongoRepository<Ticket, String> {
    @Query("{ 'passenger_id' : ?0 }")
    List<Ticket> findByPassengerId(String passengerId);
    
    @Query("{ 'trip_id' : ?0 }")
    List<Ticket> findByTripId(String tripId);

    Page<Ticket> findAll(Pageable pageable);
}
