/**
 * Alerts Redux Slice
 */

const initialState = {
  alerts: [],
  unreadCount: 0,
  loading: false,
  error: null,
};

const ALERTS_FETCH_START = 'ALERTS_FETCH_START';
const ALERTS_FETCH_SUCCESS = 'ALERTS_FETCH_SUCCESS';
const ALERTS_FETCH_ERROR = 'ALERTS_FETCH_ERROR';
const MARK_ALERT_READ = 'MARK_ALERT_READ';
const NEW_ALERT = 'NEW_ALERT';

export const fetchAlerts = () => async (dispatch) => {
  dispatch({ type: ALERTS_FETCH_START });
  try {
    const response = await fetch('https://api.stockadvisor.com/alerts');
    const data = await response.json();
    dispatch({ type: ALERTS_FETCH_SUCCESS, payload: data });
  } catch (error) {
    dispatch({ type: ALERTS_FETCH_ERROR, payload: error.message });
  }
};

const alertsReducer = (state = initialState, action) => {
  switch (action.type) {
    case ALERTS_FETCH_START:
      return { ...state, loading: true, error: null };
    case ALERTS_FETCH_SUCCESS:
      return {
        ...state,
        alerts: action.payload,
        unreadCount: action.payload.filter((a) => !a.read).length,
        loading: false,
      };
    case MARK_ALERT_READ:
      return {
        ...state,
        alerts: state.alerts.map((a) =>
          a.id === action.payload ? { ...a, read: true } : a
        ),
        unreadCount: Math.max(0, state.unreadCount - 1),
      };
    case NEW_ALERT:
      return {
        ...state,
        alerts: [action.payload, ...state.alerts],
        unreadCount: state.unreadCount + 1,
      };
    case ALERTS_FETCH_ERROR:
      return { ...state, error: action.payload, loading: false };
    default:
      return state;
  }
};

export default alertsReducer;
