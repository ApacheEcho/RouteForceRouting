/**
 * RouteForce PWA - Main Application Component
 */


import { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
// Lazy-loaded Pages
const LoginPage = lazy(() => import('./pages/LoginPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const RoutesPage = lazy(() => import('./pages/RoutesPage'));
const MapPage = lazy(() => import('./pages/MapPage'));
const TrackingPage = lazy(() => import('./pages/TrackingPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const AnalyticsDashboardPage = lazy(() => import('./pages/AnalyticsDashboardPage'));
// Components
const Layout = lazy(() => import('./components/Layout'));
const ProtectedRoute = lazy(() => import('./components/ProtectedRoute'));
// Styles
import './index.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});


function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <a href="#main-content" className="sr-only focus:not-sr-only focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Skip to main content</a>
          <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-lg font-semibold" aria-live="polite">Loading...</div>}>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginPage />} />

              {/* Protected routes */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Layout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="routes" element={<RoutesPage />} />
                <Route path="map" element={<MapPage />} />
                <Route path="tracking" element={<TrackingPage />} />
                <Route path="profile" element={<ProfilePage />} />
                <Route path="settings" element={<SettingsPage />} />
                <Route path="analytics" element={<AnalyticsDashboardPage />} />
              </Route>

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Suspense>
          {/* Toast notifications */}
          <Toaster
            position="top-center"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                iconTheme: {
                  primary: '#4ade80',
                  secondary: '#fff',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
