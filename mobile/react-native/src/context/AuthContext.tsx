/**
 * Authentication Context for RouteForce Mobile App
 */

import React, { createContext, useContext } from 'react';

// Update the import to use default export
interface RouteForceApiClient {
  login: (credentials: { email: string; password: string }) => Promise<any>;
  setTokens: (accessToken: string, refreshToken: string) => void;
  clearTokens: () => void;
}

export interface AuthContextType {
  signIn: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signOut: () => Promise<void>;
  isSignedIn: boolean;
  apiClient: RouteForceApiClient;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
