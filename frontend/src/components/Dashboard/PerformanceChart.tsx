import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { PerformanceData } from '../../types/dashboard';

interface PerformanceChartProps {
  data: PerformanceData;
  expanded?: boolean;
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({ data, expanded = false }) => {
  if (!data?.performance_trends?.trends) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Performance Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-gray-500">
            No performance data available
          </div>
        </CardContent>
      </Card>
    );
  }

  const { trends } = data.performance_trends;
  
  // Combine all trends data
  const chartData = trends.efficiency.map((item, index) => ({
    timestamp: new Date(item.timestamp).toLocaleDateString(),
    efficiency: item.value,
    deliveryTime: trends.delivery_time[index]?.value || 0,
    fuelConsumption: trends.fuel_consumption[index]?.value || 0
  }));

  if (expanded) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Efficiency Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="efficiency" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Delivery Time Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="deliveryTime" stroke="#10B981" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Fuel Consumption</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="fuelConsumption" stroke="#F59E0B" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Performance Trends</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="efficiency" stroke="#3B82F6" strokeWidth={2} name="Efficiency %" />
            <Line type="monotone" dataKey="deliveryTime" stroke="#10B981" strokeWidth={2} name="Delivery Time (h)" />
            <Line type="monotone" dataKey="fuelConsumption" stroke="#F59E0B" strokeWidth={2} name="Fuel Usage" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
