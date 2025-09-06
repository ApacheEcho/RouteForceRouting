import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto text-center px-4 sm:px-6 lg:px-8">
      {/* Hero Section */}
      <section className="mb-12 sm:mb-16" aria-labelledby="hero-heading">
        <h1 id="hero-heading" className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-gray-900 dark:text-white mb-4">
          AI-Powered Route Optimization
        </h1>
        <p className="text-lg sm:text-xl text-gray-600 dark:text-gray-300 mb-6 sm:mb-8 max-w-3xl mx-auto">
          Plan smarter routes, slash fuel costs, and delight customers with an enterprise-ready optimization platform.
        </p>
        <div className="flex justify-center gap-3">
          <Link to="/generate" className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-gray-950">
            Get Started
          </Link>
          <Link to="/dashboard" className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100 px-6 py-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-gray-950">
            View Dashboard
          </Link>
        </div>
      </section>

      {/* Quick Navigation */}
      <nav aria-label="Feature navigation" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-12">
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
      </nav>

      {/* Trust badges */}
      <section className="mb-12" aria-label="Trusted by">
        <p className="text-sm uppercase tracking-wider text-gray-500 mb-4">Trusted by teams</p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 items-center opacity-90">
          <img src="/brand-1.svg" alt="Brand 1" className="h-8 mx-auto" />
          <img src="/brand-2.svg" alt="Brand 2" className="h-8 mx-auto" />
          <img src="/brand-3.svg" alt="Brand 3" className="h-8 mx-auto" />
          <img src="/brand-4.svg" alt="Brand 4" className="h-8 mx-auto" />
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-8 mb-12 text-left" aria-labelledby="features-heading">
        <h2 id="features-heading" className="text-2xl font-bold mb-6">Key Features</h2>
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
      </section>

      {/* How it works */}
      <section className="mb-16" aria-labelledby="how-heading">
        <h2 id="how-heading" className="text-2xl font-bold mb-6">How It Works</h2>
        <ol className="grid sm:grid-cols-3 gap-6 text-left">
          <li className="p-6 bg-white dark:bg-gray-900 rounded-lg shadow-md">
            <span className="text-sm text-gray-500">Step 1</span>
            <h3 className="text-lg font-semibold mb-1">Import your data</h3>
            <p className="text-gray-600">Upload CSV or Excel files with store locations or addresses.</p>
          </li>
          <li className="p-6 bg-white dark:bg-gray-900 rounded-lg shadow-md">
            <span className="text-sm text-gray-500">Step 2</span>
            <h3 className="text-lg font-semibold mb-1">Optimize routes</h3>
            <p className="text-gray-600">Choose algorithm preferences and generate the most efficient paths.</p>
          </li>
          <li className="p-6 bg-white dark:bg-gray-900 rounded-lg shadow-md">
            <span className="text-sm text-gray-500">Step 3</span>
            <h3 className="text-lg font-semibold mb-1">Track & iterate</h3>
            <p className="text-gray-600">Monitor performance, analyze savings, and continuously improve.</p>
          </li>
        </ol>
      </section>
    </div>
  );
};

export default HomePage;
