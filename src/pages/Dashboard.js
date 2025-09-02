import React from 'react';

const Dashboard = ({ routes = [], vehicles = [], drivers = [], analytics = {} }) => {
  return (
    <div>
      <h2>Dashboard Overview - {new Date().toLocaleDateString()}</h2>
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginTop: '2rem'}}>
        <div style={{background: 'white', padding: '2rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', textAlign: 'center'}}>
          <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: '#667eea'}}>{routes.length}</div>
          <div style={{color: '#666', marginTop: '0.5rem'}}>Total Routes</div>
        </div>
        <div style={{background: 'white', padding: '2rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', textAlign: 'center'}}>
          <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: '#667eea'}}>{vehicles.filter(v => v.status === 'active').length}</div>
          <div style={{color: '#666', marginTop: '0.5rem'}}>Active Vehicles</div>
        </div>
        <div style={{background: 'white', padding: '2rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', textAlign: 'center'}}>
          <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: '#667eea'}}>{analytics.onTimeRate || 95}%</div>
          <div style={{color: '#666', marginTop: '0.5rem'}}>On-Time Rate</div>
        </div>
        <div style={{background: 'white', padding: '2rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', textAlign: 'center'}}>
          <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: '#667eea'}}>{drivers.filter(d => d.status === 'on-duty').length}</div>
          <div style={{color: '#666', marginTop: '0.5rem'}}>Active Drivers</div>
        </div>
        <div style={{background: 'white', padding: '2rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', textAlign: 'center'}}>
          <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: '#667eea'}}>${analytics.costPerMile || '2.34'}</div>
          <div style={{color: '#666', marginTop: '0.5rem'}}>Cost Per Mile</div>
        </div>
        <div style={{background: 'white', padding: '2rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', textAlign: 'center'}}>
          <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: '#667eea'}}>{analytics.totalDeliveries || 0}</div>
          <div style={{color: '#666', marginTop: '0.5rem'}}>Total Deliveries</div>
        </div>
      </div>
    
      <div style={{marginTop: '3rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem'}}>
        <div style={{background: 'white', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)'}}>
          <h3>📊 Performance Metrics</h3>
          <div style={{marginTop: '1rem'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', padding: '0.75rem', background: '#f8f9fa', borderRadius: '0.5rem', marginBottom: '0.5rem'}}>
              <span>Fuel Efficiency</span>
              <span style={{fontWeight: 'bold'}}>{analytics.fuelEfficiency || 0} MPG</span>
            </div>
            <div style={{display: 'flex', justifyContent: 'space-between', padding: '0.75rem', background: '#f8f9fa', borderRadius: '0.5rem', marginBottom: '0.5rem'}}>
              <span>Avg Delivery Time</span>
              <span style={{fontWeight: 'bold'}}>{analytics.avgDeliveryTime || 0} min</span>
            </div>
            <div style={{display: 'flex', justifyContent: 'space-between', padding: '0.75rem', background: '#f8f9fa', borderRadius: '0.5rem'}}>
              <span>Customer Rating</span>
              <span style={{fontWeight: 'bold'}}>⭐ {analytics.customerSatisfaction || 0}</span>
            </div>
          </div>
        </div>
        
        <div style={{background: 'white', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)'}}>
          <h3>🚚 Active Routes</h3>
          <div style={{marginTop: '1rem'}}>
            {routes.filter(r => r.status === 'active').slice(0, 3).map(route => (
              <div key={route.id} style={{display: 'flex', justifyContent: 'space-between', padding: '0.75rem', background: '#f8f9fa', borderRadius: '0.5rem', marginBottom: '0.5rem'}}>
                <span>{route.name}</span>
                <span style={{color: '#4caf50', fontWeight: 'bold'}}>{route.stops} stops</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
