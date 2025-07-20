/**
 * RouteForce PWA - Routes Page
 */

import React, { useState } from 'react';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  MapPinIcon,
  ClockIcon,
  TruckIcon
} from '@heroicons/react/24/outline';

interface Route {
  id: string;
  name: string;
  status: 'active' | 'completed' | 'planned';
  distance: string;
  duration: string;
  stops: number;
  efficiency: number;
  lastUpdated: string;
}

const mockRoutes: Route[] = [
  {
    id: '1',
    name: 'Downtown Delivery Route',
    status: 'active',
    distance: '45.2 km',
    duration: '2h 15m',
    stops: 12,
    efficiency: 92,
    lastUpdated: '5 minutes ago',
  },
  {
    id: '2',
    name: 'Suburban Collection Route',
    status: 'completed',
    distance: '67.8 km',
    duration: '3h 45m',
    stops: 18,
    efficiency: 88,
    lastUpdated: '2 hours ago',
  },
  {
    id: '3',
    name: 'Express Highway Route',
    status: 'planned',
    distance: '123.5 km',
    duration: '1h 30m',
    stops: 6,
    efficiency: 95,
    lastUpdated: '1 day ago',
  },
  {
    id: '4',
    name: 'Industrial District Route',
    status: 'active',
    distance: '34.7 km',
    duration: '1h 45m',
    stops: 8,
    efficiency: 85,
    lastUpdated: '15 minutes ago',
  },
];

const RoutesPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'completed' | 'planned'>('all');

  const filteredRoutes = mockRoutes.filter(route => {
    const matchesSearch = route.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || route.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: Route['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'planned':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="px-4 py-6 sm:px-6 lg:px-8">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Routes</h1>
            <p className="mt-1 text-sm text-gray-600">
              Manage and optimize your delivery routes
            </p>
          </div>
          <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-indigo-700 transition-colors">
            <PlusIcon className="h-5 w-5" />
            <span className="hidden sm:inline">New Route</span>
          </button>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="mb-6 space-y-4 sm:space-y-0 sm:flex sm:space-x-4">
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search routes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          />
        </div>
        <div className="flex items-center space-x-2">
          <FunnelIcon className="h-5 w-5 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as any)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="planned">Planned</option>
          </select>
        </div>
      </div>

      {/* Routes List */}
      <div className="bg-white shadow overflow-hidden rounded-md">
        <ul className="divide-y divide-gray-200">
          {filteredRoutes.map((route) => (
            <li key={route.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <MapPinIcon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {route.name}
                      </p>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          route.status
                        )}`}
                      >
                        {route.status}
                      </span>
                    </div>
                    <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        <TruckIcon className="h-4 w-4" />
                        <span>{route.distance}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <ClockIcon className="h-4 w-4" />
                        <span>{route.duration}</span>
                      </div>
                      <span>{route.stops} stops</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {route.efficiency}% efficient
                    </p>
                    <p className="text-sm text-gray-500">{route.lastUpdated}</p>
                  </div>
                  <button className="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                    View
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {filteredRoutes.length === 0 && (
        <div className="text-center py-12">
          <MapPinIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No routes found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your search or create a new route.
          </p>
        </div>
      )}
    </div>
  );
};

export default RoutesPage;
