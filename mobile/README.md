# RouteForce Mobile Apps

This directory contains the mobile applications for RouteForce Routing system.

## Structure

```
mobile/
├── README.md                    # This file
├── shared/                      # Shared utilities and configurations
│   ├── api/                     # API client libraries
│   ├── models/                  # Data models
│   └── utils/                   # Utility functions
├── ios/                         # iOS application (React Native)
├── android/                     # Android application (React Native)
└── web-mobile/                  # PWA mobile web version
```

## Applications

### 1. iOS App (React Native)
- **Platform**: iOS 13+
- **Tech Stack**: React Native, TypeScript
- **Features**: Driver app, route management, real-time tracking

### 2. Android App (React Native)
- **Platform**: Android 8.0+ (API 26+)
- **Tech Stack**: React Native, TypeScript
- **Features**: Driver app, route management, real-time tracking

### 3. PWA Mobile Web
- **Platform**: Cross-platform web
- **Tech Stack**: Progressive Web App, TypeScript
- **Features**: Lightweight version with offline capabilities

## API Integration

All mobile apps integrate with the RouteForce backend via:
- **Base URL**: `http://localhost:5001/api/mobile`
- **Authentication**: JWT tokens
- **Real-time**: WebSocket connections
- **Offline**: Service worker caching

## Getting Started

### Prerequisites
- Node.js 18+
- React Native CLI
- iOS: Xcode 14+
- Android: Android Studio

### Setup
```bash
cd mobile
npm install
cd ios && pod install  # iOS only
```

### Development
```bash
# iOS
npm run ios

# Android  
npm run android

# PWA
npm run web
```

## Features

### Core Features
- ✅ Driver authentication
- ✅ Route assignment and display
- ✅ Real-time GPS tracking
- ✅ Offline route caching
- ✅ Push notifications
- ✅ Route optimization feedback

### Advanced Features
- 🚧 Voice navigation
- 🚧 AR route overlay
- 🚧 Driver performance analytics
- 🚧 Fleet management
- 🚧 Customer communication

## API Endpoints Used

### Authentication
- `POST /api/mobile/auth/login`
- `POST /api/mobile/auth/refresh`
- `GET /api/mobile/auth/profile`

### Routes
- `GET /api/mobile/routes/assigned`
- `GET /api/mobile/routes/{id}`
- `POST /api/mobile/routes/{id}/status`

### Tracking
- `POST /api/mobile/tracking/location`
- `GET /api/mobile/tracking/status`

### Optimization
- `POST /api/mobile/optimize/feedback`
- `GET /api/mobile/optimize/suggestions`

## Development Status

- [x] API endpoints implemented
- [x] Mobile API documentation
- [ ] React Native project setup
- [ ] iOS app foundation
- [ ] Android app foundation
- [ ] PWA foundation
- [ ] Authentication flow
- [ ] Route display
- [ ] GPS tracking
- [ ] Offline functionality

## Next Steps

1. **Project Setup**: Initialize React Native projects
2. **Authentication**: Implement login/logout flows
3. **Route Display**: Show assigned routes with maps
4. **GPS Tracking**: Real-time location updates
5. **Offline Mode**: Cache routes for offline use
6. **Testing**: Unit and integration tests
7. **Deployment**: App store preparation
