"""
Broker Integration Service
Unified interface for connecting to multiple brokers: Alpaca, TD Ameritrade, Interactive Brokers
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import json


class OrderType(Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Order sides: BUY or SELL"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    FILLED = "filled"
    PARTIAL_FILLED = "partial_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class PositionSide(Enum):
    """Position side"""
    LONG = "long"
    SHORT = "short"


@dataclass
class Account:
    """Broker account information"""
    account_id: str
    broker: str
    account_type: str  # individual, joint, ira, etc
    cash: float
    buying_power: float
    portfolio_value: float
    total_value: float
    day_trading_buying_power: float
    equity: float
    multiplier: float
    
    def __post_init__(self):
        """Calculate account metrics"""
        self.portfolio_return_pct = ((self.total_value - self.equity) / self.equity * 100) if self.equity > 0 else 0.0


@dataclass
class Position:
    """Open position"""
    symbol: str
    side: PositionSide
    quantity: float
    entry_price: float
    current_price: float
    market_value: float
    unrealized_gain_loss: float
    unrealized_gain_loss_pct: float
    average_fill_price: float = 0.0
    asset_id: str = ""
    
    def __post_init__(self):
        """Calculate position metrics if not provided"""
        if self.unrealized_gain_loss == 0:
            if self.side == PositionSide.LONG:
                self.unrealized_gain_loss = (self.current_price - self.entry_price) * self.quantity
            else:  # SHORT
                self.unrealized_gain_loss = (self.entry_price - self.current_price) * self.quantity
        
        if self.unrealized_gain_loss_pct == 0:
            self.unrealized_gain_loss_pct = (self.unrealized_gain_loss / (self.entry_price * self.quantity) * 100) if self.entry_price > 0 else 0.0


@dataclass
class Order:
    """Order record"""
    order_id: str
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    limit_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    commission: float = 0.0
    
    def is_filled(self) -> bool:
        """Check if order is fully filled"""
        return self.status == OrderStatus.FILLED
    
    def is_open(self) -> bool:
        """Check if order is still open"""
        return self.status in [OrderStatus.PENDING, OrderStatus.ACCEPTED, OrderStatus.PARTIAL_FILLED]


@dataclass
class Trade:
    """Completed trade"""
    trade_id: str
    symbol: str
    side: OrderSide
    quantity: float
    entry_price: float
    exit_price: Optional[float] = None
    entry_date: datetime = field(default_factory=datetime.now)
    exit_date: Optional[datetime] = None
    profit_loss: float = 0.0
    profit_loss_pct: float = 0.0
    commission: float = 0.0
    
    def __post_init__(self):
        """Calculate trade metrics"""
        if self.exit_price is not None:
            if self.side == OrderSide.BUY:
                self.profit_loss = (self.exit_price - self.entry_price) * self.quantity - self.commission
            else:  # SELL
                self.profit_loss = (self.entry_price - self.exit_price) * self.quantity - self.commission
            
            self.profit_loss_pct = (self.profit_loss / (self.entry_price * self.quantity) * 100) if self.entry_price > 0 else 0.0


class BrokerAPI(ABC):
    """Abstract base class for broker integrations"""
    
    def __init__(self, api_key: str, secret_key: str, sandbox: bool = False):
        """
        Initialize broker connection
        
        Args:
            api_key: API key
            secret_key: API secret key
            sandbox: Use sandbox/paper trading environment
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.sandbox = sandbox
        self.is_connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to broker API"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from broker"""
        pass
    
    @abstractmethod
    def get_account(self) -> Account:
        """Get account information"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Get all open positions"""
        pass
    
    @abstractmethod
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get orders, optionally filtered by status"""
        pass
    
    @abstractmethod
    def place_order(self, symbol: str, quantity: float, side: OrderSide,
                   order_type: OrderType = OrderType.MARKET,
                   price: Optional[float] = None,
                   stop_price: Optional[float] = None,
                   limit_price: Optional[float] = None) -> Order:
        """Place an order"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    def get_historical_data(self, symbol: str, start_date: datetime,
                           end_date: datetime, timeframe: str = "1day") -> Dict:
        """Get historical price data"""
        pass


class AlpacaBroker(BrokerAPI):
    """Alpaca broker integration"""
    
    def __init__(self, api_key: str, secret_key: str, sandbox: bool = True):
        super().__init__(api_key, secret_key, sandbox)
        self.broker_name = "Alpaca"
        self.base_url = "https://paper-api.alpaca.markets" if sandbox else "https://api.alpaca.markets"
        self.data_base_url = "https://data.alpaca.markets"
    
    def connect(self) -> bool:
        """Connect to Alpaca API"""
        try:
            import alpaca_trade_api as tradeapi
            
            self.client = tradeapi.REST(
                self.api_key,
                self.secret_key,
                base_url=self.base_url,
                api_version='v2'
            )
            
            # Test connection
            account = self.client.get_account()
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to Alpaca: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Alpaca"""
        self.is_connected = False
        return True
    
    def get_account(self) -> Account:
        """Get Alpaca account information"""
        try:
            acc = self.client.get_account()
            
            return Account(
                account_id=acc.id,
                broker="Alpaca",
                account_type=acc.account_type,
                cash=float(acc.cash),
                buying_power=float(acc.buying_power),
                portfolio_value=float(acc.portfolio_value),
                total_value=float(acc.portfolio_value) + float(acc.cash),
                day_trading_buying_power=float(acc.daytrade_buying_power),
                equity=float(acc.equity),
                multiplier=int(acc.multiplier) if hasattr(acc, 'multiplier') else 1
            )
        except Exception as e:
            print(f"Error getting account: {e}")
            raise
    
    def get_positions(self) -> List[Position]:
        """Get Alpaca positions"""
        try:
            positions = []
            alpaca_positions = self.client.list_positions()
            
            for pos in alpaca_positions:
                position = Position(
                    symbol=pos.symbol,
                    side=PositionSide.LONG if float(pos.qty) > 0 else PositionSide.SHORT,
                    quantity=abs(float(pos.qty)),
                    entry_price=float(pos.avg_fill_price),
                    current_price=float(pos.current_price),
                    market_value=float(pos.market_value),
                    unrealized_gain_loss=float(pos.unrealized_pl),
                    unrealized_gain_loss_pct=float(pos.unrealized_plpc) * 100,
                    average_fill_price=float(pos.avg_fill_price),
                    asset_id=pos.asset_id
                )
                positions.append(position)
            
            return positions
        except Exception as e:
            print(f"Error getting positions: {e}")
            return []
    
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get Alpaca orders"""
        try:
            orders = []
            status_filter = status.value if status else None
            alpaca_orders = self.client.list_orders(status=status_filter)
            
            for order in alpaca_orders:
                order_obj = Order(
                    order_id=order.id,
                    symbol=order.symbol,
                    order_type=OrderType(order.order_type),
                    side=OrderSide(order.side),
                    quantity=float(order.qty),
                    price=float(order.limit_price) if order.limit_price else None,
                    stop_price=float(order.stop_price) if order.stop_price else None,
                    status=OrderStatus(order.status),
                    created_at=order.created_at,
                    filled_at=order.filled_at,
                    filled_quantity=float(order.filled_qty) if order.filled_qty else 0.0,
                    average_fill_price=float(order.filled_avg_price) if order.filled_avg_price else 0.0
                )
                orders.append(order_obj)
            
            return orders
        except Exception as e:
            print(f"Error getting orders: {e}")
            return []
    
    def place_order(self, symbol: str, quantity: float, side: OrderSide,
                   order_type: OrderType = OrderType.MARKET,
                   price: Optional[float] = None,
                   stop_price: Optional[float] = None,
                   limit_price: Optional[float] = None) -> Order:
        """Place Alpaca order"""
        try:
            order_data = {
                'symbol': symbol,
                'qty': quantity,
                'side': side.value,
                'type': order_type.value,
                'time_in_force': 'day'
            }
            
            if order_type == OrderType.LIMIT and limit_price:
                order_data['limit_price'] = limit_price
            elif order_type == OrderType.STOP and stop_price:
                order_data['stop_price'] = stop_price
            elif order_type == OrderType.STOP_LIMIT and stop_price and limit_price:
                order_data['stop_price'] = stop_price
                order_data['limit_price'] = limit_price
            
            response = self.client.submit_order(**order_data)
            
            return Order(
                order_id=response.id,
                symbol=response.symbol,
                order_type=OrderType(response.order_type),
                side=OrderSide(response.side),
                quantity=float(response.qty),
                price=limit_price or stop_price,
                status=OrderStatus(response.status),
                created_at=response.created_at
            )
        except Exception as e:
            print(f"Error placing order: {e}")
            raise
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel Alpaca order"""
        try:
            self.client.cancel_order(order_id)
            return True
        except Exception as e:
            print(f"Error cancelling order: {e}")
            return False
    
    def get_historical_data(self, symbol: str, start_date: datetime,
                           end_date: datetime, timeframe: str = "1day") -> Dict:
        """Get Alpaca historical data"""
        try:
            from alpaca_trade_api.rest import TimeFrame
            
            timeframe_map = {
                "1min": TimeFrame.Minute,
                "5min": TimeFrame(5, "minute"),
                "15min": TimeFrame(15, "minute"),
                "1hour": TimeFrame.Hour,
                "1day": TimeFrame.Day
            }
            
            tf = timeframe_map.get(timeframe, TimeFrame.Day)
            
            bars = self.client.get_crypto_bars(
                symbol,
                tf,
                start=start_date,
                end=end_date,
                adjustment='raw'
            )
            
            return {
                'dates': [bar.t for bar in bars],
                'opens': [bar.o for bar in bars],
                'highs': [bar.h for bar in bars],
                'lows': [bar.l for bar in bars],
                'closes': [bar.c for bar in bars],
                'volumes': [bar.v for bar in bars]
            }
        except Exception as e:
            print(f"Error getting historical data: {e}")
            return {}


class TDAmeritradeBroker(BrokerAPI):
    """TD Ameritrade broker integration"""
    
    def __init__(self, api_key: str, secret_key: str, sandbox: bool = True):
        super().__init__(api_key, secret_key, sandbox)
        self.broker_name = "TD Ameritrade"
        self.account_id = None
    
    def connect(self) -> bool:
        """Connect to TD Ameritrade API"""
        try:
            from thinkorswim import ThinkorSwim
            
            self.client = ThinkorSwim(
                account_id=self.api_key,
                token=self.secret_key
            )
            
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to TD Ameritrade: {e}")
            print("Note: TD Ameritrade integration requires thinkorswim library")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from TD Ameritrade"""
        self.is_connected = False
        return True
    
    def get_account(self) -> Account:
        """Get TD Ameritrade account information"""
        try:
            # This is a placeholder - actual implementation requires TD API
            return Account(
                account_id=self.account_id or "DEMO",
                broker="TD Ameritrade",
                account_type="individual",
                cash=0.0,
                buying_power=0.0,
                portfolio_value=0.0,
                total_value=0.0,
                day_trading_buying_power=0.0,
                equity=0.0,
                multiplier=1
            )
        except Exception as e:
            print(f"Error getting account: {e}")
            raise
    
    def get_positions(self) -> List[Position]:
        """Get TD Ameritrade positions"""
        # Placeholder implementation
        return []
    
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get TD Ameritrade orders"""
        # Placeholder implementation
        return []
    
    def place_order(self, symbol: str, quantity: float, side: OrderSide,
                   order_type: OrderType = OrderType.MARKET,
                   price: Optional[float] = None,
                   stop_price: Optional[float] = None,
                   limit_price: Optional[float] = None) -> Order:
        """Place TD Ameritrade order"""
        # Placeholder implementation
        raise NotImplementedError("TD Ameritrade order placement not yet implemented")
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel TD Ameritrade order"""
        # Placeholder implementation
        return False
    
    def get_historical_data(self, symbol: str, start_date: datetime,
                           end_date: datetime, timeframe: str = "1day") -> Dict:
        """Get TD Ameritrade historical data"""
        # Placeholder implementation
        return {}


class BrokerManager:
    """Manager for multiple broker connections"""
    
    def __init__(self):
        self.brokers: Dict[str, BrokerAPI] = {}
        self.active_broker: Optional[str] = None
    
    def add_broker(self, name: str, broker: BrokerAPI) -> bool:
        """
        Add a broker connection
        
        Args:
            name: Unique name for this broker connection
            broker: BrokerAPI instance
            
        Returns:
            True if successfully connected
        """
        try:
            if broker.connect():
                self.brokers[name] = broker
                if self.active_broker is None:
                    self.active_broker = name
                return True
            return False
        except Exception as e:
            print(f"Error adding broker {name}: {e}")
            return False
    
    def remove_broker(self, name: str) -> bool:
        """Remove a broker connection"""
        try:
            if name in self.brokers:
                self.brokers[name].disconnect()
                del self.brokers[name]
                
                if self.active_broker == name:
                    self.active_broker = list(self.brokers.keys())[0] if self.brokers else None
                
                return True
            return False
        except Exception as e:
            print(f"Error removing broker {name}: {e}")
            return False
    
    def set_active_broker(self, name: str) -> bool:
        """Set active broker"""
        if name in self.brokers:
            self.active_broker = name
            return True
        return False
    
    def get_active_broker(self) -> Optional[BrokerAPI]:
        """Get active broker instance"""
        if self.active_broker and self.active_broker in self.brokers:
            return self.brokers[self.active_broker]
        return None
    
    def get_account(self) -> Optional[Account]:
        """Get account from active broker"""
        broker = self.get_active_broker()
        if broker:
            return broker.get_account()
        return None
    
    def get_positions(self) -> List[Position]:
        """Get positions from active broker"""
        broker = self.get_active_broker()
        if broker:
            return broker.get_positions()
        return []
    
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get orders from active broker"""
        broker = self.get_active_broker()
        if broker:
            return broker.get_orders(status)
        return []
    
    def place_order(self, symbol: str, quantity: float, side: OrderSide,
                   order_type: OrderType = OrderType.MARKET,
                   price: Optional[float] = None,
                   stop_price: Optional[float] = None,
                   limit_price: Optional[float] = None) -> Optional[Order]:
        """Place order on active broker"""
        broker = self.get_active_broker()
        if broker:
            return broker.place_order(symbol, quantity, side, order_type, price, stop_price, limit_price)
        return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel order on active broker"""
        broker = self.get_active_broker()
        if broker:
            return broker.cancel_order(order_id)
        return False
    
    def list_brokers(self) -> List[str]:
        """List all connected brokers"""
        return list(self.brokers.keys())
    
    def get_broker_info(self) -> Dict:
        """Get info about all connected brokers"""
        info = {}
        for name, broker in self.brokers.items():
            info[name] = {
                'broker': broker.broker_name if hasattr(broker, 'broker_name') else 'Unknown',
                'connected': broker.is_connected,
                'active': name == self.active_broker
            }
        return info
