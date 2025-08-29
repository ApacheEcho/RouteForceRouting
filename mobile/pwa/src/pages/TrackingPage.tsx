/**
 * RouteForce PWA - Tracking Page
 */

import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { fetchTelemetry, trackSession } from '../api';
import {
  PlayIcon,
  PauseIcon,
  StopIcon,
  ClockIcon,
  MapPinIcon,
  TruckIcon,
  SignalIcon
} from '@heroicons/react/24/outline';

interface TrackingData {
  vehicleId: string;
  vehicleName: string;
  currentLocation: {
    lat: number;
    lng: number;
    address: string;
  };
  status: 'moving' | 'stopped' | 'idle';
  speed: number;
  nextStop: {
    name: string;
    eta: string;
    distance: string;
  };
  routeProgress: {
    completed: number;
    total: number;
    percentage: number;
  };
  lastUpdate: string;
}

const mockTrackingData: TrackingData = {
  vehicleId: 'VH001',
  vehicleName: 'Delivery Truck A',
  currentLocation: {
    lat: 45.5200,
    lng: -122.6750,
    address: '456 Center Ave, Portland, OR',
  },
  status: 'moving',
  speed: 35,
  nextStop: {
    name: 'Suburban Plaza',
    eta: '15 minutes',
    distance: '2.3 km',
  },
  routeProgress: {
    completed: 7,
    total: 12,
    percentage: 58,
  },
  lastUpdate: '2 minutes ago',
};

const TrackingPage: React.FC = () => {
  // Track feature usage for analytics (moved from top-level)
  useEffect(() => {
    const deviceId = window.navigator.userAgent + '_' + (window.crypto?.randomUUID?.() || Math.random().toString(36).substring(2));
    const platform = /iPhone|iPad|iPod|iOS/i.test(navigator.userAgent)
      ? 'iOS'
      : /Android/i.test(navigator.userAgent)
      ? 'Android'
      : 'Web';
    trackSession({
      device_id: deviceId,
      app_version: '1.0.0',
      device_type: platform,
      features_used: ['tracking'],
      api_calls: 1,
    });
  }, []);
  const [isTracking, setIsTracking] = useState(true);
  const [trackingData, setTrackingData] = useState<TrackingData>(mockTrackingData);
  const [loading, setLoading] = useState(true);

  // Fetch telemetry data for the vehicle on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Replace with actual vehicleId as needed
        const vehicleId = mockTrackingData.vehicleId;
        const telemetry = await fetchTelemetry(vehicleId);
        if (telemetry && telemetry.length > 0) {
          const latest = telemetry[0];
          setTrackingData(prev => ({
            ...prev,
            speed: latest.speed,
            currentLocation: {
              ...prev.currentLocation,
              lat: latest.lat,
              lng: latest.lng,
            },
            lastUpdate: new Date(latest.timestamp).toLocaleTimeString(),
          }));
        }
      } catch (e) {
        toast.error('Failed to fetch telemetry data. Showing last known values.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Simulate real-time updates (keep for demo)
  useEffect(() => {
    if (!isTracking) return;
    const interval = setInterval(() => {
      setTrackingData(prev => ({
        ...prev,
        speed: Math.floor(Math.random() * 20) + 25,
        lastUpdate: 'Just now',
      }));
    }, 5000);
    return () => clearInterval(interval);
  }, [isTracking]);

  const getStatusColor = (status: TrackingData['status']) => {
    switch (status) {
      case 'moving':
        return 'text-green-600 bg-green-100';
      case 'stopped':
        return 'text-red-600 bg-red-100';
      case 'idle':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: TrackingData['status']) => {
    switch (status) {
      case 'moving':
        return <TruckIcon className="h-5 w-5" />;
      case 'stopped':
        return <StopIcon className="h-5 w-5" />;
      case 'idle':
        return <PauseIcon className="h-5 w-5" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen" aria-live="polite" role="status">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" aria-label="Loading" />
        <span className="ml-4 text-indigo-700 font-medium">Loading vehicle data...</span>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-6 lg:px-8" role="main" aria-labelledby="tracking-title">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900" id="tracking-title">Live Tracking</h1>
            <p className="mt-1 text-sm text-gray-600">
              Real-time vehicle and route monitoring
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsTracking(!isTracking)}
              className={`p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                isTracking
                  ? 'bg-red-100 text-red-600 hover:bg-red-200'
                  : 'bg-green-100 text-green-600 hover:bg-green-200'
              }`}
              aria-label={isTracking ? 'Pause tracking' : 'Resume tracking'}
              tabIndex={0}
            >
              {isTracking ? (
                <PauseIcon className="h-5 w-5" aria-hidden="true" />
              ) : (
                <PlayIcon className="h-5 w-5" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Vehicle Status Card */}
      <div className="bg-white shadow rounded-lg mb-6" role="region" aria-label="Vehicle status">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <TruckIcon className="h-8 w-8 text-gray-400" aria-hidden="true" />
              <div>
                <h2 className="text-lg font-medium text-gray-900">
                  {trackingData.vehicleName}
                </h2>
                <p className="text-sm text-gray-500">ID: {trackingData.vehicleId}</p>
              </div>
            </div>
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${getStatusColor(trackingData.status)}`}>
              {getStatusIcon(trackingData.status)}
              <span className="text-sm font-medium capitalize">{trackingData.status}</span>
            </div>
          </div>
        </div>

        <div className="px-6 py-4">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <div className="flex items-center space-x-2 text-sm text-gray-500 mb-1">
                <SignalIcon className="h-4 w-4" />
                <span>Current Speed</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{trackingData.speed} km/h</p>
            </div>
            <div>
              <div className="flex items-center space-x-2 text-sm text-gray-500 mb-1">
                <ClockIcon className="h-4 w-4" />
                <span>Last Update</span>
              </div>
              <p className="text-sm font-medium text-gray-900">{trackingData.lastUpdate}</p>
            </div>
          </div>

          <div className="mb-4">
            <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
              <MapPinIcon className="h-4 w-4" />
              <span>Current Location</span>
            </div>
            <p className="text-sm font-medium text-gray-900">
              {trackingData.currentLocation.address}
            </p>
          </div>
        </div>
      </div>

      {/* Route Progress */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Route Progress</h3>
        </div>
        <div className="px-6 py-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              {trackingData.routeProgress.completed} of {trackingData.routeProgress.total} stops completed
            </span>
            <span className="text-sm font-medium text-indigo-600">
              {trackingData.routeProgress.percentage}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${trackingData.routeProgress.percentage}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Next Stop */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Next Stop</h3>
        </div>
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-lg font-medium text-gray-900">
                {trackingData.nextStop.name}
              </h4>
              <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                <div className="flex items-center space-x-1">
                  <ClockIcon className="h-4 w-4" />
                  <span>ETA: {trackingData.nextStop.eta}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <MapPinIcon className="h-4 w-4" />
                  <span>{trackingData.nextStop.distance} away</span>
                </div>
              </div>
            </div>
            <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
              Navigate
            </button>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-4">
        <button className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center hover:bg-blue-100 transition-colors">
          <MapPinIcon className="h-6 w-6 text-blue-600 mx-auto mb-2" />
          <span className="text-sm font-medium text-blue-900">View on Map</span>
        </button>
        <button className="bg-green-50 border border-green-200 rounded-lg p-4 text-center hover:bg-green-100 transition-colors">
          <SignalIcon className="h-6 w-6 text-green-600 mx-auto mb-2" />
          <span className="text-sm font-medium text-green-900">Send Alert</span>
        </button>
      </div>
    </div>
  );
};

export default TrackingPage;
