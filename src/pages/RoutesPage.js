import React, { useState } from 'react';
import { calculateETA, calculateFuelCost } from '../utils/routeOptimizer';

const RoutesPage = ({ routes = [] }) => {
  const [selectedRoute, setSelectedRoute] = useState(null);

  return (
    <div>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem'}}>
        <h2>Route Management</h2>
        <button style={{padding: '0.75rem 1.5rem', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', border: 'none', borderRadius: '0.5rem', cursor: 'pointer'}}>
          + Create New Route
        </button>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem'}}>
        <div>
          <div style={{background: 'white', borderRadius: '1rem', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.08)'}}>
            <table style={{width: '100%'}}>
              <thead style={{background: '#f8f9fa'}}>
                <tr>
                  <th style={{padding: '1rem', textAlign: 'left'}}>Route Name</th>
                  <th style={{padding: '1rem', textAlign: 'left'}}>Driver</th>
                  <th style={{padding: '1rem', textAlign: 'left'}}>Stops</th>
                  <th style={{padding: '1rem', textAlign: 'left'}}>Distance</th>
                  <th style={{padding: '1rem', textAlign: 'left'}}>Status</th>
                  <th style={{padding: '1rem', textAlign: 'left'}}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {routes.map(route => (
                  <tr key={route.id} style={{borderTop: '1px solid #e0e0e0'}}>
                    <td style={{padding: '1rem'}}>{route.name}</td>
                    <td style={{padding: '1rem'}}>{route.driver}</td>
                    <td style={{padding: '1rem'}}>{route.stops}</td>
                    <td style={{padding: '1rem'}}>{route.distance} mi</td>
                    <td style={{padding: '1rem'}}>
                      <span style={{
                        padding: '0.25rem 0.75rem',
                        background: route.status === 'active' ? '#e8f5e9' : route.status === 'planned' ? '#fff3e0' : '#f5f5f5',
                        color: route.status === 'active' ? '#4caf50' : route.status === 'planned' ? '#ff9800' : '#999',
                        borderRadius: '1rem',
                        fontSize: '0.875rem'
                      }}>
                        {route.status}
                      </span>
                    </td>
                    <td style={{padding: '1rem'}}>
                      <button 
                        onClick={() => setSelectedRoute(route)}
                        style={{padding: '0.5rem 1rem', background: '#667eea', color: 'white', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', marginRight: '0.5rem'}}
                      >
                        View
                      </button>
                      <button style={{padding: '0.5rem 1rem', background: '#4caf50', color: 'white', border: 'none', borderRadius: '0.25rem', cursor: 'pointer'}}>
                        Optimize
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div>
          {selectedRoute ? (
            <div style={{background: 'white', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)'}}>
              <h3>Route Details</h3>
              <div style={{marginTop: '1rem'}}>
                <p><strong>Name:</strong> {selectedRoute.name}</p>
                <p><strong>Driver:</strong> {selectedRoute.driver}</p>
                <p><strong>Total Stops:</strong> {selectedRoute.stops}</p>
                <p><strong>Distance:</strong> {selectedRoute.distance} mi</p>
                <p><strong>ETA:</strong> {calculateETA(selectedRoute.distance)}</p>
                <p><strong>Fuel Cost:</strong> ${calculateFuelCost(selectedRoute.distance)}</p>
                <div style={{marginTop: '1.5rem'}}>
                  <button style={{width: '100%', padding: '0.75rem', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', border: 'none', borderRadius: '0.5rem', cursor: 'pointer'}}>
                    Start Navigation
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div style={{background: 'white', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)'}}>
              <p>Select a route to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RoutesPage;
