/**
 * Map Screen for RouteForce Mobile App
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Dimensions,
} from 'react-native';
import MapView, { Marker, Polyline, Region } from 'react-native-maps';
import { useAuth } from '../context/AuthContext';

interface MapRoute {
  id: string;
  name: string;
  stores: MapStore[];
  polyline?: { latitude: number; longitude: number }[];
}

interface MapStore {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  visit_status: 'pending' | 'completed' | 'skipped';
  priority: number;
}

const { width, height } = Dimensions.get('window');

const MapScreen: React.FC = () => {
  const [routes, setRoutes] = useState<MapRoute[]>([]);
  const [selectedRoute, setSelectedRoute] = useState<MapRoute | null>(null);
  const [currentLocation, setCurrentLocation] = useState<{
    latitude: number;
    longitude: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const { apiClient } = useAuth();

  // Default to San Francisco area
  const [region, setRegion] = useState<Region>({
    latitude: 37.7749,
    longitude: -122.4194,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  });

  const loadRoutes = async () => {
    try {
      const assignedRoutes = await apiClient.getAssignedRoutes();
      const mapRoutes: MapRoute[] = assignedRoutes.map(route => ({
        id: route.id,
        name: route.name,
        stores: route.stores.map(store => ({
          id: store.id,
          name: store.name,
          address: store.address,
          lat: store.lat,
          lng: store.lng,
          visit_status: store.visit_status,
          priority: store.priority,
        })),
      }));
      
      setRoutes(mapRoutes);
      
      if (mapRoutes.length > 0) {
        setSelectedRoute(mapRoutes[0]);
        
        // Fit map to show all stores of the first route
        const stores = mapRoutes[0].stores;
        if (stores.length > 0) {
          const minLat = Math.min(...stores.map(s => s.lat));
          const maxLat = Math.max(...stores.map(s => s.lat));
          const minLng = Math.min(...stores.map(s => s.lng));
          const maxLng = Math.max(...stores.map(s => s.lng));
          
          setRegion({
            latitude: (minLat + maxLat) / 2,
            longitude: (minLng + maxLng) / 2,
            latitudeDelta: (maxLat - minLat) * 1.5,
            longitudeDelta: (maxLng - minLng) * 1.5,
          });
        }
      }
    } catch (error) {
      console.error('Error loading routes:', error);
      Alert.alert('Error', 'Failed to load route data');
    } finally {
      setLoading(false);
    }
  };

  const getCurrentLocation = () => {
    // In a real app, you'd use geolocation
    Alert.alert('Location', 'Location tracking would be implemented here');
  };

  const getMarkerColor = (store: MapStore) => {
    switch (store.visit_status) {
      case 'completed':
        return '#4caf50';
      case 'skipped':
        return '#f44336';
      default:
        return '#ff9800';
    }
  };

  const handleStorePress = (store: MapStore) => {
    Alert.alert(
      store.name,
      `Address: ${store.address}\nStatus: ${store.visit_status}\nPriority: ${store.priority}`,
      [
        { text: 'OK' },
        {
          text: 'Mark Visited',
          onPress: () => markStoreVisited(store),
        },
      ]
    );
  };

  const markStoreVisited = async (store: MapStore) => {
    if (!selectedRoute) return;
    
    try {
      await apiClient.markStoreVisited(selectedRoute.id, store.id);
      Alert.alert('Success', 'Store marked as visited');
      loadRoutes(); // Refresh the data
    } catch (error) {
      console.error('Error marking store visited:', error);
      Alert.alert('Error', 'Failed to mark store as visited');
    }
  };

  useEffect(() => {
    loadRoutes();
  }, []);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading map...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <MapView
        style={styles.map}
        region={region}
        onRegionChangeComplete={setRegion}
        showsUserLocation={true}
        showsMyLocationButton={true}
        followsUserLocation={false}
      >
        {selectedRoute?.stores.map((store) => (
          <Marker
            key={store.id}
            coordinate={{
              latitude: store.lat,
              longitude: store.lng,
            }}
            title={store.name}
            description={store.address}
            pinColor={getMarkerColor(store)}
            onPress={() => handleStorePress(store)}
          />
        ))}
        
        {selectedRoute?.polyline && (
          <Polyline
            coordinates={selectedRoute.polyline}
            strokeColor="#1976d2"
            strokeWidth={3}
            strokeOpacity={0.8}
          />
        )}
      </MapView>

      <View style={styles.controls}>
        <View style={styles.routeSelector}>
          <Text style={styles.routeSelectorLabel}>Current Route:</Text>
          <TouchableOpacity
            style={styles.routeSelectorButton}
            onPress={() => {
              // Show route selection modal
              Alert.alert('Route Selection', 'Route selection would be implemented here');
            }}
          >
            <Text style={styles.routeSelectorText}>
              {selectedRoute?.name || 'Select Route'}
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.actionButtons}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={getCurrentLocation}
          >
            <Text style={styles.actionButtonText}>My Location</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => {
              Alert.alert('Navigation', 'Navigation would be implemented here');
            }}
          >
            <Text style={styles.actionButtonText}>Navigate</Text>
          </TouchableOpacity>
        </View>

        {selectedRoute && (
          <View style={styles.routeInfo}>
            <Text style={styles.routeInfoTitle}>{selectedRoute.name}</Text>
            <Text style={styles.routeInfoText}>
              {selectedRoute.stores.filter(s => s.visit_status === 'completed').length}/
              {selectedRoute.stores.length} stores completed
            </Text>
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  map: {
    width: width,
    height: height,
  },
  controls: {
    position: 'absolute',
    top: 50,
    left: 16,
    right: 16,
  },
  routeSelector: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  routeSelectorLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  routeSelectorButton: {
    paddingVertical: 8,
  },
  routeSelectorText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  actionButton: {
    backgroundColor: '#1976d2',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 6,
    flex: 1,
    marginHorizontal: 4,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  routeInfo: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  routeInfoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  routeInfoText: {
    fontSize: 14,
    color: '#666',
  },
});

export default MapScreen;
