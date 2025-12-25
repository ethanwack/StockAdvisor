/**
 * Stock Detail Screen
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

const StockDetailScreen = ({ route }) => {
  const { symbol } = route.params || { symbol: 'AAPL' };
  const [stock, setStock] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, would fetch stock details
    setStock({
      symbol: symbol,
      name: 'Apple Inc.',
      price: 189.95,
      change: 2.45,
      changePercent: 1.31,
      open: 187.50,
      high: 190.12,
      low: 187.40,
      volume: 52_450_000,
      marketCap: 2_980_000_000_000,
      peRatio: 28.5,
      dividend: 0.24,
      yield: 0.50,
      description: 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.',
    });
    setLoading(false);
  }, [symbol]);

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.symbol}>{stock.symbol}</Text>
          <Text style={styles.name}>{stock.name}</Text>
        </View>
      </View>

      {/* Price Card */}
      <View style={styles.priceCard}>
        <Text style={styles.price}>${stock.price.toFixed(2)}</Text>

        <View
          style={[
            styles.changeChip,
            {
              backgroundColor:
                stock.change >= 0 ? '#4CAF5022' : '#F4433622',
            },
          ]}
        >
          <MaterialCommunityIcons
            name={stock.change >= 0 ? 'trending-up' : 'trending-down'}
            size={16}
            color={stock.change >= 0 ? '#4CAF50' : '#F44336'}
          />
          <Text
            style={{
              color: stock.change >= 0 ? '#4CAF50' : '#F44336',
              fontWeight: '600',
              marginLeft: 6,
            }}
          >
            {stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)} ({stock.changePercent.toFixed(2)}%)
          </Text>
        </View>
      </View>

      {/* Key Stats */}
      <View style={styles.statsGrid}>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Open</Text>
          <Text style={styles.statValue}>${stock.open.toFixed(2)}</Text>
        </View>

        <View style={styles.statItem}>
          <Text style={styles.statLabel}>High</Text>
          <Text style={styles.statValue}>${stock.high.toFixed(2)}</Text>
        </View>

        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Low</Text>
          <Text style={styles.statValue}>${stock.low.toFixed(2)}</Text>
        </View>

        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Volume</Text>
          <Text style={styles.statValue}>
            {(stock.volume / 1_000_000).toFixed(1)}M
          </Text>
        </View>

        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Market Cap</Text>
          <Text style={styles.statValue}>
            ${(stock.marketCap / 1_000_000_000_000).toFixed(2)}T
          </Text>
        </View>

        <View style={styles.statItem}>
          <Text style={styles.statLabel}>P/E Ratio</Text>
          <Text style={styles.statValue}>{stock.peRatio}</Text>
        </View>

        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Dividend</Text>
          <Text style={styles.statValue}>${stock.dividend.toFixed(2)}</Text>
        </View>

        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Yield</Text>
          <Text style={styles.statValue}>{stock.yield.toFixed(2)}%</Text>
        </View>
      </View>

      {/* Description */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <Text style={styles.description}>{stock.description}</Text>
      </View>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity style={styles.buyButton}>
          <MaterialCommunityIcons name="plus" size={20} color="white" />
          <Text style={styles.buyButtonText}>Add to Portfolio</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.watchButton}>
          <MaterialCommunityIcons name="heart-outline" size={20} color="#2196F3" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.alertButton}>
          <MaterialCommunityIcons name="bell-outline" size={20} color="#2196F3" />
        </TouchableOpacity>
      </View>
    </ScrollView>
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
    backgroundColor: '#121212',
  },
  header: {
    backgroundColor: '#1E1E1E',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  symbol: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
  },
  name: {
    color: '#888',
    fontSize: 12,
    marginTop: 4,
  },
  priceCard: {
    backgroundColor: '#1E1E1E',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#2196F3',
  },
  price: {
    color: 'white',
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  changeChip: {
    flexDirection: 'row',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    alignSelf: 'flex-start',
    alignItems: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  statItem: {
    width: '50%',
    padding: 12,
  },
  statLabel: {
    color: '#888',
    fontSize: 11,
    marginBottom: 4,
  },
  statValue: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  section: {
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  sectionTitle: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  description: {
    color: '#CCC',
    fontSize: 13,
    lineHeight: 20,
  },
  actionButtons: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 16,
    gap: 12,
  },
  buyButton: {
    flex: 1,
    backgroundColor: '#2196F3',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 8,
  },
  buyButtonText: {
    color: 'white',
    fontWeight: 'bold',
    marginLeft: 8,
  },
  watchButton: {
    width: 50,
    backgroundColor: '#1E1E1E',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#2196F3',
  },
  alertButton: {
    width: 50,
    backgroundColor: '#1E1E1E',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#2196F3',
  },
});

export default StockDetailScreen;
