export interface Passenger {
  id?: string;
  full_name: string;
  email: string;
  phone: string;
  document_type: 'DNI' | 'PASSPORT' | 'CE';
  document_number: string;
  date_of_birth: string;
  status?: 'active' | 'inactive';
  created_at?: string;
  updated_at?: string;
}

export interface Trip {
  id?: string;
  tripId: string; // Requerido*
  routeId: string; // Requerido*
  origin: string; // Para compatibilidad con frontend
  destination: string; // Para compatibilidad con frontend
  departure_date?: string; // Para compatibilidad con el formulario
  departure_time?: string; // Para compatibilidad con el formulario
  arrival_time?: string; // Para compatibilidad con el formulario
  departureDateTime: string; // Requerido*
  arrivalDateTime: string; // Requerido*
  price?: number; // Para compatibilidad
  finalPrice: number; // Requerido*
  available_seats?: number; // Para compatibilidad
  total_seats?: number; // Para compatibilidad
  availableSeats: number; // Requerido*
  busCapacity: number; // Requerido*
  bus_type?: string; // Para compatibilidad
  status: 'ACTIVE' | 'CANCELLED' | 'COMPLETED' | 'scheduled' | 'in-transit' | 'completed' | 'cancelled'; // Requerido*
  driverName?: string; // Opcional
  busPlate?: string; // Opcional
  createdAt?: string; // Opcional (generado por backend)
  updatedAt?: string; // Opcional (generado por backend)
}

export interface Ticket {
  // IDs y referencias principales
  id?: string;
  ticket_id?: string; // ID específico del ticket desde el backend
  passenger_id: string;
  trip_id: string;

  // Información del asiento y precio
  seat_number?: string; // Opcional según el backend
  price?: number; // Campo legacy, usar total_price para nuevos tickets
  total_price?: number; // Precio total del ticket
  currency?: string; // Moneda del precio

  // Estado y método de pago
  status?: 'ACTIVE' | 'CANCELLED' | 'USED'; // Estados legacy
  booking_status?: 'confirmed' | 'cancelled' | 'pending' | 'refunded'; // Estados del backend
  payment_method?: 'credit_card' | 'debit_card' | 'paypal' | 'bank_transfer' | 'cash';

  // Metadatos
  idempotency_key?: string; // Para evitar duplicados
  created_at?: string;
  updated_at?: string;

  // Relaciones expandidas (opcional)
  passenger?: Passenger;
  trip?: Trip;
}

export interface Analytics {
  total_passengers: number;
  total_trips: number;
  total_tickets: number;
  revenue: number;
  popular_routes: Array<{
    route: string;
    count: number;
  }>;
}