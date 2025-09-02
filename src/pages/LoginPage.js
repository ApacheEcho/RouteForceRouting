import React, { useState } from 'react';
import { login as apiLogin } from '../services/dataService';

const LoginPage = ({ onLogin }) => {
  const [selectedRole, setSelectedRole] = useState('manager');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const roles = [
    { id: 'manager', name: 'Manager', icon: '👔', color: '#667eea' },
    { id: 'driver', name: 'Driver', icon: '🚚', color: '#4caf50' },
    { id: 'sales', name: 'Sales', icon: '💼', color: '#ff9800' },
    { id: 'admin', name: 'Admin', icon: '⚙️', color: '#f44336' }
  ];

  const handleSignIn = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await apiLogin({ username, password, role: selectedRole });
      // result: { token, role }
      // store token (in-memory for now) and notify parent
      if (result && result.token) {
        localStorage.setItem('rf_token', result.token);
        onLogin(result.role || selectedRole);
      } else {
        onLogin(selectedRole);
      }
    } catch (e) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}}>
      <div style={{background: 'white', padding: '3rem', borderRadius: '1rem', boxShadow: '0 20px 60px rgba(0,0,0,0.3)', maxWidth: '500px', width: '100%'}}>
        <div style={{textAlign: 'center', marginBottom: '2rem'}}>
          <h1 style={{fontSize: '3rem', marginBottom: '0.5rem'}}>🚀</h1>
          <h1 style={{color: '#333', marginBottom: '0.5rem'}}>RouteForce Pro</h1>
          <p style={{color: '#666'}}>Fleet Management & Route Optimization</p>
        </div>
        
        <div style={{marginBottom: '1rem'}}>
          <label style={{display: 'block', marginBottom: '0.5rem', color: '#666'}}>Username</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} type="text" placeholder="Enter username" style={{width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '0.5rem', fontSize: '1rem'}} />
        </div>
        
        <div style={{marginBottom: '1rem'}}>
          <label style={{display: 'block', marginBottom: '0.5rem', color: '#666'}}>Password</label>
          <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Enter password" style={{width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '0.5rem', fontSize: '1rem'}} />
        </div>
        
        <div style={{marginBottom: '1rem'}}>
          <label style={{display: 'block', marginBottom: '1rem', color: '#666'}}>Select Role</label>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem'}}>
            {roles.map(role => (
              <button
                key={role.id}
                onClick={() => setSelectedRole(role.id)}
                style={{
                  padding: '1.25rem',
                  border: selectedRole === role.id ? `2px solid ${role.color}` : '2px solid #e0e0e0',
                  background: selectedRole === role.id ? `${role.color}10` : 'white',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  transition: 'all 0.3s'
                }}
              >
                <div style={{fontSize: '1.5rem'}}>{role.icon}</div>
                <div style={{fontWeight: 'bold', marginTop: '0.5rem'}}>{role.name}</div>
              </button>
            ))}
          </div>
        </div>
        
        {error && <div style={{color: 'red', marginBottom: '1rem'}}>{error}</div>}

        <button
          onClick={handleSignIn}
          disabled={loading}
          style={{
            width: '100%',
            padding: '1rem',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            fontSize: '1rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            transition: 'transform 0.2s'
          }}
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </div>
    </div>
  );
};

export default LoginPage;
