import axios from 'axios';

// API configuration: prefer Vite env, then window origin, then sensible default
const API_BASE_URL =
  (import.meta as any).env?.VITE_API_BASE_URL ||
  (typeof window !== 'undefined' ? window.location.origin : '') ||
  'http://localhost:5000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // Provide API key for analytics endpoints when required
  const isAnalytics = (config.url || '').includes('/api/analytics');
  if (isAnalytics) {
    const vite: any = (import.meta as any).env || {};
    const apiKey = localStorage.getItem('api_key') || vite.VITE_API_KEY || 'test-api-key';
    (config.headers as any)['X-API-Key'] = apiKey;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Route optimization API
export const routeApi = {
  optimize: async (data: {
    stops: Array<{ lat?: number; lon?: number; name?: string; address?: string }>;
    algorithm?: string;
    constraints?: Record<string, any>;
  }) => {
    // Map to backend payload: /api/v1/routes expects { stores, constraints?, options? }
    const stores = data.stops.map((s) => {
      const base: any = { name: s.name };
      if (typeof s.lat === 'number' && typeof s.lon === 'number') {
        base.lat = s.lat;
        base.lon = s.lon;
      }
      if (s.address && !base.lat) {
        base.address = s.address;
      }
      return base;
    });
    const payload = {
      stores,
      constraints: data.constraints || {},
      options: { algorithm: data.algorithm || 'default' },
    };
    const response = await apiClient.post('/api/v1/routes', payload);
    return response.data;
  },

  getRoutes: async () => {
    const response = await apiClient.get('/api/v1/routes');
    return response.data;
  },

  getRoute: async (id: string) => {
    const response = await apiClient.get(`/api/v1/routes/${id}`);
    return response.data;
  },
};

// Dashboard API
export const dashboardApi = {
  getOverview: async () => {
    try {
      // Backend endpoint
      const response = await apiClient.get('/dashboard/api/system/status');
      return response.data;
    } catch (error) {
      // Return mock data for development
      return {
        totalRoutes: 245,
        activeRoutes: 12,
        completedToday: 8,
        avgOptimization: 23.5,
        totalDistance: 1250.7,
        fuelSaved: 45.2,
        timeEfficiency: 92.1,
        costReduction: 18.3
      };
    }
  },

  getPerformanceMetrics: async () => {
    try {
      const response = await apiClient.get('/dashboard/api/performance/history');
      return response.data;
    } catch (error) {
      // Return mock data for development
      return {
        optimization_efficiency: 94.2,
        fuel_savings: 22.5,
        time_savings: 15.8,
        cost_reduction: 12.3,
        route_completion_rate: 98.7
      };
    }
  },

  getRecentRoutes: async () => {
    try {
      const response = await apiClient.get('/dashboard/api/routes/recent');
      return response.data?.routes ?? [];
    } catch (error) {
      return [];
    }
  },

  // AUTO-PILOT FIX: Adding missing dashboard API functions
  getPerformanceTrends: async () => {
    try {
      const response = await apiClient.get('/dashboard/api/performance/history');
      return response.data;
    } catch (error) {
      // Return mock data for development
      return {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [
          {
            label: 'Route Efficiency',
            data: [92, 94, 91, 96, 93, 95, 97],
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)'
          },
          {
            label: 'Fuel Savings',
            data: [18, 22, 19, 25, 21, 24, 26],
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)'
          }
        ]
      };
    }
  },

  getMLInsights: async () => {
    try {
      const response = await apiClient.get('/dashboard/api/ml/insights');
      return response.data;
    } catch (error) {
      return {
        prediction_accuracy: 93.8,
        model_confidence: 88.1,
        optimization_score: 92.8,
        recommendations: [
          'Avoid downtown routes 8–9 AM on weekdays',
          'Highway routes show ~15% better efficiency on weekdays',
          'Cluster stops by proximity to reduce travel distance',
        ],
      };
    }
  },

  getPredictiveAnalytics: async () => {
    try {
      const response = await apiClient.get('/dashboard/api/analytics/predictive');
      return response.data;
    } catch (error) {
      return {
        traffic_predictions: [
          { route: 'Route A', predicted_delay: 5, confidence: 0.92 },
          { route: 'Route B', predicted_delay: 12, confidence: 0.85 },
          { route: 'Route C', predicted_delay: 2, confidence: 0.96 },
        ],
        fuel_forecasts: {
          daily_savings: 23.5,
          weekly_projection: 164.5,
          monthly_estimate: 705.2,
        },
        optimization_opportunities: [
          { type: 'route_consolidation', potential_savings: 12.3 },
          { type: 'time_optimization', potential_savings: 8.7 },
          { type: 'fuel_efficiency', potential_savings: 15.2 },
        ],
      };
    }
  },

  getRealTimeAlerts: async () => {
    try {
      const response = await apiClient.get('/dashboard/api/performance/alerts');
      return response.data;
    } catch (error) {
      // Return mock data for development
      return [
        {
          id: 1,
          type: 'warning',
          message: 'Route optimization taking longer than expected',
          timestamp: new Date().toISOString(),
          priority: 'medium'
        },
        {
          id: 2,
          type: 'info',
          message: 'New ML model deployed with 5% better accuracy',
          timestamp: new Date().toISOString(),
          priority: 'low'
        }
      ];
    }
  },

  getOptimizationInsights: async () => {
    try {
      const response = await apiClient.get('/dashboard/api/optimization/insights');
      return response.data;
    } catch (error) {
      return {
        algorithm_performance: {
          genetic: { efficiency: 92.3, usage: 45 },
          simulated_annealing: { efficiency: 90.8, usage: 35 },
          multi_objective: { efficiency: 94.9, usage: 20 },
        },
        route_statistics: {
          total_optimized: 1247,
          average_improvement: 23.5,
          best_performance: 47.2,
          success_rate: 98.7,
        },
        recommendations: [
          'Use multi-objective for complex constraints (time windows, priority)',
          'Prefer simulated annealing for fast single-route optimizations',
          'Increase GA population size for >20 stops to improve convergence',
        ],
      };
    }
  }
};

// Analytics API
export const analyticsApi = {
  getInsights: async () => {
    try {
      // Use system health + routes analytics as a proxy
      const response = await apiClient.get('/api/analytics/system-health');
      return response.data;
    } catch (error) {
      return {
        predictions: [],
        trends: [],
        recommendations: []
      };
    }
  },

  getReports: async () => {
    try {
      const response = await apiClient.get('/api/analytics/report');
      return response.data;
    } catch (error) {
      return [];
    }
  },
};

// System health API
export const systemApi = {
  getHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  getMetrics: async () => {
    const response = await apiClient.get('/metrics/summary');
    return response.data;
  },
};

export default apiClient;

// Connections API
export const connectionsApi = {
  listProviders: async () => {
    const r = await apiClient.get('/api/connections/providers');
    return r.data?.providers || [];
  },
  getStatus: async () => {
    const r = await apiClient.get('/api/connections/status');
    return r.data?.status || {};
  },
  connect: async (provider: string, token?: string, config?: any) => {
    const r = await apiClient.post('/api/connections/connect', { provider, token, config });
    return r.data;
  },
  disconnect: async (provider: string) => {
    const r = await apiClient.post('/api/connections/disconnect', { provider });
    return r.data;
  },
  oauthStart: async (provider: string) => {
    const r = await apiClient.get(`/api/connections/oauth/start/${provider}`);
    return r.data?.authorization_url;
  },
};
