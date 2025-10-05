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

// ============================================================================
// Analytics Types - MS-Analytics Integration
// ============================================================================

export interface SummaryMetrics {
  total_passengers: number;
  active_trips: number;
  tickets_sold: number;
  total_revenue: number;
  average_occupancy: number;
  cancellation_rate: number;
}

export interface SummaryTrends {
  revenue_growth: number;
  passenger_growth: number;
}

export interface DashboardSummaryResponse {
  timestamp: string;
  summary: SummaryMetrics;
  trends?: SummaryTrends;
}

export interface TopCustomer {
  passenger_id: string;
  full_name: string;
  total_spent: number;
  tickets_purchased: number;
  segment: string;
}

export interface PassengerAnalyticsResponse {
  total_passengers: number;
  active_passengers: number;
  passenger_segments: Record<string, number>;
  top_customers: TopCustomer[];
}

export interface RouteRevenue {
  route_id: string;
  total_revenue: number;
  trips_count: number;
  avg_revenue_per_trip: number;
}

export interface DailyRevenue {
  date: string;
  revenue: number;
}

export interface RevenueTrend {
  daily: DailyRevenue[];
}

export interface RevenueAnalyticsResponse {
  total_revenue: number;
  confirmed_revenue: number;
  cancelled_revenue: number;
  by_route: RouteRevenue[];
  trend?: RevenueTrend;
}

export interface OccupancyByRoute {
  route_id: string;
  avg_occupancy: number;
  trips_count: number;
}

export interface OccupancyAnalyticsResponse {
  average_occupancy: number;
  total_capacity: number;
  total_seats_sold: number;
  by_level: Record<string, number>;
  by_route: OccupancyByRoute[];
}

export interface TripAnalyticsResponse {
  total_trips: number;
  active_trips: number;
  completed_trips: number;
  cancelled_trips: number;
  occupancy_breakdown: Record<string, number>;
}

export interface AnalyticsHealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  athena_connection: boolean;
}