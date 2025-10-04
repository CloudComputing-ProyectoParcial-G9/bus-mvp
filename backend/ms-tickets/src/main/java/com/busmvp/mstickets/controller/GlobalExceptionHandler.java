package com.busmvp.mstickets.controller;

import com.busmvp.mstickets.service.NoSeatsException;
import com.busmvp.mstickets.service.TicketNotFoundException;
import com.busmvp.mstickets.service.PassengerNotFoundException;
import com.busmvp.mstickets.service.TripNotFoundException;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.dao.DataAccessResourceFailureException;
import com.mongodb.MongoException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

import java.util.HashMap;
import java.util.Map;

@ControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(NoSeatsException.class)
    protected ResponseEntity<Object> handleNoSeats(NoSeatsException ex) {
        ErrorResponse body = new ErrorResponse("no_seats", ex.getMessage());
        return ResponseEntity.status(HttpStatus.CONFLICT).body(body);
    }

    @ExceptionHandler({com.busmvp.mstickets.service.PassengerNotFoundException.class, com.busmvp.mstickets.service.TripNotFoundException.class})
    protected ResponseEntity<Object> handleNotFoundIntegration(Exception ex) {
        ErrorResponse body = new ErrorResponse("unprocessable_entity", ex.getMessage());
        return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY).body(body);
    }

    @ExceptionHandler(TicketNotFoundException.class)
    protected ResponseEntity<Object> handleTicketNotFound(TicketNotFoundException ex) {
        ErrorResponse body = new ErrorResponse("not_found", ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(body);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    protected ResponseEntity<Object> handleIllegalArg(IllegalArgumentException ex) {
        ErrorResponse body = new ErrorResponse("bad_request", ex.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(body);
    }

    @ExceptionHandler({HttpClientErrorException.class})
    protected ResponseEntity<Object> handleHttpClientError(HttpClientErrorException ex) {
        // Map 404 from downstream services to unprocessable_entity (integration) or to not_found when relevant
        if (ex.getStatusCode() == HttpStatus.NOT_FOUND) {
            ErrorResponse body = new ErrorResponse("unprocessable_entity", ex.getMessage());
            return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY).body(body);
        }
        ErrorResponse body = new ErrorResponse("client_error", ex.getMessage());
        return ResponseEntity.status(ex.getStatusCode()).body(body);
    }

    @ExceptionHandler({ResourceAccessException.class, org.springframework.web.client.RestClientException.class})
    protected ResponseEntity<Object> handleExternalServiceUnavailable(Exception ex) {
        logger.error("External service connectivity failure", ex);
        ErrorResponse body = new ErrorResponse("service_unavailable", "External service unavailable: " + ex.getMessage());
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(body);
    }

    @ExceptionHandler({DataAccessResourceFailureException.class, MongoException.class})
    protected ResponseEntity<Object> handleDatastoreDown(Exception ex) {
        logger.error("Datastore connectivity failure", ex);
        ErrorResponse body = new ErrorResponse("service_unavailable", "Datastore unavailable: " + ex.getMessage());
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(body);
    }

    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(MethodArgumentNotValidException ex,
                                                                  HttpHeaders headers,
                                                                  HttpStatusCode status,
                                                                  WebRequest request) {
        Map<String, String> errors = new HashMap<>();
        for (FieldError fe : ex.getBindingResult().getFieldErrors()) {
            errors.put(fe.getField(), fe.getDefaultMessage());
        }
        ErrorResponse body = new ErrorResponse("validation_error", "Validation failed");
        body.setDetails(errors);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(body);
    }

    @ExceptionHandler(Exception.class)
    protected ResponseEntity<Object> handleAll(Exception ex) {
        logger.error("Unhandled exception caught by GlobalExceptionHandler", ex);
        ErrorResponse body = new ErrorResponse("internal_error", ex.getMessage());
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(body);
    }
}
