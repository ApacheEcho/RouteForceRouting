import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, useLocation } from 'react-router-dom';
import * as useAuthModule from '../hooks/useAuth';
import Header from './Header';

// Mock useAuth to control user state
describe('Header', () => {
  const mockUser = { name: 'Test User' };

  beforeEach(() => {
    vi.spyOn(useAuthModule, 'useAuth').mockReturnValue({ user: mockUser });
  });

  it('renders the correct page title for each route', () => {
    const routes = [
      { path: '/dashboard', title: 'Dashboard' },
      { path: '/routes', title: 'Routes' },
      { path: '/map', title: 'Map View' },
      { path: '/tracking', title: 'Live Tracking' },
      { path: '/profile', title: 'Profile' },
      { path: '/settings', title: 'Settings' },
      { path: '/unknown', title: 'RouteForce' },
    ];
    routes.forEach(({ path, title }) => {
      render(
        <MemoryRouter initialEntries={[path]}>
          <Header />
        </MemoryRouter>
      );
      expect(screen.getByRole('heading', { name: title })).toBeInTheDocument();
    });
  });

  it('renders the user name if available', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Header />
      </MemoryRouter>
    );
    expect(screen.getByText('Test User')).toBeInTheDocument();
  });

  it('renders fallback user label if user is missing', () => {
    vi.spyOn(useAuthModule, 'useAuth').mockReturnValue({ user: undefined });
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Header />
      </MemoryRouter>
    );
    expect(screen.getByText('User')).toBeInTheDocument();
  });

  it('renders notification and profile icons', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Header />
      </MemoryRouter>
    );
    // Bell (notifications) icon
    expect(screen.getByLabelText('View notifications')).toBeInTheDocument();
    // User profile group
    expect(screen.getByLabelText('User profile')).toBeInTheDocument();
  });

  it('renders the menu button for mobile', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Header />
      </MemoryRouter>
    );
    expect(screen.getByLabelText('Open menu')).toBeInTheDocument();
  });
});
