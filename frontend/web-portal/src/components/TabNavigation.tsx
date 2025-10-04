import React from 'react';
import { Users, MapPin, Ticket, BarChart3, Activity } from 'lucide-react';

interface TabNavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const tabs = [
  { id: 'passengers', label: 'Pasajeros', icon: Users },
  { id: 'trips', label: 'Viajes', icon: MapPin },
  { id: 'tickets', label: 'Tickets', icon: Ticket },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'health', label: 'Estado', icon: Activity },
];

export function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  return (
    <div className="border-b border-gray-200 bg-white">
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-8 overflow-x-auto">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => onTabChange(id)}
              className={`
                flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors duration-200
                ${activeTab === id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              <Icon className="w-4 h-4" />
              <span className="whitespace-nowrap">{label}</span>
            </button>
          ))}
        </div>
      </nav>
    </div>
  );
}