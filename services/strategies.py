"""
Trading Strategy Definitions
Define various technical analysis trading strategies for backtesting
"""

from abc import ABC, abstractmethod
import pandas as pd


class Strategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
    
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
        signals[fast_sma > slow_sma] = 1
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
        
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        signals = pd.Series(0, index=data.index)
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
        signals[macd > signal_line] = 1
        signals[macd < signal_line] = -1
        
        return signals
