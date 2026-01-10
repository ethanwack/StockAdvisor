"""
Strategy Backtesting Engine
Backtest trading strategies against historical data with comprehensive performance metrics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import yfinance as yf
import numpy as np
import pandas as pd

from utils.base_service import BaseService
from utils.data_models import Trade, PositionType, OrderType, BacktestResults
from utils.validators import validate_symbol, validate_date_range, ValidationError


class SimpleMovingAverageCrossover:
    """Comprehensive backtest results"""
    strategy_name: str
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    trades: List[Trade]
    equity_curve: List[float]
    dates: List[datetime]
    
    # Performance metrics
    total_return_pct: float = field(init=False)
    annual_return_pct: float = field(init=False)
    win_rate_pct: float = field(init=False)
    avg_win: float = field(init=False)
    avg_loss: float = field(init=False)
    profit_factor: float = field(init=False)
    sharpe_ratio: float = field(init=False)
    sortino_ratio: float = field(init=False)
    max_drawdown_pct: float = field(init=False)
    recovery_time: int = field(init=False)
    calmar_ratio: float = field(init=False)
    
    def __post_init__(self):
        """Calculate all performance metrics"""
        self._calculate_returns()
        self._calculate_win_metrics()
        self._calculate_risk_metrics()
        self._calculate_ratios()
    
    def _calculate_returns(self):
        """Calculate return metrics"""
        final_value = self.equity_curve[-1] if self.equity_curve else self.initial_capital
        total_return = final_value - self.initial_capital
        self.total_return_pct = (total_return / self.initial_capital * 100) if self.initial_capital > 0 else 0.0
        
        # Annualized return
        days = (self.end_date - self.start_date).days
        years = max(days / 365.25, 0.01)
        self.annual_return_pct = ((final_value / self.initial_capital) ** (1 / years) - 1) * 100
    
    def _calculate_win_metrics(self):
        """Calculate win rate and profit metrics"""
        if not self.trades:
            self.win_rate_pct = 0.0
            self.avg_win = 0.0
            self.avg_loss = 0.0
            self.profit_factor = 0.0
            return
        
        # Filter closed trades
        closed_trades = [t for t in self.trades if t.exit_price is not None]
        
        if not closed_trades:
            self.win_rate_pct = 0.0
            self.avg_win = 0.0
            self.avg_loss = 0.0
            self.profit_factor = 0.0
            return
        
        # Win rate
        winning_trades = [t for t in closed_trades if t.profit_loss > 0]
        self.win_rate_pct = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0.0
        
        # Average win/loss
        win_amounts = [t.profit_loss for t in winning_trades]
        loss_trades = [t for t in closed_trades if t.profit_loss < 0]
        loss_amounts = [abs(t.profit_loss) for t in loss_trades]
        
        self.avg_win = np.mean(win_amounts) if win_amounts else 0.0
        self.avg_loss = np.mean(loss_amounts) if loss_amounts else 0.0
        
        # Profit factor
        total_wins = sum(win_amounts) if win_amounts else 0.0
        total_losses = sum(loss_amounts) if loss_amounts else 0.0
        self.profit_factor = (total_wins / total_losses) if total_losses > 0 else (1.0 if total_wins > 0 else 0.0)
    
    def _calculate_risk_metrics(self):
        """Calculate risk metrics"""
        if not self.equity_curve:
            self.max_drawdown_pct = 0.0
            self.recovery_time = 0
            return
        
        equity = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max
        
        self.max_drawdown_pct = np.min(drawdown) * 100 if len(drawdown) > 0 else 0.0
        
        # Calculate recovery time (bars to return to previous high)
        max_dd_idx = np.argmin(drawdown)
        recovery_time = 0
        for i in range(max_dd_idx + 1, len(equity)):
            if equity[i] >= running_max[max_dd_idx]:
                recovery_time = i - max_dd_idx
                break
        self.recovery_time = recovery_time
    
    def _calculate_ratios(self):
        """Calculate risk-adjusted return ratios"""
        if len(self.equity_curve) < 2:
            self.sharpe_ratio = 0.0
            self.sortino_ratio = 0.0
            self.calmar_ratio = 0.0
            return
        
        # Calculate returns
        equity = np.array(self.equity_curve)
        returns = np.diff(equity) / equity[:-1]
        
        # Sharpe Ratio (assuming 252 trading days, 0% risk-free rate)
        excess_returns = returns
        if len(excess_returns) > 1:
            std_dev = np.std(excess_returns)
            self.sharpe_ratio = (np.mean(excess_returns) / std_dev * np.sqrt(252)) if std_dev > 0 else 0.0
        else:
            self.sharpe_ratio = 0.0
        
        # Sortino Ratio (only downside volatility)
        downside_returns = np.minimum(returns, 0)
        if len(downside_returns) > 1:
            downside_std = np.std(downside_returns)
            self.sortino_ratio = (np.mean(returns) / downside_std * np.sqrt(252)) if downside_std > 0 else 0.0
        else:
            self.sortino_ratio = 0.0
        
        # Calmar Ratio = Annual Return / Max Drawdown
        if self.max_drawdown_pct != 0:
            self.calmar_ratio = self.annual_return_pct / abs(self.max_drawdown_pct)
        else:
            self.calmar_ratio = 0.0
    
    def to_dict(self) -> Dict:
        """Convert results to dictionary"""
        return {
            'strategy_name': self.strategy_name,
            'symbol': self.symbol,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'initial_capital': self.initial_capital,
            'final_value': self.equity_curve[-1] if self.equity_curve else self.initial_capital,
            'total_return_pct': self.total_return_pct,
            'annual_return_pct': self.annual_return_pct,
            'win_rate_pct': self.win_rate_pct,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'profit_factor': self.profit_factor,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'max_drawdown_pct': self.max_drawdown_pct,
            'recovery_time': self.recovery_time,
            'calmar_ratio': self.calmar_ratio,
            'num_trades': len([t for t in self.trades if t.exit_price is not None]),
            'trades': [t.to_dict() for t in self.trades]
        }


class Strategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.trades: List[Trade] = []
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate buy/sell signals based on data
        Returns: Series with values: 1 (buy), -1 (sell), 0 (hold)
        """
        pass


class SimpleMovingAverageCrossover(Strategy):
    """SMA Crossover Strategy - Simple moving average crossover"""
    
    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        super().__init__(f"SMA_{fast_period}_{slow_period}")
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals from SMA crossover"""
        close = data['Close']
        
        fast_sma = close.rolling(window=self.fast_period).mean()
        slow_sma = close.rolling(window=self.slow_period).mean()
        
        signals = pd.Series(0, index=data.index)
        
        # Buy signal: fast SMA crosses above slow SMA
        signals[fast_sma > slow_sma] = 1
        # Sell signal: fast SMA crosses below slow SMA
        signals[fast_sma < slow_sma] = -1
        
        return signals


class RelativeStrengthIndex(Strategy):
    """RSI Strategy - Buy/Sell based on RSI levels"""
    
    def __init__(self, period: int = 14, oversold: float = 30.0, overbought: float = 70.0):
        super().__init__(f"RSI_{period}")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals from RSI"""
        close = data['Close']
        
        # Calculate RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        signals = pd.Series(0, index=data.index)
        
        # Buy when RSI < oversold, Sell when RSI > overbought
        signals[rsi < self.oversold] = 1
        signals[rsi > self.overbought] = -1
        
        return signals


class BollingerBands(Strategy):
    """Bollinger Bands Strategy - Buy/Sell at band extremes"""
    
    def __init__(self, period: int = 20, num_std: float = 2.0):
        super().__init__(f"BB_{period}")
        self.period = period
        self.num_std = num_std
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals from Bollinger Bands"""
        close = data['Close']
        
        sma = close.rolling(window=self.period).mean()
        std = close.rolling(window=self.period).std()
        
        upper_band = sma + (self.num_std * std)
        lower_band = sma - (self.num_std * std)
        
        signals = pd.Series(0, index=data.index)
        
        # Buy at lower band, Sell at upper band
        signals[close <= lower_band] = 1
        signals[close >= upper_band] = -1
        
        return signals


class MACD(Strategy):
    """MACD Strategy - Moving Average Convergence Divergence"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__(f"MACD_{fast_period}_{slow_period}_{signal_period}")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals from MACD"""
        close = data['Close']
        
        fast_ema = close.ewm(span=self.fast_period).mean()
        slow_ema = close.ewm(span=self.slow_period).mean()
        
        macd = fast_ema - slow_ema
        signal_line = macd.ewm(span=self.signal_period).mean()
        
        signals = pd.Series(0, index=data.index)
        
        # Buy when MACD crosses above signal, Sell when below
        signals[macd > signal_line] = 1
        signals[macd < signal_line] = -1
        
        return signals


class Backtester:
    """Main backtesting engine"""
    
    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.001):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital
            commission: Commission per trade as decimal (0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
    
    def backtest(self, symbol: str, strategy: Strategy, 
                start_date: datetime, end_date: datetime,
                shares_per_trade: float = 100.0) -> BacktestResults:
        """
        Run backtest for a strategy
        
        Args:
            symbol: Stock ticker
            strategy: Strategy instance with generate_signals method
            start_date: Backtest start date
            end_date: Backtest end date
            shares_per_trade: Shares to trade per signal
            
        Returns:
            BacktestResults with performance metrics
        """
        # Fetch historical data
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        
        if data.empty:
            raise ValueError(f"No data available for {symbol}")
        
        # Ensure data has required columns
        if 'Close' not in data.columns:
            raise ValueError("Data must contain 'Close' column")
        
        # Generate signals
        signals = strategy.generate_signals(data)
        
        # Simulate trading
        trades, equity_curve = self._simulate_trading(
            data, signals, shares_per_trade
        )
        
        # Create results
        results = BacktestResults(
            strategy_name=strategy.name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            trades=trades,
            equity_curve=equity_curve,
            dates=data.index.tolist()
        )
        
        return results
    
    def _simulate_trading(self, data: pd.DataFrame, signals: pd.Series,
                         shares_per_trade: float) -> Tuple[List[Trade], List[float]]:
        """
        Simulate trading based on signals
        
        Args:
            data: OHLCV data
            signals: Buy/sell signals (1, -1, 0)
            shares_per_trade: Shares per trade
            
        Returns:
            (trades, equity_curve)
        """
        trades = []
        equity_curve = [self.initial_capital]
        cash = self.initial_capital
        position = None  # Current open position
        
        for i in range(1, len(data)):
            current_date = data.index[i]
            close_price = data['Close'].iloc[i]
            signal = signals.iloc[i]
            
            # Close existing position on sell signal
            if position is not None and signal == -1:
                exit_price = close_price
                commission_cost = position.entry_cost * self.commission
                profit_loss = position.profit_loss - commission_cost if position.position_type == PositionType.LONG else position.profit_loss - commission_cost
                
                position.exit_date = current_date
                position.exit_price = exit_price
                position.profit_loss = profit_loss
                
                trades.append(position)
                
                if position.position_type == PositionType.LONG:
                    cash += exit_price * position.shares - commission_cost
                else:  # SHORT
                    cash -= exit_price * position.shares + commission_cost
                
                position = None
            
            # Open new position on buy signal
            elif position is None and signal == 1:
                entry_price = close_price
                commission_cost = entry_price * shares_per_trade * self.commission
                
                if cash >= (entry_price * shares_per_trade + commission_cost):
                    position = Trade(
                        entry_date=current_date,
                        exit_date=None,
                        symbol=data.name if hasattr(data, 'name') else 'UNKNOWN',
                        position_type=PositionType.LONG,
                        entry_price=entry_price,
                        shares=shares_per_trade
                    )
                    cash -= entry_price * shares_per_trade + commission_cost
            
            # Calculate current equity
            current_equity = cash
            if position is not None:
                if position.position_type == PositionType.LONG:
                    current_equity += close_price * position.shares
                else:  # SHORT
                    current_equity += position.entry_cost - (close_price * position.shares)
            
            equity_curve.append(current_equity)
        
        # Close any remaining position at end
        if position is not None:
            last_price = data['Close'].iloc[-1]
            position.exit_date = data.index[-1]
            position.exit_price = last_price
            trades.append(position)
        
        return trades, equity_curve
    
    def optimize_strategy(self, symbol: str, strategy_class, 
                         param_grid: Dict[str, List],
                         start_date: datetime, end_date: datetime,
                         metric: str = 'sharpe_ratio') -> Tuple[Dict, BacktestResults]:
        """
        Optimize strategy parameters using grid search
        
        Args:
            symbol: Stock ticker
            strategy_class: Strategy class to optimize
            param_grid: Dict with parameter names and values to try
            start_date: Backtest start date
            end_date: Backtest end date
            metric: Metric to optimize (sharpe_ratio, total_return_pct, win_rate_pct)
            
        Returns:
            (best_params, best_results)
        """
        import itertools
        
        best_metric = -np.inf if metric != 'max_drawdown_pct' else np.inf
        best_params = None
        best_results = None
        
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        for combination in itertools.product(*param_values):
            params = dict(zip(param_names, combination))
            
            try:
                strategy = strategy_class(**params)
                results = self.backtest(symbol, strategy, start_date, end_date)
                
                # Get metric value
                current_metric = getattr(results, metric, 0)
                
                # Update best if better
                is_better = (current_metric > best_metric) if metric != 'max_drawdown_pct' else (current_metric < best_metric)
                
                if is_better:
                    best_metric = current_metric
                    best_params = params
                    best_results = results
            
            except Exception as e:
                print(f"Error with params {params}: {e}")
                continue
        
        return best_params, best_results
    
    def compare_strategies(self, symbol: str, strategies: List[Strategy],
                          start_date: datetime, end_date: datetime) -> Dict:
        """
        Compare multiple strategies
        
        Args:
            symbol: Stock ticker
            strategies: List of Strategy instances
            start_date: Backtest start date
            end_date: Backtest end date
            
        Returns:
            Dict with results for each strategy
        """
        comparison = {}
        
        for strategy in strategies:
            try:
                results = self.backtest(symbol, strategy, start_date, end_date)
                comparison[strategy.name] = results
            except Exception as e:
                print(f"Error backtesting {strategy.name}: {e}")
                comparison[strategy.name] = None
        
        return comparison
    
    def buy_and_hold(self, symbol: str, start_date: datetime, 
                     end_date: datetime) -> BacktestResults:
        """
        Calculate buy-and-hold benchmark
        
        Args:
            symbol: Stock ticker
            start_date: Start date
            end_date: End date
            
        Returns:
            BacktestResults for buy-and-hold strategy
        """
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        
        # Buy on first day, sell on last day
        entry_price = data['Close'].iloc[0]
        exit_price = data['Close'].iloc[-1]
        shares = self.initial_capital / entry_price
        
        trade = Trade(
            entry_date=data.index[0],
            exit_date=data.index[-1],
            symbol=symbol,
            position_type=PositionType.LONG,
            entry_price=entry_price,
            exit_price=exit_price,
            shares=shares
        )
        
        # Calculate equity curve
        equity_curve = [self.initial_capital]
        for i in range(1, len(data)):
            current_value = shares * data['Close'].iloc[i]
            equity_curve.append(current_value)
        
        results = BacktestResults(
            strategy_name="Buy & Hold",
            symbol=symbol,
            start_date=data.index[0],
            end_date=data.index[-1],
            initial_capital=self.initial_capital,
            trades=[trade],
            equity_curve=equity_curve,
            dates=data.index.tolist()
        )
        
        return results
