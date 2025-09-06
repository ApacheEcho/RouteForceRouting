import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import Skeleton from '../ui/Skeleton';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { PerformanceData } from '../../types/dashboard';

interface PerformanceChartProps {
  data: PerformanceData;
  expanded?: boolean;
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({ data, expanded = false }) => {
  const reduceMotion = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const lowPower = typeof navigator !== 'undefined' && (navigator as any).hardwareConcurrency && (navigator as any).hardwareConcurrency <= 4;
  const enableAnim = !(reduceMotion || lowPower);
  if (!data?.performance_trends?.trends) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Performance Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4" aria-busy="true" aria-live="polite">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-48 w-full" />
            <div className="grid grid-cols-3 gap-3">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
            </div>
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
    // Compute a simple efficiency index combining efficiency and fuel usage (for display only)
    const indexData = chartData.map(d => ({
      timestamp: d.timestamp,
      index: Number((d.efficiency - 0.2 * d.fuelConsumption).toFixed(2)),
    }));

    return (
      <div className="rf-grid-gap grid grid-cols-1 lg:grid-cols-2 3xl:grid-cols-3 8k:grid-cols-4">
        <Card>
          <CardHeader>
            <CardTitle>Efficiency Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <figure aria-label="Efficiency trends over time">
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="efficiency" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} isAnimationActive={enableAnim} animationDuration={300} />
                </AreaChart>
              </ResponsiveContainer>
              <figcaption className="sr-only">Shows efficiency percentage across dates.</figcaption>
            </figure>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Delivery Time Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <figure aria-label="Delivery time trends over time">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="deliveryTime" stroke="#10B981" strokeWidth={2} isAnimationActive={enableAnim} animationDuration={300} />
                </LineChart>
              </ResponsiveContainer>
              <figcaption className="sr-only">Delivery time trend line by date.</figcaption>
            </figure>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Fuel Consumption</CardTitle>
          </CardHeader>
          <CardContent>
            <figure aria-label="Fuel consumption trends over time">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="fuelConsumption" stroke="#F59E0B" strokeWidth={2} isAnimationActive={enableAnim} animationDuration={300} />
                </LineChart>
              </ResponsiveContainer>
              <figcaption className="sr-only">Fuel consumption trend line by date.</figcaption>
            </figure>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Efficiency Index</CardTitle>
          </CardHeader>
          <CardContent>
            <figure aria-label="Efficiency index (efficiency adjusted by fuel usage)">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={indexData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="index" stroke="#8B5CF6" strokeWidth={2} isAnimationActive={enableAnim} animationDuration={300} />
                </LineChart>
              </ResponsiveContainer>
              <figcaption className="sr-only">Composite index illustrating overall performance trend.</figcaption>
            </figure>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Performance Trends</CardTitle>
      </CardHeader>
      <CardContent>
        <figure aria-label="Performance trends: efficiency, delivery time, fuel usage">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
            <Line type="monotone" dataKey="efficiency" stroke="#3B82F6" strokeWidth={2} name="Efficiency %" isAnimationActive={enableAnim} animationDuration={300} />
            <Line type="monotone" dataKey="deliveryTime" stroke="#10B981" strokeWidth={2} name="Delivery Time (h)" isAnimationActive={enableAnim} animationDuration={300} />
            <Line type="monotone" dataKey="fuelConsumption" stroke="#F59E0B" strokeWidth={2} name="Fuel Usage" isAnimationActive={enableAnim} animationDuration={300} />
            </LineChart>
          </ResponsiveContainer>
          <figcaption className="sr-only">Combined chart showing key performance metrics over time.</figcaption>
        </figure>
      </CardContent>
    </Card>
  );
};
