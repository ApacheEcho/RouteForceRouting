import React from 'react';
import { Link } from 'react-router-dom';

const Analytics: React.FC = () => {
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
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-2">Route Efficiency</h3>
          <div className="text-3xl font-bold text-green-600 mb-2">87%</div>
          <p className="text-gray-600">Average optimization improvement</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-2">Cost Savings</h3>
          <div className="text-3xl font-bold text-blue-600 mb-2">$2,847</div>
          <p className="text-gray-600">Monthly fuel and time savings</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-2">Routes Generated</h3>
          <div className="text-3xl font-bold text-purple-600 mb-2">1,234</div>
          <p className="text-gray-600">Total optimized routes</p>
        </div>
      </div>

      {/* Charts Placeholder */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Performance Trends</h3>
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            <p className="text-gray-500">Chart placeholder - Connect to Flask API</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Route Distribution</h3>
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            <p className="text-gray-500">Chart placeholder - Connect to Flask API</p>
          </div>
        </div>
      </div>

      {/* API Integration Status */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">API Integration Status</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span>Analytics API</span>
            <span className="text-green-600">✅ Connected</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Real-time Data</span>
            <span className="text-green-600">✅ Active</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Historical Data</span>
            <span className="text-yellow-600">⚠️ Connecting...</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
