import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardContent, CardTitle } from '../ui/Card';
import Skeleton from '../ui/Skeleton';
import { analyticsApi } from '../../services/api';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const Analytics: React.FC = () => {
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [insights, setInsights] = React.useState<any>(null);
  const [report, setReport] = React.useState<any>(null);

  React.useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [i, r] = await Promise.all([
          analyticsApi.getInsights(),
          analyticsApi.getReports(),
        ]);
        setInsights(i?.data || i);
        setReport(r?.data || r);
        setError(null);
      } catch (e: any) {
        setError(e?.message || 'Failed to load analytics');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Basic line data from report if available
  const series = (report?.timeseries || []).map((pt: any) => ({
    timestamp: pt.timestamp || pt.time || '',
    value: pt.value || pt.requests || 0,
  }));

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link to="/" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
          ← Back to Home
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📈 Analytics</h1>
        <p className="text-gray-600">Advanced insights and performance metrics</p>
      </div>

      {/* Analytics Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader><CardTitle>API Requests (24h)</CardTitle></CardHeader>
          <CardContent>
            {loading ? <Skeleton className="h-8 w-24" /> : <div className="text-3xl font-bold text-blue-600">{report?.summary?.requests_24h ?? '—'}</div>}
            <p className="text-gray-600">Total API requests last 24 hours</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Active Users</CardTitle></CardHeader>
          <CardContent>
            {loading ? <Skeleton className="h-8 w-24" /> : <div className="text-3xl font-bold text-green-600">{report?.summary?.active_users ?? insights?.active_users ?? '—'}</div>}
            <p className="text-gray-600">Unique users interacting</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Routes Generated</CardTitle></CardHeader>
          <CardContent>
            {loading ? <Skeleton className="h-8 w-24" /> : <div className="text-3xl font-bold text-purple-600">{report?.summary?.routes_generated ?? '—'}</div>}
            <p className="text-gray-600">Total optimized routes in period</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader><CardTitle>Requests Over Time</CardTitle></CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-64 w-full" />
            ) : series.length === 0 ? (
              <p className="text-gray-500">No timeseries available</p>
            ) : (
              <figure aria-label="Requests over time">
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={series}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="value" stroke="#3B82F6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
                <figcaption className="sr-only">API requests trend line.</figcaption>
              </figure>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>System Health Snapshot</CardTitle></CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                <Skeleton className="h-4 w-1/2" />
                <Skeleton className="h-4 w-2/3" />
                <Skeleton className="h-4 w-1/3" />
              </div>
            ) : (
              <ul className="text-sm text-left space-y-1">
                <li><span className="text-gray-500">CPU:</span> {insights?.system?.cpu_percent ?? '—'}%</li>
                <li><span className="text-gray-500">Memory:</span> {insights?.system?.memory_percent ?? '—'}%</li>
                <li><span className="text-gray-500">Disk:</span> {insights?.system?.disk_usage ?? '—'}%</li>
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      {/* API Integration Status */}
      <Card>
        <CardHeader><CardTitle>API Integration Status</CardTitle></CardHeader>
        <CardContent>
          {error ? (
            <p className="text-red-600">{error}</p>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span>Analytics API</span>
                <span className="text-green-600">{loading ? '…' : '✅ Connected'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>System Health</span>
                <span className="text-green-600">{insights ? '✅ Available' : '—'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Report</span>
                <span className="text-green-600">{report ? '✅ Available' : '—'}</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Analytics;
