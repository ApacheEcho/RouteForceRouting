/**
 * RouteForce PWA - Authentication Store
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

const API_BASE_URL = 'http://localhost:5000/api';

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,


      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
          });
          if (!response.ok) {
            throw new Error('Invalid credentials');
          }
          const data = await response.json();
          set({
            user: data.user,
            token: data.token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Login failed',
            isLoading: false,
          });
          throw error;
        }
      },

      // Validate token with backend
      validateToken: async (token: string | null) => {
        if (!token) return false;
        try {
          const response = await fetch(`${API_BASE_URL}/auth/validate`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
          });
          if (!response.ok) return false;
          const data = await response.json();
          return data.valid === true;
        } catch {
          return false;
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },


      checkAuth: async () => {
        const { token, logout } = get();
        if (!token) {
          set({ isAuthenticated: false });
          return;
        }
        set({ isLoading: true });
        const valid = await get().validateToken(token);
        if (valid) {
          set({ isAuthenticated: true, isLoading: false });
        } else {
          set({ isAuthenticated: false, isLoading: false, user: null, token: null });
          logout();
        }
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
