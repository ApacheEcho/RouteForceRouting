import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { DashboardData } from '../../types/dashboard';

interface MetricsGridProps {
  data: DashboardData;
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ data }) => {
  const metrics = [
    {
      title: 'Active Routes',
      value: data.performance?.performance_trends?.active_routes || 0,
      change: '+12%',
      changeType: 'positive' as const,
      icon: '🚛'
    },
    {
      title: 'Efficiency Score',
      value: `${data.performance?.performance_trends?.efficiency_score?.toFixed(1) || 0}%`,
      change: '+5.2%',
      changeType: 'positive' as const,
      icon: '⚡'
    },
    {
      title: 'Avg Delivery Time',
      value: `${data.performance?.performance_trends?.average_delivery_time?.toFixed(1) || 0}h`,
      change: '-8.3%',
      changeType: 'positive' as const,
      icon: '⏱️'
    },
    {
      title: 'Fuel Savings',
      value: `${((data.performance?.performance_trends?.fuel_consumption || 0) * 0.1).toFixed(1)}%`,
      change: '+15.7%',
      changeType: 'positive' as const,
      icon: '⛽'
    },
    {
      title: 'ML Predictions',
      value: data.mlInsights?.predictions?.length || 0,
      change: '+23%',
      changeType: 'positive' as const,
      icon: '🤖'
    },
    {
      title: 'Active Alerts',
      value: data.alerts?.real_time_alerts?.alert_summary?.total_alerts || 0,
      change: data.alerts?.real_time_alerts?.alert_summary?.critical_alerts ? '-2' : '0',
      changeType: (data.alerts?.real_time_alerts?.alert_summary?.critical_alerts || 0) > 0 ? 'negative' : 'neutral' as const,
      icon: '🚨'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 4k:grid-cols-8 8k:grid-cols-12 gap-4">
      {metrics.map((metric, index) => (
        <Card key={index} className="hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                <p className={`text-xs font-medium ${
                  metric.changeType === 'positive' ? 'text-green-600' :
                  metric.changeType === 'negative' ? 'text-red-600' :
                  'text-gray-600'
                }`}>
                  {metric.change}
                </p>
              </div>
              <div className="text-2xl">{metric.icon}</div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
