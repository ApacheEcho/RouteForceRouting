/**
 * Tracking Screen for RouteForce Mobile App
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Switch,
  Alert,
  ScrollView,
} from 'react-native';
import { useAuth } from '../context/AuthContext';

interface TrackingStatus {
  is_tracking: boolean;
  last_update: string;
  current_route?: string;
  total_distance: number;
  elapsed_time: number;
}

const TrackingScreen: React.FC = () => {
  const [trackingStatus, setTrackingStatus] = useState<TrackingStatus | null>(null);
  const [isTracking, setIsTracking] = useState(false);
  const [loading, setLoading] = useState(true);
  const { apiClient } = useAuth();

  const loadTrackingStatus = async () => {
    try {
      const status = await apiClient.getTrackingStatus();
      setTrackingStatus(status);
      setIsTracking(status.is_tracking);
    } catch (error) {
      console.error('Error loading tracking status:', error);
      Alert.alert('Error', 'Failed to load tracking status');
    } finally {
      setLoading(false);
    }
  };

  const toggleTracking = async (enabled: boolean) => {
    try {
      if (enabled) {
        // Start tracking
        await startLocationTracking();
      } else {
        // Stop tracking
        await stopLocationTracking();
      }
      setIsTracking(enabled);
      loadTrackingStatus();
    } catch (error) {
      console.error('Error toggling tracking:', error);
      Alert.alert('Error', 'Failed to toggle tracking');
      setIsTracking(!enabled); // Revert on error
    }
  };

  const startLocationTracking = async () => {
    // In a real app, you'd start location services here
    Alert.alert('Tracking Started', 'Location tracking is now active');
  };

  const stopLocationTracking = async () => {
    // In a real app, you'd stop location services here
    Alert.alert('Tracking Stopped', 'Location tracking has been disabled');
  };

  const sendLocationUpdate = async () => {
    try {
      // In a real app, you'd get actual GPS coordinates
      const mockLocation = {
        lat: 37.7749 + (Math.random() - 0.5) * 0.01,
        lng: -122.4194 + (Math.random() - 0.5) * 0.01,
        accuracy: 10,
        timestamp: new Date().toISOString(),
        speed: Math.random() * 30,
        heading: Math.random() * 360,
      };

      await apiClient.updateLocation(mockLocation);
      Alert.alert('Success', 'Location updated successfully');
      loadTrackingStatus();
    } catch (error) {
      console.error('Error updating location:', error);
      Alert.alert('Error', 'Failed to update location');
    }
  };

  const formatElapsedTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const formatDistance = (meters: number) => {
    const km = meters / 1000;
    return `${km.toFixed(1)} km`;
  };

  useEffect(() => {
    loadTrackingStatus();
    
    // Set up location tracking interval if tracking is enabled
    let interval: NodeJS.Timeout;
    if (isTracking) {
      interval = setInterval(() => {
        sendLocationUpdate();
      }, 30000); // Update every 30 seconds
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [isTracking]);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading tracking status...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Location Tracking</Text>
        <Text style={styles.headerSubtitle}>
          Monitor your route progress and location
        </Text>
      </View>

      <View style={styles.trackingToggle}>
        <View style={styles.toggleContainer}>
          <View>
            <Text style={styles.toggleTitle}>Location Tracking</Text>
            <Text style={styles.toggleSubtitle}>
              {isTracking ? 'Currently tracking your location' : 'Location tracking is disabled'}
            </Text>
          </View>
          <Switch
            value={isTracking}
            onValueChange={toggleTracking}
            trackColor={{ false: '#e0e0e0', true: '#1976d2' }}
            thumbColor={isTracking ? '#ffffff' : '#f4f3f4'}
          />
        </View>
      </View>

      {trackingStatus && (
        <View style={styles.statusContainer}>
          <Text style={styles.sectionTitle}>Tracking Status</Text>
          
          <View style={styles.statusCard}>
            <View style={styles.statusItem}>
              <Text style={styles.statusLabel}>Status</Text>
              <Text style={[
                styles.statusValue,
                { color: trackingStatus.is_tracking ? '#4caf50' : '#f44336' }
              ]}>
                {trackingStatus.is_tracking ? 'Active' : 'Inactive'}
              </Text>
            </View>

            <View style={styles.statusItem}>
              <Text style={styles.statusLabel}>Last Update</Text>
              <Text style={styles.statusValue}>
                {trackingStatus.last_update 
                  ? new Date(trackingStatus.last_update).toLocaleTimeString()
                  : 'Never'
                }
              </Text>
            </View>

            <View style={styles.statusItem}>
              <Text style={styles.statusLabel}>Current Route</Text>
              <Text style={styles.statusValue}>
                {trackingStatus.current_route || 'No active route'}
              </Text>
            </View>

            <View style={styles.statusItem}>
              <Text style={styles.statusLabel}>Total Distance</Text>
              <Text style={styles.statusValue}>
                {formatDistance(trackingStatus.total_distance)}
              </Text>
            </View>

            <View style={styles.statusItem}>
              <Text style={styles.statusLabel}>Elapsed Time</Text>
              <Text style={styles.statusValue}>
                {formatElapsedTime(trackingStatus.elapsed_time)}
              </Text>
            </View>
          </View>
        </View>
      )}

      <View style={styles.actionsContainer}>
        <Text style={styles.sectionTitle}>Actions</Text>
        
        <TouchableOpacity
          style={styles.actionButton}
          onPress={sendLocationUpdate}
          disabled={!isTracking}
        >
          <Text style={[
            styles.actionButtonText,
            !isTracking && styles.actionButtonTextDisabled
          ]}>
            Send Location Update
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={loadTrackingStatus}
        >
          <Text style={styles.actionButtonText}>Refresh Status</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, styles.secondaryButton]}
          onPress={() => Alert.alert('Settings', 'Tracking settings would be here')}
        >
          <Text style={[styles.actionButtonText, { color: '#1976d2' }]}>
            Tracking Settings
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.infoContainer}>
        <Text style={styles.sectionTitle}>Information</Text>
        <Text style={styles.infoText}>
          • Location tracking helps optimize routes and provides real-time updates
        </Text>
        <Text style={styles.infoText}>
          • Your location is only shared with your fleet manager
        </Text>
        <Text style={styles.infoText}>
          • You can disable tracking at any time
        </Text>
        <Text style={styles.infoText}>
          • Battery optimization tips: Enable only when on active routes
        </Text>
      </View>
    </ScrollView>
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
  header: {
    backgroundColor: '#1976d2',
    padding: 20,
    paddingTop: 40,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
  },
  trackingToggle: {
    backgroundColor: '#ffffff',
    margin: 16,
    borderRadius: 12,
    padding: 20,
  },
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  toggleTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  toggleSubtitle: {
    fontSize: 14,
    color: '#666',
  },
  statusContainer: {
    margin: 16,
    marginTop: 0,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  statusCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
  },
  statusItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  statusLabel: {
    fontSize: 16,
    color: '#666',
  },
  statusValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  actionsContainer: {
    margin: 16,
    marginTop: 0,
  },
  actionButton: {
    backgroundColor: '#1976d2',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    alignItems: 'center',
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#1976d2',
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  actionButtonTextDisabled: {
    color: '#ccc',
  },
  infoContainer: {
    margin: 16,
    marginTop: 0,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    lineHeight: 20,
  },
});

export default TrackingScreen;
