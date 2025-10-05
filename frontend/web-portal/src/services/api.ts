import { 
  Passenger, 
  Trip, 
  Ticket,
  DashboardSummaryResponse,
  PassengerAnalyticsResponse,
  RevenueAnalyticsResponse,
  OccupancyAnalyticsResponse,
  TripAnalyticsResponse,
  AnalyticsHealthResponse,
} from '../types';

const API_URLS = {
  passengers: import.meta.env.VITE_PASSENGERS_API,
  trips: import.meta.env.VITE_TRIPS_API,
  tickets: import.meta.env.VITE_TICKETS_API,
  history: import.meta.env.VITE_HISTORY_API,
  analytics: import.meta.env.VITE_ANALYTICS_API,
};

class ApiService {
  private async fetchWithErrorHandling(url: string, options?: RequestInit) {
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      return await response.text();
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    }
  }

  // Passengers API
  async getPassengers(page = 1, limit = 20) {
    const response = await this.fetchWithErrorHandling(`${API_URLS.passengers}/passengers?page=${page}&limit=${limit}`);
    // El backend devuelve una lista directa, la transformamos para que sea consistente
    if (Array.isArray(response)) {
      return {
        passengers: response.map(passenger => ({
          ...passenger,
          id: passenger.passenger_id || passenger.id
        })),
        total: response.length
      };
    }
    return response;
  }

  async createPassenger(passenger: Omit<Passenger, 'id' | 'created_at' | 'updated_at'>) {
    return this.fetchWithErrorHandling(`${API_URLS.passengers}/passengers`, {
      method: 'POST',
      body: JSON.stringify(passenger),
    });
  }

  async updatePassenger(id: string, passenger: Partial<Omit<Passenger, 'id' | 'created_at' | 'updated_at'>>) {
    return this.fetchWithErrorHandling(`${API_URLS.passengers}/passengers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(passenger),
    });
  }

  async getPassenger(id: string) {
    const response = await this.fetchWithErrorHandling(`${API_URLS.passengers}/passengers/${id}`);
    // Asegurar que tenga el campo id correcto
    return {
      ...response,
      id: response.passenger_id || response.id
    };
  }

  // Trips API
  async getTrips() {
    return this.fetchWithErrorHandling(`${API_URLS.trips}/api/v1/trips`);
  }

  async getRoutes() {
    return this.fetchWithErrorHandling(`${API_URLS.trips}/api/v1/routes`);
  }

  async searchTrips(origin: string, destination: string, departureDate: string) {
    const params = new URLSearchParams({
      origin,
      destination,
      departureDate,
    });
    return this.fetchWithErrorHandling(`${API_URLS.trips}/api/v1/trips/search?${params}`);
  }

  async createTrip(trip: Omit<Trip, 'id'>) {
    return this.fetchWithErrorHandling(`${API_URLS.trips}/api/v1/trips`, {
      method: 'POST',
      body: JSON.stringify(trip),
    });
  }

  async updateTrip(id: string, trip: Partial<Omit<Trip, 'id'>>) {
    return this.fetchWithErrorHandling(`${API_URLS.trips}/api/v1/trips/${id}`, {
      method: 'PUT',
      body: JSON.stringify(trip),
    });
  }

  async deleteTrip(tripId: string) {
    return this.fetchWithErrorHandling(`${API_URLS.trips}/api/v1/trips/${tripId}`, {
      method: 'DELETE',
    });
  }

  async updateTripSeats(tripId: string, seatsData: { availableSeats: number }) {
    return this.fetchWithErrorHandling(`${API_URLS.trips}/api/v1/trips/${tripId}/seats`, {
      method: 'PATCH',
      body: JSON.stringify(seatsData),
    });
  }

  // Tickets API
  async getTickets() {
    return this.fetchWithErrorHandling(`${API_URLS.tickets}/tickets`);
  }

  async getTicket(ticketId: string) {
    return this.fetchWithErrorHandling(`${API_URLS.tickets}/tickets/${ticketId}`);
  }

  async createTicket(ticket: Omit<Ticket, 'id' | 'created_at'>) {
    return this.fetchWithErrorHandling(`${API_URLS.tickets}/tickets`, {
      method: 'POST',
      body: JSON.stringify(ticket),
    });
  }

  async updateTicket(id: string, ticket: Partial<Omit<Ticket, 'id' | 'created_at'>>) {
    return this.fetchWithErrorHandling(`${API_URLS.tickets}/tickets/${id}`, {
      method: 'PUT',
      body: JSON.stringify(ticket),
    });
  }

  async cancelTicket(id: string) {
    return this.fetchWithErrorHandling(`${API_URLS.tickets}/tickets/${id}/cancel`, {
      method: 'POST',
    });
  }

  async getPassengerTicketHistory(passengerId: string) {
    return this.fetchWithErrorHandling(`${API_URLS.tickets}/tickets/passenger/${passengerId}/history`);
  }

  // Método específico para health check de tickets
  async checkTicketsHealth() {
    return this.fetchWithErrorHandling(`${API_URLS.tickets}/tickets/health`);
  }

  // Health checks generales
  async checkHealth(service: keyof typeof API_URLS) {
    const url = service === 'trips'
      ? `${API_URLS[service]}/api/v1/health`
      : service === 'tickets'
      ? `${API_URLS[service]}/tickets/health`
      : service === 'analytics'
      ? `${API_URLS[service]}/api/v1/health`
      : `${API_URLS[service]}/health`;

    return this.fetchWithErrorHandling(url);
  }

  // ============================================================================
  // Analytics API
  // ============================================================================

  /**
   * Obtiene el resumen ejecutivo del dashboard
   * Incluye métricas principales: pasajeros, viajes, tickets, ingresos, ocupación
   */
  async getDashboardSummary(): Promise<DashboardSummaryResponse> {
    return this.fetchWithErrorHandling(
      `${API_URLS.analytics}/api/v1/analytics/summary`
    );
  }

  /**
   * Obtiene analítica de pasajeros con segmentación
   * Segmentos: VIP, Frequent, Regular, Occasional
   */
  async getPassengerAnalytics(): Promise<PassengerAnalyticsResponse> {
    return this.fetchWithErrorHandling(
      `${API_URLS.analytics}/api/v1/analytics/passengers`
    );
  }

  /**
   * Obtiene analítica de ingresos por ruta y estado
   */
  async getRevenueAnalytics(): Promise<RevenueAnalyticsResponse> {
    return this.fetchWithErrorHandling(
      `${API_URLS.analytics}/api/v1/analytics/revenue`
    );
  }

  /**
   * Obtiene analítica de ocupación de buses
   * Niveles: Full (>90%), High (70-90%), Medium (50-70%), Low (30-50%), Very Low (<30%)
   */
  async getOccupancyAnalytics(): Promise<OccupancyAnalyticsResponse> {
    return this.fetchWithErrorHandling(
      `${API_URLS.analytics}/api/v1/analytics/occupancy`
    );
  }

  /**
   * Obtiene analítica de viajes por estado
   */
  async getTripAnalytics(): Promise<TripAnalyticsResponse> {
    return this.fetchWithErrorHandling(
      `${API_URLS.analytics}/api/v1/analytics/trips`
    );
  }

  /**
   * Health check específico para el servicio de analytics
   */
  async checkAnalyticsHealth(): Promise<AnalyticsHealthResponse> {
    return this.fetchWithErrorHandling(
      `${API_URLS.analytics}/api/v1/health`
    );
  }
}

export const apiService = new ApiService();