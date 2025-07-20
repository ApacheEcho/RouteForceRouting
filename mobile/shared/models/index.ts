/**
 * Core data models for RouteForce Mobile applications
 */

// User and Authentication Models
export interface Driver {
  id: string;
  email: string;
  name: string;
  phone?: string;
  vehicle_info?: VehicleInfo;
  status: 'active' | 'inactive' | 'on_route';
  created_at: string;
  last_active: string;
}

export interface VehicleInfo {
  make: string;
  model: string;
  year: number;
  license_plate: string;
  capacity_weight?: number;
  capacity_volume?: number;
}

// Location and Geography Models
export interface Location {
  lat: number;
  lng: number;
  accuracy?: number;
  timestamp?: string;
}

export interface Address {
  street: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  formatted_address?: string;
}

// Store and Route Models
export interface Store {
  id: string;
  name: string;
  address: string;
  location: Location;
  priority: number;
  estimated_service_time: number; // minutes
  visit_status: 'pending' | 'in_progress' | 'completed' | 'skipped';
  visit_time?: string;
  notes?: string;
  contact_info?: ContactInfo;
}

export interface ContactInfo {
  phone?: string;
  email?: string;
  contact_person?: string;
}

export interface Route {
  id: string;
  name: string;
  description?: string;
  stores: Store[];
  driver_id?: string;
  status: 'draft' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
  scheduled_start?: string;
  actual_start?: string;
  completed_at?: string;
  metadata: RouteMetadata;
}

export interface RouteMetadata {
  total_distance: number; // km
  estimated_duration: number; // minutes
  actual_duration?: number; // minutes
  total_stores: number;
  completed_stores: number;
  optimization_algorithm?: string;
  optimization_score?: number;
}

// Navigation and Tracking Models
export interface NavigationStep {
  instruction: string;
  distance: number; // meters
  duration: number; // seconds
  start_location: Location;
  end_location: Location;
  maneuver: string;
}

export interface RouteProgress {
  route_id: string;
  current_store_index: number;
  current_store?: Store;
  next_store?: Store;
  completed_stores: Store[];
  remaining_stores: Store[];
  current_location?: Location;
  eta_next_store?: string;
  eta_completion?: string;
  distance_remaining: number;
  time_remaining: number;
}

// API Response Models
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    per_page: number;
    total_pages: number;
    total_items: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

// Authentication Models
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: 'Bearer';
}

export interface LoginCredentials {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface AuthState {
  isAuthenticated: boolean;
  driver?: Driver;
  tokens?: AuthTokens;
  last_login?: string;
}

// Optimization Models
export interface OptimizationRequest {
  stores: Store[];
  start_location?: Location;
  algorithm?: 'default' | 'genetic' | 'simulated_annealing' | 'multi_objective';
  constraints?: OptimizationConstraints;
}

export interface OptimizationConstraints {
  max_duration?: number; // minutes
  max_distance?: number; // km
  vehicle_capacity?: number;
  time_windows?: TimeWindow[];
  avoid_tolls?: boolean;
  avoid_highways?: boolean;
}

export interface TimeWindow {
  store_id: string;
  start_time: string;
  end_time: string;
}

export interface OptimizationResult {
  optimized_route: Store[];
  original_distance: number;
  optimized_distance: number;
  improvement_percent: number;
  processing_time: number;
  algorithm_used: string;
  optimization_score: number;
}

// Notification Models
export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  data?: any;
  read: boolean;
  created_at: string;
  expires_at?: string;
}

// Settings Models
export interface AppSettings {
  theme: 'light' | 'dark' | 'auto';
  notifications_enabled: boolean;
  location_tracking: boolean;
  offline_maps: boolean;
  auto_sync: boolean;
  sound_enabled: boolean;
  voice_navigation: boolean;
  language: string;
  units: 'metric' | 'imperial';
}

// Offline Storage Models
export interface OfflineData {
  routes: Route[];
  stores: Store[];
  cached_maps: CachedMap[];
  pending_syncs: PendingSync[];
  last_sync: string;
}

export interface CachedMap {
  bounds: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
  zoom_level: number;
  cached_at: string;
  size_mb: number;
}

export interface PendingSync {
  id: string;
  type: 'location_update' | 'store_visit' | 'route_status' | 'feedback';
  data: any;
  created_at: string;
  attempts: number;
}

// Error Models
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
  user_action?: string;
}

// Analytics Models
export interface DriverPerformance {
  driver_id: string;
  period: 'day' | 'week' | 'month';
  routes_completed: number;
  total_distance: number;
  total_time: number;
  average_stops_per_hour: number;
  fuel_efficiency?: number;
  customer_ratings?: number;
  on_time_percentage: number;
}

// Utility Types
export type RouteSortBy = 'created_at' | 'scheduled_start' | 'priority' | 'distance';
export type RouteSortOrder = 'asc' | 'desc';
export type StoreStatus = Store['visit_status'];
export type RouteStatus = Route['status'];
export type NotificationType = Notification['type'];

// Default values and constants
export const DEFAULT_LOCATION: Location = {
  lat: 37.7749,
  lng: -122.4194, // San Francisco
};

export const ROUTE_STATUS_COLORS = {
  draft: '#6b7280',
  assigned: '#3b82f6',
  in_progress: '#f59e0b',
  completed: '#10b981',
  cancelled: '#ef4444',
} as const;

export const STORE_STATUS_COLORS = {
  pending: '#6b7280',
  in_progress: '#f59e0b',
  completed: '#10b981',
  skipped: '#ef4444',
} as const;

// Validation helpers
export const isValidLocation = (location: any): location is Location => {
  return (
    typeof location === 'object' &&
    typeof location.lat === 'number' &&
    typeof location.lng === 'number' &&
    location.lat >= -90 &&
    location.lat <= 90 &&
    location.lng >= -180 &&
    location.lng <= 180
  );
};

export const isValidStore = (store: any): store is Store => {
  return (
    typeof store === 'object' &&
    typeof store.id === 'string' &&
    typeof store.name === 'string' &&
    typeof store.address === 'string' &&
    isValidLocation(store.location) &&
    typeof store.priority === 'number'
  );
};

export const isValidRoute = (route: any): route is Route => {
  return (
    typeof route === 'object' &&
    typeof route.id === 'string' &&
    typeof route.name === 'string' &&
    Array.isArray(route.stores) &&
    route.stores.every(isValidStore) &&
    ['draft', 'assigned', 'in_progress', 'completed', 'cancelled'].includes(route.status)
  );
};
