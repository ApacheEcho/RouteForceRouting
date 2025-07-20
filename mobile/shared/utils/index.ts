/**
 * Utility functions for RouteForce Mobile applications
 */

import { Location, Store, Route } from '../models';

// Distance and Geolocation Utilities

/**
 * Calculate distance between two locations using Haversine formula
 * @param loc1 First location
 * @param loc2 Second location
 * @returns Distance in kilometers
 */
export function calculateDistance(loc1: Location, loc2: Location): number {
  const R = 6371; // Earth's radius in kilometers
  const dLat = toRadians(loc2.lat - loc1.lat);
  const dLng = toRadians(loc2.lng - loc1.lng);
  
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(loc1.lat)) * Math.cos(toRadians(loc2.lat)) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Convert degrees to radians
 */
function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180);
}

/**
 * Calculate bearing between two locations
 * @param loc1 Start location
 * @param loc2 End location
 * @returns Bearing in degrees (0-360)
 */
export function calculateBearing(loc1: Location, loc2: Location): number {
  const dLng = toRadians(loc2.lng - loc1.lng);
  const lat1 = toRadians(loc1.lat);
  const lat2 = toRadians(loc2.lat);
  
  const y = Math.sin(dLng) * Math.cos(lat2);
  const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLng);
  
  const bearing = Math.atan2(y, x);
  return (bearing * 180 / Math.PI + 360) % 360;
}

/**
 * Get location bounds for a set of stores
 */
export function getLocationBounds(stores: Store[]): {
  north: number;
  south: number;
  east: number;
  west: number;
  center: Location;
} {
  if (stores.length === 0) {
    throw new Error('Cannot calculate bounds for empty store list');
  }

  let north = stores[0].location.lat;
  let south = stores[0].location.lat;
  let east = stores[0].location.lng;
  let west = stores[0].location.lng;

  stores.forEach(store => {
    north = Math.max(north, store.location.lat);
    south = Math.min(south, store.location.lat);
    east = Math.max(east, store.location.lng);
    west = Math.min(west, store.location.lng);
  });

  // Add padding
  const padding = 0.01; // ~1km
  north += padding;
  south -= padding;
  east += padding;
  west -= padding;

  const center: Location = {
    lat: (north + south) / 2,
    lng: (east + west) / 2,
  };

  return { north, south, east, west, center };
}

// Route Utilities

/**
 * Calculate total distance for a route
 */
export function calculateRouteDistance(stores: Store[]): number {
  if (stores.length < 2) return 0;
  
  let totalDistance = 0;
  for (let i = 0; i < stores.length - 1; i++) {
    totalDistance += calculateDistance(stores[i].location, stores[i + 1].location);
  }
  
  return totalDistance;
}

/**
 * Calculate estimated travel time between locations
 * @param distance Distance in kilometers
 * @param averageSpeed Average speed in km/h (default: 50)
 * @returns Time in minutes
 */
export function calculateTravelTime(distance: number, averageSpeed: number = 50): number {
  return (distance / averageSpeed) * 60;
}

/**
 * Calculate route progress percentage
 */
export function calculateRouteProgress(route: Route): number {
  const completedStores = route.stores.filter(store => store.visit_status === 'completed').length;
  return route.stores.length > 0 ? (completedStores / route.stores.length) * 100 : 0;
}

/**
 * Get next unvisited store in route
 */
export function getNextStore(route: Route): Store | null {
  return route.stores.find(store => 
    store.visit_status === 'pending' || store.visit_status === 'in_progress'
  ) || null;
}

/**
 * Sort stores by distance from current location
 */
export function sortStoresByDistance(stores: Store[], currentLocation: Location): Store[] {
  return [...stores].sort((a, b) => {
    const distanceA = calculateDistance(currentLocation, a.location);
    const distanceB = calculateDistance(currentLocation, b.location);
    return distanceA - distanceB;
  });
}

// Time and Date Utilities

/**
 * Format duration in minutes to human readable format
 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${Math.round(minutes)}m`;
  }
  
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  
  if (mins === 0) {
    return `${hours}h`;
  }
  
  return `${hours}h ${mins}m`;
}

/**
 * Format distance to human readable format
 */
export function formatDistance(kilometers: number): string {
  if (kilometers < 1) {
    return `${Math.round(kilometers * 1000)}m`;
  }
  
  return `${kilometers.toFixed(1)}km`;
}

/**
 * Calculate ETA based on current time and duration
 */
export function calculateETA(durationMinutes: number): Date {
  const now = new Date();
  return new Date(now.getTime() + durationMinutes * 60000);
}

/**
 * Format ETA to time string
 */
export function formatETA(eta: Date): string {
  return eta.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Check if time is within business hours
 */
export function isWithinBusinessHours(
  time: Date = new Date(),
  startHour: number = 9,
  endHour: number = 17
): boolean {
  const hour = time.getHours();
  return hour >= startHour && hour < endHour;
}

// Storage Utilities

/**
 * Store data in local storage with expiration
 */
export function setStorageItem(key: string, data: any, expirationHours: number = 24): void {
  const item = {
    data,
    timestamp: Date.now(),
    expiration: Date.now() + (expirationHours * 60 * 60 * 1000),
  };
  
  try {
    localStorage.setItem(key, JSON.stringify(item));
  } catch (error) {
    console.warn('Failed to store data in localStorage:', error);
  }
}

/**
 * Get data from local storage, checking expiration
 */
export function getStorageItem<T>(key: string): T | null {
  try {
    const item = localStorage.getItem(key);
    if (!item) return null;
    
    const parsed = JSON.parse(item);
    
    if (parsed.expiration && Date.now() > parsed.expiration) {
      localStorage.removeItem(key);
      return null;
    }
    
    return parsed.data;
  } catch (error) {
    console.warn('Failed to retrieve data from localStorage:', error);
    return null;
  }
}

/**
 * Clear expired items from local storage
 */
export function clearExpiredStorage(): void {
  const keys = Object.keys(localStorage);
  
  keys.forEach(key => {
    try {
      const item = localStorage.getItem(key);
      if (item) {
        const parsed = JSON.parse(item);
        if (parsed.expiration && Date.now() > parsed.expiration) {
          localStorage.removeItem(key);
        }
      }
    } catch (error) {
      // Invalid JSON, remove it
      localStorage.removeItem(key);
    }
  });
}

// Validation Utilities

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate phone number format (basic)
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
  return phoneRegex.test(phone);
}

/**
 * Check if location is valid coordinates
 */
export function isValidCoordinates(lat: number, lng: number): boolean {
  return (
    typeof lat === 'number' &&
    typeof lng === 'number' &&
    lat >= -90 && lat <= 90 &&
    lng >= -180 && lng <= 180 &&
    !isNaN(lat) && !isNaN(lng)
  );
}

// Network Utilities

/**
 * Check if device is online
 */
export function isOnline(): boolean {
  return navigator.onLine;
}

/**
 * Wait for network connection
 */
export function waitForOnline(timeoutMs: number = 30000): Promise<boolean> {
  return new Promise((resolve) => {
    if (isOnline()) {
      resolve(true);
      return;
    }

    const timeout = setTimeout(() => {
      window.removeEventListener('online', onlineHandler);
      resolve(false);
    }, timeoutMs);

    const onlineHandler = () => {
      clearTimeout(timeout);
      window.removeEventListener('online', onlineHandler);
      resolve(true);
    };

    window.addEventListener('online', onlineHandler);
  });
}

/**
 * Retry function with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelayMs: number = 1000
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt === maxRetries) {
        throw lastError;
      }

      const delay = baseDelayMs * Math.pow(2, attempt);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError!;
}

// Debounce utility
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  waitMs: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), waitMs);
  };
}

// Throttle utility
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limitMs: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limitMs);
    }
  };
}

// Generate unique ID
export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Deep clone object
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as unknown as T;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item)) as unknown as T;
  }
  
  const cloned = {} as T;
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloned[key] = deepClone(obj[key]);
    }
  }
  
  return cloned;
}
