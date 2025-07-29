/**
 * RouteForce PWA - Header Component
 */

import React from 'react';
import { useLocation } from 'react-router-dom';
import { 
  Bars3Icon,
  BellIcon,
  UserCircleIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../hooks/useAuth';

const Header: React.FC = () => {
  const location = useLocation();
  const { user } = useAuth();

  const getPageTitle = () => {
    const path = location.pathname;
    switch (path) {
      case '/dashboard':
        return 'Dashboard';
      case '/routes':
        return 'Routes';
      case '/map':
        return 'Map View';
      case '/tracking':
        return 'Live Tracking';
      case '/profile':
        return 'Profile';
      case '/settings':
        return 'Settings';
      default:
        return 'RouteForce';
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-4 py-3 md:px-6">
      <div className="flex items-center justify-between">
        {/* Left side - Title */}
        <div className="flex items-center space-x-3">
          <div className="md:hidden">
            <button className="p-1 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100">
              <Bars3Icon className="h-6 w-6" />
            </button>
          </div>
          <h1 className="text-lg font-semibold text-gray-900">
            {getPageTitle()}
          </h1>
        </div>

        {/* Right side - Actions */}
        <div className="flex items-center space-x-3">
          {/* Notifications */}
          <button className="p-1 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 relative">
            <BellIcon className="h-6 w-6" />
            <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white"></span>
          </button>

          {/* User Profile */}
          <div className="flex items-center space-x-2">
            <UserCircleIcon className="h-8 w-8 text-gray-400" />
            <span className="hidden md:block text-sm font-medium text-gray-700">
              {user?.name || 'User'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
