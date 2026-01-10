"""
Strategy Backtesting Engine
Backtest trading strategies against historical data with comprehensive performance metrics
"""

from datetime import datetime
from typing import Dict, List, Tuple
import itertools
import yfinance as yf
import numpy as np
import pandas as pd

from utils.base_service import BaseService
from utils.data_models import Trade, PositionType, BacktestResults
from services.strategies import Strategy


class Backtester(BaseService):
    """Main backtesting engine for strategy evaluation"""
    
    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.001):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital
            commission: Commission per trade as decimal (0.001 = 0.1%)
        """
        super().__init__("Backtester")
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
        try:
            # Fetch historical data
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            if data.empty:
                raise ValueError(f"No data available for {symbol}")
            
            if 'Close' not in data.columns:
                raise ValueError("Data must contain 'Close' column")
            
            # Generate signals
            signals = strategy.generate_signals(data)
            
            # Simulate trading
            trades, equity_curve = self._simulate_trading(data, signals, shares_per_trade)
            
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
            
            self.logger.info(f"Backtest complete for {symbol} using {strategy.name}")
            return results
        
        except Exception as e:
            self.logger.error(f"Backtest failed for {symbol}: {e}")
            raise
    
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
        position = None
        
        for i in range(1, len(data)):
            current_date = data.index[i]
            close_price = data['Close'].iloc[i]
            signal = signals.iloc[i]
            
            # Close existing position on sell signal
            if position is not None and signal == -1:
                exit_price = close_price
                commission_cost = position.entry_cost * self.commission
                profit_loss = (exit_price - position.entry_price) * position.shares - commission_cost
                
                position.exit_date = current_date
                position.exit_price = exit_price
                position.profit_loss = profit_loss
                
                trades.append(position)
                cash += exit_price * position.shares - commission_cost
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
                current_equity += close_price * position.shares
            
            equity_curve.append(current_equity)
        
        # Close any remaining position at end
        if position is not None:
            last_price = data['Close'].iloc[-1]
            position.exit_date = data.index[-1]
            position.exit_price = last_price
            position.profit_loss = (last_price - position.entry_price) * position.shares
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
        best_metric = -np.inf if metric != 'max_drawdown_pct' else np.inf
        best_params = None
        best_results = None
        
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        for combination in itertools.product(*param_values):
            params = dict(zip(param_names, combination))
            
            try:
                strategy = strategy_class(**params)
                results = self.backtest(symbol, strategy, start_date, end_date)
                
                current_metric = getattr(results, metric, 0)
                is_better = (current_metric > best_metric) if metric != 'max_drawdown_pct' else (current_metric < best_metric)
                
                if is_better:
                    best_metric = current_metric
                    best_params = params
                    best_results = results
            
            except Exception as e:
                self.logger.debug(f"Error with params {params}: {e}")
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
                self.logger.error(f"Error backtesting {strategy.name}: {e}")
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
