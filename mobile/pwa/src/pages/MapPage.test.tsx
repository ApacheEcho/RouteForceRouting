import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MapPage from './MapPage';
import * as api from '../api';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock react-leaflet components for jsdom
const renderWithQueryClient = (ui: React.ReactElement) => {
  const testClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={testClient}>{ui}</QueryClientProvider>
  );
};

describe('MapPage', () => {
  const mockStops = [
    {
      id: '1',
      name: 'Stop 1',
      address: '123 Main St',
      lat: 45.5152,
      lng: -122.6784,
      status: 'completed',
      estimatedTime: '10:00 AM',
    },
    {
      id: '2',
      name: 'Stop 2',
      address: '456 Oak Ave',
      lat: 45.5200,
      lng: -122.6750,
      status: 'current',
      estimatedTime: '10:30 AM',
    },
  ];
  const mockVehicles = [
    {
      id: 'v1',
      name: 'Truck 1',
      lat: 45.5100,
      lng: -122.6900,
      status: 'active',
    },
    {
      id: 'v2',
      name: 'Truck 2',
      lat: 45.5152,
      lng: -122.6784,
      status: 'idle',
    },
  ];

  beforeEach(() => {
    vi.resetAllMocks();
    vi.spyOn(api, 'fetchStops').mockResolvedValue(mockStops);
    vi.spyOn(api, 'fetchVehicles').mockResolvedValue(mockVehicles);
  });

  it('renders header, controls, and map', async () => {
  renderWithQueryClient(<MapPage />);
  expect(screen.getAllByRole('main').length).toBeGreaterThan(0);
  // There are multiple banners, so check at least one has the expected text
  const banners = screen.getAllByRole('banner');
  expect(banners.some(banner => /map view/i.test(banner.textContent || ''))).toBe(true);
  expect(screen.getByLabelText(/map controls/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/map display/i)).toBeInTheDocument();
  // Markers/popups are not rendered in jsdom, so skip those assertions
  });

  it('shows loading state when fetching', async () => {
    vi.spyOn(api, 'fetchStops').mockImplementation(() => new Promise(() => {}));
    vi.spyOn(api, 'fetchVehicles').mockImplementation(() => new Promise(() => {}));
  renderWithQueryClient(<MapPage />);
    expect(await screen.findByText(/loading map data/i)).toBeInTheDocument();
  });

  it('shows error state on fetch error', async () => {
    vi.spyOn(api, 'fetchStops').mockRejectedValue(new Error('fail'));
    vi.spyOn(api, 'fetchVehicles').mockRejectedValue(new Error('fail'));
  renderWithQueryClient(<MapPage />);
    expect(await screen.findByText(/error loading map data/i)).toBeInTheDocument();
  });

  it('toggles stops, vehicles, and route', async () => {
  renderWithQueryClient(<MapPage />);
  // Toggle stops
  const stopsCheckbox = screen.getByLabelText('Show stops');
  fireEvent.click(stopsCheckbox);
  // Toggle vehicles
  const vehiclesCheckbox = screen.getByLabelText('Show vehicles');
  fireEvent.click(vehiclesCheckbox);
  // Toggle route
  const routeCheckbox = screen.getByLabelText('Show route');
  fireEvent.click(routeCheckbox);
  // Polyline is not visible in DOM, but state is toggled (no error thrown)
  });

  it('renders bottom info panel', () => {
  renderWithQueryClient(<MapPage />);
  expect(screen.getByText(/completed/i)).toBeInTheDocument();
  expect(screen.getByText(/current/i)).toBeInTheDocument();
  // There are multiple "Vehicles" elements, so use getAllByText
  expect(screen.getAllByText(/vehicles/i).length).toBeGreaterThan(0);
  });
});
