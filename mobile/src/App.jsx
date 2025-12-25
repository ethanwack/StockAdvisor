/**
 * Stock Advisor Mobile App
 * iOS/Android app for real-time portfolio monitoring and stock analysis
 */

import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import * as Notifications from 'expo-notifications';
import { Provider } from 'react-redux';
import { store } from './store';

// Screens
import DashboardScreen from './screens/DashboardScreen';
import SearchScreen from './screens/SearchScreen';
import PortfolioScreen from './screens/PortfolioScreen';
import AlertsScreen from './screens/AlertsScreen';
import SettingsScreen from './screens/SettingsScreen';
import StockDetailScreen from './screens/StockDetailScreen';
import WatchlistScreen from './screens/WatchlistScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

const DashboardStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: '#1a1a1a' },
      headerTintColor: '#2196F3',
      headerTitleStyle: { fontWeight: 'bold', color: 'white' },
    }}
  >
    <Stack.Screen
      name="Dashboard"
      component={DashboardScreen}
      options={{ title: '📊 Stock Advisor' }}
    />
    <Stack.Screen
      name="StockDetail"
      component={StockDetailScreen}
      options={{ title: 'Stock Details' }}
    />
  </Stack.Navigator>
);

const SearchStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: '#1a1a1a' },
      headerTintColor: '#2196F3',
      headerTitleStyle: { fontWeight: 'bold', color: 'white' },
    }}
  >
    <Stack.Screen
      name="Search"
      component={SearchScreen}
      options={{ title: '🔍 Stock Search' }}
    />
    <Stack.Screen
      name="SearchDetail"
      component={StockDetailScreen}
      options={{ title: 'Stock Details' }}
    />
  </Stack.Navigator>
);

const PortfolioStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: '#1a1a1a' },
      headerTintColor: '#2196F3',
      headerTitleStyle: { fontWeight: 'bold', color: 'white' },
    }}
  >
    <Stack.Screen
      name="Portfolio"
      component={PortfolioScreen}
      options={{ title: '💼 Portfolio' }}
    />
    <Stack.Screen
      name="PortfolioDetail"
      component={StockDetailScreen}
      options={{ title: 'Stock Details' }}
    />
  </Stack.Navigator>
);

const AlertsStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: '#1a1a1a' },
      headerTintColor: '#2196F3',
      headerTitleStyle: { fontWeight: 'bold', color: 'white' },
    }}
  >
    <Stack.Screen
      name="Alerts"
      component={AlertsScreen}
      options={{ title: '🔔 Alerts & Notifications' }}
    />
  </Stack.Navigator>
);

const SettingsStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: '#1a1a1a' },
      headerTintColor: '#2196F3',
      headerTitleStyle: { fontWeight: 'bold', color: 'white' },
    }}
  >
    <Stack.Screen
      name="Settings"
      component={SettingsScreen}
      options={{ title: '⚙️ Settings' }}
    />
  </Stack.Navigator>
);

export default function App() {
  useEffect(() => {
    // Request notification permissions
    Notifications.requestPermissionsAsync();

    // Listen for notifications
    const subscription = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        console.log('Notification received:', response.notification);
      }
    );

    return () => subscription.remove();
  }, []);

  return (
    <Provider store={store}>
      <NavigationContainer>
        <StatusBar barStyle="light-content" backgroundColor="#1a1a1a" />
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ color, size }) => {
              let iconName;

              if (route.name === 'DashboardStack') {
                iconName = 'chart-line';
              } else if (route.name === 'SearchStack') {
                iconName = 'magnify';
              } else if (route.name === 'PortfolioStack') {
                iconName = 'briefcase';
              } else if (route.name === 'AlertsStack') {
                iconName = 'bell';
              } else if (route.name === 'SettingsStack') {
                iconName = 'cog';
              }

              return (
                <MaterialCommunityIcons name={iconName} size={size} color={color} />
              );
            },
            tabBarActiveTintColor: '#2196F3',
            tabBarInactiveTintColor: '#888',
            tabBarStyle: { backgroundColor: '#1a1a1a', borderTopColor: '#333' },
            headerShown: false,
          })}
        >
          <Tab.Screen
            name="DashboardStack"
            component={DashboardStack}
            options={{ title: 'Dashboard' }}
          />
          <Tab.Screen
            name="SearchStack"
            component={SearchStack}
            options={{ title: 'Search' }}
          />
          <Tab.Screen
            name="PortfolioStack"
            component={PortfolioStack}
            options={{ title: 'Portfolio' }}
          />
          <Tab.Screen
            name="AlertsStack"
            component={AlertsStack}
            options={{ title: 'Alerts' }}
          />
          <Tab.Screen
            name="SettingsStack"
            component={SettingsStack}
            options={{ title: 'Settings' }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </Provider>
  );
}
