/**
 * RouteForce PWA - Dashboard Page
 */

import React from 'react';
import {
  ChartBarIcon,
  TruckIcon,
  ClockIcon,
  CurrencyDollarIcon,
  MapPinIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface StatCard {
  name: string;
  value: string;
  change: string;
  changeType: 'increase' | 'decrease' | 'neutral';
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
}

const stats: StatCard[] = [
  {
    name: 'Active Routes',
    value: '12',
    change: '+2.1%',
    changeType: 'increase',
    icon: MapPinIcon,
  },
  {
    name: 'Total Distance',
    value: '2,847 km',
    change: '+5.4%',
    changeType: 'increase',
    icon: TruckIcon,
  },
  {
    name: 'Avg. Time Saved',
    value: '23 min',
    change: '+12.5%',
    changeType: 'increase',
    icon: ClockIcon,
  },
  {
    name: 'Cost Savings',
    value: '$3,247',
    change: '+8.1%',
    changeType: 'increase',
    icon: CurrencyDollarIcon,
  },
];

const recentAlerts = [
  {
    id: 1,
    message: 'Route optimization completed for Downtown area',
    type: 'success',
    time: '5 minutes ago',
  },
  {
    id: 2,
    message: 'Traffic delay detected on Route #7',
    type: 'warning',
    time: '12 minutes ago',
  },
  {
    id: 3,
    message: 'Vehicle maintenance scheduled for tomorrow',
    type: 'info',
    time: '1 hour ago',
  },
];

const DashboardPage: React.FC = () => {
  return (
    <div className="px-4 py-6 sm:px-6 lg:px-8" role="main" aria-labelledby="dashboard-title">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900" id="dashboard-title">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-600">
          Welcome back! Here's your route management overview.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6 sm:grid-cols-4" aria-label="Route statistics">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="bg-white overflow-hidden shadow rounded-lg"
            role="region"
            aria-label={stat.name}
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <stat.icon className="h-6 w-6 text-gray-400" aria-hidden="true" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.name}
                    </dt>
                    <dd className="text-lg font-semibold text-gray-900">
                      {stat.value}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm">
                <span
                  className={`font-medium ${
                    stat.changeType === 'increase'
                      ? 'text-green-600'
                      : stat.changeType === 'decrease'
                      ? 'text-red-600'
                      : 'text-gray-600'
                  }`}
                >
                  {stat.change}
                </span>
                <span className="text-gray-500"> from last week</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Alerts */}
        <div className="bg-white shadow rounded-lg" role="region" aria-label="Recent alerts">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg leading-6 font-medium text-gray-900 mb-4" id="recent-alerts-title">
              Recent Alerts
            </h2>
            <div className="flow-root">
              <ul className="-mb-8">
                {recentAlerts.map((alert, alertIdx) => (
                  <li key={alert.id}>
                    <div className="relative pb-8">
                      {alertIdx !== recentAlerts.length - 1 ? (
                        <span
                          className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                          aria-hidden="true"
                        />
                      ) : null}
                      <div className="relative flex space-x-3">
                        <div>
                          <span
                            className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                              alert.type === 'success'
                                ? 'bg-green-500'
                                : alert.type === 'warning'
                                ? 'bg-yellow-500'
                                : 'bg-blue-500'
                            }`}
                            aria-label={alert.type === 'success' ? 'Success' : alert.type === 'warning' ? 'Warning' : 'Info'}
                          >
                            <ExclamationTriangleIcon className="h-5 w-5 text-white" aria-hidden="true" />
                          </span>
                        </div>
                        <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                          <div>
                            <p className="text-sm text-gray-500">{alert.message}</p>
                          </div>
                          <div className="text-right text-sm whitespace-nowrap text-gray-500">
                            {alert.time}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white shadow rounded-lg" role="region" aria-label="Quick actions">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg leading-6 font-medium text-gray-900 mb-4" id="quick-actions-title">
              Quick Actions
            </h2>
            <div className="grid grid-cols-1 gap-4">
              <button className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 text-left hover:bg-indigo-100 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2" aria-label="Generate Route Report">
                <div className="flex items-center">
                  <ChartBarIcon className="h-6 w-6 text-indigo-600" aria-hidden="true" />
                  <span className="ml-3 text-sm font-medium text-indigo-900">
                    Generate Route Report
                  </span>
                </div>
              </button>
              <button className="bg-green-50 border border-green-200 rounded-lg p-4 text-left hover:bg-green-100 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2" aria-label="Optimize Routes">
                <div className="flex items-center">
                  <MapPinIcon className="h-6 w-6 text-green-600" aria-hidden="true" />
                  <span className="ml-3 text-sm font-medium text-green-900">
                    Optimize Routes
                  </span>
                </div>
              </button>
              <button className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-left hover:bg-yellow-100 transition-colors">
                <div className="flex items-center">
                  <TruckIcon className="h-6 w-6 text-yellow-600" />
                  <span className="ml-3 text-sm font-medium text-yellow-900">
                    Track Vehicles
                  </span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
