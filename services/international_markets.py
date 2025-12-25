"""
International Markets Support Service
Support for major exchanges, currency conversion, foreign tax considerations
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import yfinance as yf


class Exchange(Enum):
    """Stock exchanges"""
    NYSE = "NYSE"      # United States - New York Stock Exchange
    NASDAQ = "NASDAQ"  # United States - NASDAQ
    LSE = "LSE"        # United Kingdom - London Stock Exchange
    TSE = "TSE"        # Japan - Tokyo Stock Exchange
    ASX = "ASX"        # Australia - Australian Securities Exchange
    TSX = "TSX"        # Canada - Toronto Stock Exchange
    EURONEXT = "EURONEXT"  # Europe - Euronext
    HKEX = "HKEX"      # Hong Kong - Hong Kong Stock Exchange


class Currency(Enum):
    """Major currencies"""
    USD = "USD"  # US Dollar
    GBP = "GBP"  # British Pound
    JPY = "JPY"  # Japanese Yen
    AUD = "AUD"  # Australian Dollar
    CAD = "CAD"  # Canadian Dollar
    EUR = "EUR"  # Euro
    HKD = "HKD"  # Hong Kong Dollar


@dataclass
class ExchangeInfo:
    """Information about a stock exchange"""
    exchange: Exchange
    country: str
    currency: Currency
    trading_hours_open: str  # HH:MM (UTC)
    trading_hours_close: str
    timezone: str
    settlement_days: int  # T+X settlement
    market_cap_requirement: float  # Minimum listing requirement
    dividend_tax_rate: float  # Withholding tax on dividends (0-1)
    capital_gains_tax_rate: float  # Capital gains tax (0-1)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'exchange': self.exchange.value,
            'country': self.country,
            'currency': self.currency.value,
            'trading_hours_open': self.trading_hours_open,
            'trading_hours_close': self.trading_hours_close,
            'timezone': self.timezone,
            'settlement_days': self.settlement_days,
            'market_cap_requirement': self.market_cap_requirement,
            'dividend_tax_rate': self.dividend_tax_rate,
            'capital_gains_tax_rate': self.capital_gains_tax_rate
        }


@dataclass
class InternationalStock:
    """Stock traded on international exchange"""
    symbol: str
    exchange: Exchange
    company_name: str
    currency: Currency
    price_local: float
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'exchange': self.exchange.value,
            'company_name': self.company_name,
            'currency': self.currency.value,
            'price_local': self.price_local,
            'market_cap': self.market_cap,
            'pe_ratio': self.pe_ratio,
            'dividend_yield': self.dividend_yield
        }


@dataclass
class CurrencyRate:
    """Currency exchange rate"""
    from_currency: Currency
    to_currency: Currency
    rate: float
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None


@dataclass
class InternationalTaxPosition:
    """Tax position for international holdings"""
    symbol: str
    exchange: Exchange
    shares: float
    cost_basis_local: float
    current_price_local: float
    dividend_tax_rate: float
    capital_gains_tax_rate: float
    
    def calculate_after_tax_gain(self) -> float:
        """Calculate gain after taxes"""
        unrealized_gain = (self.current_price_local - self.cost_basis_local) * self.shares
        tax_on_gain = unrealized_gain * self.capital_gains_tax_rate
        return unrealized_gain - tax_on_gain
    
    def calculate_dividend_tax(self, dividend_amount: float) -> float:
        """Calculate tax on dividend"""
        return dividend_amount * self.dividend_tax_rate
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'exchange': self.exchange.value,
            'shares': self.shares,
            'cost_basis_local': self.cost_basis_local,
            'current_price_local': self.current_price_local,
            'dividend_tax_rate': self.dividend_tax_rate,
            'capital_gains_tax_rate': self.capital_gains_tax_rate,
            'after_tax_gain': self.calculate_after_tax_gain()
        }


class ExchangeDatabase:
    """Database of international exchange information"""
    
    EXCHANGES = {
        Exchange.NYSE: ExchangeInfo(
            exchange=Exchange.NYSE,
            country="United States",
            currency=Currency.USD,
            trading_hours_open="14:30",  # 9:30 AM ET in UTC
            trading_hours_close="21:00",  # 4:00 PM ET in UTC
            timezone="America/New_York",
            settlement_days=2,
            market_cap_requirement=100e6,
            dividend_tax_rate=0.0,
            capital_gains_tax_rate=0.15  # Long-term cap gains
        ),
        Exchange.LSE: ExchangeInfo(
            exchange=Exchange.LSE,
            country="United Kingdom",
            currency=Currency.GBP,
            trading_hours_open="08:00",
            trading_hours_close="16:30",
            timezone="Europe/London",
            settlement_days=2,
            market_cap_requirement=700000,
            dividend_tax_rate=0.20,
            capital_gains_tax_rate=0.20
        ),
        Exchange.TSE: ExchangeInfo(
            exchange=Exchange.TSE,
            country="Japan",
            currency=Currency.JPY,
            trading_hours_open="00:00",  # 9:00 AM JST
            trading_hours_close="06:30",  # 3:00 PM JST
            timezone="Asia/Tokyo",
            settlement_days=3,
            market_cap_requirement=20e9,
            dividend_tax_rate=0.20,
            capital_gains_tax_rate=0.20
        ),
        Exchange.ASX: ExchangeInfo(
            exchange=Exchange.ASX,
            country="Australia",
            currency=Currency.AUD,
            trading_hours_open="22:00",  # 10:00 AM AEST
            trading_hours_close="04:00",  # 4:00 PM AEST
            timezone="Australia/Sydney",
            settlement_days=2,
            market_cap_requirement=5e6,
            dividend_tax_rate=0.15,
            capital_gains_tax_rate=0.50  # 50% inclusion on gains
        ),
        Exchange.TSX: ExchangeInfo(
            exchange=Exchange.TSX,
            country="Canada",
            currency=Currency.CAD,
            trading_hours_open="13:30",  # 9:30 AM ET
            trading_hours_close="20:00",  # 4:00 PM ET
            timezone="America/Toronto",
            settlement_days=2,
            market_cap_requirement=10e6,
            dividend_tax_rate=0.0,  # Canada-US tax treaty
            capital_gains_tax_rate=0.50  # 50% inclusion on gains
        )
    }
    
    @classmethod
    def get_exchange_info(cls, exchange: Exchange) -> Optional[ExchangeInfo]:
        """Get exchange information"""
        return cls.EXCHANGES.get(exchange)
    
    @classmethod
    def get_all_exchanges(cls) -> List[ExchangeInfo]:
        """Get all exchange information"""
        return list(cls.EXCHANGES.values())


class CurrencyConverter:
    """Convert between currencies"""
    
    def __init__(self):
        self.rates: Dict[Tuple[Currency, Currency], CurrencyRate] = {}
        self.last_update = {}
    
    def fetch_exchange_rate(self, from_currency: Currency, to_currency: Currency) -> Optional[float]:
        """
        Fetch currency exchange rate
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            Exchange rate (or None if error)
        """
        try:
            if from_currency == to_currency:
                return 1.0
            
            # Try to get from cache
            key = (from_currency, to_currency)
            if key in self.rates:
                cached_rate = self.rates[key]
                # Use cache if less than 1 hour old
                if (datetime.now() - cached_rate.timestamp).total_seconds() < 3600:
                    return cached_rate.rate
            
            # Fetch from Yahoo Finance
            pair = f"{from_currency.value}{to_currency.value}=X"
            ticker = yf.Ticker(pair)
            
            try:
                data = ticker.history(period='1d')
                if len(data) > 0:
                    rate = data['Close'].iloc[-1]
                    
                    # Cache the rate
                    self.rates[key] = CurrencyRate(
                        from_currency=from_currency,
                        to_currency=to_currency,
                        rate=float(rate),
                        timestamp=datetime.now()
                    )
                    
                    return float(rate)
            except:
                pass
            
            # Default rates if fetch fails
            default_rates = {
                (Currency.USD, Currency.GBP): 0.79,
                (Currency.GBP, Currency.USD): 1.27,
                (Currency.USD, Currency.JPY): 110.0,
                (Currency.JPY, Currency.USD): 0.0091,
                (Currency.USD, Currency.AUD): 1.35,
                (Currency.AUD, Currency.USD): 0.74,
                (Currency.USD, Currency.CAD): 1.25,
                (Currency.CAD, Currency.USD): 0.80,
                (Currency.USD, Currency.EUR): 0.92,
                (Currency.EUR, Currency.USD): 1.09,
            }
            
            return default_rates.get(key, None)
        
        except Exception as e:
            print(f"Error fetching exchange rate: {e}")
            return None
    
    def convert(self, amount: float, from_currency: Currency, 
                to_currency: Currency) -> Optional[float]:
        """
        Convert amount between currencies
        
        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            Converted amount (or None if error)
        """
        if from_currency == to_currency:
            return amount
        
        rate = self.fetch_exchange_rate(from_currency, to_currency)
        if rate is None:
            return None
        
        return amount * rate


class InternationalStockFetcher:
    """Fetch international stock data"""
    
    def __init__(self):
        self.converter = CurrencyConverter()
        self.cache = {}
    
    def fetch_stock(self, symbol: str, exchange: Exchange) -> Optional[InternationalStock]:
        """
        Fetch international stock data
        
        Args:
            symbol: Stock symbol
            exchange: Exchange where listed
            
        Returns:
            InternationalStock object
        """
        try:
            # Build full ticker symbol
            exchange_map = {
                Exchange.LSE: ".L",
                Exchange.TSE: ".T",
                Exchange.ASX: ".AX",
                Exchange.TSX: ".TO",
            }
            
            suffix = exchange_map.get(exchange, "")
            full_symbol = f"{symbol}{suffix}" if suffix else symbol
            
            ticker = yf.Ticker(full_symbol)
            info = ticker.info if hasattr(ticker, 'info') else {}
            
            exchange_info = ExchangeDatabase.get_exchange_info(exchange)
            
            stock = InternationalStock(
                symbol=symbol,
                exchange=exchange,
                company_name=info.get('longName', ''),
                currency=exchange_info.currency,
                price_local=info.get('currentPrice', 0),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield')
            )
            
            self.cache[f"{symbol}_{exchange.value}"] = stock
            return stock
        
        except Exception as e:
            print(f"Error fetching {symbol} on {exchange.value}: {e}")
            return None
    
    def convert_to_local_currency(self, stock: InternationalStock, 
                                 base_currency: Currency) -> Dict:
        """
        Convert stock price to base currency
        
        Args:
            stock: InternationalStock object
            base_currency: Currency to convert to
            
        Returns:
            Dict with converted prices
        """
        if stock.currency == base_currency:
            return {
                'price_local': stock.price_local,
                'price_base': stock.price_local,
                'exchange_rate': 1.0
            }
        
        rate = self.converter.fetch_exchange_rate(stock.currency, base_currency)
        if rate is None:
            return {}
        
        return {
            'price_local': stock.price_local,
            'price_base': stock.price_local * rate,
            'exchange_rate': rate
        }


class InternationalPortfolioManager:
    """Manage international stock portfolio"""
    
    def __init__(self, base_currency: Currency = Currency.USD):
        self.base_currency = base_currency
        self.holdings: Dict[str, InternationalStock] = {}
        self.shares: Dict[str, float] = {}
        self.tax_positions: Dict[str, InternationalTaxPosition] = {}
        self.fetcher = InternationalStockFetcher()
        self.converter = CurrencyConverter()
    
    def add_holding(self, symbol: str, exchange: Exchange, shares: float, 
                   cost_basis_local: float) -> bool:
        """Add international holding"""
        try:
            stock = self.fetcher.fetch_stock(symbol, exchange)
            if stock:
                key = f"{symbol}_{exchange.value}"
                self.holdings[key] = stock
                self.shares[key] = shares
                
                # Create tax position
                exchange_info = ExchangeDatabase.get_exchange_info(exchange)
                self.tax_positions[key] = InternationalTaxPosition(
                    symbol=symbol,
                    exchange=exchange,
                    shares=shares,
                    cost_basis_local=cost_basis_local,
                    current_price_local=stock.price_local,
                    dividend_tax_rate=exchange_info.dividend_tax_rate,
                    capital_gains_tax_rate=exchange_info.capital_gains_tax_rate
                )
                
                return True
        except Exception as e:
            print(f"Error adding holding: {e}")
        
        return False
    
    def get_portfolio_value_base_currency(self) -> Dict:
        """Get total portfolio value in base currency"""
        total_value = 0.0
        details = []
        
        for key, stock in self.holdings.items():
            shares = self.shares[key]
            local_value = stock.price_local * shares
            
            # Convert to base currency
            base_value = self.converter.convert(
                local_value,
                stock.currency,
                self.base_currency
            )
            
            if base_value:
                total_value += base_value
                details.append({
                    'symbol': stock.symbol,
                    'exchange': stock.exchange.value,
                    'shares': shares,
                    'price_local': stock.price_local,
                    'value_local': local_value,
                    'value_base': base_value
                })
        
        return {
            'total_value': total_value,
            'base_currency': self.base_currency.value,
            'holdings': details
        }
    
    def get_tax_report(self) -> Dict:
        """Generate tax report for international holdings"""
        total_gains = 0.0
        total_taxes = 0.0
        positions = []
        
        for key, position in self.tax_positions.items():
            after_tax_gain = position.calculate_after_tax_gain()
            total_gains += after_tax_gain
            
            # Estimate tax on dividends
            stock = self.holdings[key]
            annual_dividend = (stock.dividend_yield or 0) * position.shares * position.current_price_local
            dividend_tax = position.calculate_dividend_tax(annual_dividend)
            total_taxes += dividend_tax
            
            positions.append({
                'symbol': position.symbol,
                'exchange': position.exchange.value,
                'after_tax_gain': after_tax_gain,
                'dividend_tax_rate': position.dividend_tax_rate,
                'capital_gains_tax_rate': position.capital_gains_tax_rate,
                'estimated_dividend_tax': dividend_tax
            })
        
        return {
            'total_after_tax_gains': total_gains,
            'estimated_annual_taxes': total_taxes,
            'positions': positions
        }
    
    def compare_exchange_fees(self, stocks: List[str]) -> Dict:
        """Compare trading conditions across exchanges"""
        comparison = {}
        
        for exchange_info in ExchangeDatabase.get_all_exchanges():
            comparison[exchange_info.exchange.value] = {
                'country': exchange_info.country,
                'currency': exchange_info.currency.value,
                'settlement_days': exchange_info.settlement_days,
                'dividend_tax': f"{exchange_info.dividend_tax_rate*100:.0f}%",
                'capital_gains_tax': f"{exchange_info.capital_gains_tax_rate*100:.0f}%",
                'trading_hours_utc': f"{exchange_info.trading_hours_open}-{exchange_info.trading_hours_close}"
            }
        
        return comparison


class InternationalMarketAnalyzer:
    """Analyze international markets"""
    
    def __init__(self):
        self.converter = CurrencyConverter()
    
    def get_currency_strength(self, base_currency: Currency,
                             compare_to: List[Currency]) -> Dict:
        """
        Analyze currency strength
        
        Args:
            base_currency: Reference currency
            compare_to: Currencies to compare against
            
        Returns:
            Dict with strength analysis
        """
        analysis = {}
        
        for currency in compare_to:
            rate = self.converter.fetch_exchange_rate(base_currency, currency)
            if rate:
                analysis[currency.value] = {
                    'rate': rate,
                    'trend': 'stable'  # Would need historical data for trend
                }
        
        return analysis
    
    def get_regional_overview(self) -> Dict:
        """Get overview of major markets"""
        return {
            'north_america': {
                'exchanges': ['NYSE', 'NASDAQ', 'TSX'],
                'currencies': ['USD', 'CAD']
            },
            'europe': {
                'exchanges': ['LSE', 'EURONEXT'],
                'currencies': ['GBP', 'EUR']
            },
            'asia_pacific': {
                'exchanges': ['TSE', 'ASX', 'HKEX'],
                'currencies': ['JPY', 'AUD', 'HKD']
            }
        }
