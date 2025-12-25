# Stock Advisor iOS/Android Mobile App

Professional investment research and portfolio management app built with React Native and Expo.

## Features

### 📊 Dashboard
- Real-time portfolio tracking
- Daily gains/losses with percentage
- Holdings summary with performance metrics
- Quick access to top holdings

### 🔍 Stock Search
- Search stocks across all major exchanges
- View real-time prices and performance
- Navigate to detailed stock information

### 💼 Portfolio Management
- Add/remove holdings from portfolio
- Track cost basis and current value
- Monitor unrealized gains and losses
- View detailed position performance

### 🔔 Alerts & Notifications
- Price movement alerts (iOS & Android)
- Customizable alert thresholds
- Push notifications for price targets
- In-app notification history

### ⚙️ Settings & Configuration
- API configuration
- Notification preferences
- Theme customization
- Currency and language settings

## Getting Started

### Prerequisites
- Node.js 16+
- npm or yarn
- Expo CLI: `npm install -g expo-cli`

### Installation

```bash
cd mobile
npm install
```

### Development

#### iOS (macOS only)
```bash
npm run ios
```

#### Android
```bash
npm run android
```

#### Web (Testing)
```bash
npm run web
```

#### Expo Go (Quick testing)
```bash
npm start
```

Then scan the QR code with the Expo Go app on your phone.

## Building for Production

### iOS
```bash
npm run build:ios
```

Then follow the EAS Build instructions to complete the build process.

### Android
```bash
npm run build:android
```

## Project Structure

```
mobile/
├── src/
│   ├── App.jsx              # Main app component with navigation
│   ├── store.js             # Redux store configuration
│   ├── screens/             # App screens
│   │   ├── DashboardScreen.jsx
│   │   ├── SearchScreen.jsx
│   │   ├── PortfolioScreen.jsx
│   │   ├── AlertsScreen.jsx
│   │   ├── SettingsScreen.jsx
│   │   ├── StockDetailScreen.jsx
│   │   └── WatchlistScreen.jsx
│   └── slices/              # Redux slices
│       ├── stocksSlice.js
│       ├── portfolioSlice.js
│       ├── alertsSlice.js
│       └── settingsSlice.js
├── app.json                 # Expo configuration
├── package.json
└── index.js
```

## API Integration

The app connects to the Stock Advisor backend API at `https://api.stockadvisor.com`:

- `GET /stocks/search?q={query}` - Search stocks
- `GET /portfolio` - Get user portfolio
- `GET /alerts` - Get user alerts
- `POST /alerts` - Create new alert

## Authentication

API key stored securely in Expo SecureStore (encrypted on device):
- iOS: Keychain
- Android: Keystore

## Notifications

Powered by Expo Notifications:
- Real-time alerts on price movements
- Customizable notification channels
- Local and push notifications

## State Management

Redux with thunk middleware:
- **stocks**: Search results and favorites
- **portfolio**: Holdings and performance
- **alerts**: Alert rules and history
- **settings**: User preferences

## Styling

- Dark theme by default
- Material Design principles
- React Native built-in components
- Consistent color scheme (#2196F3 primary)

## Testing

```bash
npm test
```

## Troubleshooting

### Build Issues
- Clear cache: `expo clear`
- Reinstall: `rm -rf node_modules && npm install`
- Reset packager: `expo start --reset-cache`

### API Connection
- Ensure API endpoint is correct in settings
- Check API key is valid
- Verify network connectivity

### Notifications
- Check notification permissions are granted
- Ensure device has internet connection
- Test with local push notifications first

## Performance Optimization

- Memoized components with React.memo
- Lazy loading with React.lazy
- Image optimization
- Async storage for offline data

## Security

- API keys encrypted in SecureStore
- No sensitive data in AsyncStorage
- HTTPS only for API calls
- Secure token refresh mechanism

## Version History

### 1.0.0 (Initial Release)
- Dashboard with portfolio tracking
- Stock search functionality
- Portfolio management
- Alerts and notifications
- Settings and preferences

## Contributing

Contributions welcome! Please follow the project structure and style guidelines.

## License

MIT License - See LICENSE file for details

## Support

- 📧 Email: support@stockadvisor.com
- 🐛 Issues: GitHub Issues
- 💬 Discord: [Community Discord]

## Future Features

- 📈 Advanced charting with candlestick analysis
- 🤖 AI-powered recommendations
- 💰 Options trading interface
- 📊 Portfolio analytics and rebalancing
- 🌍 International market support
- 📱 Widget support (iOS)
