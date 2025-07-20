/**
 * Settings Screen for RouteForce Mobile App
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Switch,
  TouchableOpacity,
  Alert,
} from 'react-native';

const SettingsScreen: React.FC = () => {
  const [settings, setSettings] = useState({
    notifications: true,
    locationTracking: true,
    autoSync: true,
    backgroundRefresh: false,
    soundAlerts: true,
    vibration: true,
    darkMode: false,
  });

  const toggleSetting = (key: keyof typeof settings) => {
    setSettings(prev => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleAbout = () => {
    Alert.alert(
      'About RouteForce Mobile',
      'Version 1.0.0\n\nRoute optimization and tracking app for delivery drivers.\n\n© 2024 RouteForce Systems'
    );
  };

  const handleHelp = () => {
    Alert.alert(
      'Help & Support',
      'For assistance, please contact:\n\n• Email: support@routeforce.com\n• Phone: 1-800-ROUTES\n• Help Center: help.routeforce.com'
    );
  };

  const handlePrivacy = () => {
    Alert.alert('Privacy Policy', 'Privacy policy would be displayed here');
  };

  const handleTerms = () => {
    Alert.alert('Terms of Service', 'Terms of service would be displayed here');
  };

  const handleClearCache = () => {
    Alert.alert(
      'Clear Cache',
      'This will clear all cached data including offline routes. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: () => Alert.alert('Success', 'Cache cleared successfully'),
        },
      ]
    );
  };

  const SettingRow = ({ 
    title, 
    description, 
    value, 
    onToggle 
  }: {
    title: string;
    description?: string;
    value: boolean;
    onToggle: () => void;
  }) => (
    <View style={styles.settingRow}>
      <View style={styles.settingInfo}>
        <Text style={styles.settingTitle}>{title}</Text>
        {description && (
          <Text style={styles.settingDescription}>{description}</Text>
        )}
      </View>
      <Switch
        value={value}
        onValueChange={onToggle}
        trackColor={{ false: '#e0e0e0', true: '#1976d2' }}
        thumbColor={value ? '#ffffff' : '#f4f3f4'}
      />
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notifications</Text>
        
        <SettingRow
          title="Push Notifications"
          description="Receive notifications for route updates and alerts"
          value={settings.notifications}
          onToggle={() => toggleSetting('notifications')}
        />
        
        <SettingRow
          title="Sound Alerts"
          description="Play sounds for notifications"
          value={settings.soundAlerts}
          onToggle={() => toggleSetting('soundAlerts')}
        />
        
        <SettingRow
          title="Vibration"
          description="Vibrate for notifications"
          value={settings.vibration}
          onToggle={() => toggleSetting('vibration')}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Location & Tracking</Text>
        
        <SettingRow
          title="Location Tracking"
          description="Allow app to track your location for route optimization"
          value={settings.locationTracking}
          onToggle={() => toggleSetting('locationTracking')}
        />
        
        <SettingRow
          title="Background Refresh"
          description="Update location and sync data in background"
          value={settings.backgroundRefresh}
          onToggle={() => toggleSetting('backgroundRefresh')}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data & Sync</Text>
        
        <SettingRow
          title="Auto Sync"
          description="Automatically sync data when connected to WiFi"
          value={settings.autoSync}
          onToggle={() => toggleSetting('autoSync')}
        />

        <TouchableOpacity
          style={styles.actionButton}
          onPress={handleClearCache}
        >
          <Text style={styles.actionButtonText}>Clear Cache</Text>
          <Text style={styles.actionButtonSubtext}>
            Remove cached routes and offline data
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Appearance</Text>
        
        <SettingRow
          title="Dark Mode"
          description="Use dark theme for the app interface"
          value={settings.darkMode}
          onToggle={() => toggleSetting('darkMode')}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Support & Legal</Text>
        
        <TouchableOpacity
          style={styles.actionButton}
          onPress={handleHelp}
        >
          <Text style={styles.actionButtonText}>Help & Support</Text>
          <Text style={styles.actionButtonSubtext}>
            Get help and contact support
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={handleAbout}
        >
          <Text style={styles.actionButtonText}>About</Text>
          <Text style={styles.actionButtonSubtext}>
            App version and information
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={handlePrivacy}
        >
          <Text style={styles.actionButtonText}>Privacy Policy</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={handleTerms}
        >
          <Text style={styles.actionButtonText}>Terms of Service</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>RouteForce Mobile v1.0.0</Text>
        <Text style={styles.footerText}>Build 2024.1.0</Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  section: {
    backgroundColor: '#ffffff',
    marginTop: 20,
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingTitle: {
    fontSize: 16,
    color: '#333',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 18,
  },
  actionButton: {
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  actionButtonText: {
    fontSize: 16,
    color: '#333',
    marginBottom: 2,
  },
  actionButtonSubtext: {
    fontSize: 14,
    color: '#666',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
    marginTop: 20,
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
});

export default SettingsScreen;
