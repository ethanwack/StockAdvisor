"""
Options Pricing and Analysis Service
Provides Black-Scholes pricing, Greeks calculations, and strategy analysis
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf
import numpy as np
from scipy.stats import norm


class OptionType(Enum):
    """Option type: CALL or PUT"""
    CALL = "call"
    PUT = "put"


class StrategyType(Enum):
    """Option strategy types"""
    LONG_CALL = "long_call"
    LONG_PUT = "long_put"
    SHORT_CALL = "short_call"
    SHORT_PUT = "short_put"
    BULL_CALL_SPREAD = "bull_call_spread"
    BEAR_CALL_SPREAD = "bear_call_spread"
    BULL_PUT_SPREAD = "bull_put_spread"
    BEAR_PUT_SPREAD = "bear_put_spread"
    IRON_CONDOR = "iron_condor"
    BUTTERFLY = "butterfly"
    STRADDLE = "straddle"
    STRANGLE = "strangle"


@dataclass
class Greeks:
    """Option Greeks (sensitivity measures)"""
    delta: float  # Price change per $1 move in underlying
    gamma: float  # Rate of delta change
    theta: float  # Time decay per day
    vega: float   # Volatility sensitivity per 1% change
    rho: float    # Interest rate sensitivity
    
    def __str__(self) -> str:
        return (f"Greeks(delta={self.delta:.4f}, gamma={self.gamma:.4f}, "
                f"theta={self.theta:.4f}, vega={self.vega:.4f}, rho={self.rho:.4f})")


@dataclass
class Option:
    """Single option contract"""
    symbol: str
    option_type: OptionType
    strike: float
    expiration: datetime
    current_price: float
    underlying_price: float
    volatility: float
    risk_free_rate: float = 0.05
    dividend_yield: float = 0.0
    
    # Calculated fields
    price: float = field(init=False)
    greeks: Greeks = field(init=False)
    intrinsic_value: float = field(init=False)
    time_value: float = field(init=False)
    days_to_expiration: float = field(init=False)
    moneyness: float = field(init=False)
    
    def __post_init__(self):
        """Calculate option metrics after initialization"""
        self.days_to_expiration = max(0.0, 
            (self.expiration - datetime.now()).total_seconds() / (365.25 * 86400))
        
        # Calculate intrinsic value
        if self.option_type == OptionType.CALL:
            self.intrinsic_value = max(0, self.underlying_price - self.strike)
        else:  # PUT
            self.intrinsic_value = max(0, self.strike - self.underlying_price)
        
        # Calculate price and Greeks using Black-Scholes
        self.price, self.greeks = self._black_scholes()
        self.time_value = max(0, self.price - self.intrinsic_value)
        self.moneyness = self.underlying_price / self.strike
    
    def _black_scholes(self) -> Tuple[float, Greeks]:
        """
        Calculate option price and Greeks using Black-Scholes model
        Returns: (price, Greeks)
        """
        S = self.underlying_price
        K = self.strike
        T = self.days_to_expiration
        r = self.risk_free_rate
        sigma = self.volatility
        q = self.dividend_yield
        
        # Handle expiration
        if T <= 0:
            if self.option_type == OptionType.CALL:
                return max(0, S - K), Greeks(
                    delta=1.0 if S > K else 0.0,
                    gamma=0.0, theta=0.0, vega=0.0, rho=0.0
                )
            else:
                return max(0, K - S), Greeks(
                    delta=-1.0 if K > S else 0.0,
                    gamma=0.0, theta=0.0, vega=0.0, rho=0.0
                )
        
        # Calculate d1 and d2
        d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        # Standard normal distribution
        N_d1 = norm.cdf(d1)
        N_d2 = norm.cdf(d2)
        n_d1 = norm.pdf(d1)
        
        # Calculate price
        if self.option_type == OptionType.CALL:
            price = S * math.exp(-q * T) * N_d1 - K * math.exp(-r * T) * N_d2
            delta = math.exp(-q * T) * N_d1
        else:  # PUT
            price = K * math.exp(-r * T) * (1 - N_d2) - S * math.exp(-q * T) * (1 - N_d1)
            delta = math.exp(-q * T) * (N_d1 - 1)
        
        # Calculate Greeks
        gamma = math.exp(-q * T) * n_d1 / (S * sigma * math.sqrt(T))
        
        vega = S * math.exp(-q * T) * n_d1 * math.sqrt(T) / 100  # Per 1% change
        
        if self.option_type == OptionType.CALL:
            theta = (-S * math.exp(-q * T) * n_d1 * sigma / (2 * math.sqrt(T)) 
                    - r * K * math.exp(-r * T) * N_d2 
                    + q * S * math.exp(-q * T) * N_d1) / 365
            rho = K * T * math.exp(-r * T) * N_d2 / 100  # Per 1% change
        else:  # PUT
            theta = (-S * math.exp(-q * T) * n_d1 * sigma / (2 * math.sqrt(T)) 
                    + r * K * math.exp(-r * T) * (1 - N_d2) 
                    - q * S * math.exp(-q * T) * (1 - N_d1)) / 365
            rho = -K * T * math.exp(-r * T) * (1 - N_d2) / 100  # Per 1% change
        
        greeks = Greeks(delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho)
        
        return price, greeks


@dataclass
class Strategy:
    """Options strategy combining multiple legs"""
    strategy_type: StrategyType
    legs: List[Option]
    name: str = ""
    
    # Calculated fields
    total_cost: float = field(init=False)
    max_profit: float = field(init=False)
    max_loss: float = field(init=False)
    breakeven_points: List[float] = field(init=False)
    
    def __post_init__(self):
        """Calculate strategy metrics"""
        self.total_cost = self._calculate_total_cost()
        self.max_profit, self.max_loss = self._calculate_max_profit_loss()
        self.breakeven_points = self._calculate_breakeven()
        
        if not self.name:
            self.name = self.strategy_type.value.replace("_", " ").title()
    
    def _calculate_total_cost(self) -> float:
        """Calculate total cost of strategy"""
        cost = 0.0
        for i, leg in enumerate(self.legs):
            # Determine multiplier (buy = +1, sell = -1)
            multiplier = self._get_leg_multiplier(i)
            cost += leg.price * 100 * multiplier  # Standard contract = 100 shares
        return cost
    
    def _calculate_max_profit_loss(self) -> Tuple[float, float]:
        """
        Calculate maximum profit and loss at expiration
        Simplified calculation based on strike prices and costs
        """
        # Create price range for analysis
        if not self.legs:
            return 0.0, 0.0
        
        strikes = sorted([leg.strike for leg in self.legs])
        min_price = strikes[0] * 0.5
        max_price = strikes[-1] * 1.5
        prices = np.linspace(min_price, max_price, 200)
        
        payoffs = [self._calculate_payoff(p) for p in prices]
        max_profit = max(payoffs) - abs(self.total_cost)
        max_loss = min(payoffs) - abs(self.total_cost)
        
        return max_profit, max_loss
    
    def _calculate_payoff(self, underlying_price: float) -> float:
        """Calculate total payoff at given underlying price"""
        payoff = 0.0
        for i, leg in enumerate(self.legs):
            multiplier = self._get_leg_multiplier(i)
            if leg.option_type == OptionType.CALL:
                leg_payoff = max(0, underlying_price - leg.strike)
            else:  # PUT
                leg_payoff = max(0, leg.strike - underlying_price)
            payoff += leg_payoff * 100 * multiplier  # Standard contract
        return payoff
    
    def _get_leg_multiplier(self, leg_index: int) -> int:
        """Get multiplier for leg (buy=+1, sell=-1)"""
        if self.strategy_type in [StrategyType.LONG_CALL, StrategyType.LONG_PUT,
                                   StrategyType.BULL_CALL_SPREAD, StrategyType.BULL_PUT_SPREAD]:
            return 1 if leg_index == 0 else -1
        elif self.strategy_type in [StrategyType.SHORT_CALL, StrategyType.SHORT_PUT]:
            return -1
        elif self.strategy_type == StrategyType.BEAR_CALL_SPREAD:
            return -1 if leg_index == 0 else 1
        elif self.strategy_type == StrategyType.BEAR_PUT_SPREAD:
            return -1 if leg_index == 0 else 1
        else:
            return 1 if leg_index % 2 == 0 else -1
    
    def _calculate_breakeven(self) -> List[float]:
        """Calculate breakeven price(s) at expiration"""
        # Simplified: iterate through prices to find where payoff = cost
        if not self.legs:
            return []
        
        strikes = sorted([leg.strike for leg in self.legs])
        min_price = strikes[0] * 0.3
        max_price = strikes[-1] * 2.0
        prices = np.linspace(min_price, max_price, 1000)
        
        breakevens = []
        prev_profit = None
        
        for price in prices:
            current_payoff = self._calculate_payoff(price)
            profit = current_payoff - abs(self.total_cost)
            
            if prev_profit is not None:
                # Check if crossing zero profit line
                if (prev_profit < 0 and profit >= 0) or (prev_profit >= 0 and profit < 0):
                    breakevens.append(float(price))
            
            prev_profit = profit
        
        return breakevens


class OptionsAnalyzer:
    """Main options analysis service"""
    
    def __init__(self, risk_free_rate: float = 0.05):
        """
        Initialize Options Analyzer
        
        Args:
            risk_free_rate: Current risk-free rate (default 5%)
        """
        self.risk_free_rate = risk_free_rate
        self.cache = {}
    
    def get_historical_volatility(self, symbol: str, days: int = 30) -> float:
        """
        Calculate historical volatility using standard deviation of returns
        
        Args:
            symbol: Stock ticker
            days: Number of days to use for calculation
            
        Returns:
            Annualized volatility as decimal
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=f"{days}d")
            
            if len(hist) < 2:
                return 0.20  # Default 20% if insufficient data
            
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * math.sqrt(252)  # Annualize
            
            return max(0.05, min(volatility, 2.0))  # Clamp 5% to 200%
        except Exception as e:
            print(f"Error calculating volatility for {symbol}: {e}")
            return 0.20  # Default 20%
    
    def get_implied_volatility(self, symbol: str) -> float:
        """
        Get implied volatility estimate (uses historical as proxy)
        In production, would integrate with options data source
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Implied volatility as decimal
        """
        return self.get_historical_volatility(symbol, days=60)
    
    def price_option(self, symbol: str, option_type: OptionType, 
                    strike: float, expiration: datetime, 
                    current_price: Optional[float] = None,
                    volatility: Optional[float] = None) -> Option:
        """
        Price a single option using Black-Scholes
        
        Args:
            symbol: Stock ticker
            option_type: CALL or PUT
            strike: Strike price
            expiration: Expiration datetime
            current_price: Current stock price (fetches if None)
            volatility: Volatility (calculates if None)
            
        Returns:
            Option object with price and Greeks
        """
        # Get current price if not provided
        if current_price is None:
            try:
                ticker = yf.Ticker(symbol)
                current_price = ticker.info.get('currentPrice') or ticker.history(period="1d")['Close'].iloc[-1]
            except Exception as e:
                print(f"Error fetching price for {symbol}: {e}")
                raise
        
        # Get volatility if not provided
        if volatility is None:
            volatility = self.get_historical_volatility(symbol)
        
        # Get dividend yield
        try:
            ticker = yf.Ticker(symbol)
            dividend_yield = (ticker.info.get('dividendRate', 0) / current_price) if current_price > 0 else 0.0
        except:
            dividend_yield = 0.0
        
        return Option(
            symbol=symbol,
            option_type=option_type,
            strike=strike,
            expiration=expiration,
            current_price=current_price,
            underlying_price=current_price,
            volatility=volatility,
            risk_free_rate=self.risk_free_rate,
            dividend_yield=dividend_yield
        )
    
    def create_strategy(self, strategy_type: StrategyType, 
                       symbol: str, legs_config: List[Dict],
                       expiration: datetime,
                       current_price: Optional[float] = None,
                       volatility: Optional[float] = None) -> Strategy:
        """
        Create an options strategy
        
        Args:
            strategy_type: Type of strategy
            symbol: Stock ticker
            legs_config: List of dicts with {option_type, strike} for each leg
            expiration: Expiration datetime
            current_price: Current stock price
            volatility: Volatility
            
        Returns:
            Strategy object with analysis
        """
        legs = []
        for leg_config in legs_config:
            option = self.price_option(
                symbol=symbol,
                option_type=leg_config['option_type'],
                strike=leg_config['strike'],
                expiration=expiration,
                current_price=current_price,
                volatility=volatility
            )
            legs.append(option)
        
        return Strategy(
            strategy_type=strategy_type,
            legs=legs,
            name=f"{symbol} {strategy_type.value.replace('_', ' ').title()}"
        )
    
    def analyze_strategy_range(self, strategy: Strategy, 
                              underlying_range: Tuple[float, float],
                              steps: int = 100) -> Dict:
        """
        Analyze strategy P&L across underlying price range
        
        Args:
            strategy: Strategy to analyze
            underlying_range: (min_price, max_price) tuple
            steps: Number of price points to analyze
            
        Returns:
            Dict with analysis data: prices, payoffs, profits, max_profit, max_loss, breakevens
        """
        min_price, max_price = underlying_range
        prices = np.linspace(min_price, max_price, steps)
        
        payoffs = []
        profits = []
        
        for price in prices:
            payoff = strategy._calculate_payoff(price)
            profit = payoff - abs(strategy.total_cost)
            payoffs.append(payoff)
            profits.append(profit)
        
        return {
            'prices': prices.tolist(),
            'payoffs': payoffs,
            'profits': profits,
            'max_profit': strategy.max_profit,
            'max_loss': strategy.max_loss,
            'breakevens': strategy.breakeven_points,
            'total_cost': strategy.total_cost,
            'strategy_name': strategy.name
        }
    
    def suggest_strategy(self, symbol: str, outlook: str, 
                        max_cost: float = 5000.0) -> Dict:
        """
        Suggest an options strategy based on market outlook
        
        Args:
            symbol: Stock ticker
            outlook: 'bullish', 'bearish', or 'neutral'
            max_cost: Maximum cost tolerance
            
        Returns:
            Dict with suggested strategy and analysis
        """
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            raise
        
        expiration = datetime.now() + timedelta(days=30)
        
        recommendations = {
            'bullish': [
                {
                    'strategy': StrategyType.LONG_CALL,
                    'description': 'Long Call - Buy ATM call',
                    'config': [{'option_type': OptionType.CALL, 'strike': current_price}]
                },
                {
                    'strategy': StrategyType.BULL_CALL_SPREAD,
                    'description': 'Bull Call Spread - Lower cost, limited profit',
                    'config': [
                        {'option_type': OptionType.CALL, 'strike': current_price},
                        {'option_type': OptionType.CALL, 'strike': current_price * 1.05}
                    ]
                }
            ],
            'bearish': [
                {
                    'strategy': StrategyType.LONG_PUT,
                    'description': 'Long Put - Buy ATM put',
                    'config': [{'option_type': OptionType.PUT, 'strike': current_price}]
                },
                {
                    'strategy': StrategyType.BEAR_CALL_SPREAD,
                    'description': 'Bear Call Spread - Sell upside potential for credit',
                    'config': [
                        {'option_type': OptionType.CALL, 'strike': current_price},
                        {'option_type': OptionType.CALL, 'strike': current_price * 1.05}
                    ]
                }
            ],
            'neutral': [
                {
                    'strategy': StrategyType.IRON_CONDOR,
                    'description': 'Iron Condor - Profit from stagnation',
                    'config': [
                        {'option_type': OptionType.CALL, 'strike': current_price * 1.05},
                        {'option_type': OptionType.CALL, 'strike': current_price * 1.10},
                        {'option_type': OptionType.PUT, 'strike': current_price * 0.95},
                        {'option_type': OptionType.PUT, 'strike': current_price * 0.90}
                    ]
                }
            ]
        }
        
        results = []
        for rec in recommendations.get(outlook.lower(), []):
            try:
                strategy = self.create_strategy(
                    strategy_type=rec['strategy'],
                    symbol=symbol,
                    legs_config=rec['config'],
                    expiration=expiration,
                    current_price=current_price
                )
                
                if abs(strategy.total_cost) <= max_cost:
                    analysis = self.analyze_strategy_range(
                        strategy,
                        (current_price * 0.8, current_price * 1.2)
                    )
                    
                    results.append({
                        'strategy': rec['strategy'].value,
                        'description': rec['description'],
                        'cost': strategy.total_cost,
                        'max_profit': strategy.max_profit,
                        'max_loss': strategy.max_loss,
                        'breakevens': strategy.breakeven_points,
                        'analysis': analysis
                    })
            except Exception as e:
                print(f"Error creating {rec['strategy'].value}: {e}")
                continue
        
        return {
            'symbol': symbol,
            'outlook': outlook,
            'current_price': current_price,
            'expiration': expiration.isoformat(),
            'recommendations': results
        }
