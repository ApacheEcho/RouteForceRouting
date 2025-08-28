/**
 * RouteForce PWA - Analytics Dashboard Page (React)
 */



import React, { useEffect, useState } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, BarElement, CategoryScale, LinearScale, LineElement, PointElement, Title } from 'chart.js';
import { Doughnut, Bar, Line } from 'react-chartjs-2';
import {
  fetchSystemHealth,
  fetchMobileAnalytics,
  fetchRouteAnalytics,
  fetchDriverAnalytics,
  fetchAPIAnalytics,
  SystemHealth,
  MobileAnalytics,
  RouteAnalytics,
  DriverAnalytics,
  APIAnalytics,
} from '../api';

ChartJS.register(ArcElement, Tooltip, Legend, BarElement, CategoryScale, LinearScale, LineElement, PointElement, Title);



const AnalyticsDashboardPage: React.FC = () => {
  // State for analytics data
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [mobileAnalytics, setMobileAnalytics] = useState<MobileAnalytics | null>(null);
  const [apiAnalytics, setAPIAnalytics] = useState<APIAnalytics | null>(null);
  const [performanceData, setPerformanceData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const [sys, mobile, api, route] = await Promise.all([
          fetchSystemHealth(),
          fetchMobileAnalytics(),
          fetchAPIAnalytics(),
          fetchRouteAnalytics(),
        ]);
        setSystemHealth(sys);
        setMobileAnalytics(mobile);
        setAPIAnalytics(api);
        setPerformanceData({
          labels: Object.keys(route.algorithm_usage || {}),
          datasets: [
            {
              label: 'Routes Generated',
              data: Object.values(route.algorithm_usage || {}),
              backgroundColor: '#007bff',
              borderColor: '#007bff',
              fill: false,
              tension: 0.4,
            },
          ],
        });
      } catch (e: any) {
        setError(e.message || 'Failed to load analytics');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Chart data transforms
  const healthData = systemHealth
    ? {
        labels: ['Health', 'Remaining'],
        datasets: [
          {
            label: 'Health Score',
            data: [systemHealth.health_score, 100 - systemHealth.health_score],
            backgroundColor: ['#28a745', '#e9ecef'],
            borderWidth: 0,
          },
        ],
      }
    : {
        labels: ['Health'],
        datasets: [
          {
            label: 'Health Score',
            data: [0, 100],
            backgroundColor: ['#e9ecef', '#e9ecef'],
            borderWidth: 0,
          },
        ],
      };

  const apiData = apiAnalytics
    ? {
        labels: ['Avg', 'Median', 'P95', 'Max'],
        datasets: [
          {
            label: 'Response Time (ms)',
            data: [
              (apiAnalytics.performance.avg_response_time || 0) * 1000,
              (apiAnalytics.performance.median_response_time || 0) * 1000,
              (apiAnalytics.performance.p95_response_time || 0) * 1000,
              (apiAnalytics.performance.max_response_time || 0) * 1000,
            ],
            borderColor: '#28a745',
            backgroundColor: 'rgba(40, 167, 69, 0.1)',
            fill: true,
            tension: 0.4,
          },
        ],
      }
    : {
        labels: ['Avg', 'Median', 'P95', 'Max'],
        datasets: [
          {
            label: 'Response Time (ms)',
            data: [0, 0, 0, 0],
            borderColor: '#28a745',
            backgroundColor: 'rgba(40, 167, 69, 0.1)',
            fill: true,
            tension: 0.4,
          },
        ],
      };

  const mobileUsageData = mobileAnalytics
    ? {
        labels: Object.keys(mobileAnalytics.device_types || {}),
        datasets: [
          {
            label: 'Devices',
            data: Object.values(mobileAnalytics.device_types || {}),
            backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545'],
          },
        ],
      }
    : {
        labels: ['iOS', 'Android', 'Web'],
        datasets: [
          {
            label: 'Devices',
            data: [0, 0, 0],
            backgroundColor: ['#007bff', '#28a745', '#ffc107'],
          },
        ],
      };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 text-gray-400">Loading analytics...</div>
    );
  }
  if (error) {
    return (
      <div className="flex items-center justify-center h-96 text-red-500">{error}</div>
    );
  }

  return (
    <main className="px-2 py-4 sm:px-4 md:px-6 lg:px-8 min-h-screen bg-gray-50" role="main" aria-labelledby="analytics-dashboard-title">
      <h1 className="text-2xl font-bold text-gray-900 mb-6 focus:outline-none" id="analytics-dashboard-title" tabIndex={-1}>
        Analytics Dashboard
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 lg:gap-8">
        {/* System Health Card */}
  <section className="bg-white rounded-xl shadow-lg p-4 md:p-6" aria-label="System Health" tabIndex={0}>
          <h2 className="text-xl font-semibold text-gray-800 mb-4" id="system-health-heading">System Health</h2>
          <div className="h-40 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Doughnut
              data={healthData}
              options={{
                cutout: '70%',
                plugins: {
                  legend: { display: false },
                },
                maintainAspectRatio: false,
              }}
              style={{ maxHeight: 120, maxWidth: 120 }}
            />
            <div className="ml-6">
              <div className="text-2xl font-bold text-green-700">{systemHealth?.health_score ?? '--'}</div>
              <div className="text-sm text-gray-500">{systemHealth?.status ?? ''}</div>
              <div className="text-xs text-gray-400 mt-2">Uptime: {systemHealth?.uptime ?? '--'}</div>
              <div className="text-xs text-gray-400">Active Sessions: {systemHealth?.active_sessions ?? '--'}</div>
            </div>
          </div>
        </section>
        {/* Performance Trends Card */}
  <section className="bg-white rounded-xl shadow-lg p-4 md:p-6" aria-label="Performance Trends" tabIndex={0}>
          <h2 className="text-xl font-semibold text-gray-800 mb-4" id="performance-trends-heading">Performance Trends</h2>
          <div className="h-40 flex items-center justify-center">
            {performanceData && (
              <Bar
                data={performanceData}
                options={{
                  plugins: { legend: { display: false } },
                  maintainAspectRatio: false,
                  scales: { y: { beginAtZero: true } },
                }}
                style={{ maxHeight: 120, maxWidth: 220 }}
              />
            )}
          </div>
        </section>
        {/* API Analytics Card */}
  <section className="bg-white rounded-xl shadow-lg p-4 md:p-6 lg:col-span-2" aria-label="API Analytics" tabIndex={0}>
          <h2 className="text-xl font-semibold text-gray-800 mb-4" id="api-analytics-heading">API Analytics</h2>
          <div className="h-40 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Line
              data={apiData}
              options={{
                plugins: { legend: { display: false } },
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } },
              }}
              style={{ maxHeight: 120, maxWidth: 220 }}
            />
            <div className="ml-6">
              <div className="text-xs text-gray-400">Total Requests: {apiAnalytics?.total_requests ?? '--'}</div>
              <div className="text-xs text-gray-400">Error Rate: {apiAnalytics?.error_rate ?? '--'}%</div>
            </div>
          </div>
        </section>
        {/* Mobile Usage Card */}
  <section className="bg-white rounded-xl shadow-lg p-4 md:p-6" aria-label="Mobile Usage" tabIndex={0}>
          <h2 className="text-xl font-semibold text-gray-800 mb-4" id="mobile-usage-heading">Mobile Usage</h2>
          <div className="h-40 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Doughnut
              data={mobileUsageData}
              options={{
                plugins: { legend: { position: 'bottom' } },
                maintainAspectRatio: false,
              }}
              style={{ maxHeight: 120, maxWidth: 120 }}
            />
            <div className="ml-6">
              <div className="text-xs text-gray-400">Sessions: {mobileAnalytics?.total_sessions ?? '--'}</div>
              <div className="text-xs text-gray-400">Devices: {mobileAnalytics?.unique_devices ?? '--'}</div>
              <div className="text-xs text-gray-400">API Calls: {mobileAnalytics?.total_api_calls ?? '--'}</div>
            </div>
          </div>
        </section>
        {/* Real-time Activity Feed */}
  <section className="bg-white rounded-xl shadow-lg p-4 md:p-6" aria-label="Real-time Activity" tabIndex={0}>
          <h2 className="text-xl font-semibold text-gray-800 mb-4" id="activity-feed-heading">Real-time Activity</h2>
          <div className="h-40 flex items-center justify-center text-gray-400" aria-live="polite">[Activity Feed]</div>
        </section>
      </div>
    </main>
  );
};

export default AnalyticsDashboardPage;
