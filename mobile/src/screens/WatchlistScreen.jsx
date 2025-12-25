/**
 * Watchlist Screen
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
} from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';

const WatchlistScreen = ({ navigation }) => {
  const [watchlist, setWatchlist] = useState([
    {
      id: '1',
      symbol: 'AAPL',
      name: 'Apple Inc.',
      price: 189.95,
      change: 2.45,
      changePercent: 1.31,
    },
    {
      id: '2',
      symbol: 'MSFT',
      name: 'Microsoft Corp.',
      price: 375.04,
      change: -1.23,
      changePercent: -0.33,
    },
    {
      id: '3',
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      price: 140.35,
      change: 3.12,
      changePercent: 2.27,
    },
  ]);
  const [loading, setLoading] = useState(false);

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={watchlist}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.watchItem}
            onPress={() =>
              navigation.navigate('StockDetail', { symbol: item.symbol })
            }
          >
            <View style={styles.itemLeft}>
              <Text style={styles.itemSymbol}>{item.symbol}</Text>
              <Text style={styles.itemName}>{item.name}</Text>
            </View>

            <View style={styles.itemRight}>
              <Text style={styles.itemPrice}>${item.price.toFixed(2)}</Text>
              <Text
                style={[
                  styles.itemChange,
                  { color: item.change >= 0 ? '#4CAF50' : '#F44336' },
                ]}
              >
                {item.change >= 0 ? '+' : ''}${item.change.toFixed(2)} ({item.changePercent.toFixed(2)}%)
              </Text>
            </View>

            <TouchableOpacity
              style={styles.removeButton}
              onPress={() =>
                setWatchlist(watchlist.filter((w) => w.id !== item.id))
              }
            >
              <MaterialCommunityIcons name="close" size={20} color="#888" />
            </TouchableOpacity>
          </TouchableOpacity>
        )}
        scrollEnabled={true}
        ListEmptyComponent={
          <View style={styles.centerContainer}>
            <MaterialCommunityIcons name="heart-off" size={48} color="#888" />
            <Text style={styles.emptyText}>No watchlist items</Text>
          </View>
        }
      />
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
  watchItem: {
    backgroundColor: '#1E1E1E',
    marginHorizontal: 16,
    marginVertical: 6,
    padding: 12,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  itemLeft: {
    flex: 1,
  },
  itemSymbol: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  itemName: {
    color: '#888',
    fontSize: 12,
    marginTop: 2,
  },
  itemRight: {
    alignItems: 'flex-end',
    marginRight: 12,
  },
  itemPrice: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  itemChange: {
    fontWeight: '600',
    fontSize: 12,
    marginTop: 2,
  },
  removeButton: {
    padding: 8,
  },
});

export default WatchlistScreen;
