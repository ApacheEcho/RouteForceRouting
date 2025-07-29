import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto text-center px-4 sm:px-6 lg:px-8">
      {/* Hero Section */}
      <div className="mb-8 sm:mb-12">
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
          🚀 RouteForce Pro
        </h1>
        <p className="text-lg sm:text-xl text-gray-600 mb-6 sm:mb-8">
          AI-Powered Route Optimization Platform
        </p>
        <p className="text-base sm:text-lg text-gray-500 mb-6 sm:mb-8 max-w-3xl mx-auto">
          Optimize delivery routes, reduce costs, and improve efficiency with advanced machine learning algorithms.
        </p>
      </div>

      {/* Navigation Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8 sm:mb-12">
        <Link
          to="/generate"
          className="block p-4 sm:p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 border border-gray-200 hover:border-blue-300 transform hover:-translate-y-1"
        >
          <div className="text-2xl sm:text-3xl mb-3 sm:mb-4">📍</div>
          <h3 className="text-lg sm:text-xl font-semibold mb-2">Route Generator</h3>
          <p className="text-sm sm:text-base text-gray-600">Upload stores and generate optimized routes</p>
        </Link>

        <Link
          to="/dashboard"
          className="block p-4 sm:p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 border border-gray-200 hover:border-green-300 transform hover:-translate-y-1"
        >
          <div className="text-2xl sm:text-3xl mb-3 sm:mb-4">📊</div>
          <h3 className="text-lg sm:text-xl font-semibold mb-2">Dashboard</h3>
          <p className="text-sm sm:text-base text-gray-600">Real-time monitoring and analytics</p>
        </Link>

        <Link
          to="/analytics"
          className="block p-4 sm:p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 border border-gray-200 hover:border-purple-300 transform hover:-translate-y-1"
        >
          <div className="text-2xl sm:text-3xl mb-3 sm:mb-4">📈</div>
          <h3 className="text-lg sm:text-xl font-semibold mb-2">Analytics</h3>
          <p className="text-sm sm:text-base text-gray-600">Advanced insights and reporting</p>
        </Link>

        <Link
          to="/playbook"
          className="block p-4 sm:p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 border border-gray-200 hover:border-orange-300 transform hover:-translate-y-1"
        >
          <div className="text-2xl sm:text-3xl mb-3 sm:mb-4">⚙️</div>
          <h3 className="text-lg sm:text-xl font-semibold mb-2">Playbook</h3>
          <p className="text-sm sm:text-base text-gray-600">Create optimization rule chains</p>
        </Link>
      </div>

      {/* Features Section */}
      <div className="bg-white rounded-lg shadow-md p-8 mb-8">
        <h2 className="text-2xl font-bold mb-6">Key Features</h2>
        <div className="grid md:grid-cols-2 gap-6 text-left">
          <div>
            <h4 className="font-semibold mb-2">🧠 AI-Powered Optimization</h4>
            <p className="text-gray-600">Machine learning algorithms for optimal route planning</p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">⚡ Real-time Tracking</h4>
            <p className="text-gray-600">Live progress monitoring and updates</p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">📱 Multi-platform Support</h4>
            <p className="text-gray-600">Web, mobile, and API integration</p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">🔒 Enterprise Security</h4>
            <p className="text-gray-600">JWT authentication and role-based access</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex justify-center space-x-4">
        <Link
          to="/generate"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Get Started
        </Link>
        <Link
          to="/auth"
          className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors"
        >
          Sign In
        </Link>
      </div>
    </div>
  );
};

export default HomePage;
