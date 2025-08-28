/**
 * RouteForce PWA - Map Page
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchStops, fetchVehicles, Stop, Vehicle } from '../api';
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

  // Fetch stops and vehicles from backend
  const {
    data: stops,
    isLoading: stopsLoading,
    error: stopsError
  } = useQuery({ queryKey: ['stops'], queryFn: fetchStops });

  const {
    data: vehicles,
    isLoading: vehiclesLoading,
    error: vehiclesError
  } = useQuery({ queryKey: ['vehicles'], queryFn: fetchVehicles });

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
    <div className="h-screen flex flex-col" role="main" aria-labelledby="map-title">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 px-4 py-3" role="banner">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold text-gray-900" id="map-title">Map View</h1>
          <div className="flex items-center space-x-2">
            <button className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2" aria-label="Search" tabIndex={0}>
              <MagnifyingGlassIcon className="h-5 w-5" aria-hidden="true" />
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2" aria-label="Filter" tabIndex={0}>
              <AdjustmentsHorizontalIcon className="h-5 w-5" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>

      {/* Map Controls */}
      <div className="bg-white border-b border-gray-200 px-4 py-2" role="region" aria-label="Map controls">
        <div className="flex items-center space-x-4 text-sm">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showStops}
              onChange={(e) => setShowStops(e.target.checked)}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              aria-label="Show stops"
            />
            <span className="text-gray-700">Stops</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showVehicles}
              onChange={(e) => setShowVehicles(e.target.checked)}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              aria-label="Show vehicles"
            />
            <span className="text-gray-700">Vehicles</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showRoute}
              onChange={(e) => setShowRoute(e.target.checked)}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              aria-label="Show route"
            />
            <span className="text-gray-700">Route</span>
          </label>
        </div>
      </div>

      {/* Map */}
      <div className="flex-1 relative" role="region" aria-label="Map display">
        <MapContainer
          center={center}
          zoom={13}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {/* Loading/Error States */}
          {(stopsLoading || vehiclesLoading) && (
            <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-70 z-10" aria-live="polite" role="status">
              <span className="text-lg font-semibold text-gray-700">Loading map data...</span>
            </div>
          )}
          {(stopsError || vehiclesError) && (
            <div className="absolute inset-0 flex items-center justify-center bg-red-100 z-10" aria-live="assertive" role="alert">
              <span className="text-lg font-semibold text-red-700">Error loading map data</span>
            </div>
          )}

          {/* Route Polyline (remains static for now) */}
          {showRoute && (
            <Polyline
              positions={[
                [45.5152, -122.6784],
                [45.5200, -122.6750],
                [45.5100, -122.6900],
              ]}
              color="blue"
              weight={4}
              opacity={0.7}
            />
          )}

          {/* Stops */}
          {showStops && stops && stops.map((stop) => (
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
                    }`} aria-label={stop.status}>
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
          {showVehicles && vehicles && vehicles.map((vehicle) => (
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
