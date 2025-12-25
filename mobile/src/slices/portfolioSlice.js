/**
 * Portfolio Redux Slice
 */

const initialState = {
  holdings: [],
  totalValue: 0,
  dayChange: 0,
  loading: false,
  error: null,
};

const PORTFOLIO_FETCH_START = 'PORTFOLIO_FETCH_START';
const PORTFOLIO_FETCH_SUCCESS = 'PORTFOLIO_FETCH_SUCCESS';
const PORTFOLIO_FETCH_ERROR = 'PORTFOLIO_FETCH_ERROR';
const ADD_HOLDING = 'ADD_HOLDING';
const REMOVE_HOLDING = 'REMOVE_HOLDING';

export const fetchPortfolio = () => async (dispatch) => {
  dispatch({ type: PORTFOLIO_FETCH_START });
  try {
    const response = await fetch('https://api.stockadvisor.com/portfolio');
    const data = await response.json();
    dispatch({ type: PORTFOLIO_FETCH_SUCCESS, payload: data });
  } catch (error) {
    dispatch({ type: PORTFOLIO_FETCH_ERROR, payload: error.message });
  }
};

const portfolioReducer = (state = initialState, action) => {
  switch (action.type) {
    case PORTFOLIO_FETCH_START:
      return { ...state, loading: true, error: null };
    case PORTFOLIO_FETCH_SUCCESS:
      return {
        ...state,
        holdings: action.payload.holdings,
        totalValue: action.payload.totalValue,
        dayChange: action.payload.dayChange,
        loading: false,
      };
    case ADD_HOLDING:
      return {
        ...state,
        holdings: [...state.holdings, action.payload],
      };
    case REMOVE_HOLDING:
      return {
        ...state,
        holdings: state.holdings.filter((h) => h.id !== action.payload),
      };
    case PORTFOLIO_FETCH_ERROR:
      return { ...state, error: action.payload, loading: false };
    default:
      return state;
  }
};

export default portfolioReducer;
