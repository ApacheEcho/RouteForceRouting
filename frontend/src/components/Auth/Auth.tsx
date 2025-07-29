import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Auth: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Handle successful auth
        console.log('Auth successful:', data);
        // Redirect to dashboard or store token
      } else {
        console.error('Auth error:', data);
      }
    } catch (error) {
      console.error('Network error:', error);
    }
  };

  return (
    <div className="max-w-md mx-auto">
      {/* Header */}
      <div className="mb-8 text-center">
        <Link to="/" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
          ← Back to Home
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {isLogin ? '🔐 Sign In' : '📝 Sign Up'}
        </h1>
        <p className="text-gray-600">
          {isLogin ? 'Welcome back to RouteForce' : 'Create your RouteForce account'}
        </p>
      </div>

      {/* Auth Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              className="w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="your@email.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              className="w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="••••••••"
            />
          </div>

          {!isLogin && (
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                required
                className="w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="••••••••"
              />
            </div>
          )}

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
          >
            {isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        {/* Toggle between login/register */}
        <div className="mt-6 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            {isLogin
              ? "Don't have an account? Sign up"
              : 'Already have an account? Sign in'}
          </button>
        </div>

        {/* Demo Credentials */}
        <div className="mt-6 p-4 bg-gray-50 rounded-md">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Demo Credentials:</h4>
          <div className="text-xs text-gray-600 space-y-1">
            <div>Admin: admin@demo.routeforce.com</div>
            <div>User: user@demo.routeforce.com</div>
            <div>Password: (any password)</div>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="mt-8 text-center">
        <h3 className="text-lg font-semibold mb-4">Why RouteForce?</h3>
        <div className="space-y-2 text-sm text-gray-600">
          <div>🚀 AI-powered route optimization</div>
          <div>📊 Real-time analytics and insights</div>
          <div>🔒 Enterprise-grade security</div>
          <div>📱 Multi-platform support</div>
        </div>
      </div>
    </div>
  );
};

export default Auth;
