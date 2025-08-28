// --- Analytics Dashboard API ---
export interface SystemHealth {
  health_score: number;
  status: string;
  uptime: string;
  active_sessions: number;
}

export interface MobileAnalytics {
  total_sessions: number;
  unique_devices: number;
  total_api_calls: number;
  device_types: Record<string, number>;
}

export interface RouteAnalytics {
  total_routes: number;
  success_rate: number;
  avg_optimization_time: number;
  algorithm_usage: Record<string, number>;
}

export interface DriverAnalytics {
  total_drivers: number;
  avg_customer_rating: number;
  total_location_updates: number;
  top_performers: Array<{ driver_id: string; avg_rating: number }>;
}

export interface APIAnalytics {
  total_requests: number;
  error_rate: number;
  performance: {
    avg_response_time: number;
    median_response_time: number;
    p95_response_time: number;
    max_response_time: number;
  };
}

const ANALYTICS_BASE_URL = '/api/analytics';

export async function fetchSystemHealth(): Promise<SystemHealth> {
  const res = await fetch(`${ANALYTICS_BASE_URL}/system-health`);
  if (!res.ok) throw new Error('Failed to fetch system health');
  const result = await res.json();
  return result.data;
}

export async function fetchMobileAnalytics(timeframe = '24h'): Promise<MobileAnalytics> {
  const res = await fetch(`${ANALYTICS_BASE_URL}/mobile?timeframe=${timeframe}`);
  if (!res.ok) throw new Error('Failed to fetch mobile analytics');
  const result = await res.json();
  return result.data;
}

export async function fetchRouteAnalytics(timeframe = '24h'): Promise<RouteAnalytics> {
  const res = await fetch(`${ANALYTICS_BASE_URL}/routes?timeframe=${timeframe}`);
  if (!res.ok) throw new Error('Failed to fetch route analytics');
  const result = await res.json();
  return result.data;
}

export async function fetchDriverAnalytics(timeframe = '24h'): Promise<DriverAnalytics> {
  const res = await fetch(`${ANALYTICS_BASE_URL}/drivers?timeframe=${timeframe}`);
  if (!res.ok) throw new Error('Failed to fetch driver analytics');
  const result = await res.json();
  return result.data;
}

export async function fetchAPIAnalytics(timeframe = '24h'): Promise<APIAnalytics> {
  const res = await fetch(`${ANALYTICS_BASE_URL}/api-usage?timeframe=${timeframe}`);
  if (!res.ok) throw new Error('Failed to fetch API analytics');
  const result = await res.json();
  return result.data;
}
// --- Offline Support & Background Sync ---
// Utility to queue failed requests in IndexedDB for later sync
export async function queueOfflineRequest(type: string, data: any, url: string, method: string) {
  if (!('serviceWorker' in navigator)) return;
  const registration = await navigator.serviceWorker.ready;
  registration.active?.postMessage({
    type: 'QUEUE_OFFLINE_REQUEST',
    data: { type, data, url, method }
  });
}

// Example usage in API methods (pseudo):
// try { await fetch(...); } catch (e) { await queueOfflineRequest('route-update', data, url, 'PATCH'); }
// Route Management
export interface Route {
  id: string;
  name: string;
  status: string;
}

export async function fetchRoutes(): Promise<Route[]> {
  const res = await fetch(`${API_BASE_URL}/routes`);
  if (!res.ok) throw new Error('Failed to fetch routes');
  return res.json();
}

export async function createRoute(route: Partial<Route>): Promise<Route> {
  const res = await fetch(`${API_BASE_URL}/routes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(route),
  });
  if (!res.ok) throw new Error('Failed to create route');
  return res.json();
}

export async function updateRoute(id: string, route: Partial<Route>): Promise<Route> {
  const res = await fetch(`${API_BASE_URL}/routes/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(route),
  });
  if (!res.ok) throw new Error('Failed to update route');
  return res.json();
}

export async function deleteRoute(id: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/routes/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete route');
}

// Stop Management
export async function fetchStopsForRoute(routeId: string): Promise<Stop[]> {
  const res = await fetch(`${API_BASE_URL}/routes/${routeId}/stops`);
  if (!res.ok) throw new Error('Failed to fetch stops for route');
  return res.json();
}

export async function updateStopStatus(routeId: string, stopId: string, status: Stop['status']): Promise<Stop> {
  const res = await fetch(`${API_BASE_URL}/routes/${routeId}/stops/${stopId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error('Failed to update stop status');
  return res.json();
}

// Driver Status Update
export async function updateDriverStatus(driverId: string, status: string, metadata?: Record<string, any>): Promise<{ success: boolean; status: string; updated_at: string }> {
  const res = await fetch(`${API_BASE_URL}/driver/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ driver_id: driverId, status, metadata }),
  });
  if (!res.ok) throw new Error('Failed to update driver status');
  return res.json();
}
// Session Analytics Tracking
export interface SessionData {
  device_id: string;
  app_version?: string;
  device_type?: string;
  features_used?: string[];
  api_calls?: number;
}

export async function trackSession(data: SessionData): Promise<{ success: boolean; message?: string }> {
  const res = await fetch(`${API_BASE_URL}/track/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to track session');
  return res.json();
}
// RouteForce PWA - Shared API Client

import { API_BASE_URL } from '../stores/authStore';

export interface Stop {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  status: 'pending' | 'completed' | 'current';
  estimatedTime: string;
}

export interface Vehicle {
  id: string;
  name: string;
  lat: number;
  lng: number;
  status: 'active' | 'idle' | 'maintenance';
}

export async function fetchStops(): Promise<Stop[]> {
  const res = await fetch(`${API_BASE_URL}/stops`);
  if (!res.ok) throw new Error('Failed to fetch stops');
  return res.json();
}

export async function fetchVehicles(): Promise<Vehicle[]> {
  const res = await fetch(`${API_BASE_URL}/vehicles`);
  if (!res.ok) throw new Error('Failed to fetch vehicles');
  return res.json();
}


// Telemetry
export interface Telemetry {
  id: string;
  vehicleId: string;
  timestamp: string;
  lat: number;
  lng: number;
  speed: number;
  status: string;
}

export async function fetchTelemetry(vehicleId: string): Promise<Telemetry[]> {
  const res = await fetch(`${API_BASE_URL}/vehicles/${vehicleId}/telemetry`);
  if (!res.ok) throw new Error('Failed to fetch telemetry');
  return res.json();
}

// Device Registration
export interface DeviceRegistration {
  deviceId: string;
  userId: string;
  platform: string;
  pushToken?: string;
}

export async function registerDevice(data: DeviceRegistration): Promise<{ success: boolean; message?: string }> {
  const res = await fetch(`${API_BASE_URL}/devices/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to register device');
  return res.json();
}
