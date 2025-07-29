/**
 * RouteForce PWA - Main Layout Component
 */

import React from 'react';
import { Outlet } from 'react-router-dom';
import Navigation from './Navigation';
import Header from './Header';

const Layout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <Header />
      
      {/* Main Content */}
      <main className="flex-1 pb-16 md:pb-0">
        <Outlet />
      </main>
      
      {/* Bottom Navigation for mobile */}
      <Navigation />
    </div>
  );
};

export default Layout;
