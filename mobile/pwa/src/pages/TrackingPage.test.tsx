
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TrackingPage from './TrackingPage';

// Mock the API calls to prevent network errors and allow UI to render
import { vi } from 'vitest';
vi.mock('../api', () => ({
  fetchTelemetry: vi.fn(() => Promise.resolve([])),
  trackSession: vi.fn(() => Promise.resolve()),
}));

describe('TrackingPage', () => {

  it('renders the tracking page header and subtitle', async () => {
    render(<TrackingPage />);
    expect(await screen.findByRole('heading', { name: /live tracking/i })).toBeInTheDocument();
    expect(await screen.findByText(/real-time vehicle and route monitoring/i)).toBeInTheDocument();
  });

  it('renders vehicle status card with vehicle name, id, and status', async () => {
    render(<TrackingPage />);
    expect(await screen.findByText(/delivery truck a/i)).toBeInTheDocument();
    expect(await screen.findByText(/id: vh001/i)).toBeInTheDocument();
    expect(await screen.findByText(/moving/i)).toBeInTheDocument();
    expect(await screen.findByText(/current speed/i)).toBeInTheDocument();
    expect(await screen.findByText(/last update/i)).toBeInTheDocument();
    expect(await screen.findByText(/current location/i)).toBeInTheDocument();
    expect(await screen.findByText(/456 center ave, portland, or/i)).toBeInTheDocument();
  });

  it('renders route progress section', async () => {
    render(<TrackingPage />);
    expect(await screen.findByText(/route progress/i)).toBeInTheDocument();
    expect(await screen.findByText(/7 of 12 stops completed/i)).toBeInTheDocument();
    expect(await screen.findByText(/58%/i)).toBeInTheDocument();
  });

  it('renders next stop section', async () => {
    render(<TrackingPage />);
    expect(await screen.findByText(/next stop/i)).toBeInTheDocument();
    expect(await screen.findByText(/suburban plaza/i)).toBeInTheDocument();
    expect(await screen.findByText(/eta: 15 minutes/i)).toBeInTheDocument();
    expect(await screen.findByText(/2.3 km away/i)).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /navigate/i })).toBeInTheDocument();
  });

  it('renders quick action buttons', async () => {
    render(<TrackingPage />);
    expect(await screen.findByText(/view on map/i)).toBeInTheDocument();
    expect(await screen.findByText(/send alert/i)).toBeInTheDocument();
  });

  it('toggles tracking state when pause/resume button is clicked', async () => {
    render(<TrackingPage />);
    const pauseBtn = await screen.findByRole('button', { name: /pause tracking/i });
    expect(pauseBtn).toBeInTheDocument();
    fireEvent.click(pauseBtn);
    // After clicking, the button should now be for resuming
    expect(await screen.findByRole('button', { name: /resume tracking/i })).toBeInTheDocument();
  });

  it('shows loading state initially', async () => {
    // To test loading, we need to mock useState to return loading=true
    // This is a smoke test to ensure the loading UI is present
    render(<TrackingPage />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText(/loading vehicle data/i)).toBeInTheDocument();
  });
});
