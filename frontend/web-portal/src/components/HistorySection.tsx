import React, { useState, useEffect } from 'react';
import { Search, User, BarChart, MapPin, Calendar, DollarSign, Activity } from 'lucide-react';
import { apiService } from '../services/api';
import { PassengerHistory, DashboardSummary } from '../types';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';
import { useDataRefresh } from '../contexts/DataRefreshContext';

export function HistorySection() {
  const { refreshTrigger } = useDataRefresh();
  const [activeView, setActiveView] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Estado para diferentes vistas
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(null);
  const [passengerHistory, setPassengerHistory] = useState<PassengerHistory | null>(null);
  const [systemHealth, setSystemHealth] = useState<any>(null);

  // Formularios
  const [passengerSearchId, setPassengerSearchId] = useState('');

  // Cargar dashboard por defecto
  useEffect(() => {
    if (activeView === 'dashboard') {
      loadDashboard();
    }
  }, [activeView]);

  // Recargar dashboard cuando se notifica un cambio en los datos
  useEffect(() => {
    if (refreshTrigger > 0 && activeView === 'dashboard' && dashboardData) {
      loadDashboard();
    }
  }, [refreshTrigger]);

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getDashboardSummary();
      setDashboardData(data);
    } catch (err) {
      setError(`Error al cargar el dashboard: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const loadPassengerHistory = async () => {
    if (!passengerSearchId.trim()) {
      setError('Por favor ingrese un ID de pasajero');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getPassengerHistory(passengerSearchId);
      setPassengerHistory(data);
    } catch (err) {
      setError(`Error al cargar historial del pasajero: ${err}`);
      setPassengerHistory(null);
    } finally {
      setLoading(false);
    }
  };





  const loadSystemHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getSystemHealth();
      setSystemHealth(data);
    } catch (err) {
      setError(`Error al cargar estado del sistema: ${err}`);
      setSystemHealth(null);
    } finally {
      setLoading(false);
    }
  };

  const handleViewChange = (view: string) => {
    setActiveView(view);
    setError(null);

    // Limpiar datos de otras vistas
    if (view !== 'dashboard') setDashboardData(null);
    if (view !== 'passenger') setPassengerHistory(null);
    if (view !== 'health') setSystemHealth(null);
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard General</h2>
        <button
          onClick={loadDashboard}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Actualizar
        </button>
      </div>

      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <User className="w-8 h-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm text-gray-600">Pasajeros (Mes Actual)</p>
                <p className="text-2xl font-semibold">{dashboardData.monthly_stats.current_month.passengers}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <MapPin className="w-8 h-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm text-gray-600">Viajes (Mes Actual)</p>
                <p className="text-2xl font-semibold">{dashboardData.monthly_stats.current_month.trips}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <Calendar className="w-8 h-8 text-purple-500" />
              <div className="ml-4">
                <p className="text-sm text-gray-600">Total Tickets</p>
                <p className="text-2xl font-semibold">{dashboardData.total_tickets}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <DollarSign className="w-8 h-8 text-yellow-500" />
              <div className="ml-4">
                <p className="text-sm text-gray-600">Ingresos Totales</p>
                <p className="text-2xl font-semibold">${dashboardData.total_revenue.toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {dashboardData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-lg font-semibold mb-4">Estadísticas Mensuales</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Mes actual - Pasajeros:</span>
                <span className="font-semibold">{dashboardData.monthly_stats.current_month.passengers}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Mes actual - Viajes:</span>
                <span className="font-semibold">{dashboardData.monthly_stats.current_month.trips}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Mes actual - Tickets:</span>
                <span className="font-semibold">{dashboardData.monthly_stats.current_month.tickets}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Crecimiento:</span>
                <span className="font-semibold">{dashboardData.monthly_stats.growth_rate}%</span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-lg font-semibold mb-4">Información General</h3>
            <div className="space-y-3">
              <div>
                <span className="text-gray-600 block">Rutas activas:</span>
                <span className="font-semibold">{dashboardData.active_routes}</span>
              </div>
              <div>
                <span className="text-gray-600 block">Total de tickets:</span>
                <span className="font-semibold">{dashboardData.total_tickets}</span>
              </div>
              <div>
                <span className="text-gray-600 block">Ingresos totales:</span>
                <span className="font-semibold">${dashboardData.total_revenue}</span>
              </div>
              <div>
                <span className="text-gray-600 block">Última actualización:</span>
                <span className="text-sm text-gray-500">{new Date(dashboardData.last_updated).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderPassengerSearch = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow border">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Historial de Pasajero</h2>
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Ingrese ID del pasajero"
            value={passengerSearchId}
            onChange={(e) => setPassengerSearchId(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={loadPassengerHistory}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
          >
            <Search className="w-4 h-4" />
            Buscar
          </button>
        </div>
      </div>

      {passengerHistory && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-lg font-semibold mb-4">Información del Pasajero</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="text-gray-600 block">Nombre:</span>
                <span className="font-semibold">{passengerHistory.passenger.full_name}</span>
              </div>
              <div>
                <span className="text-gray-600 block">Email:</span>
                <span className="font-semibold">{passengerHistory.passenger.email}</span>
              </div>
              <div>
                <span className="text-gray-600 block">Teléfono:</span>
                <span className="font-semibold">{passengerHistory.passenger.phone}</span>
              </div>
              <div>
                <span className="text-gray-600 block">Documento:</span>
                <span className="font-semibold">{passengerHistory.passenger.document_type} - {passengerHistory.passenger.document_number}</span>
              </div>
              <div>
                <span className="text-gray-600 block">Estado:</span>
                <span className={`px-2 py-1 rounded text-sm ${passengerHistory.passenger.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {passengerHistory.passenger.status}
                </span>
              </div>
              <div>
                <span className="text-gray-600 block">Fecha de nacimiento:</span>
                <span className="font-semibold">{new Date(passengerHistory.passenger.date_of_birth).toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-lg font-semibold mb-4">Estadísticas de Viaje</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">{passengerHistory.statistics.total_trips}</p>
                <p className="text-gray-600">Total Viajes</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">${passengerHistory.statistics.total_spent}</p>
                <p className="text-gray-600">Total Gastado</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-semibold text-purple-600">{passengerHistory.statistics.favorite_route}</p>
                <p className="text-gray-600">Ruta Favorita</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-semibold text-orange-600">{passengerHistory.statistics.favorite_destination}</p>
                <p className="text-gray-600">Destino Favorito</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-lg font-semibold mb-4">Historial de Tickets</h3>
            {passengerHistory.recent_tickets.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ticket ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Viaje</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Asiento</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha Compra</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precio</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {passengerHistory.recent_tickets.map((ticket: any, index: number) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {ticket.ticket_id ? ticket.ticket_id.substring(0, 20) + '...' : 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {ticket.trip_id || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {ticket.seat_number || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {ticket.purchase_date && ticket.purchase_date !== '0001-01-01T00:00:00Z'
                            ? new Date(ticket.purchase_date).toLocaleDateString()
                            : 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            ticket.booking_status === 'confirmed' ? 'bg-green-100 text-green-800' :
                            ticket.booking_status === 'cancelled' ? 'bg-red-100 text-red-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {ticket.booking_status || 'N/A'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {ticket.total_price > 0 ? `${ticket.currency || 'PEN'} ${ticket.total_price.toFixed(2)}` : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-gray-500">
                  <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No hay historial de tickets disponible para este pasajero</p>
                  <p className="text-sm mt-2">Los tickets aparecerán aquí cuando el pasajero realice compras</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );





  const renderSystemHealth = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Estado del Sistema</h2>
        <button
          onClick={loadSystemHealth}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
        >
          <Activity className="w-4 h-4" />
          Verificar Estado
        </button>
      </div>

      {systemHealth && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold">Estado General del Sistema</h3>
            <span className={`px-3 py-1 rounded text-sm font-semibold ${
              systemHealth.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {systemHealth.status === 'healthy' ? 'Saludable' : 'Con problemas'}
            </span>
          </div>

          {systemHealth.services && (
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">Estado de Microservicios:</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(systemHealth.services).map(([service, health]: [string, any]) => (
                  <div key={service} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{service}</span>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        health.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {health.status === 'healthy' ? 'OK' : 'Error'}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      Última verificación: {new Date(health.last_check).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow border">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: BarChart },
              { id: 'passenger', label: 'Historial Pasajero', icon: User },
              { id: 'health', label: 'Estado Sistema', icon: Activity },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => handleViewChange(id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                  activeView === id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}

      {!loading && !error && (
        <>
          {activeView === 'dashboard' && renderDashboard()}
          {activeView === 'passenger' && renderPassengerSearch()}
          {activeView === 'health' && renderSystemHealth()}
        </>
      )}
    </div>
  );
}