import React, { useState, useEffect } from 'react';
import './App.css';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import RoutesPage from './pages/RoutesPage';
import FleetPage from './pages/FleetPage';
import DriversPage from './pages/DriversPage';
import AnalyticsPage from './pages/AnalyticsPage';
import { fetchRoutes, fetchVehicles, fetchDrivers, fetchAnalytics } from './services/dataService';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userRole, setUserRole] = useState('');
  const [activeView, setActiveView] = useState('dashboard');
  const [routes, setRoutes] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [analytics, setAnalytics] = useState({});

  useEffect(() => {
    // Load data when component mounts
    fetchRoutes().then(setRoutes);
    fetchVehicles().then(setVehicles);
    fetchDrivers().then(setDrivers);
    fetchAnalytics().then(setAnalytics);
  }, []);

  const handleLogin = (role) => {
    setIsLoggedIn(true);
    setUserRole(role);
    setActiveView('dashboard');
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserRole('');
  };

  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
            <h1 style={{margin: 0}}>🚀 RouteForce Pro</h1>
            <span className="badge">{userRole.toUpperCase()}</span>
          </div>
          <div style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
            <span className="status">⚡ Live</span>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </header>
      
      <nav className="nav-bar">
        <button 
          className={activeView === 'dashboard' ? 'active' : ''} 
          onClick={() => setActiveView('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={activeView === 'routes' ? 'active' : ''} 
          onClick={() => setActiveView('routes')}
        >
          📍 Routes
        </button>
        <button 
          className={activeView === 'fleet' ? 'active' : ''} 
          onClick={() => setActiveView('fleet')}
        >
          🚛 Fleet
        </button>
        <button 
          className={activeView === 'drivers' ? 'active' : ''} 
          onClick={() => setActiveView('drivers')}
        >
          👥 Drivers
        </button>
        <button 
          className={activeView === 'analytics' ? 'active' : ''} 
          onClick={() => setActiveView('analytics')}
        >
          📈 Analytics
        </button>
      </nav>
      
      <main className="main-content">
        {activeView === 'dashboard' && (
          <Dashboard 
            routes={routes} 
            vehicles={vehicles} 
            drivers={drivers} 
            analytics={analytics} 
          />
        )}
        {activeView === 'routes' && <RoutesPage routes={routes} />}
        {activeView === 'fleet' && <FleetPage vehicles={vehicles} />}
        {activeView === 'drivers' && <DriversPage drivers={drivers} />}
        {activeView === 'analytics' && <AnalyticsPage analytics={analytics} />}
      </main>
    </div>
  );
}

export default App;
