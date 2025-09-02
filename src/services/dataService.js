// Mock data service for routes, vehicles, drivers, analytics
export const getRoutes = () => [
  { id: 1, origin: 'A', destination: 'B', status: 'active', name: 'Route A→B', stops: 5, distance: 12 },
  { id: 2, origin: 'B', destination: 'C', status: 'planned', name: 'Route B→C', stops: 8, distance: 25 },
];

export const getVehicles = () => [
  { id: 1, number: 'RF-1001', type: 'Van', status: 'active', mileage: 12000, fuel: 78 },
  { id: 2, number: 'RF-1002', type: 'Truck', status: 'maintenance', mileage: 54000, fuel: 34 },
];

export const getDrivers = () => [
  { id: 1, name: 'Alice Johnson', status: 'on-duty', routes: 2, rating: 4.9, phone: '555-0101' },
  { id: 2, name: 'Bob Smith', status: 'on-break', routes: 1, rating: 4.6, phone: '555-0102' },
];

export const getAnalytics = () => ({
  totalRoutes: 2,
  activeVehicles: 1,
  completedDeliveries: 10,
  onTimeRate: 95,
  avgDeliveryTime: 28,
  costPerMile: 2.34,
  fuelEfficiency: 8.6,
  totalDeliveries: 120
});

const API_BASE = process.env.REACT_APP_API_BASE_URL || process.env.API_BASE_URL || 'http://localhost:5000';

export const fetchRoutes = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/routes`);
    if (!res.ok) throw new Error('Network error fetching routes');
    return await res.json();
  } catch (e) {
    return Promise.resolve(getRoutes());
  }
};

export const fetchVehicles = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/vehicles`);
    if (!res.ok) throw new Error('Network error fetching vehicles');
    return await res.json();
  } catch (e) {
    return Promise.resolve(getVehicles());
  }
};

export const fetchDrivers = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/drivers`);
    if (!res.ok) throw new Error('Network error fetching drivers');
    return await res.json();
  } catch (e) {
    return Promise.resolve(getDrivers());
  }
};

export const fetchAnalytics = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/analytics`);
    if (!res.ok) throw new Error('Network error fetching analytics');
    return await res.json();
  } catch (e) {
    return Promise.resolve(getAnalytics());
  }
};

export const login = async ({ username, password, role }) => {
  try {
    const res = await fetch(`${API_BASE}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, role }),
    });
    if (!res.ok) throw new Error('Login failed');
    return await res.json();
  } catch (e) {
    // fallback to mock token
    return Promise.resolve({ token: `dev-token-${username}`, role: role || 'manager' });
  }
};
