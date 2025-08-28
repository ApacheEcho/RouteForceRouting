/**
 * RouteForce PWA - Bottom Navigation Component
 */

import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  MapIcon,
  RectangleStackIcon,
  RadioIcon,
  UserIcon
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  MapIcon as MapIconSolid,
  RectangleStackIcon as RectangleStackIconSolid,
  RadioIcon as RadioIconSolid,
  UserIcon as UserIconSolid
} from '@heroicons/react/24/solid';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  activeIcon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
}

const navItems: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: HomeIcon,
    activeIcon: HomeIconSolid,
  },
  {
    name: 'Routes',
    href: '/routes',
    icon: RectangleStackIcon,
    activeIcon: RectangleStackIconSolid,
  },
  {
    name: 'Map',
    href: '/map',
    icon: MapIcon,
    activeIcon: MapIconSolid,
  },
  {
    name: 'Tracking',
    href: '/tracking',
    icon: RadioIcon,
    activeIcon: RadioIconSolid,
  },
  {
    name: 'Profile',
    href: '/profile',
    icon: UserIcon,
    activeIcon: UserIconSolid,
  },
];

const Navigation: React.FC = () => {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 md:hidden" role="navigation" aria-label="Main Navigation">
      <div className="grid grid-cols-5 py-2">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            aria-label={item.name}
            tabIndex={0}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center py-2 px-1 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                isActive
                  ? 'text-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive ? (
                  <item.activeIcon className="h-6 w-6 mb-1" aria-hidden="true" />
                ) : (
                  <item.icon className="h-6 w-6 mb-1" aria-hidden="true" />
                )}
                <span>{item.name}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
};

export default Navigation;
