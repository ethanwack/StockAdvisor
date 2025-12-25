/**
 * Settings Screen
 */

import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  Switch,
  Alert,
  TextInput,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import * as SecureStore from 'expo-secure-store';

const SettingsScreen = () => {
  const dispatch = useDispatch();
  const settings = useSelector((state) => state.settings);
  const [apiKey, setApiKey] = useState('');

  const handleToggleNotifications = async (value) => {
    if (value) {
      // In a real app, would request permissions
      Alert.alert('Notifications Enabled', 'You will receive alerts on this device');
    }
  };

  const handleSetApiKey = async () => {
    if (!apiKey) {
      Alert.alert('Error', 'Please enter an API key');
      return;
    }

    try {
      await SecureStore.setItemAsync('apiToken', apiKey);
      Alert.alert('Success', 'API key saved securely');
      setApiKey('');
    } catch (error) {
      Alert.alert('Error', 'Failed to save API key');
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* API Configuration */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>API Configuration</Text>

        <View style={styles.card}>
          <Text style={styles.label}>API Endpoint</Text>
          <Text style={styles.value}>https://api.stockadvisor.com</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>API Key</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter API key"
            placeholderTextColor="#666"
            value={apiKey}
            onChangeText={setApiKey}
            secureTextEntry
          />
          <TouchableOpacity
            style={styles.button}
            onPress={handleSetApiKey}
          >
            <Text style={styles.buttonText}>Save API Key</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Notifications */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notifications</Text>

        <View style={styles.settingRow}>
          <View>
            <Text style={styles.settingLabel}>Enable Notifications</Text>
            <Text style={styles.settingDescription}>
              Get alerts on price movements
            </Text>
          </View>
          <Switch
            value={settings.notifications}
            onValueChange={handleToggleNotifications}
            trackColor={{ false: '#333', true: '#2196F3' }}
          />
        </View>

        <View style={styles.settingRow}>
          <View>
            <Text style={styles.settingLabel}>Sound</Text>
            <Text style={styles.settingDescription}>
              Play sound for notifications
            </Text>
          </View>
          <Switch
            value={true}
            trackColor={{ false: '#333', true: '#2196F3' }}
          />
        </View>

        <View style={styles.settingRow}>
          <View>
            <Text style={styles.settingLabel}>Vibration</Text>
            <Text style={styles.settingDescription}>
              Vibrate on notifications
            </Text>
          </View>
          <Switch
            value={true}
            trackColor={{ false: '#333', true: '#2196F3' }}
          />
        </View>
      </View>

      {/* Appearance */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Appearance</Text>

        <View style={styles.settingRow}>
          <View>
            <Text style={styles.settingLabel}>Theme</Text>
            <Text style={styles.settingDescription}>
              {settings.theme === 'dark' ? 'Dark Mode' : 'Light Mode'}
            </Text>
          </View>
          <MaterialCommunityIcons
            name={settings.theme === 'dark' ? 'moon-waning-crescent' : 'white-balance-sunny'}
            size={20}
            color="#2196F3"
          />
        </View>
      </View>

      {/* Preferences */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Preferences</Text>

        <View style={styles.card}>
          <Text style={styles.label}>Currency</Text>
          <Text style={styles.value}>{settings.currency}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>Language</Text>
          <Text style={styles.value}>
            {settings.language === 'en' ? 'English' : 'Other'}
          </Text>
        </View>
      </View>

      {/* About */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>

        <View style={styles.card}>
          <Text style={styles.label}>Version</Text>
          <Text style={styles.value}>1.0.0</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>Build</Text>
          <Text style={styles.value}>2024.01.001</Text>
        </View>

        <TouchableOpacity style={styles.linkButton}>
          <Text style={styles.linkButtonText}>🔗 Visit Website</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.linkButton}>
          <Text style={styles.linkButtonText}>📖 Documentation</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.linkButton}>
          <Text style={styles.linkButtonText}>💬 Support</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  card: {
    backgroundColor: '#1E1E1E',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  label: {
    color: '#888',
    fontSize: 12,
    marginBottom: 4,
  },
  value: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  input: {
    backgroundColor: '#2A2A2A',
    color: 'white',
    borderRadius: 6,
    padding: 10,
    marginVertical: 8,
  },
  button: {
    backgroundColor: '#2196F3',
    padding: 10,
    borderRadius: 6,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1E1E1E',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  settingLabel: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  settingDescription: {
    color: '#888',
    fontSize: 12,
    marginTop: 2,
  },
  linkButton: {
    backgroundColor: '#2196F3',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  linkButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
});

export default SettingsScreen;
