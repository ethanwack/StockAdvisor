/**
 * Alerts Screen
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  FlatList,
  StyleSheet,
  Text,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { fetchAlerts } from '../slices/alertsSlice';
import { MaterialCommunityIcons } from '@expo/vector-icons';

const AlertsScreen = () => {
  const dispatch = useDispatch();
  const { alerts, loading } = useSelector((state) => state.alerts);
  const [filter, setFilter] = useState('all'); // all, unread

  useEffect(() => {
    dispatch(fetchAlerts());
  }, [dispatch]);

  const filteredAlerts =
    filter === 'unread' ? alerts.filter((a) => !a.read) : alerts;

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return '#F44336';
      case 'high':
        return '#FF9800';
      case 'medium':
        return '#FFC107';
      default:
        return '#4CAF50';
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Filter */}
      <View style={styles.filterRow}>
        <TouchableOpacity
          style={[
            styles.filterButton,
            filter === 'all' && styles.filterActive,
          ]}
          onPress={() => setFilter('all')}
        >
          <Text
            style={[
              styles.filterText,
              filter === 'all' && styles.filterTextActive,
            ]}
          >
            All ({alerts.length})
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.filterButton,
            filter === 'unread' && styles.filterActive,
          ]}
          onPress={() => setFilter('unread')}
        >
          <Text
            style={[
              styles.filterText,
              filter === 'unread' && styles.filterTextActive,
            ]}
          >
            Unread ({alerts.filter((a) => !a.read).length})
          </Text>
        </TouchableOpacity>
      </View>

      {/* Alerts List */}
      {filteredAlerts.length === 0 ? (
        <View style={styles.centerContainer}>
          <MaterialCommunityIcons name="bell-off" size={48} color="#888" />
          <Text style={styles.emptyText}>
            {filter === 'unread'
              ? 'No unread alerts'
              : 'No alerts'}
          </Text>
        </View>
      ) : (
        <FlatList
          data={filteredAlerts}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <View style={styles.alertCard}>
              <View
                style={[
                  styles.severityIndicator,
                  { backgroundColor: getSeverityColor(item.severity) },
                ]}
              />

              <View style={styles.alertContent}>
                <View style={styles.alertHeader}>
                  <Text style={styles.alertSymbol}>{item.symbol}</Text>
                  <Text style={styles.alertTime}>{item.timestamp}</Text>
                </View>

                <Text style={styles.alertMessage}>{item.message}</Text>

                {item.unread && (
                  <View style={styles.unreadBadge}>
                    <Text style={styles.unreadText}>Unread</Text>
                  </View>
                )}
              </View>
            </View>
          )}
          scrollEnabled={true}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    color: '#888',
    fontSize: 14,
    marginTop: 16,
  },
  filterRow: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#1E1E1E',
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  filterButton: {
    marginRight: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#333',
  },
  filterActive: {
    backgroundColor: '#2196F3',
    borderColor: '#2196F3',
  },
  filterText: {
    color: '#888',
    fontSize: 12,
    fontWeight: '600',
  },
  filterTextActive: {
    color: 'white',
  },
  alertCard: {
    flexDirection: 'row',
    backgroundColor: '#1E1E1E',
    marginHorizontal: 16,
    marginVertical: 6,
    borderRadius: 8,
    overflow: 'hidden',
  },
  severityIndicator: {
    width: 4,
  },
  alertContent: {
    flex: 1,
    padding: 12,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  alertSymbol: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  alertTime: {
    color: '#666',
    fontSize: 11,
  },
  alertMessage: {
    color: '#CCC',
    fontSize: 12,
    marginTop: 4,
    lineHeight: 16,
  },
  unreadBadge: {
    backgroundColor: '#2196F3',
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    marginTop: 8,
  },
  unreadText: {
    color: 'white',
    fontSize: 10,
    fontWeight: '600',
  },
});

export default AlertsScreen;
