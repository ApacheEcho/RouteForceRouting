import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { MetricsGrid } from './MetricsGrid';
import { PerformanceChart } from './PerformanceChart';
import { AlertsPanel } from './AlertsPanel';
import { OptimizationInsights } from './OptimizationInsights';
import { MLInsights } from './MLInsights';
import { PredictiveAnalytics } from './PredictiveAnalytics';
import { Button } from '../ui/Button';
import { RefreshCw, Download, Settings } from 'lucide-react';
import { dashboardApi } from '../../services/api';
import { DashboardData } from '../../types/dashboard';

interface DashboardProps {
  className?: string;
}

export const Dashboard: React.FC<DashboardProps> = ({ className = '' }) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  const fetchDashboardData = async () => {
    try {
      setRefreshing(true);
      const [
        performanceData,
        mlInsights,
        predictiveData,
        alerts,
        optimizationData
      ] = await Promise.all([
        dashboardApi.getPerformanceTrends(),
        dashboardApi.getMLInsights(),
        dashboardApi.getPredictiveAnalytics(),
        dashboardApi.getRealTimeAlerts(),
        dashboardApi.getOptimizationInsights()
      ]);

      setData({
        performance: performanceData,
        mlInsights,
        predictive: predictiveData,
        alerts,
        optimization: optimizationData
      });
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const handleExportData = () => {
    if (!data) return;
    
    const exportData = {
      timestamp: new Date().toISOString(),
      dashboard_data: data
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dashboard-export-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Dashboard Error</h3>
        <p className="text-red-600 mb-4">{error}</p>
        <Button onClick={fetchDashboardData} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'performance', label: 'Performance', icon: '⚡' },
    { id: 'ml-insights', label: 'ML Insights', icon: '🤖' },
    { id: 'predictive', label: 'Predictive', icon: '🔮' },
    { id: 'optimization', label: 'Optimization', icon: '🎯' }
  ];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">RouteForce Dashboard</h1>
          <p className="text-gray-600 mt-1">Enterprise Analytics & Optimization Platform</p>
        </div>
        
        <div className="flex space-x-3">
          <Button
            onClick={fetchDashboardData}
            disabled={refreshing}
            variant="outline"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          <Button onClick={handleExportData} variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          
          <Button variant="outline">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {/* Alerts Panel */}
      {data?.alerts && (
        <AlertsPanel alerts={data.alerts} />
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {activeTab === 'overview' && data && (
          <div className="space-y-6">
            <MetricsGrid data={data} />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <PerformanceChart data={data.performance} />
              <Card>
                <CardHeader>
                  <CardTitle>Quick Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                      <span className="font-medium">Active Routes</span>
                      <span className="text-blue-600 font-bold">
                        {data.performance?.performance_trends?.active_routes || 0}
                      </span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                      <span className="font-medium">Efficiency Score</span>
                      <span className="text-green-600 font-bold">
                        {data.performance?.performance_trends?.efficiency_score?.toFixed(1) || 'N/A'}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                      <span className="font-medium">ML Predictions</span>
                      <span className="text-purple-600 font-bold">
                        {data.mlInsights?.predictions?.length || 0}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {activeTab === 'performance' && data?.performance && (
          <PerformanceChart data={data.performance} expanded />
        )}

        {activeTab === 'ml-insights' && data?.mlInsights && (
          <MLInsights data={data.mlInsights} />
        )}

        {activeTab === 'predictive' && data?.predictive && (
          <PredictiveAnalytics data={data.predictive} />
        )}

        {activeTab === 'optimization' && data?.optimization && (
          <OptimizationInsights data={data.optimization} />
        )}
      </div>
    </div>
  );
};

export default Dashboard;
