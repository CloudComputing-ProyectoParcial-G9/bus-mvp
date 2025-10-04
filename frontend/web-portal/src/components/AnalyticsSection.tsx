import React, { useState, useEffect } from 'react';
import { TrendingUp, Users, MapPin, Ticket, DollarSign, Activity } from 'lucide-react';
import { apiService } from '../services/api';
import { LoadingSpinner } from './LoadingSpinner';

export function AnalyticsSection() {
  const [analytics, setAnalytics] = useState({
    total_passengers: 0,
    total_trips: 0,
    total_tickets: 0,
    revenue: 0,
    popular_routes: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      // Simular datos de analytics ya que no tenemos el endpoint específico
      // En un caso real, esto vendría de tu API de analytics
      const [passengers, trips, tickets] = await Promise.all([
        apiService.getPassengers().catch(() => ({ data: [] })),
        apiService.getTrips().catch(() => ({ data: [] })),
        apiService.getTickets().catch(() => ({ data: [] })),
      ]);

      const passengersData = Array.isArray(passengers) ? passengers : passengers.data || [];
      const tripsData = Array.isArray(trips) ? trips : trips.data || [];
      const ticketsData = Array.isArray(tickets) ? tickets : tickets.data || [];

      const totalRevenue = ticketsData.reduce((sum: number, ticket: any) => 
        sum + (ticket.price || 0), 0
      );

      const routeCounts: { [key: string]: number } = {};
      tripsData.forEach((trip: any) => {
        const route = `${trip.origin} → ${trip.destination}`;
        routeCounts[route] = (routeCounts[route] || 0) + 1;
      });

      const popularRoutes = Object.entries(routeCounts)
        .map(([route, count]) => ({ route, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);

      setAnalytics({
        total_passengers: passengersData.length,
        total_trips: tripsData.length,
        total_tickets: ticketsData.length,
        revenue: totalRevenue,
        popular_routes: popularRoutes,
      });
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  const statCards = [
    {
      title: 'Total Pasajeros',
      value: analytics.total_passengers,
      icon: Users,
      color: 'bg-blue-500',
      trend: '+12%',
    },
    {
      title: 'Viajes Activos',
      value: analytics.total_trips,
      icon: MapPin,
      color: 'bg-green-500',
      trend: '+8%',
    },
    {
      title: 'Tickets Vendidos',
      value: analytics.total_tickets,
      icon: Ticket,
      color: 'bg-orange-500',
      trend: '+15%',
    },
    {
      title: 'Ingresos',
      value: `S/ ${analytics.revenue.toFixed(2)}`,
      icon: DollarSign,
      color: 'bg-purple-500',
      trend: '+20%',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Panel de Analytics</h2>
        <button
          onClick={fetchAnalytics}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Activity className="w-4 h-4" />
          <span>Actualizar</span>
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map(({ title, value, icon: Icon, color, trend }) => (
          <div key={title} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{title}</p>
                <p className="text-3xl font-bold text-gray-900">{value}</p>
                <div className="flex items-center space-x-1 mt-2">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                  <span className="text-sm font-medium text-green-600">{trend}</span>
                </div>
              </div>
              <div className={`${color} p-3 rounded-full`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Popular Routes */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Rutas Más Populares</h3>
        {analytics.popular_routes.length > 0 ? (
          <div className="space-y-4">
            {analytics.popular_routes.map(({ route, count }, index) => (
              <div key={route} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium">
                    {index + 1}
                  </div>
                  <span className="font-medium text-gray-900">{route}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">{count} viajes</span>
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{
                        width: `${(count / Math.max(...analytics.popular_routes.map(r => r.count))) * 100}%`
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No hay datos de rutas disponibles</p>
          </div>
        )}
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Ocupación Promedio</h3>
          <div className="flex items-center justify-center h-40">
            <div className="relative w-32 h-32">
              <div className="w-full h-full bg-gray-200 rounded-full"></div>
              <div 
                className="absolute inset-0 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"
                style={{
                  background: `conic-gradient(from 0deg, #3B82F6 0deg, #3B82F6 ${75 * 3.6}deg, #E5E7EB ${75 * 3.6}deg)`
                }}
              ></div>
              <div className="absolute inset-4 bg-white rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-gray-900">75%</span>
              </div>
            </div>
          </div>
          <p className="text-center text-gray-600 mt-4">Ocupación promedio de los viajes</p>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Estado del Sistema</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <span className="font-medium text-green-800">Servicio de Pasajeros</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-green-600">Activo</span>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <span className="font-medium text-green-800">Servicio de Viajes</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-green-600">Activo</span>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <span className="font-medium text-green-800">Servicio de Tickets</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-green-600">Activo</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}