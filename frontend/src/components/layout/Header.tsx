import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import ThemeToggle from '../ui/ThemeToggle';
import DensityToggle from '../ui/DensityToggle';
import HealthStatus from '../ui/HealthStatus';

// Simple route prefetchers
const prefetchMap: Record<string, () => Promise<unknown>> = {
  '/dashboard': () => import('../Dashboard/Dashboard'),
  '/analytics': () => import('../Analytics/Analytics'),
  '/generate': () => import('../RouteGenerator/RouteGenerator'),
  '/playbook': () => import('../PlaybookGUI/PlaybookGUI'),
  '/connections': () => import('../Connections/Connections'),
  '/auth': () => import('../Auth/Auth'),
  '/': () => import('../HomePage/HomePage'),
};

const NavLink: React.FC<{ to: string; children: React.ReactNode }> = ({ to, children }) => {
  const location = useLocation();
  const active = location.pathname === to;
  return (
    <Link
      to={to}
      onMouseEnter={() => { const f = prefetchMap[to]; if (f) f().catch(() => {}); }}
      className={`px-3 py-2 rounded-md text-sm font-medium ${
        active ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'
      }`}
      aria-current={active ? 'page' : undefined}
    >
      {children}
    </Link>
  );
};

export const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-40 backdrop-blur bg-white/70 dark:bg-gray-950/70 border-b border-gray-200 dark:border-gray-800">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link to="/" className="inline-flex items-center space-x-2" aria-label="RouteForce home">
            <img src="/logo.svg" alt="RouteForce" className="h-6 w-auto" />
          </Link>
          <nav className="hidden md:flex items-center space-x-1" aria-label="Primary">
            <NavLink to="/dashboard">Dashboard</NavLink>
            <NavLink to="/analytics">Analytics</NavLink>
            <NavLink to="/generate">Generate</NavLink>
            <NavLink to="/playbook">Playbook</NavLink>
            <NavLink to="/connections">Connections</NavLink>
          </nav>
        </div>
        <div className="flex items-center space-x-3">
          <HealthStatus />
          <ThemeToggle />
          <DensityToggle />
        </div>
      </div>
    </header>
  );
};

export default Header;
