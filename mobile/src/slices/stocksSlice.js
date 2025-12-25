/**
 * Stocks Redux Slice
 */

const initialState = {
  stocks: [],
  searchResults: [],
  loading: false,
  error: null,
};

const STOCKS_FETCH_START = 'STOCKS_FETCH_START';
const STOCKS_FETCH_SUCCESS = 'STOCKS_FETCH_SUCCESS';
const STOCKS_FETCH_ERROR = 'STOCKS_FETCH_ERROR';
const SEARCH_STOCKS = 'SEARCH_STOCKS';

export const fetchStocks = (query) => async (dispatch) => {
  dispatch({ type: STOCKS_FETCH_START });
  try {
    const response = await fetch(
      `https://api.stockadvisor.com/stocks/search?q=${query}`
    );
    const data = await response.json();
    dispatch({ type: SEARCH_STOCKS, payload: data });
  } catch (error) {
    dispatch({ type: STOCKS_FETCH_ERROR, payload: error.message });
  }
};

const stocksReducer = (state = initialState, action) => {
  switch (action.type) {
    case STOCKS_FETCH_START:
      return { ...state, loading: true, error: null };
    case STOCKS_FETCH_SUCCESS:
      return { ...state, stocks: action.payload, loading: false };
    case SEARCH_STOCKS:
      return { ...state, searchResults: action.payload, loading: false };
    case STOCKS_FETCH_ERROR:
      return { ...state, error: action.payload, loading: false };
    default:
      return state;
  }
};

export default stocksReducer;
