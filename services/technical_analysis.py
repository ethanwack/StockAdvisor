"""
Technical Analysis Tools Service
Advanced charting, pattern recognition, volume analysis, trend identification
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TrendDirection(Enum):
    """Trend direction"""
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"


class ChartPattern(Enum):
    """Chart patterns"""
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIANGLE = "triangle"
    WEDGE = "wedge"
    FLAG = "flag"


@dataclass
class SupportResistance:
    """Support/Resistance level"""
    level: float
    type: str  # "support" or "resistance"
    strength: float  # 0-1, how many times price bounced
    timestamp: datetime = None


@dataclass
class TechnicalLevel:
    """Technical support/resistance level"""
    price: float
    type: str  # "support", "resistance", "pivot"
    touches: int  # Number of times touched
    strength: float  # 0-100
    last_touch: datetime = None


@dataclass
class VolumeAnalysis:
    """Volume analysis data"""
    current_volume: float
    average_volume: float
    volume_ratio: float  # current / average
    volume_trend: str  # "increasing", "decreasing", "normal"
    price_volume_trend: float  # +/- trend correlation
    on_balance_volume: float  # Cumulative volume indicator


@dataclass
class FibonacciLevels:
    """Fibonacci retracement levels"""
    high: float
    low: float
    levels: Dict[str, float]  # {"0.236": price, "0.382": price, etc}
    
    def calculate(self):
        """Calculate Fibonacci levels"""
        diff = self.high - self.low
        self.levels = {
            "0.0": self.low,
            "0.236": self.low + diff * 0.236,
            "0.382": self.low + diff * 0.382,
            "0.5": self.low + diff * 0.5,
            "0.618": self.low + diff * 0.618,
            "0.786": self.low + diff * 0.786,
            "1.0": self.high
        }
        return self.levels


@dataclass
class CandlePattern:
    """Candlestick pattern detection"""
    name: str
    bullish: bool
    reliability: float  # 0-1
    date: datetime
    description: str


class TechnicalIndicator:
    """Calculate technical indicators"""
    
    @staticmethod
    def moving_average(prices: pd.Series, period: int = 20) -> pd.Series:
        """Simple moving average"""
        return prices.rolling(window=period).mean()
    
    @staticmethod
    def exponential_moving_average(prices: pd.Series, period: int = 20) -> pd.Series:
        """Exponential moving average"""
        return prices.ewm(span=period).mean()
    
    @staticmethod
    def bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        return {
            'upper': upper,
            'middle': sma,
            'lower': lower,
            'width': upper - lower,
            'position': (prices - lower) / (upper - lower)  # 0-1 position in band
        }
    
    @staticmethod
    def atr(highs: pd.Series, lows: pd.Series, closes: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range"""
        tr1 = highs - lows
        tr2 = abs(highs - closes.shift())
        tr3 = abs(lows - closes.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
    
    @staticmethod
    def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """MACD - Moving Average Convergence Divergence"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def stochastic(highs: pd.Series, lows: pd.Series, closes: pd.Series, 
                   period: int = 14, smooth_k: int = 3) -> Dict:
        """Stochastic Oscillator"""
        low_min = lows.rolling(window=period).min()
        high_max = highs.rolling(window=period).max()
        
        fast_k = 100 * (closes - low_min) / (high_max - low_min)
        slow_k = fast_k.rolling(window=smooth_k).mean()
        slow_d = slow_k.rolling(window=smooth_k).mean()
        
        return {
            'fast_k': fast_k,
            'slow_k': slow_k,
            'slow_d': slow_d
        }
    
    @staticmethod
    def adx(highs: pd.Series, lows: pd.Series, closes: pd.Series, period: int = 14) -> pd.Series:
        """Average Directional Index - Trend strength"""
        plus_dm = highs.diff().clip(lower=0)
        minus_dm = (-lows.diff()).clip(lower=0)
        
        tr1 = highs - lows
        tr2 = abs(highs - closes.shift())
        tr3 = abs(lows - closes.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        plus_di = 100 * plus_dm.rolling(window=period).mean() / atr
        minus_di = 100 * minus_dm.rolling(window=period).mean() / atr
        
        di_diff = abs(plus_di - minus_di)
        di_sum = plus_di + minus_di
        
        dx = 100 * di_diff / di_sum
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def obv(closes: pd.Series, volumes: pd.Series) -> pd.Series:
        """On-Balance Volume"""
        obv = (np.sign(closes.diff()) * volumes).fillna(0).cumsum()
        return obv


class PatternRecognition:
    """Recognize chart patterns"""
    
    @staticmethod
    def detect_candlestick_patterns(highs: pd.Series, lows: pd.Series, 
                                   closes: pd.Series) -> List[CandlePattern]:
        """Detect candlestick patterns"""
        patterns = []
        
        # Hammer (bullish reversal)
        for i in range(1, len(closes)):
            body = abs(closes.iloc[i] - closes.iloc[i-1])
            upper_wick = highs.iloc[i] - max(closes.iloc[i], closes.iloc[i-1])
            lower_wick = min(closes.iloc[i], closes.iloc[i-1]) - lows.iloc[i]
            
            if body > 0 and lower_wick > body * 2 and upper_wick < body * 0.5:
                patterns.append(CandlePattern(
                    name="Hammer",
                    bullish=True,
                    reliability=0.7,
                    date=closes.index[i],
                    description="Potential bullish reversal"
                ))
        
        # Shooting Star (bearish reversal)
        for i in range(1, len(closes)):
            body = abs(closes.iloc[i] - closes.iloc[i-1])
            upper_wick = highs.iloc[i] - max(closes.iloc[i], closes.iloc[i-1])
            lower_wick = min(closes.iloc[i], closes.iloc[i-1]) - lows.iloc[i]
            
            if body > 0 and upper_wick > body * 2 and lower_wick < body * 0.5:
                patterns.append(CandlePattern(
                    name="Shooting Star",
                    bullish=False,
                    reliability=0.7,
                    date=closes.index[i],
                    description="Potential bearish reversal"
                ))
        
        return patterns
    
    @staticmethod
    def detect_support_resistance(prices: pd.Series, window: int = 5) -> List[SupportResistance]:
        """Detect support and resistance levels"""
        levels = []
        
        # Find local minima (support)
        for i in range(window, len(prices) - window):
            if prices.iloc[i] == prices.iloc[i-window:i+window].min():
                levels.append(SupportResistance(
                    level=prices.iloc[i],
                    type="support",
                    strength=0.5,
                    timestamp=prices.index[i]
                ))
        
        # Find local maxima (resistance)
        for i in range(window, len(prices) - window):
            if prices.iloc[i] == prices.iloc[i-window:i+window].max():
                levels.append(SupportResistance(
                    level=prices.iloc[i],
                    type="resistance",
                    strength=0.5,
                    timestamp=prices.index[i]
                ))
        
        return levels
    
    @staticmethod
    def identify_trend(prices: pd.Series, period: int = 20) -> TrendDirection:
        """Identify current trend"""
        sma = prices.rolling(window=period).mean()
        current_price = prices.iloc[-1]
        sma_value = sma.iloc[-1]
        
        if current_price > sma_value * 1.02:
            return TrendDirection.UPTREND
        elif current_price < sma_value * 0.98:
            return TrendDirection.DOWNTREND
        else:
            return TrendDirection.SIDEWAYS


class VolumeAnalyzer:
    """Analyze volume patterns"""
    
    @staticmethod
    def analyze_volume(volumes: pd.Series, closes: pd.Series) -> VolumeAnalysis:
        """Analyze volume"""
        current_vol = volumes.iloc[-1]
        avg_vol = volumes.rolling(window=20).mean().iloc[-1]
        ratio = current_vol / avg_vol if avg_vol > 0 else 1
        
        # Volume trend
        vol_trend = "normal"
        if ratio > 1.2:
            vol_trend = "increasing"
        elif ratio < 0.8:
            vol_trend = "decreasing"
        
        # Price-Volume Trend
        price_change = (closes.iloc[-1] - closes.iloc[-20]) / closes.iloc[-20]
        volume_change = (current_vol - volumes.iloc[-20]) / volumes.iloc[-20]
        pvt = price_change * volume_change
        
        # On-Balance Volume
        obv = (np.sign(closes.diff()) * volumes).fillna(0).cumsum().iloc[-1]
        
        return VolumeAnalysis(
            current_volume=current_vol,
            average_volume=avg_vol,
            volume_ratio=ratio,
            volume_trend=vol_trend,
            price_volume_trend=pvt,
            on_balance_volume=obv
        )
    
    @staticmethod
    def detect_volume_breakout(closes: pd.Series, volumes: pd.Series) -> bool:
        """Detect volume breakout"""
        avg_vol = volumes.rolling(window=20).mean().iloc[-1]
        current_vol = volumes.iloc[-1]
        return current_vol > avg_vol * 1.5


class TechnicalAnalyzer:
    """Main technical analysis engine"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.data = None
        self.indicators = {}
        self.patterns = []
        self.support_resistance = []
    
    def fetch_data(self, period: str = '1y') -> pd.DataFrame:
        """Fetch stock data"""
        ticker = yf.Ticker(self.symbol)
        self.data = ticker.history(period=period)
        return self.data
    
    def calculate_indicators(self):
        """Calculate all technical indicators"""
        if self.data is None:
            return
        
        closes = self.data['Close']
        highs = self.data['High']
        lows = self.data['Low']
        volumes = self.data['Volume']
        
        # Moving averages
        self.indicators['sma_20'] = TechnicalIndicator.moving_average(closes, 20)
        self.indicators['sma_50'] = TechnicalIndicator.moving_average(closes, 50)
        self.indicators['sma_200'] = TechnicalIndicator.moving_average(closes, 200)
        self.indicators['ema_12'] = TechnicalIndicator.exponential_moving_average(closes, 12)
        self.indicators['ema_26'] = TechnicalIndicator.exponential_moving_average(closes, 26)
        
        # Bollinger Bands
        self.indicators['bollinger'] = TechnicalIndicator.bollinger_bands(closes, 20, 2)
        
        # RSI
        self.indicators['rsi'] = TechnicalIndicator.rsi(closes, 14)
        
        # MACD
        self.indicators['macd'] = TechnicalIndicator.macd(closes, 12, 26, 9)
        
        # Stochastic
        self.indicators['stochastic'] = TechnicalIndicator.stochastic(highs, lows, closes, 14, 3)
        
        # ADX
        self.indicators['adx'] = TechnicalIndicator.adx(highs, lows, closes, 14)
        
        # ATR
        self.indicators['atr'] = TechnicalIndicator.atr(highs, lows, closes, 14)
        
        # OBV
        self.indicators['obv'] = TechnicalIndicator.obv(closes, volumes)
    
    def detect_patterns(self):
        """Detect chart patterns"""
        if self.data is None:
            return
        
        highs = self.data['High']
        lows = self.data['Low']
        closes = self.data['Close']
        
        # Candlestick patterns
        self.patterns = PatternRecognition.detect_candlestick_patterns(highs, lows, closes)
        
        # Support/Resistance
        self.support_resistance = PatternRecognition.detect_support_resistance(closes, 5)
    
    def get_trend(self) -> TrendDirection:
        """Get current trend"""
        if self.data is None:
            return None
        
        return PatternRecognition.identify_trend(self.data['Close'], 20)
    
    def get_volume_analysis(self) -> VolumeAnalysis:
        """Get volume analysis"""
        if self.data is None:
            return None
        
        return VolumeAnalyzer.analyze_volume(self.data['Volume'], self.data['Close'])
    
    def get_fibonacci_levels(self, lookback: int = 52) -> FibonacciLevels:
        """Get Fibonacci retracement levels"""
        if self.data is None:
            return None
        
        recent = self.data['Close'].tail(lookback)
        high = recent.max()
        low = recent.min()
        
        fib = FibonacciLevels(high=high, low=low)
        fib.calculate()
        return fib
    
    def get_support_resistance_levels(self, count: int = 5) -> List[TechnicalLevel]:
        """Get key support/resistance levels"""
        levels = []
        
        # Group support/resistance by price proximity
        if self.support_resistance:
            sorted_levels = sorted(self.support_resistance, key=lambda x: x.level)
            
            # Merge nearby levels
            merged = []
            for level in sorted_levels:
                if not merged or abs(level.level - merged[-1].level) > self.data['Close'].std():
                    merged.append(level)
                else:
                    merged[-1].strength += 0.1
            
            # Convert to TechnicalLevel
            for level in merged[-count:]:
                strength = min(100, int(level.strength * 50))
                levels.append(TechnicalLevel(
                    price=level.level,
                    type=level.type,
                    touches=1,
                    strength=strength,
                    last_touch=level.timestamp
                ))
        
        return levels
    
    def get_summary(self) -> Dict:
        """Get complete technical analysis summary"""
        if self.data is None:
            return None
        
        current_price = self.data['Close'].iloc[-1]
        rsi = self.indicators['rsi'].iloc[-1]
        macd = self.indicators['macd']
        adx = self.indicators['adx'].iloc[-1]
        
        return {
            'symbol': self.symbol,
            'current_price': current_price,
            'trend': self.get_trend().value,
            'rsi': rsi,
            'rsi_signal': 'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'neutral',
            'macd_signal': 'bullish' if macd['histogram'].iloc[-1] > 0 else 'bearish',
            'adx': adx,
            'trend_strength': 'strong' if adx > 25 else 'weak',
            'patterns': [p.name for p in self.patterns[-3:]],  # Last 3 patterns
            'volume': self.get_volume_analysis(),
            'support_resistance': self.get_support_resistance_levels(3)
        }
