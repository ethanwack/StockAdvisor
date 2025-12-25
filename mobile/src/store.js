/**
 * Redux Store Configuration
 */

import { createStore, combineReducers, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';
import stocksReducer from './slices/stocksSlice';
import portfolioReducer from './slices/portfolioSlice';
import alertsReducer from './slices/alertsSlice';
import settingsReducer from './slices/settingsSlice';

const rootReducer = combineReducers({
  stocks: stocksReducer,
  portfolio: portfolioReducer,
  alerts: alertsReducer,
  settings: settingsReducer,
});

export const store = createStore(rootReducer, applyMiddleware(thunk));
