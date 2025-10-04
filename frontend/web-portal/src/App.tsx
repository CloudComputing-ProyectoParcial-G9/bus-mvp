import React, { useState } from 'react';
import { Bus } from 'lucide-react';
import { TabNavigation } from './components/TabNavigation';
import { PassengersSection } from './components/PassengersSection';
import { TripsSection } from './components/TripsSection';
import { TicketsSection } from './components/TicketsSection';
import { AnalyticsSection } from './components/AnalyticsSection';
import { HealthSection } from './components/HealthSection';

function App() {
  const [activeTab, setActiveTab] = useState('passengers');

  const renderActiveSection = () => {
    switch (activeTab) {
      case 'passengers':
        return <PassengersSection />;
      case 'trips':
        return <TripsSection />;
      case 'tickets':
        return <TicketsSection />;
      case 'analytics':
        return <AnalyticsSection />;
      case 'health':
        return <HealthSection />;
      default:
        return <PassengersSection />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Bus className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Sistema de Gestión de Transporte</h1>
              <p className="text-sm text-gray-600">Panel administrativo para microservicios</p>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content */}
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderActiveSection()}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-8">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-gray-600">
            <p>&copy; 2025 Sistema de Gestión de Transporte. Todos los derechos reservados.</p>
            <p className="text-sm mt-2">Microservicios conectados: Pasajeros, Viajes, Tickets, Analytics</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;