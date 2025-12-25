/**
 * Stock Search Screen
 */

import React, { useState } from 'react';
import {
  View,
  TextInput,
  FlatList,
  StyleSheet,
  Text,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { fetchStocks } from '../slices/stocksSlice';
import { MaterialCommunityIcons } from '@expo/vector-icons';

const SearchScreen = ({ navigation }) => {
  const [query, setQuery] = useState('');
  const dispatch = useDispatch();
  const { searchResults, loading } = useSelector((state) => state.stocks);

  const handleSearch = (text) => {
    setQuery(text);
    if (text.length > 1) {
      dispatch(fetchStocks(text));
    }
  };

  return (
    <View style={styles.container}>
      {/* Search Bar */}
      <View style={styles.searchBar}>
        <MaterialCommunityIcons name="magnify" size={20} color="#888" />
        <TextInput
          style={styles.searchInput}
          placeholder="Search stocks..."
          placeholderTextColor="#666"
          value={query}
          onChangeText={handleSearch}
        />
        {query ? (
          <TouchableOpacity onPress={() => setQuery('')}>
            <MaterialCommunityIcons name="close" size={20} color="#888" />
          </TouchableOpacity>
        ) : null}
      </View>

      {/* Results */}
      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#2196F3" />
        </View>
      ) : searchResults.length === 0 && query ? (
        <View style={styles.centerContainer}>
          <Text style={styles.emptyText}>No results found</Text>
        </View>
      ) : (
        <FlatList
          data={searchResults}
          keyExtractor={(item) => item.symbol}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.resultCard}
              onPress={() =>
                navigation.navigate('SearchDetail', { symbol: item.symbol })
              }
            >
              <View>
                <Text style={styles.resultSymbol}>{item.symbol}</Text>
                <Text style={styles.resultName}>{item.name}</Text>
              </View>
              <View style={styles.resultPrice}>
                <Text style={styles.price}>${item.price.toFixed(2)}</Text>
                <Text
                  style={[
                    styles.change,
                    { color: item.change >= 0 ? '#4CAF50' : '#F44336' },
                  ]}
                >
                  {item.change >= 0 ? '+' : ''}{item.changePercent.toFixed(2)}%
                </Text>
              </View>
            </TouchableOpacity>
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
  searchBar: {
    backgroundColor: '#1E1E1E',
    margin: 16,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
  },
  searchInput: {
    flex: 1,
    color: 'white',
    padding: 12,
    fontSize: 14,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    color: '#888',
    fontSize: 14,
  },
  resultCard: {
    backgroundColor: '#1E1E1E',
    marginHorizontal: 16,
    marginVertical: 4,
    padding: 12,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  resultSymbol: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  resultName: {
    color: '#888',
    fontSize: 12,
    marginTop: 2,
  },
  resultPrice: {
    alignItems: 'flex-end',
  },
  price: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  change: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 2,
  },
});

export default SearchScreen;
