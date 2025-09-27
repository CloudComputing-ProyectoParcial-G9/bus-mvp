import React, { useState, useEffect } from 'react';
import { Plus, Edit, Search, User } from 'lucide-react';
import { apiService } from '../services/api';
import { Passenger } from '../types';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';

export function PassengersSection() {
  const [passengers, setPassengers] = useState<Passenger[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingPassenger, setEditingPassenger] = useState<Passenger | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const [formData, setFormData] = useState<Passenger>({
    full_name: '',
    email: '',
    phone: '',
    document_type: 'DNI',
    document_number: '',
    date_of_birth: '',
  });

  useEffect(() => {
    fetchPassengers();
  }, []);

  const fetchPassengers = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getPassengers();
      // El backend devuelve { passengers: [...], total: number }
      const passengersData = response.passengers || response.data || response || [];
      setPassengers(Array.isArray(passengersData) ? passengersData : []);
    } catch (err) {
      console.error('Error fetching passengers:', err);
      setError('Error al cargar los pasajeros');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      console.log('Enviando datos:', formData);

      if (editingPassenger) {
        // Para actualización, usar el passenger_id si está disponible
        const passengerId = editingPassenger.id || (editingPassenger as Passenger & { passenger_id?: string }).passenger_id;
        if (!passengerId) {
          throw new Error('ID de pasajero no disponible para actualización');
        }
        const response = await apiService.updatePassenger(passengerId, formData);
        console.log('Pasajero actualizado:', response);
      } else {
        const response = await apiService.createPassenger(formData);
        console.log('Pasajero creado:', response);
      }

      setShowForm(false);
      setEditingPassenger(null);
      resetForm();
      await fetchPassengers();
    } catch (err) {
      console.error('Error al guardar el pasajero:', err);
      setError(`Error al guardar el pasajero: ${err instanceof Error ? err.message : 'Error desconocido'}`);
    }
  };

  const resetForm = () => {
    setFormData({
      full_name: '',
      email: '',
      phone: '',
      document_type: 'DNI',
      document_number: '',
      date_of_birth: '',
    });
  };

  const handleEdit = (passenger: Passenger) => {
    setEditingPassenger(passenger);
    // Mapear los datos del pasajero al formato del formulario
    setFormData({
      full_name: passenger.full_name,
      email: passenger.email,
      phone: passenger.phone,
      document_type: passenger.document_type,
      document_number: passenger.document_number,
      date_of_birth: passenger.date_of_birth,
    });
    setShowForm(true);
  };

  const filteredPassengers = passengers.filter(passenger =>
    passenger.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    passenger.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    passenger.document_number.includes(searchTerm)
  );

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={fetchPassengers} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-2xl font-bold text-gray-900">Gestión de Pasajeros</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Nuevo Pasajero</span>
        </button>
      </div>

      <div className="relative">
        <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar pasajeros..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">
            {editingPassenger ? 'Editar Pasajero' : 'Nuevo Pasajero'}
          </h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombre Completo</label>
              <input
                type="text"
                required
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de Nacimiento</label>
              <input
                type="date"
                required
                value={formData.date_of_birth}
                onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
              <input
                type="tel"
                required
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Documento</label>
              <select
                value={formData.document_type}
                onChange={(e) => setFormData({ ...formData, document_type: e.target.value as 'DNI' | 'PASSPORT' | 'CE' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="DNI">DNI</option>
                <option value="PASSPORT">Pasaporte</option>
                <option value="CE">Carné de Extranjería</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Número de Documento</label>
              <input
                type="text"
                required
                value={formData.document_number}
                onChange={(e) => setFormData({ ...formData, document_number: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="md:col-span-2 flex space-x-3">
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                {editingPassenger ? 'Actualizar' : 'Crear'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  setEditingPassenger(null);
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
        {filteredPassengers.map((passenger) => (
          <div key={passenger.id} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="bg-blue-100 p-2 rounded-full">
                  <User className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{passenger.full_name}</h3>
                  <p className="text-sm text-gray-500">{passenger.email}</p>
                </div>
              </div>
              <button
                onClick={() => handleEdit(passenger)}
                className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                title="Editar pasajero"
              >
                <Edit className="w-4 h-4 text-gray-500" />
              </button>
            </div>
            <div className="space-y-2 text-sm">
              <p><span className="font-medium">Teléfono:</span> {passenger.phone}</p>
              <p><span className="font-medium">{passenger.document_type}:</span> {passenger.document_number}</p>
              {passenger.created_at && (
                <p><span className="font-medium">Registrado:</span> {new Date(passenger.created_at).toLocaleDateString()}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredPassengers.length === 0 && (
        <div className="text-center py-8">
          <User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No hay pasajeros registrados</p>
        </div>
      )}
    </div>
  );
}