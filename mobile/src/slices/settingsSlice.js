/**
 * Settings Redux Slice
 */

const initialState = {
  theme: 'dark',
  notifications: true,
  currency: 'USD',
  language: 'en',
  apiToken: null,
};

const UPDATE_SETTING = 'UPDATE_SETTING';
const SET_API_TOKEN = 'SET_API_TOKEN';

const settingsReducer = (state = initialState, action) => {
  switch (action.type) {
    case UPDATE_SETTING:
      return {
        ...state,
        [action.payload.key]: action.payload.value,
      };
    case SET_API_TOKEN:
      return {
        ...state,
        apiToken: action.payload,
      };
    default:
      return state;
  }
};

export default settingsReducer;
