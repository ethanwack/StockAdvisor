"""
Dividend Tracker Service
Dividend calendar, yield tracking, ex-date reminders, dividend reinvestment calculator
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import yfinance as yf


class DividendFrequency(Enum):
    """Dividend payment frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi-annual"
    ANNUAL = "annual"
    SPECIAL = "special"


@dataclass
class DividendPayment:
    """Single dividend payment record"""
    symbol: str
    ex_date: datetime
    record_date: datetime
    payment_date: datetime
    amount: float
    frequency: DividendFrequency
    yield_percent: Optional[float] = None
    paid: bool = False
    
    def days_until_ex_date(self) -> int:
        """Days until ex-dividend date"""
        return (self.ex_date - datetime.now()).days
    
    def days_until_payment(self) -> int:
        """Days until payment date"""
        return (self.payment_date - datetime.now()).days
    
    def is_upcoming(self, days: int = 30) -> bool:
        """Check if dividend is upcoming within specified days"""
        return 0 <= self.days_until_ex_date() <= days
    
    def has_passed_ex_date(self) -> bool:
        """Check if ex-dividend date has passed"""
        return self.ex_date < datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'ex_date': self.ex_date.isoformat(),
            'record_date': self.record_date.isoformat(),
            'payment_date': self.payment_date.isoformat(),
            'amount': self.amount,
            'frequency': self.frequency.value,
            'yield_percent': self.yield_percent,
            'paid': self.paid
        }


@dataclass
class DividendHistory:
    """Dividend payment history for a stock"""
    symbol: str
    company_name: Optional[str] = None
    current_yield: float = 0.0
    annual_dividend: float = 0.0
    payout_frequency: DividendFrequency = DividendFrequency.QUARTERLY
    payment_history: List[DividendPayment] = field(default_factory=list)
    last_payment_date: Optional[datetime] = None
    next_payment_date: Optional[datetime] = None
    
    def add_payment(self, payment: DividendPayment):
        """Add dividend payment to history"""
        self.payment_history.append(payment)
        self.payment_history.sort(key=lambda x: x.payment_date)
    
    def get_payments_by_year(self, year: int) -> List[DividendPayment]:
        """Get payments for a specific year"""
        return [p for p in self.payment_history if p.payment_date.year == year]
    
    def get_annual_dividend(self, year: Optional[int] = None) -> float:
        """Get annual dividend amount"""
        if year is None:
            year = datetime.now().year
        
        payments = self.get_payments_by_year(year)
        return sum(p.amount for p in payments)
    
    def get_dividend_growth(self, years: int = 5) -> float:
        """Calculate dividend growth rate (CAGR)"""
        current_year = datetime.now().year
        start_year = current_year - years
        
        start_dividend = self.get_annual_dividend(start_year)
        current_dividend = self.get_annual_dividend(current_year)
        
        if start_dividend <= 0:
            return 0.0
        
        cagr = (((current_dividend / start_dividend) ** (1/years)) - 1) * 100
        return cagr
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'company_name': self.company_name,
            'current_yield': self.current_yield,
            'annual_dividend': self.annual_dividend,
            'payout_frequency': self.payout_frequency.value,
            'payment_history': [p.to_dict() for p in self.payment_history],
            'last_payment_date': self.last_payment_date.isoformat() if self.last_payment_date else None,
            'next_payment_date': self.next_payment_date.isoformat() if self.next_payment_date else None
        }


@dataclass
class PortfolioDividendPlan:
    """Portfolio-wide dividend plan"""
    holdings: Dict[str, float] = field(default_factory=dict)  # symbol -> shares
    next_payment: Optional[datetime] = None
    upcoming_payments: List[DividendPayment] = field(default_factory=list)
    monthly_dividend_income: float = 0.0
    
    def add_holding(self, symbol: str, shares: float):
        """Add stock holding"""
        self.holdings[symbol] = shares
    
    def remove_holding(self, symbol: str):
        """Remove stock holding"""
        if symbol in self.holdings:
            del self.holdings[symbol]
    
    def update_dividend_info(self, dividend_data: Dict[str, Dict]):
        """Update with dividend payment information"""
        self.upcoming_payments = []
        total_monthly = 0.0
        
        for symbol, dividend_info in dividend_data.items():
            if symbol not in self.holdings:
                continue
            
            shares = self.holdings[symbol]
            
            if 'next_payment' in dividend_info:
                next_payment = dividend_info['next_payment']
                amount = dividend_info.get('amount', 0)
                dividend_income = amount * shares
                
                self.upcoming_payments.append(DividendPayment(
                    symbol=symbol,
                    ex_date=next_payment,
                    record_date=next_payment + timedelta(days=1),
                    payment_date=next_payment + timedelta(days=30),
                    amount=amount,
                    frequency=DividendFrequency.QUARTERLY,
                    yield_percent=dividend_info.get('yield', 0)
                ))
                
                if next_payment.month == datetime.now().month:
                    total_monthly += dividend_income
        
        self.monthly_dividend_income = total_monthly
        self.upcoming_payments.sort(key=lambda x: x.ex_date)
        
        if self.upcoming_payments:
            self.next_payment = self.upcoming_payments[0].ex_date
    
    def get_projected_annual_income(self, holdings: Optional[Dict[str, float]] = None) -> float:
        """Project annual dividend income"""
        if holdings is None:
            holdings = self.holdings
        
        annual = 0.0
        for symbol, shares in holdings.items():
            # This would require dividend data lookup
            pass
        
        return annual


class DividendDataFetcher:
    """Fetch dividend information from Yahoo Finance"""
    
    def __init__(self):
        self.cache = {}
        self.last_update = {}
    
    def fetch_dividend_history(self, symbol: str, years: int = 5) -> DividendHistory:
        """
        Fetch dividend history for a stock
        
        Args:
            symbol: Stock symbol
            years: Years of history to fetch
            
        Returns:
            DividendHistory object
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get info
            info = ticker.info if hasattr(ticker, 'info') else {}
            
            # Get dividends
            dividends = ticker.dividends
            
            # Create history
            history = DividendHistory(
                symbol=symbol,
                company_name=info.get('longName', ''),
                current_yield=info.get('dividendYield', 0) or 0,
            )
            
            # Get dividend frequency (estimate from recent payments)
            if len(dividends) > 0:
                # Most recent dividend
                last_div = dividends.index[-1]
                amount = dividends.iloc[-1]
                
                # Estimate frequency
                if len(dividends) > 1:
                    prev_div = dividends.index[-2]
                    days_between = (last_div - prev_div).days
                    
                    if 20 <= days_between <= 40:
                        history.payout_frequency = DividendFrequency.MONTHLY
                    elif 80 <= days_between <= 100:
                        history.payout_frequency = DividendFrequency.QUARTERLY
                    elif 170 <= days_between <= 190:
                        history.payout_frequency = DividendFrequency.SEMI_ANNUAL
                    elif 350 <= days_between <= 370:
                        history.payout_frequency = DividendFrequency.ANNUAL
                
                history.last_payment_date = last_div
                
                # Add recent dividends as payments
                cutoff_date = datetime.now() - timedelta(days=365*years)
                
                for date, div_amount in dividends.items():
                    if date.timestamp() >= cutoff_date.timestamp():
                        payment = DividendPayment(
                            symbol=symbol,
                            ex_date=date,
                            record_date=date + timedelta(days=1),
                            payment_date=date + timedelta(days=30),
                            amount=float(div_amount),
                            frequency=history.payout_frequency,
                            yield_percent=history.current_yield,
                            paid=date < datetime.now()
                        )
                        history.add_payment(payment)
                
                # Calculate next payment date
                if history.last_payment_date:
                    if history.payout_frequency == DividendFrequency.MONTHLY:
                        history.next_payment_date = history.last_payment_date + timedelta(days=30)
                    elif history.payout_frequency == DividendFrequency.QUARTERLY:
                        history.next_payment_date = history.last_payment_date + timedelta(days=91)
                    elif history.payout_frequency == DividendFrequency.SEMI_ANNUAL:
                        history.next_payment_date = history.last_payment_date + timedelta(days=182)
                    else:
                        history.next_payment_date = history.last_payment_date + timedelta(days=365)
            
            # Calculate annual dividend
            current_year = datetime.now().year
            history.annual_dividend = history.get_annual_dividend(current_year)
            
            # Cache
            self.cache[symbol] = history
            self.last_update[symbol] = datetime.now()
            
            return history
        
        except Exception as e:
            print(f"Error fetching dividend data for {symbol}: {e}")
            return DividendHistory(symbol=symbol)
    
    def get_upcoming_ex_dates(self, symbols: List[str], days: int = 30) -> List[DividendPayment]:
        """
        Get upcoming ex-dividend dates
        
        Args:
            symbols: List of stock symbols
            days: Look ahead days
            
        Returns:
            List of upcoming dividend payments
        """
        upcoming = []
        
        for symbol in symbols:
            history = self.fetch_dividend_history(symbol)
            
            for payment in history.payment_history:
                if payment.is_upcoming(days):
                    upcoming.append(payment)
        
        upcoming.sort(key=lambda x: x.ex_date)
        return upcoming


class DividendReinvestmentCalculator:
    """Calculate dividend reinvestment scenarios (DRIP)"""
    
    @staticmethod
    def calculate_drip(
        initial_shares: float,
        annual_dividend_per_share: float,
        dividend_frequency: DividendFrequency,
        years: int,
        annual_growth_rate: float = 0.0,
        stock_price: float = 100.0
    ) -> Dict:
        """
        Calculate DRIP accumulation
        
        Args:
            initial_shares: Starting number of shares
            annual_dividend_per_share: Dividend per share per year
            dividend_frequency: How often dividends are paid
            years: Time period to calculate
            annual_growth_rate: Expected annual stock price growth
            stock_price: Current stock price
            
        Returns:
            Dict with DRIP calculation results
        """
        
        # Determine payments per year
        freq_map = {
            DividendFrequency.MONTHLY: 12,
            DividendFrequency.QUARTERLY: 4,
            DividendFrequency.SEMI_ANNUAL: 2,
            DividendFrequency.ANNUAL: 1
        }
        payments_per_year = freq_map.get(dividend_frequency, 4)
        dividend_per_payment = annual_dividend_per_share / payments_per_year
        
        shares = initial_shares
        price = stock_price
        accumulated_value = 0.0
        history = []
        
        for year in range(years):
            year_shares = shares
            year_dividends = 0.0
            year_reinvested_shares = 0.0
            
            # Process each dividend payment
            for payment in range(payments_per_year):
                # Calculate dividend for this payment
                dividend_cash = shares * dividend_per_payment
                year_dividends += dividend_cash
                
                # Reinvest dividend (assuming DRIP)
                reinvested_shares = dividend_cash / price
                shares += reinvested_shares
                year_reinvested_shares += reinvested_shares
                
                # Stock price growth (annualize and divide by frequency)
                price *= (1 + annual_growth_rate / payments_per_year)
            
            accumulated_value = shares * price
            
            history.append({
                'year': year + 1,
                'shares': shares,
                'price': price,
                'dividends': year_dividends,
                'reinvested_shares': year_reinvested_shares,
                'portfolio_value': accumulated_value
            })
        
        # Calculate results
        initial_value = initial_shares * stock_price
        final_value = accumulated_value
        total_gain = final_value - initial_value
        total_return_percent = (total_gain / initial_value) * 100
        
        return {
            'initial_investment': initial_value,
            'final_value': final_value,
            'total_gain': total_gain,
            'total_return_percent': total_return_percent,
            'final_shares': shares,
            'share_growth': shares - initial_shares,
            'history': history
        }
    
    @staticmethod
    def compare_drip_vs_no_drip(
        initial_shares: float,
        annual_dividend_per_share: float,
        dividend_frequency: DividendFrequency,
        years: int,
        annual_growth_rate: float = 0.0,
        stock_price: float = 100.0
    ) -> Dict:
        """
        Compare DRIP vs taking dividends as cash
        
        Args:
            Same as calculate_drip
            
        Returns:
            Comparison dict with both scenarios
        """
        
        with_drip = DividendReinvestmentCalculator.calculate_drip(
            initial_shares, annual_dividend_per_share, dividend_frequency,
            years, annual_growth_rate, stock_price
        )
        
        # Without DRIP: dividends are taken as cash
        shares = initial_shares
        price = stock_price
        cash_dividends = 0.0
        
        for year in range(years):
            # Get dividend cash for the year
            year_div = shares * annual_dividend_per_share
            cash_dividends += year_div
            
            # Price grows but share count stays same
            price *= (1 + annual_growth_rate)
        
        without_drip = {
            'initial_investment': initial_shares * stock_price,
            'final_value': shares * price,
            'cash_dividends': cash_dividends,
            'total_gain': (shares * price) + cash_dividends - (initial_shares * stock_price),
            'total_return_percent': (((shares * price + cash_dividends) / (initial_shares * stock_price)) - 1) * 100,
            'final_shares': shares
        }
        
        return {
            'with_drip': with_drip,
            'without_drip': without_drip,
            'drip_advantage': with_drip['final_value'] - without_drip['final_value'],
            'better_option': 'DRIP' if with_drip['final_value'] > without_drip['final_value'] else 'Cash Dividends'
        }


class DividendTracker:
    """Main dividend tracking engine"""
    
    def __init__(self):
        self.fetcher = DividendDataFetcher()
        self.tracked_stocks: Dict[str, DividendHistory] = {}
        self.portfolio_plan: Optional[PortfolioDividendPlan] = None
    
    def add_stock(self, symbol: str) -> DividendHistory:
        """Add stock to dividend tracker"""
        history = self.fetcher.fetch_dividend_history(symbol)
        self.tracked_stocks[symbol] = history
        return history
    
    def remove_stock(self, symbol: str):
        """Remove stock from tracker"""
        if symbol in self.tracked_stocks:
            del self.tracked_stocks[symbol]
    
    def get_dividend_info(self, symbol: str) -> Optional[DividendHistory]:
        """Get dividend info for a stock"""
        if symbol not in self.tracked_stocks:
            return self.add_stock(symbol)
        return self.tracked_stocks[symbol]
    
    def get_upcoming_dividends(self, days: int = 30) -> List[DividendPayment]:
        """Get upcoming dividend payments"""
        upcoming = self.fetcher.get_upcoming_ex_dates(
            list(self.tracked_stocks.keys()),
            days
        )
        return upcoming
    
    def get_dividend_yield_portfolio(self, holdings: Dict[str, float]) -> float:
        """
        Calculate weighted dividend yield for portfolio
        
        Args:
            holdings: Dict of symbol -> shares
            
        Returns:
            Weighted portfolio dividend yield
        """
        total_value = 0.0
        dividend_income = 0.0
        
        for symbol, shares in holdings.items():
            history = self.get_dividend_info(symbol)
            
            # Estimate current price (would need real-time data in production)
            current_price = 100.0  # Placeholder
            
            position_value = shares * current_price
            position_dividend_income = shares * history.annual_dividend
            
            total_value += position_value
            dividend_income += position_dividend_income
        
        if total_value > 0:
            return (dividend_income / total_value) * 100
        return 0.0
    
    def get_summary(self) -> Dict:
        """Get summary of dividend tracking"""
        total_annual_dividend = 0.0
        average_yield = 0.0
        upcoming = self.get_upcoming_dividends(30)
        
        for history in self.tracked_stocks.values():
            total_annual_dividend += history.annual_dividend
            average_yield += history.current_yield
        
        if self.tracked_stocks:
            average_yield /= len(self.tracked_stocks)
        
        return {
            'tracked_stocks': len(self.tracked_stocks),
            'total_annual_dividend': total_annual_dividend,
            'average_yield': average_yield,
            'upcoming_dividends_30_days': len(upcoming),
            'next_payment': upcoming[0].ex_date if upcoming else None
        }
