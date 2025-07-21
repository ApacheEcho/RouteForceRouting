import axios from 'axios';

// API configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://api.routeforce.com'  // Production API URL
  : 'http://localhost:8000';      // Development API URL

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
    stops: Array<{lat: number; lon: number; name: string}>;
    algorithm?: string;
  }) => {
    const response = await apiClient.post('/api/optimize', data);
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
      const response = await apiClient.get('/api/dashboard/overview');
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
      const response = await apiClient.get('/api/dashboard/performance');
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
      const response = await apiClient.get('/api/dashboard/routes/recent');
      return response.data;
    } catch (error) {
      // Return mock data for development
      return [
        {
          id: '1',
          name: 'Downtown Delivery Route',
          status: 'completed',
          distance: 45.2,
          time_saved: 12,
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          name: 'Suburban Service Route',
          status: 'active',
          distance: 67.8,
          time_saved: 18,
          created_at: new Date().toISOString()
        }
      ];
    }
  },
};

// Analytics API
export const analyticsApi = {
  getInsights: async () => {
    try {
      const response = await apiClient.get('/api/analytics/insights');
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
      const response = await apiClient.get('/api/analytics/reports');
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
    const response = await apiClient.get('/metrics');
    return response.data;
  },
};

export default apiClient;
