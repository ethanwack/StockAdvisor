/**
 * Dashboard Screen
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
  RefreshControl,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { fetchPortfolio } from '../slices/portfolioSlice';
import { MaterialCommunityIcons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

const DashboardScreen = ({ navigation }) => {
  const dispatch = useDispatch();
  const { holdings, totalValue, dayChange, loading } = useSelector(
    (state) => state.portfolio
  );
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    dispatch(fetchPortfolio());
  }, [dispatch]);

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    dispatch(fetchPortfolio()).finally(() => setRefreshing(false));
  }, [dispatch]);

  if (loading && !refreshing) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  const dayChangePercent = (dayChange / totalValue) * 100;
  const isPositive = dayChange >= 0;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Portfolio Summary Card */}
      <View style={styles.summaryCard}>
        <Text style={styles.summaryLabel}>Total Portfolio Value</Text>
        <Text style={styles.totalValue}>${totalValue.toFixed(2)}</Text>

        <View style={styles.changeRow}>
          <View
            style={[
              styles.changeChip,
              { backgroundColor: isPositive ? '#4CAF50' : '#F44336' },
            ]}
          >
            <MaterialCommunityIcons
              name={isPositive ? 'trending-up' : 'trending-down'}
              size={16}
              color="white"
            />
            <Text style={styles.changeText}>
              {isPositive ? '+' : ''}${Math.abs(dayChange).toFixed(2)} ({dayChangePercent.toFixed(2)}%)
            </Text>
          </View>
        </View>
      </View>

      {/* Holdings List */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Your Holdings</Text>

        {holdings.length === 0 ? (
          <View style={styles.emptyState}>
            <MaterialCommunityIcons name="briefcase-off" size={48} color="#888" />
            <Text style={styles.emptyText}>No holdings yet</Text>
            <TouchableOpacity
              style={styles.addButton}
              onPress={() => navigation.navigate('SearchStack')}
            >
              <Text style={styles.addButtonText}>Add Stock</Text>
            </TouchableOpacity>
          </View>
        ) : (
          holdings.map((holding) => (
            <TouchableOpacity
              key={holding.id}
              style={styles.holdingCard}
              onPress={() =>
                navigation.navigate('StockDetail', { symbol: holding.symbol })
              }
            >
              <View style={styles.holdingLeft}>
                <Text style={styles.holdingSymbol}>{holding.symbol}</Text>
                <Text style={styles.holdingName}>{holding.name}</Text>
                <Text style={styles.holdingShares}>{holding.shares} shares</Text>
              </View>

              <View style={styles.holdingRight}>
                <Text style={styles.holdingValue}>
                  ${(holding.currentPrice * holding.shares).toFixed(2)}
                </Text>
                <Text
                  style={[
                    styles.holdingReturn,
                    {
                      color:
                        holding.dayChange >= 0
                          ? '#4CAF50'
                          : '#F44336',
                    },
                  ]}
                >
                  {holding.dayChange >= 0 ? '+' : ''}
                  {holding.dayChangePercent.toFixed(2)}%
                </Text>
              </View>
            </TouchableOpacity>
          ))
        )}
      </View>

      {/* Quick Stats */}
      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <MaterialCommunityIcons name="trending-up" size={24} color="#2196F3" />
          <Text style={styles.statValue}>{holdings.length}</Text>
          <Text style={styles.statLabel}>Holdings</Text>
        </View>

        <View style={styles.statCard}>
          <MaterialCommunityIcons name="percent" size={24} color="#FF9800" />
          <Text style={styles.statValue}>
            {((dayChange / totalValue) * 100).toFixed(1)}%
          </Text>
          <Text style={styles.statLabel}>Day Return</Text>
        </View>

        <View style={styles.statCard}>
          <MaterialCommunityIcons name="target" size={24} color="#4CAF50" />
          <Text style={styles.statValue}>—</Text>
          <Text style={styles.statLabel}>Allocation</Text>
        </View>
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
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#121212',
  },
  summaryCard: {
    backgroundColor: '#1E1E1E',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#2196F3',
  },
  summaryLabel: {
    color: '#888',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 8,
  },
  totalValue: {
    color: 'white',
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  changeRow: {
    flexDirection: 'row',
  },
  changeChip: {
    flexDirection: 'row',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    alignItems: 'center',
  },
  changeText: {
    color: 'white',
    fontWeight: '600',
    marginLeft: 6,
    fontSize: 12,
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
  emptyState: {
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    color: '#888',
    fontSize: 14,
    marginTop: 12,
  },
  addButton: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 16,
  },
  addButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  holdingCard: {
    backgroundColor: '#1E1E1E',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  holdingLeft: {
    flex: 1,
  },
  holdingSymbol: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  holdingName: {
    color: '#888',
    fontSize: 12,
    marginTop: 2,
  },
  holdingShares: {
    color: '#666',
    fontSize: 11,
    marginTop: 2,
  },
  holdingRight: {
    alignItems: 'flex-end',
  },
  holdingValue: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  holdingReturn: {
    fontWeight: '600',
    fontSize: 12,
    marginTop: 2,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 32,
  },
  statCard: {
    width: (width - 52) / 3,
    backgroundColor: '#1E1E1E',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
  },
  statValue: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 8,
  },
  statLabel: {
    color: '#888',
    fontSize: 10,
    marginTop: 4,
  },
});

export default DashboardScreen;
