import { render, screen, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import AnalyticsDashboardPage from './AnalyticsDashboardPage';

// Mock chart components to avoid rendering actual charts
vi.mock('react-chartjs-2', () => ({
  Doughnut: (props: any) => <div data-testid="doughnut-chart">Doughnut Chart</div>,
  Bar: (props: any) => <div data-testid="bar-chart">Bar Chart</div>,
  Line: (props: any) => <div data-testid="line-chart">Line Chart</div>,
}));

// Mock API calls
vi.mock('../api', () => ({
  fetchSystemHealth: vi.fn(),
  fetchMobileAnalytics: vi.fn(),
  fetchAPIAnalytics: vi.fn(),
  fetchRouteAnalytics: vi.fn(),
}));

import { fetchSystemHealth, fetchMobileAnalytics, fetchAPIAnalytics, fetchRouteAnalytics } from '../api';

describe('AnalyticsDashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });


  it('shows loading state initially', () => {
    act(() => {
      render(<AnalyticsDashboardPage />);
    });
    expect(screen.getByText(/loading analytics/i)).toBeInTheDocument();
  });

  it('shows error state if API throws', async () => {
    (fetchSystemHealth as any).mockRejectedValue(new Error('fail'));
    (fetchMobileAnalytics as any).mockResolvedValue({});
    (fetchAPIAnalytics as any).mockResolvedValue({});
    (fetchRouteAnalytics as any).mockResolvedValue({});
    await act(async () => {
      render(<AnalyticsDashboardPage />);
    });
    await waitFor(() => {
      expect(screen.getByText(/fail/i)).toBeInTheDocument();
    });
  });

  it('renders dashboard data on success', async () => {
    (fetchSystemHealth as any).mockResolvedValue({
      health_score: 95,
      status: 'OK',
      uptime: '1d',
      active_sessions: 3,
    });
    (fetchMobileAnalytics as any).mockResolvedValue({
      total_sessions: 10,
      unique_devices: 5,
      total_api_calls: 100,
      device_types: { iOS: 3, Android: 2 },
    });
    (fetchAPIAnalytics as any).mockResolvedValue({
      total_requests: 1000,
      error_rate: 0.5,
      performance: {
        avg_response_time: 0.1,
        median_response_time: 0.09,
        p95_response_time: 0.2,
        max_response_time: 0.5,
      },
    });
    (fetchRouteAnalytics as any).mockResolvedValue({
      algorithm_usage: { A: 10, B: 20 },
    });
    await act(async () => {
      render(<AnalyticsDashboardPage />);
    });
    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.getByRole('main')).toBeInTheDocument();
    });
    // Headings
    expect(screen.getByText(/analytics dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/system health/i)).toBeInTheDocument();
    expect(screen.getByText(/performance trends/i)).toBeInTheDocument();
    expect(screen.getByText(/api analytics/i)).toBeInTheDocument();
    expect(screen.getByText(/mobile usage/i)).toBeInTheDocument();
    // Chart placeholders
    expect(screen.getAllByTestId('doughnut-chart').length).toBeGreaterThan(0);
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  // Data
  expect(screen.getByText('95')).toBeInTheDocument(); // health_score
  expect(screen.getByText('OK')).toBeInTheDocument(); // status
  // There are multiple 'Sessions', so check for the correct value
  const sessionDivs = screen.getAllByText(/sessions/i);
  expect(sessionDivs.some(div => div.textContent?.includes('10'))).toBe(true); // Sessions: 10
  expect(screen.getByText(/devices/i)).toBeInTheDocument();
  expect(screen.getByText(/api calls/i)).toBeInTheDocument();
  expect(screen.getByText(/total requests/i)).toBeInTheDocument();
  expect(screen.getByText(/error rate/i)).toBeInTheDocument();
  });
});
