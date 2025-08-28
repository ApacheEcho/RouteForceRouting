import { act } from 'react-dom/test-utils';
import { useAuthStore } from './authStore';

describe('authStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  });

  it('has correct initial state', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('sets error on failed login', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false });
    await act(async () => {
      try {
        await useAuthStore.getState().login('bad@example.com', 'wrong');
      } catch (e) {
        // error is expected, do nothing
      }
    });
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.error).toBe('Invalid credentials');
    expect(state.user).toBeNull();
  });

  it('sets user and token on successful login', async () => {
    const fakeUser = { id: '1', email: 'test@example.com', name: 'Test User', role: 'user' };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ user: fakeUser, token: 'token123' }),
    });
    await act(async () => {
      await useAuthStore.getState().login('test@example.com', 'password');
    });
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user).toEqual(fakeUser);
    expect(state.token).toBe('token123');
    expect(state.error).toBeNull();
  });

  it('clears user and token on logout', () => {
    useAuthStore.setState({
      user: { id: '1', email: 'test@example.com', name: 'Test User', role: 'user' },
      token: 'token123',
      isAuthenticated: true,
      isLoading: false,
      error: null,
    });
    act(() => {
      useAuthStore.getState().logout();
    });
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('clears error with clearError', () => {
    useAuthStore.setState({ error: 'Some error' } as any);
    act(() => {
      useAuthStore.getState().clearError();
    });
    expect(useAuthStore.getState().error).toBeNull();
  });
});
