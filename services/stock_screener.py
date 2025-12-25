"""
Advanced Stock Screener Service
Multi-criteria filtering with saved screens and bulk analysis
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
from enum import Enum
import yfinance as yf
import pandas as pd
from datetime import datetime


class ComparisonOperator(Enum):
    """Comparison operators for filtering"""
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="
    IN_RANGE = "in_range"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"


class SortOrder(Enum):
    """Sort order"""
    ASCENDING = "asc"
    DESCENDING = "desc"


@dataclass
class FilterCriteria:
    """Single filter criterion"""
    field: str  # e.g., 'pe_ratio', 'market_cap', 'dividend_yield'
    operator: ComparisonOperator
    value: any
    value2: Optional[any] = None  # For IN_RANGE operator
    
    def evaluate(self, field_value: any) -> bool:
        """Evaluate if field value matches criteria"""
        if field_value is None:
            return False
        
        if self.operator == ComparisonOperator.EQUALS:
            return field_value == self.value
        elif self.operator == ComparisonOperator.NOT_EQUALS:
            return field_value != self.value
        elif self.operator == ComparisonOperator.GREATER_THAN:
            return float(field_value) > float(self.value)
        elif self.operator == ComparisonOperator.LESS_THAN:
            return float(field_value) < float(self.value)
        elif self.operator == ComparisonOperator.GREATER_THAN_OR_EQUAL:
            return float(field_value) >= float(self.value)
        elif self.operator == ComparisonOperator.LESS_THAN_OR_EQUAL:
            return float(field_value) <= float(self.value)
        elif self.operator == ComparisonOperator.IN_RANGE:
            val = float(field_value)
            return float(self.value) <= val <= float(self.value2)
        elif self.operator == ComparisonOperator.CONTAINS:
            return str(self.value).lower() in str(field_value).lower()
        elif self.operator == ComparisonOperator.STARTS_WITH:
            return str(field_value).lower().startswith(str(self.value).lower())
        
        return False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'field': self.field,
            'operator': self.operator.value,
            'value': self.value,
            'value2': self.value2
        }


@dataclass
class SortCriteria:
    """Sort criteria"""
    field: str
    order: SortOrder = SortOrder.DESCENDING
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'field': self.field,
            'order': self.order.value
        }


@dataclass
class ScreenResult:
    """Result of a screen"""
    symbol: str
    name: Optional[str] = None
    price: Optional[float] = None
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    dividend_yield: Optional[float] = None
    earnings_growth: Optional[float] = None
    revenue_growth: Optional[float] = None
    profit_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    volume: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    score: float = 0.0  # Match score based on criteria
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'price': self.price,
            'pe_ratio': self.pe_ratio,
            'market_cap': self.market_cap,
            'dividend_yield': self.dividend_yield,
            'earnings_growth': self.earnings_growth,
            'revenue_growth': self.revenue_growth,
            'profit_margin': self.profit_margin,
            'debt_to_equity': self.debt_to_equity,
            'rsi': self.rsi,
            'macd': self.macd,
            'volume': self.volume,
            'sector': self.sector,
            'industry': self.industry,
            'score': self.score
        }


@dataclass
class SavedScreen:
    """Saved screen configuration"""
    name: str
    description: str = ""
    filters: List[FilterCriteria] = field(default_factory=list)
    sort: Optional[SortCriteria] = None
    limit: int = 50
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    results_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'filters': [f.to_dict() for f in self.filters],
            'sort': self.sort.to_dict() if self.sort else None,
            'limit': self.limit,
            'created_at': self.created_at.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'results_count': self.results_count
        }


class StockDataFetcher:
    """Fetch stock data for screening"""
    
    # Pre-defined universes
    UNIVERSES = {
        'sp500': [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BERKB', 'V', 'JNJ',
            'WMT', 'JPM', 'PG', 'XOM', 'MA', 'HD', 'PFE', 'KO', 'ABBV', 'LLY'
        ],
        'tech': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AMD', 'ADBE', 'CRM', 'NFLX', 'TSLA'],
        'dividend': ['JNJ', 'PG', 'KO', 'PEP', 'CSCO', 'IBM', 'MCD', 'AXP', 'NEE', 'SO'],
        'growth': ['NVDA', 'TSLA', 'AMD', 'NFLX', 'SHOP', 'ZOOM', 'ROKU', 'PAYC', 'DDOG', 'CRWD'],
        'value': ['BAC', 'GE', 'F', 'GM', 'IBM', 'VZ', 'T', 'CVX', 'COP', 'SLB'],
        'small_cap': ['NWL', 'EXPE', 'CPRT', 'CRVS', 'DKNG', 'MRVL', 'CRWD', 'ZM', 'TTD', 'FTNT']
    }
    
    def __init__(self):
        self.cache = {}
        self.last_fetch_time = {}
    
    def fetch_stock_data(self, symbol: str) -> Dict:
        """
        Fetch comprehensive stock data
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with stock data
        """
        try:
            # Try to get from cache
            if symbol in self.cache:
                return self.cache[symbol]
            
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            hist = ticker.history(period='1y')
            
            # Get info
            info = ticker.info if hasattr(ticker, 'info') else {}
            
            # Get financials
            try:
                financials = ticker.quarterly_financials
            except:
                financials = None
            
            # Calculate metrics
            rsi = self._calculate_rsi(hist['Close'])
            macd = self._calculate_macd(hist['Close'])
            
            data = {
                'symbol': symbol,
                'name': info.get('longName', ''),
                'price': info.get('currentPrice', 0),
                'pe_ratio': info.get('trailingPE', None),
                'forward_pe': info.get('forwardPE', None),
                'market_cap': info.get('marketCap', None),
                'dividend_yield': info.get('dividendYield', None),
                'earnings_growth': info.get('earningsGrowth', None),
                'revenue_growth': info.get('revenueGrowth', None),
                'profit_margin': info.get('profitMargins', None),
                'debt_to_equity': info.get('debtToEquity', None),
                'rsi': rsi,
                'macd': macd,
                'volume': info.get('volume', None),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                '52w_high': info.get('fiftyTwoWeekHigh', None),
                '52w_low': info.get('fiftyTwoWeekLow', None),
                'average_volume': info.get('averageVolume', None),
                'beta': info.get('beta', None),
                'roa': info.get('returnOnAssets', None),
                'roe': info.get('returnOnEquity', None)
            }
            
            # Cache
            self.cache[symbol] = data
            self.last_fetch_time[symbol] = datetime.now()
            
            return data
        
        except Exception as e:
            return {
                'symbol': symbol,
                'error': str(e)
            }
    
    def _calculate_rsi(self, prices, period: int = 14) -> float:
        """Calculate RSI"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except:
            return None
    
    def _calculate_macd(self, prices, fast: int = 12, slow: int = 26) -> float:
        """Calculate MACD"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd = ema_fast - ema_slow
            return float(macd.iloc[-1])
        except:
            return None
    
    def get_universe(self, universe_name: str) -> List[str]:
        """Get predefined stock universe"""
        return self.UNIVERSES.get(universe_name.lower(), [])


class StockScreener:
    """Advanced stock screener with filtering and analysis"""
    
    def __init__(self):
        self.fetcher = StockDataFetcher()
        self.saved_screens: Dict[str, SavedScreen] = {}
        self.recent_results: Dict[str, List[ScreenResult]] = {}
    
    def create_screen(self, name: str, description: str = "") -> SavedScreen:
        """Create new saved screen"""
        screen = SavedScreen(name=name, description=description)
        self.saved_screens[name] = screen
        return screen
    
    def add_filter(self, screen_name: str, field: str, operator: ComparisonOperator, 
                   value: any, value2: Optional[any] = None):
        """Add filter to screen"""
        if screen_name not in self.saved_screens:
            raise ValueError(f"Screen '{screen_name}' not found")
        
        criteria = FilterCriteria(field, operator, value, value2)
        self.saved_screens[screen_name].filters.append(criteria)
    
    def set_sort(self, screen_name: str, field: str, order: SortOrder = SortOrder.DESCENDING):
        """Set sort criteria for screen"""
        if screen_name not in self.saved_screens:
            raise ValueError(f"Screen '{screen_name}' not found")
        
        self.saved_screens[screen_name].sort = SortCriteria(field, order)
    
    def run_screen(self, screen_name: str, universe: str = 'sp500') -> List[ScreenResult]:
        """
        Run a saved screen
        
        Args:
            screen_name: Name of saved screen
            universe: Stock universe to screen
            
        Returns:
            List of ScreenResult
        """
        if screen_name not in self.saved_screens:
            raise ValueError(f"Screen '{screen_name}' not found")
        
        screen = self.saved_screens[screen_name]
        symbols = self.fetcher.get_universe(universe)
        
        results = []
        
        # Fetch and filter stocks
        for symbol in symbols:
            data = self.fetcher.fetch_stock_data(symbol)
            
            if 'error' in data:
                continue
            
            # Check if all filters pass
            match_count = 0
            for filter_criteria in screen.filters:
                field_value = data.get(filter_criteria.field)
                if filter_criteria.evaluate(field_value):
                    match_count += 1
            
            # Calculate match score
            if len(screen.filters) > 0:
                score = (match_count / len(screen.filters)) * 100
            else:
                score = 100.0
            
            # Only include if passes filters or no filters
            if len(screen.filters) == 0 or match_count == len(screen.filters):
                result = ScreenResult(
                    symbol=data['symbol'],
                    name=data.get('name'),
                    price=data.get('price'),
                    pe_ratio=data.get('pe_ratio'),
                    market_cap=data.get('market_cap'),
                    dividend_yield=data.get('dividend_yield'),
                    earnings_growth=data.get('earnings_growth'),
                    revenue_growth=data.get('revenue_growth'),
                    profit_margin=data.get('profit_margin'),
                    debt_to_equity=data.get('debt_to_equity'),
                    rsi=data.get('rsi'),
                    macd=data.get('macd'),
                    volume=data.get('volume'),
                    sector=data.get('sector'),
                    industry=data.get('industry'),
                    score=score
                )
                results.append(result)
        
        # Sort results
        if screen.sort:
            reverse = (screen.sort.order == SortOrder.DESCENDING)
            results.sort(
                key=lambda x: getattr(x, screen.sort.field) or 0,
                reverse=reverse
            )
        else:
            # Default: sort by score
            results.sort(key=lambda x: x.score, reverse=True)
        
        # Limit results
        results = results[:screen.limit]
        
        # Update screen
        screen.last_run = datetime.now()
        screen.results_count = len(results)
        
        # Save results
        self.recent_results[screen_name] = results
        
        return results
    
    def quick_screen(self, universe: str = 'sp500', 
                    filters: Optional[List[FilterCriteria]] = None,
                    sort: Optional[SortCriteria] = None,
                    limit: int = 50) -> List[ScreenResult]:
        """
        Quick screen without saving
        
        Args:
            universe: Stock universe
            filters: List of filters to apply
            sort: Sort criteria
            limit: Max results
            
        Returns:
            List of ScreenResult
        """
        symbols = self.fetcher.get_universe(universe)
        results = []
        
        for symbol in symbols:
            data = self.fetcher.fetch_stock_data(symbol)
            
            if 'error' in data:
                continue
            
            # Check filters
            if filters:
                passes_all = True
                for filter_criteria in filters:
                    field_value = data.get(filter_criteria.field)
                    if not filter_criteria.evaluate(field_value):
                        passes_all = False
                        break
                
                if not passes_all:
                    continue
            
            # Add to results
            result = ScreenResult(
                symbol=data['symbol'],
                name=data.get('name'),
                price=data.get('price'),
                pe_ratio=data.get('pe_ratio'),
                market_cap=data.get('market_cap'),
                dividend_yield=data.get('dividend_yield'),
                earnings_growth=data.get('earnings_growth'),
                revenue_growth=data.get('revenue_growth'),
                profit_margin=data.get('profit_margin'),
                debt_to_equity=data.get('debt_to_equity'),
                rsi=data.get('rsi'),
                macd=data.get('macd'),
                volume=data.get('volume'),
                sector=data.get('sector'),
                industry=data.get('industry'),
                score=100.0
            )
            results.append(result)
        
        # Sort
        if sort:
            reverse = (sort.order == SortOrder.DESCENDING)
            results.sort(
                key=lambda x: getattr(x, sort.field) or 0,
                reverse=reverse
            )
        
        # Limit
        return results[:limit]
    
    def get_saved_screens(self) -> List[SavedScreen]:
        """Get all saved screens"""
        return list(self.saved_screens.values())
    
    def delete_screen(self, name: str):
        """Delete saved screen"""
        if name in self.saved_screens:
            del self.saved_screens[name]
    
    def export_results(self, screen_name: str) -> pd.DataFrame:
        """Export screen results to DataFrame"""
        if screen_name not in self.recent_results:
            return pd.DataFrame()
        
        results = self.recent_results[screen_name]
        data = [r.to_dict() for r in results]
        return pd.DataFrame(data)
    
    def get_sector_breakdown(self, screen_name: str) -> Dict[str, int]:
        """Get sector breakdown of screen results"""
        if screen_name not in self.recent_results:
            return {}
        
        sectors = {}
        for result in self.recent_results[screen_name]:
            sector = result.sector or "Unknown"
            sectors[sector] = sectors.get(sector, 0) + 1
        
        return sectors
    
    def get_stats(self, screen_name: str) -> Dict:
        """Get statistics of screen results"""
        if screen_name not in self.recent_results:
            return {}
        
        results = self.recent_results[screen_name]
        
        pe_ratios = [r.pe_ratio for r in results if r.pe_ratio]
        yields = [r.dividend_yield for r in results if r.dividend_yield]
        
        return {
            'total_results': len(results),
            'avg_pe_ratio': sum(pe_ratios) / len(pe_ratios) if pe_ratios else None,
            'avg_dividend_yield': sum(yields) / len(yields) if yields else None,
            'sectors': self.get_sector_breakdown(screen_name),
            'top_by_rsi': sorted(results, key=lambda x: x.rsi or 0, reverse=True)[:5],
            'top_by_price': sorted(results, key=lambda x: x.price or 0, reverse=True)[:5]
        }
