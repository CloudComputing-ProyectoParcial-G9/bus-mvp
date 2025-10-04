import React, { useState, useEffect } from 'react';
import { Plus, X, Search, Ticket as TicketIcon, User, MapPin } from 'lucide-react';
import { apiService } from '../services/api';
import { Ticket, Passenger, Trip } from '../types';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';

export function TicketsSection() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [passengers, setPassengers] = useState<Passenger[]>([]);
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const [formData, setFormData] = useState<Ticket>({
    passenger_id: '',
    trip_id: '',
    seat_number: '',
    status: 'ACTIVE',
    payment_method: 'credit_card',
  });

  useEffect(() => {
    const loadData = async () => {
      await Promise.all([
        fetchTickets(),
        fetchPassengers(),
        fetchTrips()
      ]);
    };
    loadData();
  }, []);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getTickets();
      // El backend devuelve { data: [], limit: 20, page: 1 }
      setTickets(Array.isArray(response) ? response : response.data || []);
    } catch (err: unknown) {
      console.error('Error al cargar los tickets:', err);
      setError('Error al cargar los tickets');
    } finally {
      setLoading(false);
    }
  };

  const fetchPassengers = async () => {
    try {
      const response = await apiService.getPassengers(1, 100);
      setPassengers(response.passengers || []);
    } catch (err: unknown) {
      console.error('Error al cargar los pasajeros:', err);
    }
  };

  const fetchTrips = async () => {
    try {
      const response = await apiService.getTrips();
      setTrips(Array.isArray(response) ? response : response.data || []);
    } catch (err: unknown) {
      console.error('Error al cargar los viajes:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);

      // Preparar los datos para enviar al backend (formato snake_case correcto)
      const ticketData = {
        passenger_id: formData.passenger_id, // ✅ OBLIGATORIO
        trip_id: formData.trip_id,           // ✅ OBLIGATORIO
        seat_number: formData.seat_number || undefined,     // ⚪ OPCIONAL
        payment_method: formData.payment_method || undefined, // ⚪ OPCIONAL
        idempotency_key: `ticket_${Date.now()}_${Math.random().toString(36).substr(2, 9)}` // ⚪ OPCIONAL
      };

      // Remover campos undefined para enviar solo los necesarios
      const cleanData = Object.fromEntries(
        Object.entries(ticketData).filter(([, value]) => value !== undefined)
      );

      console.log('Enviando datos:', cleanData);
      await apiService.createTicket(cleanData as unknown as Omit<Ticket, 'id' | 'created_at'>);
      setShowForm(false);
      resetForm();
      fetchTickets();
    } catch (err: unknown) {
      console.error('Error completo al crear el ticket:', err);

      // Mostrar error más detallado
      let errorMessage = 'Error al crear el ticket';
      if (err instanceof Error) {
        errorMessage += ': ' + err.message;
      }
      // Intentar obtener detalles adicionales del error HTTP
      try {
        const errorObj = err as { response?: { data?: { message?: string } } };
        if (errorObj.response?.data?.message) {
          errorMessage += ' - ' + errorObj.response.data.message;
        }
      } catch {
        // Ignorar errores de parsing
      }

      setError(errorMessage);
    }
  };

  const handleCancelTicket = async (id: string) => {
    if (window.confirm('¿Estás seguro de que quieres cancelar este ticket?')) {
      try {
        setError(null);
        await apiService.cancelTicket(id);
        fetchTickets();
      } catch (err: unknown) {
        console.error('Error al cancelar el ticket:', err);
        setError('Error al cancelar el ticket');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      passenger_id: '',
      trip_id: '',
      seat_number: '',
      status: 'ACTIVE',
      payment_method: 'credit_card',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'bg-green-100 text-green-800';
      case 'CANCELLED': return 'bg-red-100 text-red-800';
      case 'USED': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredTickets = tickets.filter(ticket =>
    ticket.seat_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ticket.passenger_id.includes(searchTerm) ||
    ticket.trip_id.includes(searchTerm)
  );

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={fetchTickets} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-2xl font-bold text-gray-900">Gestión de Tickets</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Nuevo Ticket</span>
        </button>
      </div>

      <div className="relative">
        <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar tickets..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Nuevo Ticket</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* ID del Pasajero con dropdown y campo de texto */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ID del Pasajero</label>
              <div className="space-y-2">
                <select
                  value={formData.passenger_id}
                  onChange={(e) => setFormData({ ...formData, passenger_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Seleccionar pasajero...</option>
                  {passengers.map((passenger) => (
                    <option key={passenger.id} value={passenger.id || ''}>
                      {passenger.full_name} - {passenger.document_number}
                    </option>
                  ))}
                </select>
                <input
                  type="text"
                  required
                  value={formData.passenger_id}
                  onChange={(e) => setFormData({ ...formData, passenger_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="O escribe el ID del pasajero: passenger-123"
                />
              </div>
            </div>

            {/* ID del Viaje con dropdown y campo de texto */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ID del Viaje</label>
              <div className="space-y-2">
                <select
                  value={formData.trip_id}
                  onChange={(e) => setFormData({ ...formData, trip_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Seleccionar viaje...</option>
                  {trips.map((trip) => (
                    <option key={trip.id || trip.tripId} value={trip.id || trip.tripId}>
                      {trip.origin} → {trip.destination} ({new Date(trip.departureDateTime).toLocaleDateString()}) - S/{trip.finalPrice || trip.price}
                    </option>
                  ))}
                </select>
                <input
                  type="text"
                  required
                  value={formData.trip_id}
                  onChange={(e) => setFormData({ ...formData, trip_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="O escribe el ID del viaje: trip-456"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Número de Asiento</label>
              <input
                type="text"
                required
                value={formData.seat_number}
                onChange={(e) => setFormData({ ...formData, seat_number: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ej: 12A"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Método de Pago</label>
              <select
                value={formData.payment_method || 'credit_card'}
                onChange={(e) => setFormData({ ...formData, payment_method: e.target.value as 'credit_card' | 'debit_card' | 'paypal' | 'bank_transfer' | 'cash' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="credit_card">Tarjeta de Crédito</option>
                <option value="debit_card">Tarjeta de Débito</option>
                <option value="paypal">PayPal</option>
                <option value="bank_transfer">Transferencia Bancaria</option>
                <option value="cash">Efectivo</option>
              </select>
            </div>
            <div className="md:col-span-2 flex space-x-3">
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Crear Ticket
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  resetForm();
                }}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredTickets.map((ticket) => (
          <div key={ticket.id} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="bg-orange-100 p-2 rounded-full">
                  <TicketIcon className="w-5 h-5 text-orange-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Asiento {ticket.seat_number}</h3>
                  <p className="text-sm text-gray-500">ID: {ticket.id}</p>
                </div>
              </div>
              <div className="flex flex-col items-end space-y-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.status || 'ACTIVE')}`}>
                  {ticket.status}
                </span>
                {ticket.status === 'ACTIVE' && (
                  <button
                    onClick={() => handleCancelTicket(ticket.id!)}
                    className="p-1 hover:bg-red-100 rounded-full transition-colors"
                    title="Cancelar ticket"
                  >
                    <X className="w-4 h-4 text-red-500" />
                  </button>
                )}
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex items-center space-x-2">
                <User className="w-4 h-4 text-gray-400" />
                <span>Pasajero: {ticket.passenger_id}</span>
              </div>
              <div className="flex items-center space-x-2">
                <MapPin className="w-4 h-4 text-gray-400" />
                <span>Viaje: {ticket.trip_id}</span>
              </div>
              {ticket.created_at && (
                <p className="text-xs text-gray-500">
                  Creado: {new Date(ticket.created_at).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredTickets.length === 0 && (
        <div className="text-center py-8">
          <TicketIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No hay tickets registrados</p>
          <p className="text-sm text-gray-400 mt-2">
            Haz clic en "Nuevo Ticket" para crear el primer ticket
          </p>
        </div>
      )}
    </div>
  );
}