"""
Centralized Data Models
All @dataclass definitions used across the project
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum
import numpy as np


# ==================== BACKTESTING MODELS ====================

class OrderType(Enum):
    """Order types"""
    BUY = "buy"
    SELL = "sell"


class PositionType(Enum):
    """Position types"""
    LONG = "long"
    SHORT = "short"


@dataclass
class Trade:
    """Individual trade record"""
    entry_date: datetime
    exit_date: Optional[datetime]
    symbol: str
    position_type: PositionType
    entry_price: float
    exit_price: Optional[float] = None
    shares: float = 100.0
    
    # Calculated fields
    entry_cost: float = field(init=False)
    exit_cost: float = field(init=False)
    profit_loss: float = field(init=False)
    profit_loss_pct: float = field(init=False)
    duration_days: int = field(init=False)
    
    def __post_init__(self):
        """Calculate trade metrics"""
        self.entry_cost = self.entry_price * self.shares
        
        if self.exit_price is not None:
            self.exit_cost = self.exit_price * self.shares
            
            if self.position_type == PositionType.LONG:
                self.profit_loss = self.exit_cost - self.entry_cost
            else:  # SHORT
                self.profit_loss = self.entry_cost - self.exit_cost
            
            self.profit_loss_pct = (self.profit_loss / self.entry_cost * 100) if self.entry_cost > 0 else 0.0
            
            self.duration_days = (self.exit_date - self.entry_date).days
        else:
            self.exit_cost = 0.0
            self.profit_loss = 0.0
            self.profit_loss_pct = 0.0
            self.duration_days = (datetime.now() - self.entry_date).days
    
    def to_dict(self) -> Dict:
        """Convert trade to dictionary"""
        return {
            'entry_date': self.entry_date.isoformat(),
            'exit_date': self.exit_date.isoformat() if self.exit_date else None,
            'symbol': self.symbol,
            'position_type': self.position_type.value,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'shares': self.shares,
            'profit_loss': self.profit_loss,
            'profit_loss_pct': self.profit_loss_pct,
            'duration_days': self.duration_days
        }


# ==================== ALERT MODELS ====================

class AlertConditionType(Enum):
    """Types of alert conditions"""
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PRICE_CHANGE_PERCENT = "price_change_percent"
    VOLUME_SPIKE = "volume_spike"
    RSI_OVERSOLD = "rsi_oversold"
    RSI_OVERBOUGHT = "rsi_overbought"
    MOVING_AVERAGE_CROSS = "moving_average_cross"
    MACD_SIGNAL_CROSS = "macd_signal_cross"
    EARNINGS_ANNOUNCEMENT = "earnings_announcement"
    DIVIDEND_ANNOUNCEMENT = "dividend_announcement"
    NEWS_KEYWORD = "news_keyword"
    CUSTOM_SCRIPT = "custom_script"


class LogicOperator(Enum):
    """Logic operators for combining conditions"""
    AND = "and"
    OR = "or"


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"
    IN_APP = "in_app"


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AlertCondition:
    """Single alert condition"""
    id: str
    type: AlertConditionType
    symbol: str
    parameters: Dict
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'type': self.type.value,
            'symbol': self.symbol,
            'parameters': self.parameters,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class AlertRule:
    """Alert rule with AND/OR logic for multiple conditions"""
    id: str
    name: str
    conditions: List[AlertCondition]
    logic: LogicOperator
    notifications: List[NotificationChannel]
    severity: AlertSeverity
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'conditions': [c.to_dict() for c in self.conditions],
            'logic': self.logic.value,
            'notifications': [n.value for n in self.notifications],
            'severity': self.severity.value,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class AlertEvent:
    """Alert event triggered"""
    id: str
    rule_id: str
    triggered_at: datetime
    triggered_conditions: Dict[str, bool]
    message: str
    severity: AlertSeverity
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'triggered_at': self.triggered_at.isoformat(),
            'triggered_conditions': self.triggered_conditions,
            'message': self.message,
            'severity': self.severity.value
        }


@dataclass
class BacktestResults:
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
            self.sortino_ratio = (np.mean(excess_returns) / downside_std * np.sqrt(252)) if downside_std > 0 else 0.0
        else:
            self.sortino_ratio = 0.0
        
        # Calmar Ratio (return / max drawdown)
        if self.max_drawdown_pct < 0:
            self.calmar_ratio = self.annual_return_pct / abs(self.max_drawdown_pct) if abs(self.max_drawdown_pct) > 0 else 0.0
        else:
            self.calmar_ratio = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'strategy_name': self.strategy_name,
            'symbol': self.symbol,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'initial_capital': self.initial_capital,
            'trades': [t.to_dict() for t in self.trades],
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
            'calmar_ratio': self.calmar_ratio
        }

@dataclass
class Position:
    """Stock position"""
    symbol: str
    shares: float
    purchase_price: float
    purchase_date: datetime
    current_price: float
    
    @property
    def cost_basis(self) -> float:
        """Total cost to acquire"""
        return self.shares * self.purchase_price
    
    @property
    def current_value(self) -> float:
        """Current position value"""
        return self.shares * self.current_price
    
    @property
    def gain_loss(self) -> float:
        """Gain or loss"""
        return self.current_value - self.cost_basis
    
    @property
    def gain_loss_pct(self) -> float:
        """Gain or loss percentage"""
        if self.cost_basis == 0:
            return 0.0
        return (self.gain_loss / self.cost_basis) * 100


# ==================== SCREENER MODELS ====================

@dataclass
class ScreenerCriteria:
    """Stock screener filtering criteria"""
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_market_cap: Optional[float] = None
    max_market_cap: Optional[float] = None
    min_pe_ratio: Optional[float] = None
    max_pe_ratio: Optional[float] = None
    min_dividend_yield: Optional[float] = None
    max_dividend_yield: Optional[float] = None
    min_growth_rate: Optional[float] = None
    max_growth_rate: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items() if v is not None}
