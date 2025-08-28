import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginPage from './LoginPage';
import { useAuth } from '../hooks/useAuth';
import * as api from '../api';
import toast from 'react-hot-toast';

vi.mock('../hooks/useAuth');
vi.mock('../api');
vi.mock('react-hot-toast');

describe('LoginPage', () => {
  const mockLogin = vi.fn();
  const mockClearError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useAuth as any).mockReturnValue({
      login: mockLogin,
      isLoading: false,
      isAuthenticated: false,
      error: '',
      clearError: mockClearError,
    });
  });

  it('renders login heading, subtitle, and demo credentials', () => {
    render(<LoginPage />);
    expect(screen.getByRole('heading', { name: /sign in to routeforce/i })).toBeInTheDocument();
    expect(screen.getByText(/access your route management dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/demo credentials/i)).toBeInTheDocument();
  });

  it('renders email and password fields and sign in button', () => {
    render(<LoginPage />);
    expect(screen.getByPlaceholderText(/email address/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('shows validation errors for invalid email and short password', async () => {
    render(<LoginPage />);
    const emailInput = screen.getByPlaceholderText(/email address/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    fireEvent.input(emailInput, { target: { value: 'bademail' } });
    fireEvent.input(passwordInput, { target: { value: '123' } });
    const form = emailInput.closest('form');
    if (form) {
      fireEvent.submit(form);
    }
    await waitFor(() => {
      expect(screen.getByText((content) => content.includes('valid email address'))).toBeInTheDocument();
      expect(screen.getByText((content) => content.includes('Password must be at least 6 characters'))).toBeInTheDocument();
    });
  });

  it('toggles password visibility', () => {
    render(<LoginPage />);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const toggleBtn = passwordInput.parentElement?.querySelector('button');
    expect(passwordInput).toHaveAttribute('type', 'password');
    if (toggleBtn) {
      fireEvent.click(toggleBtn);
      expect(passwordInput).toHaveAttribute('type', 'text');
      fireEvent.click(toggleBtn);
      expect(passwordInput).toHaveAttribute('type', 'password');
    }
  });

  it('shows loading spinner when isLoading is true', () => {
    (useAuth as any).mockReturnValue({
      login: mockLogin,
      isLoading: true,
      isAuthenticated: false,
      error: '',
      clearError: mockClearError,
    });
    render(<LoginPage />);
    // The button is disabled and has no accessible name when loading, so select by role only
  const buttons = screen.getAllByRole('button');
  // The submit button is the second button (after the password toggle)
  const submitBtn = buttons.find(btn => btn.type === 'submit');
  expect(submitBtn).toBeDisabled();
  expect(submitBtn?.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('calls login and device/session APIs on successful submit', async () => {
    (api.registerDevice as any).mockResolvedValue({});
    (api.trackSession as any).mockResolvedValue({});
    mockLogin.mockResolvedValue({});
    render(<LoginPage />);
    fireEvent.change(screen.getByPlaceholderText(/email address/i), { target: { value: 'user@example.com' } });
    fireEvent.change(screen.getByPlaceholderText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    await waitFor(() => {
      expect(mockClearError).toHaveBeenCalled();
      expect(mockLogin).toHaveBeenCalledWith('user@example.com', 'password123');
      expect(api.registerDevice).toHaveBeenCalled();
      expect(api.trackSession).toHaveBeenCalled();
      expect(toast.success).toHaveBeenCalledWith(expect.stringMatching(/welcome back/i));
    });
  });

  it('shows error toast on failed login', async () => {
    mockLogin.mockRejectedValue(new Error('fail'));
    (useAuth as any).mockReturnValue({
      login: mockLogin,
      isLoading: false,
      isAuthenticated: false,
      error: 'Login failed',
      clearError: mockClearError,
    });
    render(<LoginPage />);
    fireEvent.change(screen.getByPlaceholderText(/email address/i), { target: { value: 'user@example.com' } });
    fireEvent.change(screen.getByPlaceholderText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Login failed');
    });
  });
});
