/**
 * RouteForce Mobile API Client
 * TypeScript client for RouteForce Mobile API endpoints
 */

interface ApiConfig {
  baseUrl: string;
  timeout: number;
  headers: Record<string, string>;
}

interface AuthCredentials {
  email: string;
  password: string;
}

interface AuthResponse {
  success: boolean;
  access_token: string;
  refresh_token: string;
  expires_in: number;
  driver_id: string;
}

interface Route {
  id: string;
  name: string;
  stores: Store[];
  status: 'assigned' | 'in_progress' | 'completed';
  created_at: string;
  updated_at: string;
  total_distance: number;
  estimated_duration: number;
}

interface Store {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  priority: number;
  visit_status: 'pending' | 'completed' | 'skipped';
  visit_time?: string;
}

interface LocationUpdate {
  lat: number;
  lng: number;
  accuracy: number;
  timestamp: string;
  speed?: number;
  heading?: number;
}

class RouteForceApiClient {
  private config: ApiConfig;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor(baseUrl: string = 'http://localhost:5001') {
    this.config = {
      baseUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    };
  }

  /**
   * Set authentication tokens
   */
  setTokens(accessToken: string, refreshToken: string): void {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    this.config.headers['Authorization'] = `Bearer ${accessToken}`;
  }

  /**
   * Clear authentication tokens
   */
  clearTokens(): void {
    this.accessToken = null;
    this.refreshToken = null;
    delete this.config.headers['Authorization'];
  }

  /**
   * Make HTTP request with error handling and retry logic
   */
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;
    
    const requestOptions: RequestInit = {
      ...options,
      headers: {
        ...this.config.headers,
        ...options.headers,
      },
      signal: AbortSignal.timeout(this.config.timeout),
    };

    try {
      const response = await fetch(url, requestOptions);
      
      if (response.status === 401 && this.refreshToken) {
        // Try to refresh token
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          // Retry original request with new token
          requestOptions.headers = {
            ...requestOptions.headers,
            'Authorization': `Bearer ${this.accessToken}`,
          };
          const retryResponse = await fetch(url, requestOptions);
          return await this.handleResponse<T>(retryResponse);
        }
      }

      return await this.handleResponse<T>(response);
    } catch (error) {
      throw new Error(`Network error: ${error.message}`);
    }
  }

  /**
   * Handle API response
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP ${response.status}`);
    }

    const data = await response.json();
    return data;
  }

  // Authentication Methods

  /**
   * Login with email and password
   */
  async login(credentials: AuthCredentials): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/api/mobile/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    if (response.success) {
      this.setTokens(response.access_token, response.refresh_token);
    }

    return response;
  }

  /**
   * Refresh access token
   */
  async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) {
      return false;
    }

    try {
      const response = await this.request<AuthResponse>('/api/mobile/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });

      if (response.success) {
        this.setTokens(response.access_token, response.refresh_token);
        return true;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearTokens();
    }

    return false;
  }

  /**
   * Logout and clear tokens
   */
  async logout(): Promise<void> {
    try {
      await this.request('/api/mobile/auth/logout', {
        method: 'POST',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearTokens();
    }
  }

  /**
   * Get current user profile
   */
  async getProfile(): Promise<any> {
    return this.request('/api/mobile/auth/profile');
  }

  // Route Methods

  /**
   * Get assigned routes for current driver
   */
  async getAssignedRoutes(): Promise<Route[]> {
    const response = await this.request<{ routes: Route[] }>('/api/mobile/routes/assigned');
    return response.routes;
  }

  /**
   * Get specific route details
   */
  async getRoute(routeId: string): Promise<Route> {
    return this.request<Route>(`/api/mobile/routes/${routeId}`);
  }

  /**
   * Update route status
   */
  async updateRouteStatus(routeId: string, status: string): Promise<void> {
    await this.request(`/api/mobile/routes/${routeId}/status`, {
      method: 'POST',
      body: JSON.stringify({ status }),
    });
  }

  /**
   * Mark store as visited
   */
  async markStoreVisited(routeId: string, storeId: string): Promise<void> {
    await this.request(`/api/mobile/routes/${routeId}/stores/${storeId}/visit`, {
      method: 'POST',
      body: JSON.stringify({ 
        visit_time: new Date().toISOString(),
        status: 'completed' 
      }),
    });
  }

  // Tracking Methods

  /**
   * Send location update
   */
  async updateLocation(location: LocationUpdate): Promise<void> {
    await this.request('/api/mobile/tracking/location', {
      method: 'POST',
      body: JSON.stringify(location),
    });
  }

  /**
   * Get current tracking status
   */
  async getTrackingStatus(): Promise<any> {
    return this.request('/api/mobile/tracking/status');
  }

  // Optimization Methods

  /**
   * Submit route optimization feedback
   */
  async submitOptimizationFeedback(feedback: {
    route_id: string;
    rating: number;
    comments?: string;
    alternative_suggestion?: Store[];
  }): Promise<void> {
    await this.request('/api/mobile/optimize/feedback', {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  /**
   * Get optimization suggestions
   */
  async getOptimizationSuggestions(routeId: string): Promise<any> {
    return this.request(`/api/mobile/optimize/suggestions?route_id=${routeId}`);
  }

  // Offline sync methods

  /**
   * Download route data for offline use
   */
  async downloadRouteForOffline(routeId: string): Promise<any> {
    return this.request(`/api/mobile/offline/download/${routeId}`);
  }

  /**
   * Upload cached data when back online
   */
  async syncOfflineData(data: any): Promise<void> {
    await this.request('/api/mobile/offline/sync', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.request<{ status: string }>('/api/mobile/health');
      return response.status === 'healthy';
    } catch {
      return false;
    }
  }
}

export default RouteForceApiClient;
export type { 
  ApiConfig, 
  AuthCredentials, 
  AuthResponse, 
  Route, 
  Store, 
  LocationUpdate 
};
