/**
 * Dashboard Screen for RouteForce Mobile App
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useAuth } from '../context/AuthContext';

interface DashboardStats {
  total_routes: number;
  completed_routes: number;
  active_routes: number;
  total_stores: number;
  visited_stores: number;
}

interface RecentRoute {
  id: string;
  name: string;
  status: string;
  stores_count: number;
  completed_stores: number;
  updated_at: string;
}

const DashboardScreen: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentRoutes, setRecentRoutes] = useState<RecentRoute[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const { apiClient, signOut } = useAuth();

  const loadDashboardData = async () => {
    try {
      // In a real app, you'd have specific dashboard endpoints
      const routes = await apiClient.getAssignedRoutes();
      
      // Calculate stats from routes
      const dashboardStats: DashboardStats = {
        total_routes: routes.length,
        completed_routes: routes.filter(r => r.status === 'completed').length,
        active_routes: routes.filter(r => r.status === 'in_progress').length,
        total_stores: routes.reduce((sum, r) => sum + r.stores.length, 0),
        visited_stores: routes.reduce((sum, r) => 
          sum + r.stores.filter(s => s.visit_status === 'completed').length, 0
        ),
      };

      setStats(dashboardStats);
      
      // Set recent routes (last 5)
      setRecentRoutes(routes.slice(0, 5).map(route => ({
        id: route.id,
        name: route.name,
        status: route.status,
        stores_count: route.stores.length,
        completed_stores: route.stores.filter(s => s.visit_status === 'completed').length,
        updated_at: route.updated_at,
      })));
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      Alert.alert('Error', 'Failed to load dashboard data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboardData();
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Logout', style: 'destructive', onPress: signOut },
      ]
    );
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading dashboard...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Welcome Back!</Text>
        <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </View>

      {stats && (
        <View style={styles.statsContainer}>
          <Text style={styles.sectionTitle}>Today's Overview</Text>
          
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.total_routes}</Text>
              <Text style={styles.statLabel}>Total Routes</Text>
            </View>
            
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.active_routes}</Text>
              <Text style={styles.statLabel}>Active Routes</Text>
            </View>
            
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.completed_routes}</Text>
              <Text style={styles.statLabel}>Completed</Text>
            </View>
            
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>
                {stats.visited_stores}/{stats.total_stores}
              </Text>
              <Text style={styles.statLabel}>Stores Visited</Text>
            </View>
          </View>
        </View>
      )}

      <View style={styles.routesContainer}>
        <Text style={styles.sectionTitle}>Recent Routes</Text>
        
        {recentRoutes.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>No routes assigned yet</Text>
          </View>
        ) : (
          recentRoutes.map((route) => (
            <View key={route.id} style={styles.routeCard}>
              <View style={styles.routeHeader}>
                <Text style={styles.routeName}>{route.name}</Text>
                <View style={[styles.statusBadge, getStatusStyle(route.status)]}>
                  <Text style={styles.statusText}>{route.status}</Text>
                </View>
              </View>
              
              <Text style={styles.routeProgress}>
                Progress: {route.completed_stores}/{route.stores_count} stores
              </Text>
              
              <Text style={styles.routeTime}>
                Updated: {new Date(route.updated_at).toLocaleDateString()}
              </Text>
            </View>
          ))
        )}
      </View>

      <View style={styles.quickActions}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionButtonText}>Start Route</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionButtonText}>View All Routes</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionButtonText}>Update Location</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const getStatusStyle = (status: string) => {
  switch (status) {
    case 'completed':
      return { backgroundColor: '#4caf50' };
    case 'in_progress':
      return { backgroundColor: '#ff9800' };
    case 'assigned':
      return { backgroundColor: '#2196f3' };
    default:
      return { backgroundColor: '#757575' };
  }
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#1976d2',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  logoutButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 6,
  },
  logoutText: {
    color: '#ffffff',
    fontWeight: '600',
  },
  statsContainer: {
    padding: 20,
    backgroundColor: '#ffffff',
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1976d2',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#757575',
    textAlign: 'center',
  },
  routesContainer: {
    padding: 20,
    backgroundColor: '#ffffff',
    marginBottom: 10,
  },
  emptyState: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    color: '#757575',
    fontSize: 16,
  },
  routeCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  routeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  routeName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  routeProgress: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  routeTime: {
    fontSize: 12,
    color: '#999',
  },
  quickActions: {
    padding: 20,
    backgroundColor: '#ffffff',
  },
  actionButton: {
    backgroundColor: '#1976d2',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default DashboardScreen;
