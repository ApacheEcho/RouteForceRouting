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
  queueOfflineRequest
} from './index';
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


