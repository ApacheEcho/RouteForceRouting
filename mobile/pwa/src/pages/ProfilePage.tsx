/**
 * RouteForce PWA - Profile Page
 */

import React from 'react';
import {
  UserIcon,
  EnvelopeIcon,
  PhoneIcon,
  BriefcaseIcon,
  MapPinIcon,
  CalendarIcon,
  PencilIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../hooks/useAuth';

interface ProfileStat {
  label: string;
  value: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
}

const profileStats: ProfileStat[] = [
  {
    label: 'Routes Completed',
    value: '247',
    icon: MapPinIcon,
  },
  {
    label: 'Total Distance',
    value: '15,432 km',
    icon: MapPinIcon,
  },
  {
    label: 'Avg. Efficiency',
    value: '92%',
    icon: BriefcaseIcon,
  },
  {
    label: 'Member Since',
    value: 'Jan 2023',
    icon: CalendarIcon,
  },
];

const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="px-4 py-6 sm:px-6 lg:px-8" role="main" aria-labelledby="profile-title">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900" id="profile-title">Profile</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage your account information and view your performance
        </p>
      </div>

      {/* Profile Header */}
      <div className="bg-white shadow rounded-lg mb-6" role="region" aria-label="Profile header">
        <div className="px-6 py-8">
          <div className="flex items-center space-x-6">
            <div className="flex-shrink-0">
              <div className="h-24 w-24 rounded-full bg-indigo-100 flex items-center justify-center">
                <UserIcon className="h-12 w-12 text-indigo-600" aria-hidden="true" />
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    {user?.name || 'John Doe'}
                  </h2>
                  <p className="text-lg text-gray-600">{user?.role || 'Route Manager'}</p>
                </div>
                <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2" aria-label="Edit profile" tabIndex={0}>
                  <PencilIcon className="h-4 w-4" aria-hidden="true" />
                  <span>Edit</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <div className="bg-white shadow rounded-lg mb-6" role="region" aria-label="Contact information">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Contact Information</h2>
        </div>
        <div className="px-6 py-4">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <EnvelopeIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
              <div>
                <p className="text-sm font-medium text-gray-900">Email</p>
                <p className="text-sm text-gray-600">{user?.email || 'john.doe@routeforce.com'}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <PhoneIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
              <div>
                <p className="text-sm font-medium text-gray-900">Phone</p>
                <p className="text-sm text-gray-600">+1 (555) 123-4567</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <MapPinIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
              <div>
                <p className="text-sm font-medium text-gray-900">Location</p>
                <p className="text-sm text-gray-600">Portland, Oregon, USA</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Stats */}
      <div className="bg-white shadow rounded-lg mb-6" role="region" aria-label="Performance stats">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Performance Stats</h2>
        </div>
        <div className="px-6 py-4">
          <div className="grid grid-cols-2 gap-4">
            {profileStats.map((stat, index) => (
              <div key={index} className="text-center p-4 bg-gray-50 rounded-lg" aria-label={stat.label}>
                <stat.icon className="h-6 w-6 text-indigo-600 mx-auto mb-2" aria-hidden="true" />
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-gray-600">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg" role="region" aria-label="Recent activity">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Activity</h2>
        </div>
        <div className="px-6 py-4">
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                  <MapPinIcon className="h-4 w-4 text-green-600" aria-hidden="true" />
                </div>
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">
                  Completed <span className="font-medium">Downtown Delivery Route</span>
                </p>
                <p className="text-xs text-gray-500">2 hours ago</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <BriefcaseIcon className="h-4 w-4 text-blue-600" aria-hidden="true" />
                </div>
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">
                  Optimized route efficiency improved by <span className="font-medium">15%</span>
                </p>
                <p className="text-xs text-gray-500">1 day ago</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-yellow-100 flex items-center justify-center">
                  <CalendarIcon className="h-4 w-4 text-yellow-600" aria-hidden="true" />
                </div>
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">
                  Scheduled <span className="font-medium">5 new routes</span> for this week
                </p>
                <p className="text-xs text-gray-500">3 days ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
