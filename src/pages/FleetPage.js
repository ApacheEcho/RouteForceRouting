import React from 'react';

const FleetPage = ({ vehicles = [] }) => {
  return (
    <div>
      <h2>Fleet Management</h2>
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginTop: '2rem'}}>
        {vehicles.map(vehicle => (
          <div key={vehicle.id} style={{background: 'white', borderRadius: '1rem', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.08)'}}>
            <div style={{background: 'linear-gradient(135deg, #667eea, #764ba2)', padding: '1rem', textAlign: 'center'}}>
              <span style={{fontSize: '3rem'}}>{vehicle.type === 'Truck' ? '🚛' : vehicle.type === 'Van' ? '🚐' : '🚗'}</span>
            </div>
            <div style={{padding: '1.5rem'}}>
              <h3>{vehicle.number}</h3>
              <div style={{marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
                <div style={{display: 'flex', justifyContent: 'space-between'}}>
                  <span>Status:</span>
                  <span style={{fontWeight: 'bold', color: vehicle.status === 'active' ? '#4caf50' : '#ff9800'}}>
                    {vehicle.status}
                  </span>
                </div>
                <div style={{display: 'flex', justifyContent: 'space-between'}}>
                  <span>Mileage:</span>
                  <span style={{fontWeight: 'bold'}}>{vehicle.mileage.toLocaleString()} mi</span>
                </div>
                <div style={{display: 'flex', justifyContent: 'space-between'}}>
                  <span>Fuel Level:</span>
                  <span style={{fontWeight: 'bold'}}>{vehicle.fuel}%</span>
                </div>
                <div style={{marginTop: '0.5rem', height: '6px', background: '#e0e0e0', borderRadius: '3px', overflow: 'hidden'}}>
                  <div style={{height: '100%', width: `${vehicle.fuel}%`, background: vehicle.fuel > 50 ? '#4caf50' : vehicle.fuel > 25 ? '#ff9800' : '#f44336'}}></div>
                </div>
              </div>
              <button style={{width: '100%', marginTop: '1.5rem', padding: '0.75rem', background: '#667eea', color: 'white', border: 'none', borderRadius: '0.5rem', cursor: 'pointer'}}>
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FleetPage;
