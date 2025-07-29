# RouteForce Shared API Client

This directory contains the shared TypeScript API client for both React Native and PWA applications.

## Features

- **Type-safe API calls** with full TypeScript support
- **Authentication management** with automatic token handling
- **Error handling** with custom error types
- **Utility functions** for formatting and calculations
- **Platform-agnostic** design works with both React Native and web

## Usage

### Basic Setup

```typescript
import { RouteForceAPI, apiClient } from './apiClient';

// Use the default instance
const user = await apiClient.login({
  email: 'user@example.com',
  password: 'password'
});

// Or create a custom instance
const api = new RouteForceAPI('https://api.yourserver.com');
```

### Authentication

```typescript
// Login
const { user, token } = await apiClient.login({
  email: 'admin@routeforce.com',
  password: 'password123'
});

// Token is automatically stored and used for subsequent requests
const routes = await apiClient.getRoutes();

// Logout
await apiClient.logout();
```

### Route Management

```typescript
// Get all routes
const routes = await apiClient.getRoutes();

// Get specific route
const route = await apiClient.getRoute('route-id');

// Create new route
const newRoute = await apiClient.createRoute({
  name: 'New Delivery Route',
  status: 'planned'
});

// Optimize route
const optimizedRoute = await apiClient.optimizeRoute({
  algorithm: 'genetic',
  stores: [
    { name: 'Store A', address: '123 Main St' },
    { name: 'Store B', address: '456 Oak Ave' }
  ]
});
```

### Real-time Tracking

```typescript
// Get vehicle tracking data
const trackingData = await apiClient.getTrackingData('vehicle-id');

// Update vehicle location
await apiClient.updateVehicleLocation('vehicle-id', 45.5152, -122.6784);
```

### Error Handling

```typescript
import { handleAPIError, APIError } from './apiClient';

try {
  await apiClient.getRoutes();
} catch (error) {
  const message = handleAPIError(error);
  console.error(message);
  
  if (error instanceof APIError && error.status === 401) {
    // Handle unauthorized access
    // Redirect to login
  }
}
```

### Utility Functions

```typescript
import { formatDistance, formatDuration, calculateEfficiency } from './apiClient';

// Format distances
const distance = formatDistance(1500); // "1.5 km"

// Format durations
const duration = formatDuration(3900); // "1h 5m"

// Calculate route efficiency
const efficiency = calculateEfficiency(120, 100); // 83%
```

## Types

All API types are exported and can be used throughout your application:

```typescript
import { Route, Stop, Vehicle, User } from './apiClient';

const route: Route = {
  id: '1',
  name: 'Delivery Route',
  status: 'active',
  // ... other properties
};
```

## Configuration

The API client uses sensible defaults but can be configured:

```typescript
const api = new RouteForceAPI('https://your-api-server.com/api');

// Set custom headers or interceptors as needed
```

## Platform Compatibility

This client works seamlessly with:
- **React Native** using the built-in fetch API
- **PWA/Web** using the browser's fetch API
- **Node.js** environments (with appropriate polyfills)

The client automatically handles platform-specific differences and provides a consistent interface across all platforms.
