/**
 * RouteForce PWA - Settings Page
 */

import React, { useState } from 'react';
import {
  BellIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  DevicePhoneMobileIcon,
  MapIcon,
  UserIcon,
  ArrowRightOnRectangleIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';

interface SettingItem {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  type: 'toggle' | 'select' | 'action';
  value?: boolean | string;
  options?: { label: string; value: string }[];
  action?: () => void;
}

const SettingsPage: React.FC = () => {
  const { logout } = useAuth();
  const [pushNotifications, setPushNotifications] = useState(true);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [language, setLanguage] = useState('en');
  const [units, setUnits] = useState('metric');

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
  };

  const settings: SettingItem[] = [
    {
      id: 'notifications',
      title: 'Notifications',
      description: 'Manage your notification preferences',
      icon: BellIcon,
      type: 'toggle',
    },
    {
      id: 'appearance',
      title: 'Appearance',
      description: 'Customize the app appearance',
      icon: darkMode ? MoonIcon : SunIcon,
      type: 'toggle',
    },
    {
      id: 'language',
      title: 'Language',
      description: 'Choose your preferred language',
      icon: GlobeAltIcon,
      type: 'select',
      value: language,
      options: [
        { label: 'English', value: 'en' },
        { label: 'Spanish', value: 'es' },
        { label: 'French', value: 'fr' },
        { label: 'German', value: 'de' },
      ],
    },
    {
      id: 'units',
      title: 'Units',
      description: 'Distance and measurement units',
      icon: MapIcon,
      type: 'select',
      value: units,
      options: [
        { label: 'Metric (km)', value: 'metric' },
        { label: 'Imperial (miles)', value: 'imperial' },
      ],
    },
    {
      id: 'account',
      title: 'Account Settings',
      description: 'Manage your account information',
      icon: UserIcon,
      type: 'action',
      action: () => toast('Account settings coming soon'),
    },
    {
      id: 'privacy',
      title: 'Privacy & Security',
      description: 'Control your privacy settings',
      icon: ShieldCheckIcon,
      type: 'action',
      action: () => toast('Privacy settings coming soon'),
    },
    {
      id: 'offline',
      title: 'Offline Maps',
      description: 'Download maps for offline use',
      icon: DevicePhoneMobileIcon,
      type: 'action',
      action: () => toast('Offline maps coming soon'),
    },
  ];

  const renderSettingControl = (setting: SettingItem) => {
    switch (setting.type) {
      case 'toggle':
        if (setting.id === 'notifications') {
          return (
            <button
              onClick={() => setPushNotifications(!pushNotifications)}
              className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                pushNotifications ? 'bg-indigo-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  pushNotifications ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          );
        } else if (setting.id === 'appearance') {
          return (
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                darkMode ? 'bg-indigo-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  darkMode ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          );
        }
        break;

      case 'select':
        return (
          <select
            value={setting.value as string}
            onChange={(e) => {
              if (setting.id === 'language') {
                setLanguage(e.target.value);
              } else if (setting.id === 'units') {
                setUnits(e.target.value);
              }
            }}
            className="block w-24 px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
          >
            {setting.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'action':
        return (
          <button
            onClick={setting.action}
            className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
          >
            Configure
          </button>
        );

      default:
        return null;
    }
  };

  return (
    <div className="px-4 py-6 sm:px-6 lg:px-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-600">
          Customize your RouteForce experience
        </p>
      </div>

      {/* Settings List */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="divide-y divide-gray-200">
          {settings.map((setting) => (
            <div key={setting.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <setting.icon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-medium text-gray-900">
                      {setting.title}
                    </h3>
                    <p className="text-sm text-gray-500">{setting.description}</p>
                  </div>
                </div>
                <div className="flex-shrink-0">
                  {renderSettingControl(setting)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Notification Settings */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Notification Preferences</h3>
        </div>
        <div className="px-6 py-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">Push Notifications</p>
                <p className="text-sm text-gray-500">Receive notifications on your device</p>
              </div>
              <button
                onClick={() => setPushNotifications(!pushNotifications)}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                  pushNotifications ? 'bg-indigo-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    pushNotifications ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">Email Notifications</p>
                <p className="text-sm text-gray-500">Receive notifications via email</p>
              </div>
              <button
                onClick={() => setEmailNotifications(!emailNotifications)}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                  emailNotifications ? 'bg-indigo-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    emailNotifications ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Account Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4">
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2 border border-red-300 rounded-lg text-red-700 bg-red-50 hover:bg-red-100 transition-colors"
          >
            <ArrowRightOnRectangleIcon className="h-5 w-5" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      {/* App Info */}
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>RouteForce PWA v1.0.0</p>
        <p>© 2024 RouteForce Technologies</p>
      </div>
    </div>
  );
};

export default SettingsPage;
