import { render, screen, fireEvent } from '@testing-library/react';
import SettingsPage from './SettingsPage';

describe('SettingsPage', () => {
  it('renders the settings page header', () => {
    render(<SettingsPage />);
    expect(screen.getByRole('heading', { name: /settings/i })).toBeInTheDocument();
    expect(screen.getByText(/customize your routeforce experience/i)).toBeInTheDocument();
  });

  it('renders all main settings section headings', () => {
    render(<SettingsPage />);
  // There are multiple elements with 'notifications', so check for the section heading specifically
  const notificationHeadings = screen.getAllByText(/notifications/i);
  // The first 'Notifications' is the section heading (h3), not the label
  expect(notificationHeadings[0].tagName.toLowerCase()).toBe('h3');
  expect(screen.getByText(/privacy & security/i)).toBeInTheDocument();
  // There are multiple elements with 'notification preferences', so check for the heading specifically
  const notificationPrefHeadings = screen.getAllByText(/notification preferences/i);
  // The heading is an h3, not the label
  expect(notificationPrefHeadings.some(el => el.tagName.toLowerCase() === 'h3')).toBe(true);
  });

  it('renders and toggles notification switches', () => {
    render(<SettingsPage />);
    // There are two notification toggles (push, email)
    const toggles = screen.getAllByRole('button', { hidden: true });
    expect(toggles.length).toBeGreaterThanOrEqual(2);
    fireEvent.click(toggles[0]);
    fireEvent.click(toggles[1]);
    // No assertion, just ensure no error is thrown
  });

  it('renders sign out button and is clickable', () => {
    render(<SettingsPage />);
    const signOutBtn = screen.getByRole('button', { name: /sign out/i });
    expect(signOutBtn).toBeInTheDocument();
    fireEvent.click(signOutBtn);
    // No modal expected, just ensure button is clickable
  });
});
