import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Search, MapPin, Clock, DollarSign, Users } from 'lucide-react';
import { apiService } from '../services/api';
import { Trip } from '../types';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';
import { useDataRefresh } from '../contexts/DataRefreshContext';

export function TripsSection() {
  const { triggerRefresh } = useDataRefresh();

  // Rutas disponibles basadas en el seeder del backend
  const availableRoutes = [
    { id: "LIM_CUZ_001", origin: "Lima", destination: "Cusco", name: "Lima → Cusco Express", price: 120.00 },
    { id: "LIM_ARE_002", origin: "Lima", destination: "Arequipa", name: "Lima → Arequipa Ejecutivo", price: 95.50 },
    { id: "LIM_TRU_003", origin: "Lima", destination: "Trujillo", name: "Lima → Trujillo Directo", price: 75.00 },
    { id: "ARE_CUZ_004", origin: "Arequipa", destination: "Cusco", name: "Arequipa → Cusco Turístico", price: 60.00 },
    { id: "CUZ_PUN_005", origin: "Cusco", destination: "Puno", name: "Cusco → Puno Altiplano", price: 65.00 },
    { id: "LIM_ICA_006", origin: "Lima", destination: "Ica", name: "Lima → Ica Express", price: 45.00 }
  ];

  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTrip, setEditingTrip] = useState<Trip | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<string>('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchParams, setSearchParams] = useState({
    origin: '',
    destination: '',
    departureDate: '',
  });

  const [formData, setFormData] = useState<Trip>({
    tripId: '', // Se genera automáticamente
    routeId: '', // Se selecciona del dropdown
    origin: '',
    destination: '',
    departureDateTime: '', // Se genera automáticamente
    arrivalDateTime: '', // Se genera automáticamente
    departure_date: '',
    departure_time: '',
    arrival_time: '',
    price: 0,
    finalPrice: 0,
    available_seats: 0,
    availableSeats: 0,
    total_seats: 0,
    busCapacity: 0,
    bus_type: '',
    status: 'scheduled', // Estado por defecto
    driverName: '',
    busPlate: '',
  });

  useEffect(() => {
    fetchTrips();
  }, []);

  const fetchTrips = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getTrips();

      let tripsData = [];
      if (response && response.data) {
        tripsData = Array.isArray(response.data) ? response.data : [response.data];
      } else if (Array.isArray(response)) {
        tripsData = response;
      } else {
        tripsData = [];
      }

      setTrips(tripsData);
    } catch (err) {
      console.error('Error loading trips:', err);
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(`Error al cargar los viajes: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    // Si no hay parámetros de búsqueda, mostrar todos los viajes
    if (!searchParams.origin && !searchParams.destination && !searchParams.departureDate) {
      setIsSearching(false);
      fetchTrips();
      return;
    }

    // Validar que al menos origen y destino estén completos
    if (!searchParams.origin || !searchParams.destination) {
      setError('Por favor ingresa al menos origen y destino para buscar');
      return;
    }

    // Validar que departureDate esté completo
    if (!searchParams.departureDate) {
      setError('⚠️ Por favor selecciona una fecha de salida para buscar');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setIsSearching(true);

      const response = await apiService.searchTrips(
        searchParams.origin,
        searchParams.destination,
        searchParams.departureDate
      );

      // Verificar si el backend devolvió una advertencia
      if (response && response.success === false && response.warning) {
        setError(`⚠️ ${response.warning}\n${response.hint || ''}`);
        setTrips([]);
        setIsSearching(false);
        setLoading(false);
        return;
      }

      let tripsData = [];
      if (response && response.data) {
        tripsData = Array.isArray(response.data) ? response.data : [response.data];
      } else if (Array.isArray(response)) {
        tripsData = response;
      } else {
        tripsData = [];
      }

      setTrips(tripsData);

      // Mostrar mensaje si no se encontraron viajes
      if (tripsData.length === 0) {
        setError('ℹ️ No se encontraron viajes para los criterios de búsqueda especificados');
      }
    } catch (err) {
      console.error('Error searching trips:', err);
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(`❌ Error al buscar viajes: ${errorMessage}`);
      setTrips([]);
      setIsSearching(false);
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setSearchParams({
      origin: '',
      destination: '',
      departureDate: '',
    });
    setIsSearching(false);
    fetchTrips();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);

      if (editingTrip) {
        // Para UPDATE, usar el tripId del backend
        const tripId = editingTrip.tripId || editingTrip.id;
        if (!tripId) {
          throw new Error('No se encontró ID del viaje para actualizar');
        }

        // Convertir datos del frontend al formato del backend
        // Construir fechas correctamente sin forzar UTC
        const departureDate = new Date(`${formData.departure_date}T${formData.departure_time}:00`);
        const arrivalDate = new Date(`${formData.departure_date}T${formData.arrival_time}:00`);

        const updateData = {
          origin: formData.origin,
          destination: formData.destination,
          departureDateTime: departureDate.toISOString(),
          arrivalDateTime: arrivalDate.toISOString(),
          busCapacity: formData.total_seats,
          availableSeats: formData.available_seats,
          finalPrice: formData.price,
          status: (formData.status === 'ACTIVE' ? 'scheduled' : formData.status.toLowerCase()) as Trip['status']
        };

        await apiService.updateTrip(tripId, updateData);
      } else {
        // Para CREATE - Formato correcto según validaciones del backend

        // Usar ruta seleccionada o primera disponible
        const routeToUse = availableRoutes.find(r =>
          r.origin.toLowerCase() === (formData.origin || '').toLowerCase() &&
          r.destination.toLowerCase() === (formData.destination || '').toLowerCase()
        ) || availableRoutes[0]; // Default a Lima-Cusco

        // 1. Generar tripId con formato correcto: TRP_YYYYMMDD_ORG_DST_HH
        const now = new Date();
        const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '');
        const hour = String(now.getHours()).padStart(2, '0');
        const origin3 = routeToUse.origin.slice(0, 3).toUpperCase();
        const dest3 = routeToUse.destination.slice(0, 3).toUpperCase();
        const tripId = `TRP_${dateStr}_${origin3}_${dest3}_${hour}`;

        // 2. Usar routeId de la ruta seleccionada
        const routeId = routeToUse.id;

        // 3. Construir fechas en hora local y convertir a ISO
        // No usar 'Z' al final para evitar problemas de zona horaria
        const departureDate = new Date(`${formData.departure_date}T${formData.departure_time}:00`);

        // Calcular arrival automáticamente para evitar errores (mínimo 2 horas después)
        let arrivalDate = new Date(departureDate.getTime() + (2 * 60 * 60 * 1000)); // +2 horas
        if (formData.arrival_time) {
          // Si el usuario especificó hora de llegada, usarla pero validar
          const userArrival = new Date(`${formData.departure_date}T${formData.arrival_time}:00`);
          if (userArrival > departureDate) {
            const timeDiff = userArrival.getTime() - departureDate.getTime();
            const minutesDiff = timeDiff / (1000 * 60);
            if (minutesDiff >= 30) { // Mínimo 30 minutos
              arrivalDate = userArrival;
            }
          }
        }

        const departureTime = departureDate.toISOString();
        const arrivalTime = arrivalDate.toISOString();

        const tripData = {
          tripId: tripId,
          routeId: routeId,
          origin: routeToUse.origin,
          destination: routeToUse.destination,
          departureDateTime: departureTime,
          arrivalDateTime: arrivalTime,
          busCapacity: parseInt((formData.total_seats || 40).toString()),
          availableSeats: parseInt((formData.available_seats || formData.total_seats || 40).toString()),
          finalPrice: parseFloat((formData.price || routeToUse.price).toString()),
          status: 'scheduled' as Trip['status'],
          driverName: formData.bus_type || 'Driver Asignado',
          busPlate: `${origin3}-${Math.floor(Math.random() * 999).toString().padStart(3, '0')}`
        };

        // Validaciones antes de enviar
        const errors = [];

        // Validar formato tripId
        const tripIdPattern = /^TRP_\d{8}_[A-Z]{3}_[A-Z]{3}_\d{2}$/;
        if (!tripIdPattern.test(tripData.tripId)) {
          errors.push("TripId debe seguir formato: TRP_YYYYMMDD_ORG_DST_HH");
        }

        // Validar fechas
        const departure = new Date(tripData.departureDateTime);
        const arrival = new Date(tripData.arrivalDateTime);

        if (arrival <= departure) {
          errors.push("Hora de llegada debe ser después de la salida");
        }

        const durationMs = arrival.getTime() - departure.getTime();
        const durationMinutes = durationMs / (1000 * 60);
        if (durationMinutes < 30) {
          errors.push("Duración mínima del viaje: 30 minutos");
        }

        // Validar asientos
        if (tripData.availableSeats > tripData.busCapacity) {
          errors.push("Asientos disponibles no pueden exceder capacidad");
        }

        if (errors.length > 0) {
          throw new Error('Errores de validación: ' + errors.join(', '));
        }

        await apiService.createTrip(tripData);
      }

      setShowForm(false);
      setEditingTrip(null);
      resetForm();
      await fetchTrips();
      triggerRefresh(); // Notificar a otros componentes que los datos cambiaron
    } catch (err) {
      console.error('Error saving trip:', err);
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(`Error al guardar el viaje: ${errorMessage}`);
    }
  };

  const handleDelete = async (trip: Trip) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este viaje?')) {
      try {
        setError(null);
        const tripId = trip.tripId || trip.id;
        if (!tripId) {
          throw new Error('No se encontró ID del viaje');
        }

        await apiService.deleteTrip(tripId);
        await fetchTrips();
        triggerRefresh(); // Notificar a otros componentes que los datos cambiaron
      } catch (err) {
        console.error('Error deleting trip:', err);
        const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
        setError(`Error al eliminar el viaje: ${errorMessage}`);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      tripId: '',
      routeId: '',
      origin: '',
      destination: '',
      departureDateTime: '',
      arrivalDateTime: '',
      departure_date: '',
      departure_time: '',
      arrival_time: '',
      price: 0,
      finalPrice: 0,
      available_seats: 0,
      availableSeats: 0,
      total_seats: 0,
      busCapacity: 0,
      bus_type: '',
      status: 'scheduled',
      driverName: '',
      busPlate: '',
    });
    setSelectedRoute('');
  };

  const handleEdit = (trip: Trip) => {
    setEditingTrip(trip);

    // Mapear datos del backend al formato del formulario
    const mappedData = {
      tripId: trip.tripId || '',
      routeId: trip.routeId || '',
      origin: trip.origin,
      destination: trip.destination,
      departureDateTime: trip.departureDateTime || '',
      arrivalDateTime: trip.arrivalDateTime || '',
      departure_date: trip.departureDateTime ? trip.departureDateTime.split('T')[0] : '',
      departure_time: trip.departureDateTime ? trip.departureDateTime.split('T')[1]?.slice(0,5) : '',
      arrival_time: trip.arrivalDateTime ? trip.arrivalDateTime.split('T')[1]?.slice(0,5) : '',
      price: (() => {
        const price = trip.finalPrice || trip.price || 0;
        return typeof price === 'string' ? parseFloat(price) : Number(price);
      })(),
      finalPrice: (() => {
        const price = trip.finalPrice || trip.price || 0;
        return typeof price === 'string' ? parseFloat(price) : Number(price);
      })(),
      available_seats: trip.availableSeats || trip.available_seats || 0,
      availableSeats: trip.availableSeats || trip.available_seats || 0,
      total_seats: trip.busCapacity || trip.total_seats || 0,
      busCapacity: trip.busCapacity || trip.total_seats || 0,
      bus_type: trip.bus_type || 'Estándar',
      driverName: trip.driverName || '',
      busPlate: trip.busPlate || '',
      status: trip.status === 'scheduled' ? 'ACTIVE' : (trip.status?.toUpperCase() as Trip['status']) || 'ACTIVE'
    };

    setFormData(mappedData);
    setSelectedRoute(trip.routeId || '');
    setShowForm(true);
  };

  const handleUpdateSeats = async (trip: Trip, newAvailableSeats: number) => {
    try {
      setError(null);
      const tripId = trip.tripId || trip.id;
      if (!tripId) {
        throw new Error('No se encontró ID del viaje');
      }

      await apiService.updateTripSeats(tripId, { availableSeats: newAvailableSeats });
      await fetchTrips();
      triggerRefresh(); // Notificar a otros componentes que los datos cambiaron
    } catch (err) {
      console.error('Error updating seats:', err);
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(`Error al actualizar los asientos: ${errorMessage}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
      case 'scheduled': return 'bg-green-100 text-green-800';
      case 'CANCELLED':
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'COMPLETED':
      case 'completed': return 'bg-blue-100 text-blue-800';
      case 'in-transit': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };



  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner />
          <p className="mt-4 text-gray-600">Cargando viajes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Gestión de Viajes</h2>
          <ErrorMessage message={error} onRetry={fetchTrips} />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <h2 className="text-2xl font-bold text-gray-900">Gestión de Viajes</h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Nuevo Viaje</span>
          </button>
        </div>

      {/* Search Form */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Buscar Viajes</h3>
          {isSearching && (
            <button
              onClick={handleClearSearch}
              className="text-sm text-blue-600 hover:text-blue-800 underline"
            >
              Mostrar todos los viajes
            </button>
          )}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Origen *</label>
            <input
              type="text"
              value={searchParams.origin}
              onChange={(e) => setSearchParams({ ...searchParams, origin: e.target.value })}
              placeholder="Lima, Cusco, Arequipa..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Destino *</label>
            <input
              type="text"
              value={searchParams.destination}
              onChange={(e) => setSearchParams({ ...searchParams, destination: e.target.value })}
              placeholder="Lima, Cusco, Arequipa..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fecha (opcional)</label>
            <input
              type="date"
              value={searchParams.departureDate}
              onChange={(e) => setSearchParams({ ...searchParams, departureDate: e.target.value })}
              min={new Date().toISOString().split('T')[0]}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-end space-x-2">
            <button
              onClick={handleSearch}
              disabled={loading}
              className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:bg-green-400 transition-colors flex items-center justify-center space-x-2"
            >
              <Search className="w-4 h-4" />
              <span>{loading ? 'Buscando...' : 'Buscar'}</span>
            </button>
          </div>
        </div>
        {isSearching && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-700">
              📍 Mostrando resultados para: <strong>{searchParams.origin}</strong> → <strong>{searchParams.destination}</strong>
              {searchParams.departureDate && (
                <span> el <strong>{new Date(searchParams.departureDate).toLocaleDateString('es-ES')}</strong></span>
              )}
            </p>
          </div>
        )}
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">
            {editingTrip ? 'Editar Viaje' : 'Nuevo Viaje'}
          </h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Ruta</label>
              <select
                required
                value={selectedRoute}
                onChange={(e) => {
                  setSelectedRoute(e.target.value);
                  const route = availableRoutes.find(r => r.id === e.target.value);
                  if (route) {
                    setFormData({
                      ...formData,
                      origin: route.origin,
                      destination: route.destination,
                      price: route.price
                    });
                  }
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Selecciona una ruta</option>
                {availableRoutes.map((route) => (
                  <option key={route.id} value={route.id}>
                    {route.name} - S/ {route.price.toFixed(2)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de Salida</label>
              <input
                type="date"
                required
                value={formData.departure_date}
                onChange={(e) => setFormData({ ...formData, departure_date: e.target.value })}
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hora de Salida</label>
              <input
                type="time"
                required
                value={formData.departure_time}
                onChange={(e) => setFormData({ ...formData, departure_time: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hora de Llegada</label>
              <input
                type="time"
                required
                value={formData.arrival_time}
                onChange={(e) => setFormData({ ...formData, arrival_time: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Precio</label>
              <input
                type="number"
                required
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Asientos Totales</label>
              <input
                type="number"
                required
                value={formData.total_seats}
                onChange={(e) => setFormData({ ...formData, total_seats: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Asientos Disponibles</label>
              <input
                type="number"
                required
                value={formData.available_seats}
                onChange={(e) => setFormData({ ...formData, available_seats: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Bus</label>
              <input
                type="text"
                required
                value={formData.bus_type}
                onChange={(e) => setFormData({ ...formData, bus_type: e.target.value })}
                placeholder="Ej: Económico, VIP, Cama"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="lg:col-span-3 flex space-x-3">
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                {editingTrip ? 'Actualizar' : 'Crear'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  setEditingTrip(null);
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {trips.map((trip, index) => (
          <div key={trip.tripId || trip.id || index} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="bg-blue-100 p-2 rounded-full">
                  <MapPin className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{trip.origin} → {trip.destination}</h3>
                  <p className="text-sm text-gray-500">ID: {trip.tripId || trip.id || 'N/A'}</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(trip.status)}`}>
                  {trip.status}
                </span>
                <button
                  onClick={() => handleEdit(trip)}
                  className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                  title="Editar viaje"
                >
                  <Edit className="w-4 h-4 text-gray-500" />
                </button>
                <button
                  onClick={() => handleDelete(trip)}
                  className="p-1 hover:bg-red-100 rounded-full transition-colors"
                  title="Eliminar viaje"
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-gray-400" />
                <span>
                  {trip.departureDateTime ? new Date(trip.departureDateTime).toLocaleTimeString('es-ES', {hour: '2-digit', minute: '2-digit'}) : 'N/A'} -
                  {trip.arrivalDateTime ? new Date(trip.arrivalDateTime).toLocaleTimeString('es-ES', {hour: '2-digit', minute: '2-digit'}) : 'N/A'}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <DollarSign className="w-4 h-4 text-gray-400" />
                <span>S/ {(() => {
                  const price = trip.finalPrice || trip.price || 0;
                  return typeof price === 'string' ? parseFloat(price).toFixed(2) : Number(price).toFixed(2);
                })()}</span>
              </div>
            </div>

            <div className="mt-4 bg-gray-50 p-3 rounded-lg">
              <div className="flex justify-between items-center text-sm">
                <span>Asientos disponibles: <span className="font-medium">{trip.availableSeats || trip.available_seats || 0}</span></span>
                <span>Total: <span className="font-medium">{trip.busCapacity || trip.total_seats || 0}</span></span>
              </div>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full transition-all duration-300"
                  style={{
                    width: `${(() => {
                      const total = trip.busCapacity || trip.total_seats || 0;
                      const available = trip.availableSeats || trip.available_seats || 0;
                      return total > 0 ? ((total - available) / total) * 100 : 0;
                    })()}%`
                  }}
                ></div>
              </div>

              {/* Control para actualizar asientos */}
              <div className="mt-3 flex items-center space-x-2">
                <Users className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600">Actualizar asientos:</span>
                <input
                  type="number"
                  min="0"
                  max={trip.busCapacity || trip.total_seats || 0}
                  defaultValue={trip.availableSeats || trip.available_seats || 0}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onBlur={(e) => {
                    const newValue = parseInt(e.target.value);
                    const currentValue = trip.availableSeats || trip.available_seats || 0;
                    if (newValue !== currentValue && !isNaN(newValue)) {
                      handleUpdateSeats(trip, newValue);
                    }
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      const target = e.target as HTMLInputElement;
                      const newValue = parseInt(target.value);
                      const currentValue = trip.availableSeats || trip.available_seats || 0;
                      if (newValue !== currentValue && !isNaN(newValue)) {
                        handleUpdateSeats(trip, newValue);
                      }
                    }
                  }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {trips.length === 0 && (
        <div className="text-center py-8">
          <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No hay viajes registrados</p>
          <button
            onClick={fetchTrips}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            🔄 Recargar viajes
          </button>
        </div>
      )}
    </div>
  );
}