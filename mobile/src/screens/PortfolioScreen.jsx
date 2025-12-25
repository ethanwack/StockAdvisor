/**
 * Portfolio Screen
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  Alert,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { fetchPortfolio } from '../slices/portfolioSlice';
import { MaterialCommunityIcons } from '@expo/vector-icons';

const PortfolioScreen = ({ navigation }) => {
  const dispatch = useDispatch();
  const { holdings, totalValue, dayChange, loading } = useSelector(
    (state) => state.portfolio
  );
  const [addingStock, setAddingStock] = useState(false);
  const [symbol, setSymbol] = useState('');
  const [shares, setShares] = useState('');

  useEffect(() => {
    dispatch(fetchPortfolio());
  }, [dispatch]);

  const handleAddStock = () => {
    if (!symbol || !shares) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    // In a real app, would call API
    Alert.alert('Success', `Added ${shares} shares of ${symbol}`);
    setSymbol('');
    setShares('');
    setAddingStock(false);
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Summary */}
      <View style={styles.summaryCard}>
        <Text style={styles.summaryLabel}>Total Portfolio Value</Text>
        <Text style={styles.totalValue}>${totalValue.toFixed(2)}</Text>
      </View>

      {/* Holdings */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Holdings ({holdings.length})</Text>
          <TouchableOpacity onPress={() => setAddingStock(!addingStock)}>
            <MaterialCommunityIcons name="plus" size={24} color="#2196F3" />
          </TouchableOpacity>
        </View>

        {addingStock && (
          <View style={styles.addForm}>
            <TextInput
              style={styles.input}
              placeholder="Symbol (e.g., AAPL)"
              placeholderTextColor="#666"
              value={symbol}
              onChangeText={setSymbol}
              autoCapitalize="characters"
            />
            <TextInput
              style={styles.input}
              placeholder="Number of shares"
              placeholderTextColor="#666"
              value={shares}
              onChangeText={setShares}
              keyboardType="decimal-pad"
            />
            <TouchableOpacity
              style={styles.addButton}
              onPress={handleAddStock}
            >
              <Text style={styles.addButtonText}>Add to Portfolio</Text>
            </TouchableOpacity>
          </View>
        )}

        {holdings.map((holding) => (
          <TouchableOpacity
            key={holding.id}
            style={styles.holdingCard}
            onPress={() =>
              navigation.navigate('PortfolioDetail', { symbol: holding.symbol })
            }
          >
            <View>
              <Text style={styles.symbol}>{holding.symbol}</Text>
              <Text style={styles.shares}>{holding.shares} shares @ ${holding.costBasis.toFixed(2)}</Text>
            </View>
            <View style={styles.rightAlign}>
              <Text style={styles.value}>
                ${(holding.currentPrice * holding.shares).toFixed(2)}
              </Text>
              <Text
                style={[
                  styles.gain,
                  { color: holding.gain >= 0 ? '#4CAF50' : '#F44336' },
                ]}
              >
                {holding.gain >= 0 ? '+' : ''}${holding.gain.toFixed(2)}
              </Text>
            </View>
          </TouchableOpacity>
        ))}
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
  },
  summaryLabel: {
    color: '#888',
    fontSize: 12,
    marginBottom: 8,
  },
  totalValue: {
    color: 'white',
    fontSize: 28,
    fontWeight: 'bold',
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  addForm: {
    backgroundColor: '#1E1E1E',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  input: {
    backgroundColor: '#2A2A2A',
    color: 'white',
    borderRadius: 6,
    padding: 10,
    marginBottom: 8,
    fontSize: 14,
  },
  addButton: {
    backgroundColor: '#2196F3',
    padding: 12,
    borderRadius: 6,
    alignItems: 'center',
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
  },
  symbol: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  shares: {
    color: '#888',
    fontSize: 12,
    marginTop: 4,
  },
  rightAlign: {
    alignItems: 'flex-end',
  },
  value: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  gain: {
    fontWeight: '600',
    fontSize: 12,
    marginTop: 4,
  },
});

export default PortfolioScreen;
