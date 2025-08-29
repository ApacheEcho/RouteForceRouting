import { render, screen, fireEvent } from '@testing-library/react';
import SettingsPage from './SettingsPage';

describe('SettingsPage', () => {
  it('renders the settings page header', () => {
    render(<SettingsPage />);
    expect(screen.getByRole('main')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /settings/i })).toBeInTheDocument();
  });

  it('renders all settings sections', () => {
    render(<SettingsPage />);
    // Check for common section headings or labels
    expect(screen.getByText(/account/i)).toBeInTheDocument();
    expect(screen.getByText(/notifications/i)).toBeInTheDocument();
    expect(screen.getByText(/privacy/i)).toBeInTheDocument();
    expect(screen.getByText(/theme/i)).toBeInTheDocument();
  });

  it('toggles dark mode if present', () => {
    render(<SettingsPage />);
    const themeToggle = screen.queryByLabelText(/dark mode|theme/i);
    if (themeToggle) {
      fireEvent.click(themeToggle);
      // No assertion, just ensure no error is thrown
    }
  });

  it('renders save button and is clickable', () => {
    render(<SettingsPage />);
    const saveBtn = screen.getByRole('button', { name: /save/i });
    expect(saveBtn).toBeInTheDocument();
    fireEvent.click(saveBtn);
    // No modal expected, just ensure button is clickable
  });

  it('renders all regions with correct labels', () => {
    render(<SettingsPage />);
    expect(screen.getByRole('region', { name: /account/i })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: /notifications/i })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: /privacy/i })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: /theme/i })).toBeInTheDocument();
  });
});
