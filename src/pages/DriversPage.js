import React from 'react';

const DriversPage = ({ drivers = [] }) => {
  return (
    <div>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem'}}>
        <h2>Driver Management</h2>
        <button style={{padding: '0.75rem 1.5rem', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', border: 'none', borderRadius: '0.5rem', cursor: 'pointer'}}>
          + Add Driver
        </button>
      </div>
      
      <div style={{background: 'white', borderRadius: '1rem', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.08)'}}>
        <table style={{width: '100%'}}>
          <thead style={{background: '#f8f9fa'}}>
            <tr>
              <th style={{padding: '1rem', textAlign: 'left'}}>Name</th>
              <th style={{padding: '1rem', textAlign: 'left'}}>Status</th>
              <th style={{padding: '1rem', textAlign: 'left'}}>Routes Today</th>
              <th style={{padding: '1rem', textAlign: 'left'}}>Rating</th>
              <th style={{padding: '1rem', textAlign: 'left'}}>Phone</th>
              <th style={{padding: '1rem', textAlign: 'left'}}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {drivers.map(driver => (
              <tr key={driver.id} style={{borderTop: '1px solid #e0e0e0'}}>
                <td style={{padding: '1rem'}}>{driver.name}</td>
                <td style={{padding: '1rem'}}>
                  <span style={{
                    padding: '0.25rem 0.75rem',
                    background: driver.status === 'on-duty' ? '#e8f5e9' : driver.status === 'on-break' ? '#fff3e0' : '#f5f5f5',
                    color: driver.status === 'on-duty' ? '#4caf50' : driver.status === 'on-break' ? '#ff9800' : '#999',
                    borderRadius: '1rem',
                    fontSize: '0.875rem'
                  }}>
                    {driver.status}
                  </span>
                </td>
                <td style={{padding: '1rem'}}>{driver.routes}</td>
                <td style={{padding: '1rem'}}>⭐ {driver.rating}</td>
                <td style={{padding: '1rem'}}>{driver.phone}</td>
                <td style={{padding: '1rem'}}>
                  <button style={{padding: '0.5rem 1rem', background: '#667eea', color: 'white', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', marginRight: '0.5rem'}}>
                    Assign Route
                  </button>
                  <button style={{padding: '0.5rem 1rem', background: '#f0f0f0', color: '#333', border: 'none', borderRadius: '0.25rem', cursor: 'pointer'}}>
                    View Profile
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DriversPage;
