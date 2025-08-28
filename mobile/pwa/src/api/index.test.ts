import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

describe('API Functionality', () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it('fetchRoutes returns data on success', async () => {
    const mockRoutes = [{ id: '1', name: 'Route 1', status: 'active' }];
    global.fetch = vi.fn(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve(mockRoutes)
    })) as any;
    const result = await fetchRoutes();
    expect(result).toEqual(mockRoutes);
    expect(global.fetch).toHaveBeenCalled();
  });

  it('fetchRoutes throws on error', async () => {
    global.fetch = vi.fn(() => Promise.resolve({ ok: false })) as any;
    await expect(fetchRoutes()).rejects.toThrow('Failed to fetch routes');
  });

  it('createRoute returns created route on success', async () => {
    const newRoute = { name: 'New Route' };
    const createdRoute = { id: '2', name: 'New Route', status: 'active' };
    global.fetch = vi.fn(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve(createdRoute)
    })) as any;
    const result = await createRoute(newRoute);
    expect(result).toEqual(createdRoute);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/routes'),
      expect.objectContaining({ method: 'POST' })
    );
  });

  it('createRoute throws on error', async () => {
    global.fetch = vi.fn(() => Promise.resolve({ ok: false })) as any;
    await expect(createRoute({ name: 'fail' })).rejects.toThrow('Failed to create route');
  });
});

import {
  fetchRoutes,
  createRoute,
  updateRoute,
  deleteRoute,
  fetchStopsForRoute,
  updateStopStatus,
  updateDriverStatus,
  queueOfflineRequest,
  fetchSystemHealth,
  fetchMobileAnalytics,
  fetchRouteAnalytics,
  fetchDriverAnalytics,
  fetchAPIAnalytics,
  fetchStops,
  fetchVehicles,
  fetchTelemetry,
  registerDevice,
  trackSession
} from './index';
describe('Analytics API', () => {
  afterEach(() => { vi.restoreAllMocks(); });
  it('fetchSystemHealth returns data', async () => {
    const mockData = { data: { health_score: 99, status: 'ok', uptime: '1d', active_sessions: 2 } };
    global.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(mockData) })) as any;
    const result = await fetchSystemHealth();
    expect(result).toEqual(mockData.data);
  });
  it('fetchSystemHealth throws on error', async () => {
    global.fetch = vi.fn(() => Promise.resolve({ ok: false })) as any;
    await expect(fetchSystemHealth()).rejects.toThrow('Failed to fetch system health');
  });
  it('fetchMobileAnalytics returns data', async () => {
    const mockData = { data: { total_sessions: 1, unique_devices: 1, total_api_calls: 1, device_types: {} } };
    global.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(mockData) })) as any;
    const result = await fetchMobileAnalytics();
    expect(result).toEqual(mockData.data);
  });
  it('fetchRouteAnalytics returns data', async () => {
    const mockData = { data: { total_routes: 1, success_rate: 1, avg_optimization_time: 1, algorithm_usage: {} } };
    global.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(mockData) })) as any;
    const result = await fetchRouteAnalytics();
    expect(result).toEqual(mockData.data);
  });
  it('fetchDriverAnalytics returns data', async () => {
    const mockData = { data: { total_drivers: 1, avg_customer_rating: 5, total_location_updates: 1, top_performers: [] } };
    global.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(mockData) })) as any;
    const result = await fetchDriverAnalytics();
    expect(result).toEqual(mockData.data);
  });
  it('fetchAPIAnalytics returns data', async () => {
    const mockData = { data: { total_requests: 1, error_rate: 0, performance: { avg_response_time: 1, median_response_time: 1, p95_response_time: 1, max_response_time: 1 } } };
    global.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(mockData) })) as any;
    const result = await fetchAPIAnalytics();
    expect(result).toEqual(mockData.data);
  });
});

describe('Stops, Vehicles, Telemetry, Device APIs', () => {
  afterEach(() => { vi.restoreAllMocks(); });
  it('fetchStops returns data', async () => {
    const mockStops = [{ id: '1', name: 'Stop', address: '', lat: 0, lng: 0, status: 'pending', estimatedTime: '' }];
    global.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(mockStops) })) as any;
    const result = await fetchStops();
    expect(result).toEqual(mockStops);
  });
  it('fetchVehicles returns data', async () => {
    const mockVehicles = [{ id: '1', name: 'V', lat: 0, lng: 0, status: 'active' }];
    global.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(mockVehicles) })) as any;
    const result = await fetchVehicles();
    expect(result).toEqual(mockVehicles);
  });
  it('fetchTelemetry returns data', async () => {
    const mockTelemetry = [{ id: '1', vehicleId: '1', timestamp: '', lat: 0, lng: 0, speed: 0, status: '' }];
    global.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(mockTelemetry) })) as any;
    const result = await fetchTelemetry('1');
    expect(result).toEqual(mockTelemetry);
  });
  it('registerDevice returns data', async () => {
    const mockResp = { success: true };
    global.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(mockResp) })) as any;
    const result = await registerDevice({ deviceId: 'd', userId: 'u', platform: 'p' });
    expect(result).toEqual(mockResp);
  });
  it('trackSession returns data', async () => {
    const mockResp = { success: true };
    global.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(mockResp) })) as any;
    const result = await trackSession({ device_id: 'd' });
    expect(result).toEqual(mockResp);
  });
});

describe('queueOfflineRequest', () => {
  it('posts message to service worker if available', async () => {
    const postMessage = vi.fn();
    const ready = Promise.resolve({ active: { postMessage } });
    Object.defineProperty(global.navigator, 'serviceWorker', {
      value: { ready }, configurable: true
    });
    await queueOfflineRequest('type', { foo: 1 }, '/url', 'POST');
    expect(postMessage).toHaveBeenCalledWith({
      type: 'QUEUE_OFFLINE_REQUEST',
      data: { type: 'type', data: { foo: 1 }, url: '/url', method: 'POST' }
    });
  });
  it('does nothing if serviceWorker not in navigator', async () => {
    Object.defineProperty(global.navigator, 'serviceWorker', { value: undefined, configurable: true });
    await expect(queueOfflineRequest('type', {}, '/url', 'POST')).resolves.toBeUndefined();
  });
});
import { vi } from 'vitest';

describe('API Exports', () => {
  it('should export fetchRoutes', () => {
    expect(typeof fetchRoutes).toBe('function');
  });
  it('should export createRoute', () => {
    expect(typeof createRoute).toBe('function');
  });
  it('should export updateRoute', () => {
    expect(typeof updateRoute).toBe('function');
  });
  it('should export deleteRoute', () => {
    expect(typeof deleteRoute).toBe('function');
  });
  it('should export fetchStopsForRoute', () => {
    expect(typeof fetchStopsForRoute).toBe('function');
  });
  it('should export updateStopStatus', () => {
    expect(typeof updateStopStatus).toBe('function');
  });
  it('should export updateDriverStatus', () => {
    expect(typeof updateDriverStatus).toBe('function');
  });
  it('should export queueOfflineRequest', () => {
    expect(typeof queueOfflineRequest).toBe('function');
  });
});


