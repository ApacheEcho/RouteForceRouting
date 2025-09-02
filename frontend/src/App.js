import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState('Checking...');

  useEffect(() => {
    fetch('http://localhost:5000/api/health')
      .then(res => res.json())
      .then(data => setHealth('Connected ✅'))
      .catch(() => setHealth('Not connected ❌'));

    fetch('http://localhost:5000/api/dashboard/stats')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(console.error);
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>🚀 RouteForce Pro</h1>
        <p>Backend Status: <strong>{health}</strong></p>
      </header>
      
      {stats && (
        <div className="dashboard">
          <h2>Dashboard Overview</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{stats.total_routes}</div>
              <div className="stat-label">Total Routes</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.active_routes}</div>
              <div className="stat-label">Active Routes</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.total_drivers}</div>
              <div className="stat-label">Total Drivers</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.total_vehicles}</div>
              <div className="stat-label">Total Vehicles</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.deliveries_today}</div>
              <div className="stat-label">Deliveries Today</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.on_time_rate}%</div>
              <div className="stat-label">On-Time Rate</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
