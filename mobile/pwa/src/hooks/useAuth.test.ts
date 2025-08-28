
import { renderHook, act } from '@testing-library/react';
import { useAuth } from './useAuth';
import { useAuthStore } from '../stores/authStore';

// Mock zustand store
vi.mock('../stores/authStore');

const mockUser = { id: '1', email: 'test@example.com', name: 'Test User', role: 'user' };

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns default auth state', () => {
    (useAuthStore as unknown as { mockReturnValue: Function }).mockReturnValue({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      login: vi.fn(),
      logout: vi.fn(),
      checkAuth: vi.fn(),
      clearError: vi.fn(),
    });
    const { result } = renderHook(() => useAuth());
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('returns authenticated state', () => {
    (useAuthStore as unknown as { mockReturnValue: Function }).mockReturnValue({
      user: mockUser,
      token: 'token123',
      isAuthenticated: true,
      isLoading: false,
      error: null,
      login: vi.fn(),
      logout: vi.fn(),
      checkAuth: vi.fn(),
      clearError: vi.fn(),
    });
    const { result } = renderHook(() => useAuth());
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.token).toBe('token123');
  });

  it('calls login and logout', () => {
    const login = vi.fn();
    const logout = vi.fn();
    (useAuthStore as unknown as { mockReturnValue: Function }).mockReturnValue({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      login,
      logout,
      checkAuth: vi.fn(),
      clearError: vi.fn(),
    });
    const { result } = renderHook(() => useAuth());
    act(() => {
      result.current.login('test@example.com', 'password');
      result.current.logout();
    });
    expect(login).toHaveBeenCalledWith('test@example.com', 'password');
    expect(logout).toHaveBeenCalled();
  });

  it('calls clearError', () => {
    const clearError = vi.fn();
    (useAuthStore as unknown as { mockReturnValue: Function }).mockReturnValue({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: 'Some error',
      login: vi.fn(),
      logout: vi.fn(),
      checkAuth: vi.fn(),
      clearError,
    });
    const { result } = renderHook(() => useAuth());
    act(() => {
      result.current.clearError();
    });
    expect(clearError).toHaveBeenCalled();
  });
});
