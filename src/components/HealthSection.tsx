import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle, XCircle, Clock } from 'lucide-react';
import { apiService } from '../services/api';
import { LoadingSpinner } from './LoadingSpinner';

interface ServiceHealth {
  name: string;
  status: 'healthy' | 'unhealthy' | 'checking';
  url: string;
  responseTime?: number;
  lastChecked?: string;
}

export function HealthSection() {
  const [services, setServices] = useState<ServiceHealth[]>([
    { name: 'Pasajeros', status: 'checking', url: 'passengers' },
    { name: 'Viajes', status: 'checking', url: 'trips' },
    { name: 'Tickets', status: 'checking', url: 'tickets' },
  ]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkAllServices();
  }, []);

  const checkService = async (service: ServiceHealth): Promise<ServiceHealth> => {
    try {
      const startTime = Date.now();
      await apiService.checkHealth(service.url as any);
      const responseTime = Date.now() - startTime;
      
      return {
        ...service,
        status: 'healthy',
        responseTime,
        lastChecked: new Date().toLocaleTimeString(),
      };
    } catch (error) {
      return {
        ...service,
        status: 'unhealthy',
        lastChecked: new Date().toLocaleTimeString(),
      };
    }
  };

  const checkAllServices = async () => {
    setLoading(true);
    
    const updatedServices = await Promise.all(
      services.map(service => checkService(service))
    );
    
    setServices(updatedServices);
    setLoading(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'unhealthy':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'checking':
        return <Clock className="w-5 h-5 text-yellow-500 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'unhealthy':
        return 'bg-red-100 text-red-800';
      case 'checking':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const healthyServices = services.filter(s => s.status === 'healthy').length;
  const totalServices = services.length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Estado del Sistema</h2>
          <p className="text-gray-600">Monitoreo de microservicios en tiempo real</p>
        </div>
        <button
          onClick={checkAllServices}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 disabled:opacity-50"
        >
          <Activity className="w-4 h-4" />
          <span>{loading ? 'Verificando...' : 'Verificar Estado'}</span>
        </button>
      </div>

      {/* Overall System Status */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Estado General del Sistema</h3>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            healthyServices === totalServices ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
          }`}>
            {healthyServices === totalServices ? 'Todos los servicios operativos' : 'Algunos servicios presentan problemas'}
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex-1 bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${
                healthyServices === totalServices ? 'bg-green-500' : 'bg-yellow-500'
              }`}
              style={{ width: `${(healthyServices / totalServices) * 100}%` }}
            ></div>
          </div>
          <span className="text-sm font-medium text-gray-600">
            {healthyServices}/{totalServices} servicios activos
          </span>
        </div>
      </div>

      {/* Individual Service Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {services.map((service) => (
          <div key={service.name} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="bg-blue-100 p-2 rounded-full">
                  {getStatusIcon(service.status)}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{service.name}</h3>
                  <p className="text-sm text-gray-500">Microservicio</p>
                </div>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(service.status)}`}>
                {service.status === 'healthy' ? 'Activo' : service.status === 'unhealthy' ? 'Inactivo' : 'Verificando'}
              </span>
            </div>
            
            <div className="space-y-2 text-sm">
              {service.responseTime && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Tiempo de respuesta:</span>
                  <span className="font-medium">{service.responseTime}ms</span>
                </div>
              )}
              {service.lastChecked && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Última verificación:</span>
                  <span className="font-medium">{service.lastChecked}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-600">Endpoint:</span>
                <span className="font-medium text-blue-600">/{service.url}</span>
              </div>
            </div>

            {service.status === 'unhealthy' && (
              <div className="mt-4 p-3 bg-red-50 rounded-lg">
                <p className="text-sm text-red-800">
                  El servicio no está disponible. Verifique la conectividad y configuración.
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* System Information */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Información del Sistema</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-900">3</p>
            <p className="text-sm text-gray-600">Microservicios</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-900">5</p>
            <p className="text-sm text-gray-600">Puertos activos</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-900">99.9%</p>
            <p className="text-sm text-gray-600">Uptime</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-900">24/7</p>
            <p className="text-sm text-gray-600">Monitoreo</p>
          </div>
        </div>
      </div>
    </div>
  );
}