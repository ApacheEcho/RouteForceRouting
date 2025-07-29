/**
 * RouteForce Mobile App - Main Application Component
 * React Native TypeScript Application
 */

import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import RouteScreen from './src/screens/RouteScreen';
import MapScreen from './src/screens/MapScreen';
import TrackingScreen from './src/screens/TrackingScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import SettingsScreen from './src/screens/SettingsScreen';

// Services
import RouteForceApiClient from '../shared/api/client';
import { AuthContext, AuthContextType } from './src/context/AuthContext';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Theme configuration
const theme = {
  colors: {
    primary: '#1976d2',
    accent: '#03dac4',
    background: '#f5f5f5',
    surface: '#ffffff',
    text: '#000000',
    placeholder: '#757575',
  },
};

// Tab Navigator for authenticated users
function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName = '';

          switch (route.name) {
            case 'Dashboard':
              iconName = 'dashboard';
              break;
            case 'Routes':
              iconName = 'route';
              break;
            case 'Map':
              iconName = 'map';
              break;
            case 'Tracking':
              iconName = 'location-on';
              break;
            case 'Profile':
              iconName = 'person';
              break;
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: '#757575',
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: '#ffffff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ title: 'Dashboard' }}
      />
      <Tab.Screen 
        name="Routes" 
        component={RouteScreen}
        options={{ title: 'My Routes' }}
      />
      <Tab.Screen 
        name="Map" 
        component={MapScreen}
        options={{ title: 'Live Map' }}
      />
      <Tab.Screen 
        name="Tracking" 
        component={TrackingScreen}
        options={{ title: 'Tracking' }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ title: 'Profile' }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [userToken, setUserToken] = useState<string | null>(null);
  const [apiClient] = useState(new RouteForceApiClient());

  // Check for existing authentication on app start
  useEffect(() => {
    const bootstrapAsync = async () => {
      try {
        const token = await AsyncStorage.getItem('userToken');
        const refreshToken = await AsyncStorage.getItem('refreshToken');
        
        if (token && refreshToken) {
          apiClient.setTokens(token, refreshToken);
          setUserToken(token);
        }
      } catch (e) {
        console.error('Error loading authentication state:', e);
      } finally {
        setIsLoading(false);
      }
    };

    bootstrapAsync();
  }, []);

  const authContext: AuthContextType = {
    signIn: async (email: string, password: string) => {
      try {
        const response = await apiClient.login({ email, password });
        
        if (response.success) {
          await AsyncStorage.setItem('userToken', response.access_token);
          await AsyncStorage.setItem('refreshToken', response.refresh_token);
          await AsyncStorage.setItem('driverId', response.driver_id);
          
          apiClient.setTokens(response.access_token, response.refresh_token);
          setUserToken(response.access_token);
          
          return { success: true };
        } else {
          return { success: false, error: 'Invalid credentials' };
        }
      } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: 'Network error' };
      }
    },
    
    signOut: async () => {
      try {
        await AsyncStorage.multiRemove(['userToken', 'refreshToken', 'driverId']);
        apiClient.clearTokens();
        setUserToken(null);
      } catch (error) {
        console.error('Logout error:', error);
      }
    },
    
    isSignedIn: !!userToken,
    apiClient,
  };

  if (isLoading) {
    // TODO: Add proper splash screen
    return null;
  }

  return (
    <PaperProvider theme={theme}>
      <AuthContext.Provider value={authContext}>
        <NavigationContainer>
          <Stack.Navigator screenOptions={{ headerShown: false }}>
            {userToken == null ? (
              // No token found, user isn't signed in
              <Stack.Screen 
                name="Login" 
                component={LoginScreen}
                options={{
                  title: 'Sign In',
                  animationTypeForReplace: !userToken ? 'pop' : 'push',
                }}
              />
            ) : (
              // User is signed in
              <>
                <Stack.Screen name="Main" component={MainTabNavigator} />
                <Stack.Screen 
                  name="Settings" 
                  component={SettingsScreen}
                  options={{ 
                    headerShown: true,
                    title: 'Settings',
                    headerStyle: { backgroundColor: theme.colors.primary },
                    headerTintColor: '#ffffff',
                  }}
                />
              </>
            )}
          </Stack.Navigator>
        </NavigationContainer>
      </AuthContext.Provider>
    </PaperProvider>
  );
}
