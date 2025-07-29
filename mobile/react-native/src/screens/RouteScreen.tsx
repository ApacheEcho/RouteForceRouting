/**
 * Route Screen for RouteForce Mobile App
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  Alert,
} from 'react-native';
import { useAuth } from '../context/AuthContext';

interface Route {
  id: string;
  name: string;
  stores: Store[];
  status: 'assigned' | 'in_progress' | 'completed';
  created_at: string;
  updated_at: string;
  total_distance: number;
  estimated_duration: number;
}

interface Store {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  priority: number;
  visit_status: 'pending' | 'completed' | 'skipped';
  visit_time?: string;
}

const RouteScreen: React.FC = () => {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const { apiClient } = useAuth();

  const loadRoutes = async () => {
    try {
      const assignedRoutes = await apiClient.getAssignedRoutes();
      setRoutes(assignedRoutes);
    } catch (error) {
      console.error('Error loading routes:', error);
      Alert.alert('Error', 'Failed to load routes');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadRoutes();
  };

  const handleRoutePress = (route: Route) => {
    // Navigate to route details
    Alert.alert('Route Details', `Selected: ${route.name}`);
  };

  const handleStartRoute = async (routeId: string) => {
    try {
      await apiClient.updateRouteStatus(routeId, 'in_progress');
      Alert.alert('Success', 'Route started successfully');
      loadRoutes(); // Refresh the list
    } catch (error) {
      console.error('Error starting route:', error);
      Alert.alert('Error', 'Failed to start route');
    }
  };

  const handleCompleteRoute = async (routeId: string) => {
    Alert.alert(
      'Complete Route',
      'Are you sure you want to mark this route as completed?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Complete',
          onPress: async () => {
            try {
              await apiClient.updateRouteStatus(routeId, 'completed');
              Alert.alert('Success', 'Route completed successfully');
              loadRoutes();
            } catch (error) {
              console.error('Error completing route:', error);
              Alert.alert('Error', 'Failed to complete route');
            }
          },
        },
      ]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#4caf50';
      case 'in_progress':
        return '#ff9800';
      case 'assigned':
        return '#2196f3';
      default:
        return '#757575';
    }
  };

  const getProgressPercentage = (route: Route) => {
    const completed = route.stores.filter(s => s.visit_status === 'completed').length;
    return Math.round((completed / route.stores.length) * 100);
  };

  const renderRouteItem = ({ item: route }: { item: Route }) => {
    const progress = getProgressPercentage(route);
    const completedStores = route.stores.filter(s => s.visit_status === 'completed').length;

    return (
      <TouchableOpacity
        style={styles.routeCard}
        onPress={() => handleRoutePress(route)}
      >
        <View style={styles.routeHeader}>
          <Text style={styles.routeName}>{route.name}</Text>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(route.status) }]}>
            <Text style={styles.statusText}>{route.status}</Text>
          </View>
        </View>

        <View style={styles.routeInfo}>
          <Text style={styles.routeDetail}>
            Progress: {completedStores}/{route.stores.length} stores ({progress}%)
          </Text>
          <Text style={styles.routeDetail}>
            Distance: {route.total_distance.toFixed(1)} km
          </Text>
          <Text style={styles.routeDetail}>
            Estimated: {Math.round(route.estimated_duration / 60)} minutes
          </Text>
        </View>

        <View style={styles.progressBarContainer}>
          <View style={styles.progressBarBackground}>
            <View 
              style={[styles.progressBarFill, { width: `${progress}%` }]}
            />
          </View>
        </View>

        <View style={styles.routeActions}>
          {route.status === 'assigned' && (
            <TouchableOpacity
              style={[styles.actionButton, styles.startButton]}
              onPress={() => handleStartRoute(route.id)}
            >
              <Text style={styles.actionButtonText}>Start Route</Text>
            </TouchableOpacity>
          )}
          
          {route.status === 'in_progress' && (
            <TouchableOpacity
              style={[styles.actionButton, styles.completeButton]}
              onPress={() => handleCompleteRoute(route.id)}
            >
              <Text style={styles.actionButtonText}>Complete Route</Text>
            </TouchableOpacity>
          )}
          
          <TouchableOpacity
            style={[styles.actionButton, styles.viewButton]}
            onPress={() => handleRoutePress(route)}
          >
            <Text style={[styles.actionButtonText, { color: '#1976d2' }]}>
              View Details
            </Text>
          </TouchableOpacity>
        </View>
      </TouchableOpacity>
    );
  };

  useEffect(() => {
    loadRoutes();
  }, []);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading routes...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={routes}
        renderItem={renderRouteItem}
        keyExtractor={(item) => item.id}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={styles.listContainer}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>No routes assigned</Text>
            <Text style={styles.emptySubtext}>
              Check back later or contact your fleet manager
            </Text>
          </View>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContainer: {
    padding: 16,
  },
  routeCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  routeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  routeName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  routeInfo: {
    marginBottom: 12,
  },
  routeDetail: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  progressBarContainer: {
    marginBottom: 16,
  },
  progressBarBackground: {
    height: 6,
    backgroundColor: '#e0e0e0',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#4caf50',
    borderRadius: 3,
  },
  routeActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionButton: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  startButton: {
    backgroundColor: '#4caf50',
  },
  completeButton: {
    backgroundColor: '#ff9800',
  },
  viewButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#1976d2',
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  emptyState: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 18,
    color: '#666',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
});

export default RouteScreen;
