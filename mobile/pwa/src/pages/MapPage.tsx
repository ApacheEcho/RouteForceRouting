/**
 * RouteForce PWA - Map Page
 */

import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import {
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  MapPinIcon,
  TruckIcon
} from '@heroicons/react/24/outline';

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface Stop {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  status: 'pending' | 'completed' | 'current';
  estimatedTime: string;
}

interface Vehicle {
  id: string;
  name: string;
  lat: number;
  lng: number;
  status: 'active' | 'idle' | 'maintenance';
}

const mockStops: Stop[] = [
  {
    id: '1',
    name: 'Downtown Store',
    address: '123 Main St',
    lat: 45.5152,
    lng: -122.6784,
    status: 'completed',
    estimatedTime: '09:00',
  },
  {
    id: '2',
    name: 'City Center Mall',
    address: '456 Center Ave',
    lat: 45.5200,
    lng: -122.6750,
    status: 'current',
    estimatedTime: '10:30',
  },
  {
    id: '3',
    name: 'Suburban Plaza',
    address: '789 Suburb Rd',
    lat: 45.5100,
    lng: -122.6900,
    status: 'pending',
    estimatedTime: '12:00',
  },
];

const mockVehicles: Vehicle[] = [
  {
    id: '1',
    name: 'Truck A',
    lat: 45.5200,
    lng: -122.6750,
    status: 'active',
  },
  {
    id: '2',
    name: 'Van B',
    lat: 45.5050,
    lng: -122.6850,
    status: 'idle',
  },
];

const routeCoordinates: [number, number][] = [
  [45.5152, -122.6784],
  [45.5200, -122.6750],
  [45.5100, -122.6900],
];

const MapPage: React.FC = () => {
  const [showStops, setShowStops] = useState(true);
  const [showVehicles, setShowVehicles] = useState(true);
  const [showRoute, setShowRoute] = useState(true);

  const center: [number, number] = [45.5152, -122.6784]; // Portland, OR

  const getStopIcon = (status: Stop['status']) => {
    const color = status === 'completed' ? 'green' : status === 'current' ? 'blue' : 'red';
    return new L.Icon({
      iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });
  };

  const getVehicleIcon = (status: Vehicle['status']) => {
    const color = status === 'active' ? 'orange' : status === 'idle' ? 'grey' : 'black';
    return new L.Icon({
      iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold text-gray-900">Map View</h1>
          <div className="flex items-center space-x-2">
            <button className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-md">
              <MagnifyingGlassIcon className="h-5 w-5" />
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-md">
              <AdjustmentsHorizontalIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Map Controls */}
      <div className="bg-white border-b border-gray-200 px-4 py-2">
        <div className="flex items-center space-x-4 text-sm">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showStops}
              onChange={(e) => setShowStops(e.target.checked)}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span className="text-gray-700">Stops</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showVehicles}
              onChange={(e) => setShowVehicles(e.target.checked)}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span className="text-gray-700">Vehicles</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showRoute}
              onChange={(e) => setShowRoute(e.target.checked)}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span className="text-gray-700">Route</span>
          </label>
        </div>
      </div>

      {/* Map */}
      <div className="flex-1 relative">
        <MapContainer
          center={center}
          zoom={13}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {/* Route Polyline */}
          {showRoute && (
            <Polyline
              positions={routeCoordinates}
              color="blue"
              weight={4}
              opacity={0.7}
            />
          )}
          
          {/* Stops */}
          {showStops && mockStops.map((stop) => (
            <Marker
              key={stop.id}
              position={[stop.lat, stop.lng]}
              icon={getStopIcon(stop.status)}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-semibold">{stop.name}</h3>
                  <p className="text-sm text-gray-600">{stop.address}</p>
                  <p className="text-sm">
                    <span className={`capitalize ${
                      stop.status === 'completed' ? 'text-green-600' :
                      stop.status === 'current' ? 'text-blue-600' : 'text-red-600'
                    }`}>
                      {stop.status}
                    </span>
                    {' • '}
                    <span className="text-gray-600">ETA: {stop.estimatedTime}</span>
                  </p>
                </div>
              </Popup>
            </Marker>
          ))}
          
          {/* Vehicles */}
          {showVehicles && mockVehicles.map((vehicle) => (
            <Marker
              key={vehicle.id}
              position={[vehicle.lat, vehicle.lng]}
              icon={getVehicleIcon(vehicle.status)}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-semibold">{vehicle.name}</h3>
                  <p className="text-sm">
                    <span className={`capitalize ${
                      vehicle.status === 'active' ? 'text-green-600' :
                      vehicle.status === 'idle' ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {vehicle.status}
                    </span>
                  </p>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* Bottom Info Panel */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="flex items-center justify-center space-x-1 text-green-600">
              <MapPinIcon className="h-4 w-4" />
              <span className="text-sm font-medium">Completed</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">1</p>
          </div>
          <div>
            <div className="flex items-center justify-center space-x-1 text-blue-600">
              <MapPinIcon className="h-4 w-4" />
              <span className="text-sm font-medium">Current</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">1</p>
          </div>
          <div>
            <div className="flex items-center justify-center space-x-1 text-orange-600">
              <TruckIcon className="h-4 w-4" />
              <span className="text-sm font-medium">Vehicles</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">2</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapPage;
