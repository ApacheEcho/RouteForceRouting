import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Navigation from './Navigation';

// Mock heroicons
vi.mock('@heroicons/react/24/outline', () => ({
  HomeIcon: () => <svg data-testid="icon-home" />, 
  MapIcon: () => <svg data-testid="icon-map" />, 
  RectangleStackIcon: () => <svg data-testid="icon-routes" />, 
  RadioIcon: () => <svg data-testid="icon-tracking" />, 
  UserIcon: () => <svg data-testid="icon-profile" />
}));
vi.mock('@heroicons/react/24/solid', () => ({
  HomeIcon: () => <svg data-testid="icon-home-solid" />, 
  MapIcon: () => <svg data-testid="icon-map-solid" />, 
  RectangleStackIcon: () => <svg data-testid="icon-routes-solid" />, 
  RadioIcon: () => <svg data-testid="icon-tracking-solid" />, 
  UserIcon: () => <svg data-testid="icon-profile-solid" />
}));

describe('Navigation', () => {
  it('renders all navigation items', () => {
    render(
      <MemoryRouter>
        <Navigation />
      </MemoryRouter>
    );
    expect(screen.getByLabelText('Dashboard')).toBeInTheDocument();
    expect(screen.getByLabelText('Routes')).toBeInTheDocument();
    expect(screen.getByLabelText('Map')).toBeInTheDocument();
    expect(screen.getByLabelText('Tracking')).toBeInTheDocument();
    expect(screen.getByLabelText('Profile')).toBeInTheDocument();
  });

  it('renders correct icons for inactive state', () => {
    render(
      <MemoryRouter initialEntries={['/profile']}>
        <Navigation />
      </MemoryRouter>
    );
    // Only Profile should be active, others inactive
    expect(screen.getByTestId('icon-profile-solid')).toBeInTheDocument();
    expect(screen.getByTestId('icon-home')).toBeInTheDocument();
    expect(screen.getByTestId('icon-routes')).toBeInTheDocument();
    expect(screen.getByTestId('icon-map')).toBeInTheDocument();
    expect(screen.getByTestId('icon-tracking')).toBeInTheDocument();
  });

  it('renders correct icon for active route', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Navigation />
      </MemoryRouter>
    );
    expect(screen.getByTestId('icon-home-solid')).toBeInTheDocument();
  });
});
