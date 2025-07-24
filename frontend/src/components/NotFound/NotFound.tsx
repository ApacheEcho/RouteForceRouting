import React from 'react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
  return (
    <div className="max-w-2xl mx-auto text-center">
      {/* 404 Illustration */}
      <div className="text-6xl mb-8">🚫</div>
      
      {/* Error Message */}
      <h1 className="text-4xl font-bold text-gray-900 mb-4">
        404 - Page Not Found
      </h1>
      
      <p className="text-xl text-gray-600 mb-8">
        Sorry, the page you're looking for doesn't exist or has been moved.
      </p>

      {/* Navigation Options */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 className="text-lg font-semibold mb-4">Where would you like to go?</h3>
        
        <div className="grid md:grid-cols-2 gap-4">
          <Link
            to="/"
            className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="text-2xl mb-2">🏠</div>
            <div className="font-medium">Homepage</div>
            <div className="text-sm text-gray-600">Back to RouteForce main page</div>
          </Link>

          <Link
            to="/dashboard"
            className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="text-2xl mb-2">📊</div>
            <div className="font-medium">Dashboard</div>
            <div className="text-sm text-gray-600">View your analytics</div>
          </Link>

          <Link
            to="/generate"
            className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="text-2xl mb-2">📍</div>
            <div className="font-medium">Route Generator</div>
            <div className="text-sm text-gray-600">Create optimized routes</div>
          </Link>

          <Link
            to="/analytics"
            className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="text-2xl mb-2">📈</div>
            <div className="font-medium">Analytics</div>
            <div className="text-sm text-gray-600">Performance insights</div>
          </Link>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="space-y-4">
        <Link
          to="/"
          className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Take Me Home
        </Link>
        
        <div className="text-sm text-gray-500">
          <p>If you believe this is an error, please contact support.</p>
        </div>
      </div>

      {/* Helpful Links */}
      <div className="mt-12 pt-8 border-t border-gray-200">
        <h4 className="font-medium mb-4">Need Help?</h4>
        <div className="flex justify-center space-x-6 text-sm">
          <a href="#" className="text-blue-600 hover:text-blue-800">Documentation</a>
          <a href="#" className="text-blue-600 hover:text-blue-800">Support</a>
          <a href="#" className="text-blue-600 hover:text-blue-800">Contact</a>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
