# RouteForce Mobile App

React Native application for RouteForce route optimization and driver management.

## Features

- 🚗 **Driver Dashboard**: View assigned routes and manage deliveries
- 🗺️ **Interactive Maps**: Real-time navigation with route optimization
- 📍 **GPS Tracking**: Live location tracking and route progress
- 📱 **Offline Mode**: Continue working without internet connection
- 🔔 **Push Notifications**: Route updates and important alerts
- 📊 **Performance Analytics**: Track delivery metrics and efficiency
- 🔐 **Secure Authentication**: Biometric and token-based login
- 🎯 **Route Optimization**: AI-powered route suggestions

## Prerequisites

- Node.js 18+
- React Native CLI
- iOS: Xcode 14+ and iOS Simulator
- Android: Android Studio and Android SDK

## Quick Start

```bash
# Install dependencies
npm install

# iOS setup
cd ios && pod install && cd ..

# Start Metro bundler
npm start

# Run on iOS
npm run ios

# Run on Android
npm run android
```

## Project Structure

```
src/
├── components/           # Reusable UI components
├── screens/             # Application screens
├── navigation/          # Navigation configuration
├── services/           # API and data services
├── store/              # Redux store and slices
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── types/              # TypeScript type definitions
├── assets/             # Images, fonts, etc.
└── config/             # App configuration
```

## Key Technologies

- **React Native 0.73**: Cross-platform mobile framework
- **TypeScript**: Type-safe development
- **React Navigation**: Navigation management
- **Redux Toolkit**: State management
- **React Native Maps**: Interactive maps
- **Geolocation Services**: GPS tracking
- **Push Notifications**: Real-time alerts
- **AsyncStorage**: Local data persistence
- **Keychain**: Secure credential storage

## Development

### Running Tests
```bash
npm test
```

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

### Building for Production

#### iOS
```bash
npm run build:ios
```

#### Android
```bash
npm run build:android
```

## Configuration

### Environment Variables
Create `.env` file:
```
API_BASE_URL=http://localhost:5001
MAPS_API_KEY=your_google_maps_key
PUSH_NOTIFICATION_KEY=your_firebase_key
```

### Permissions

#### iOS (Info.plist)
- Location access
- Camera access
- Microphone access
- Push notifications

#### Android (AndroidManifest.xml)
- ACCESS_FINE_LOCATION
- ACCESS_COARSE_LOCATION
- CAMERA
- RECORD_AUDIO
- VIBRATE

## API Integration

The app integrates with RouteForce backend APIs:
- Authentication endpoints
- Route management
- Driver tracking
- Analytics data
- Real-time updates

## Deployment

### iOS App Store
1. Build release version
2. Archive in Xcode
3. Upload to App Store Connect
4. Submit for review

### Google Play Store
1. Generate signed APK
2. Upload to Google Play Console
3. Submit for review

## Troubleshooting

### Common Issues

#### Metro bundler not starting
```bash
npm start -- --reset-cache
```

#### iOS build failures
```bash
cd ios && pod install && cd ..
npm run clean
```

#### Android build failures
```bash
cd android && ./gradlew clean && cd ..
```

## Contributing

1. Create feature branch
2. Make changes
3. Add tests
4. Submit pull request

## Performance

- Code splitting for optimal bundle size
- Image optimization and lazy loading
- Efficient list rendering with FlatList
- Background task optimization
- Memory leak prevention

## Security

- Secure credential storage with Keychain
- API request encryption
- Biometric authentication
- Certificate pinning
- Data validation and sanitization
