/**
 * RouteForce Shared API Client
 * TypeScript client for both React Native and PWA
 */

// Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  token: string;
}

export interface Route {
  id: string;
  name: string;
  status: 'active' | 'completed' | 'planned';
  distance: string;
  duration: string;
  stops: number;
  efficiency: number;
  lastUpdated: string;
  coordinates?: [number, number][];
}

export interface Stop {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  status: 'pending' | 'completed' | 'current';
  estimatedTime: string;
  actualTime?: string;
}

export interface Vehicle {
  id: string;
  name: string;
  lat: number;
  lng: number;
  status: 'active' | 'idle' | 'maintenance';
  speed?: number;
}

export interface OptimizationRequest {
  algorithm: 'genetic' | 'simulated_annealing' | 'nearest_neighbor';
  stores: Array<{
    name: string;
    address: string;
    lat?: number;
    lng?: number;
  }>;
  depot?: {
    name: string;
    address: string;
    lat?: number;
    lng?: number;
  };
  parameters?: {
    population_size?: number;
    generations?: number;
    mutation_rate?: number;
    crossover_rate?: number;
    temperature?: number;
    cooling_rate?: number;
  };
}

export interface OptimizationResponse {
  route: Route;
  stops: Stop[];
  metadata: {
    algorithm: string;
    total_distance: number;
    estimated_time: number;
    optimization_time: number;
    efficiency_score: number;
  };
}

// API Client Class
export class RouteForceAPI {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = 'http://localhost:5000/api') {
    this.baseURL = baseURL;
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        message: response.statusText,
      }));
      throw new Error(errorData.message || 'Request failed');
    }

    return response.json();
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.request<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    this.setToken(response.token);
    return response;
  }

  async logout(): Promise<void> {
    await this.request('/auth/logout', {
      method: 'POST',
    });
    this.clearToken();
  }

  async validateToken(): Promise<User> {
    return this.request<User>('/auth/validate');
  }

  // Routes
  async getRoutes(): Promise<Route[]> {
    return this.request<Route[]>('/routes');
  }

  async getRoute(id: string): Promise<Route> {
    return this.request<Route>(`/routes/${id}`);
  }

  async createRoute(route: Partial<Route>): Promise<Route> {
    return this.request<Route>('/routes', {
      method: 'POST',
      body: JSON.stringify(route),
    });
  }

  async updateRoute(id: string, route: Partial<Route>): Promise<Route> {
    return this.request<Route>(`/routes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(route),
    });
  }

  async deleteRoute(id: string): Promise<void> {
    await this.request(`/routes/${id}`, {
      method: 'DELETE',
    });
  }

  // Route Optimization
  async optimizeRoute(request: OptimizationRequest): Promise<OptimizationResponse> {
    return this.request<OptimizationResponse>('/routes/optimize', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Stops
  async getStops(routeId: string): Promise<Stop[]> {
    return this.request<Stop[]>(`/routes/${routeId}/stops`);
  }

  async updateStop(routeId: string, stopId: string, status: Stop['status']): Promise<Stop> {
    return this.request<Stop>(`/routes/${routeId}/stops/${stopId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }

  // Vehicles
  async getVehicles(): Promise<Vehicle[]> {
    return this.request<Vehicle[]>('/vehicles');
  }

  async getVehicle(id: string): Promise<Vehicle> {
    return this.request<Vehicle>(`/vehicles/${id}`);
  }

  async updateVehicleLocation(id: string, lat: number, lng: number): Promise<Vehicle> {
    return this.request<Vehicle>(`/vehicles/${id}/location`, {
      method: 'PATCH',
      body: JSON.stringify({ lat, lng }),
    });
  }

  // Analytics
  async getDashboardStats(): Promise<{
    activeRoutes: number;
    totalDistance: string;
    avgTimeSaved: string;
    costSavings: string;
  }> {
    return this.request('/analytics/dashboard');
  }

  async getRouteAnalytics(routeId: string): Promise<{
    efficiency: number;
    completionTime: number;
    fuelConsumption: number;
    emissions: number;
  }> {
    return this.request(`/analytics/routes/${routeId}`);
  }

  // Real-time tracking
  async getTrackingData(vehicleId: string): Promise<{
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
  }> {
    return this.request(`/tracking/${vehicleId}`);
  }
}

// Default API instance
export const apiClient = new RouteForceAPI();

// Utility functions
export const formatDistance = (meters: number): string => {
  if (meters < 1000) {
    return `${Math.round(meters)} m`;
  }
  return `${(meters / 1000).toFixed(1)} km`;
};

export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
};

export const formatDateTime = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString();
};

export const calculateEfficiency = (
  actualDistance: number,
  optimalDistance: number
): number => {
  return Math.round((optimalDistance / actualDistance) * 100);
};

// Error handling utilities
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export const handleAPIError = (error: unknown): string => {
  if (error instanceof APIError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

export default RouteForceAPI;
