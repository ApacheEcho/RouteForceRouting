export interface DashboardData {
  performance?: PerformanceData;
  mlInsights?: MLInsightsData;
  predictive?: PredictiveData;
  alerts?: AlertsData;
  optimization?: OptimizationData;
}

export interface PerformanceData {
  success: boolean;
  performance_trends?: {
    active_routes: number;
    efficiency_score: number;
    average_delivery_time: number;
    fuel_consumption: number;
    route_optimization_score: number;
    trends: {
      efficiency: Array<{ timestamp: string; value: number }>;
      delivery_time: Array<{ timestamp: string; value: number }>;
      fuel_consumption: Array<{ timestamp: string; value: number }>;
    };
  };
}

export interface MLInsightsData {
  success: boolean;
  predictions?: Array<{
    id: string;
    type: string;
    confidence: number;
    prediction: any;
    timestamp: string;
  }>;
  model_performance?: {
    accuracy: number;
    confidence_score: number;
    training_samples: number;
  };
}

export interface PredictiveData {
  success: boolean;
  demand_forecast?: Array<{
    location: string;
    predicted_demand: number;
    confidence: number;
    factors: string[];
  }>;
  capacity_optimization?: {
    current_utilization: number;
    predicted_peak: number;
    recommendations: string[];
  };
}

export interface AlertsData {
  success: boolean;
  real_time_alerts?: {
    active_alerts: Array<{
      id: string;
      type: string;
      priority: 'high' | 'medium' | 'low';
      severity?: 'critical' | 'warning' | 'info';
      title: string;
      description: string;
      action?: string;
      timestamp: string;
    }>;
    health_score: number;
    recommendations: string[];
    alert_summary: {
      total_alerts: number;
      high_priority: number;
      medium_priority: number;
      low_priority: number;
      critical_alerts?: number;
      warning_alerts?: number;
    };
  };
  timestamp?: string;
}

export interface OptimizationData {
  success: boolean;
  optimization_insights?: {
    current_efficiency: number;
    potential_improvement: number;
    cost_savings: number;
    recommendations: Array<{
      type: string;
      description: string;
      impact: string;
      priority: string;
    }>;
    algorithm_performance: {
      genetic_algorithm?: {
        generations: number;
        best_fitness: number;
        convergence_rate: number;
      };
      simulated_annealing?: {
        temperature: number;
        acceptance_rate: number;
        improvement_rate: number;
      };
    };
  };
}
