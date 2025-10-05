import { useState, useEffect } from 'react';
import { TrendingUp, Users, MapPin, Ticket, DollarSign, Activity, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { LoadingSpinner } from './LoadingSpinner';
import type { DashboardSummaryResponse } from '../types';

export function AnalyticsSection() {
  const [summary, setSummary] = useState<DashboardSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Consumir endpoint real de analytics
      const data = await apiService.getDashboardSummary();
      setSummary(data);
      
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setError('Error al cargar analíticas. Por favor, verifica que el servicio ms-analytics esté activo.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  
  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Panel de Analytics</h2>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-red-800 mb-2">
                Error al cargar analíticas
              </h3>
              <p className="text-sm text-red-700 mb-3">
                {error}
              </p>
              <button
                onClick={fetchAnalytics}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm"
              >
                Reintentar
              </button>
            </div>
          </div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-yellow-800 mb-2">
                Servicio de Analytics no disponible
              </h3>
              <p className="text-sm text-yellow-700 mb-3">
                El microservicio ms-analytics no está respondiendo. Asegúrate de:
              </p>
              <ul className="list-disc list-inside space-y-1 text-sm text-yellow-700">
                <li>El servicio está corriendo en <code className="bg-yellow-100 px-1 rounded">http://localhost:8005</code></li>
                <li>AWS credentials están configuradas correctamente</li>
                <li>La base de datos Glue existe y tiene datos</li>
                <li>El bucket S3 para resultados está accesible</li>
              </ul>
              <div className="mt-4">
                <code className="text-xs bg-yellow-100 px-2 py-1 rounded block">
                  cd backend/ms-analytics && python -m uvicorn src.main:app --reload --port 8005
                </code>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!summary) return null;

  const { summary: metrics, trends } = summary;

  const statCards = [
    {
      title: 'Total Pasajeros',
      value: metrics.total_passengers.toLocaleString(),
      icon: Users,
      color: 'bg-blue-500',
      trend: trends?.passenger_growth ? `${trends.passenger_growth > 0 ? '+' : ''}${trends.passenger_growth.toFixed(1)}%` : 'N/A',
      trendPositive: (trends?.passenger_growth || 0) >= 0,
    },
    {
      title: 'Viajes Activos',
      value: metrics.active_trips.toLocaleString(),
      icon: MapPin,
      color: 'bg-green-500',
      trend: `${metrics.active_trips} activos`,
      trendPositive: true,
    },
    {
      title: 'Tickets Vendidos',
      value: metrics.tickets_sold.toLocaleString(),
      icon: Ticket,
      color: 'bg-orange-500',
      trend: `${metrics.cancellation_rate.toFixed(1)}% cancelados`,
      trendPositive: metrics.cancellation_rate < 10,
    },
    {
      title: 'Ingresos Totales',
      value: `S/ ${metrics.total_revenue.toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      icon: DollarSign,
      color: 'bg-purple-500',
      trend: trends?.revenue_growth ? `${trends.revenue_growth > 0 ? '+' : ''}${trends.revenue_growth.toFixed(1)}%` : 'N/A',
      trendPositive: (trends?.revenue_growth || 0) >= 0,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Panel de Analytics</h2>
          <p className="text-sm text-gray-500 mt-1">
            Datos de AWS Athena • Actualizado: {new Date(summary.timestamp).toLocaleString('es-PE')}
          </p>
        </div>
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
        {statCards.map(({ title, value, icon: Icon, color, trend, trendPositive }) => (
          <div key={title} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">{title}</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
                <div className="flex items-center space-x-1 mt-2">
                  <TrendingUp 
                    className={`w-4 h-4 ${trendPositive ? 'text-green-500' : 'text-red-500'} ${!trendPositive && 'rotate-180'}`} 
                  />
                  <span className={`text-sm font-medium ${trendPositive ? 'text-green-600' : 'text-red-600'}`}>
                    {trend}
                  </span>
                </div>
              </div>
              <div className={`${color} p-3 rounded-full`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Occupancy Gauge */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Ocupación Promedio</h3>
          <div className="flex items-center justify-center h-40">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full" viewBox="0 0 100 100">
                {/* Background circle */}
                <circle
                  className="text-gray-200"
                  strokeWidth="10"
                  stroke="currentColor"
                  fill="transparent"
                  r="40"
                  cx="50"
                  cy="50"
                />
                {/* Progress circle */}
                <circle
                  className="text-blue-500"
                  strokeWidth="10"
                  strokeDasharray={`${metrics.average_occupancy * 2.51327} 251.327`}
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="transparent"
                  r="40"
                  cx="50"
                  cy="50"
                  style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%' }}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-bold text-gray-900">
                  {metrics.average_occupancy.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
          <p className="text-center text-gray-600 mt-4">
            Ocupación promedio de los buses
          </p>
        </div>

        {/* System Status */}
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Métricas del Sistema</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <span className="font-medium text-blue-800">Tasa de Cancelación</span>
              <span className={`text-sm font-semibold ${
                metrics.cancellation_rate < 10 ? 'text-green-600' : 
                metrics.cancellation_rate < 20 ? 'text-yellow-600' : 
                'text-red-600'
              }`}>
                {metrics.cancellation_rate.toFixed(2)}%
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <span className="font-medium text-green-800">Tickets por Viaje</span>
              <span className="text-sm font-semibold text-green-600">
                {metrics.active_trips > 0 ? (metrics.tickets_sold / metrics.active_trips).toFixed(1) : '0'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
              <span className="font-medium text-purple-800">Ingreso Promedio</span>
              <span className="text-sm font-semibold text-purple-600">
                S/ {metrics.tickets_sold > 0 ? (metrics.total_revenue / metrics.tickets_sold).toFixed(2) : '0.00'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Activity className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-blue-800">
              <strong>Datos en tiempo real:</strong> Estas métricas son calculadas directamente desde AWS Athena 
              sobre el datalake completo. Para análisis más detallados, usa las pestañas específicas de 
              Pasajeros, Viajes o Tickets.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}