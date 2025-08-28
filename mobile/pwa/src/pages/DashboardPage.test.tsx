import { render, screen } from '@testing-library/react';
import DashboardPage from './DashboardPage';

describe('DashboardPage', () => {
  it('renders dashboard heading and welcome message', () => {
    render(<DashboardPage />);
    expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
    expect(screen.getByText(/welcome back/i)).toBeInTheDocument();
  });

  it('renders all stat cards with correct names and values', () => {
    render(<DashboardPage />);
    const stats = [
      { name: 'Active Routes', value: '12' },
      { name: 'Total Distance', value: '2,847 km' },
      { name: 'Avg. Time Saved', value: '23 min' },
      { name: 'Cost Savings', value: '$3,247' },
    ];
    stats.forEach(({ name, value }) => {
      const region = screen.getByRole('region', { name });
      expect(region).toBeInTheDocument();
      expect(screen.getByText(name)).toBeInTheDocument();
      expect(screen.getByText(value)).toBeInTheDocument();
    });
  });

  it('renders all recent alerts with correct messages and types', () => {
    render(<DashboardPage />);
    const alerts = [
      'Route optimization completed for Downtown area',
      'Traffic delay detected on Route #7',
      'Vehicle maintenance scheduled for tomorrow',
    ];
    alerts.forEach((msg) => {
      expect(screen.getByText(msg)).toBeInTheDocument();
    });
    // Check alert types by aria-label
    expect(screen.getByLabelText('Success')).toBeInTheDocument();
    expect(screen.getByLabelText('Warning')).toBeInTheDocument();
    expect(screen.getByLabelText('Info')).toBeInTheDocument();
  });

  it('renders all quick action buttons with correct labels', () => {
    render(<DashboardPage />);
    expect(screen.getByRole('button', { name: /generate route report/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /optimize routes/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /track vehicles/i })).toBeInTheDocument();
  });
});
