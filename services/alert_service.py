"""Real-time alert system for price targets, buy/sell signals, and custom triggers"""

import threading
import time
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime
import json
from dataclasses import dataclass, asdict
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    """Alert configuration"""
    id: str
    symbol: str
    alert_type: str  # 'price_above', 'price_below', 'buy_signal', 'sell_signal'
    target_value: float
    is_active: bool = True
    created_at: str = None
    triggered_at: Optional[str] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class AlertService:
    """Service for managing and monitoring stock alerts"""
    
    def __init__(self, db=None, check_interval=300):
        """
        Initialize alert service
        
        Args:
            db: Database instance for persistence
            check_interval: Seconds between alert checks (default 5 minutes)
        """
        self.db = db
        self.check_interval = check_interval
        self.alerts: Dict[str, Alert] = {}
        self.is_running = False
        self.monitor_thread = None
        self.alert_callbacks: List[Callable] = []
        self._load_alerts()
    
    def add_alert(self, symbol: str, alert_type: str, target_value: float, notes: str = "") -> Alert:
        """
        Add a new alert
        
        Args:
            symbol: Stock ticker symbol
            alert_type: Type of alert ('price_above', 'price_below', 'buy_signal', 'sell_signal')
            target_value: Price target or signal threshold
            notes: Optional notes for the alert
            
        Returns:
            Alert object created
        """
        alert_id = f"{symbol}_{alert_type}_{datetime.now().timestamp()}"
        alert = Alert(
            id=alert_id,
            symbol=symbol.upper(),
            alert_type=alert_type,
            target_value=target_value,
            notes=notes
        )
        
        self.alerts[alert_id] = alert
        self._save_alerts()
        
        logger.info(f"Alert created: {symbol} {alert_type} at {target_value}")
        return alert
    
    def remove_alert(self, alert_id: str) -> bool:
        """Remove an alert"""
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            self._save_alerts()
            logger.info(f"Alert removed: {alert_id}")
            return True
        return False
    
    def get_alerts(self, symbol: Optional[str] = None) -> List[Alert]:
        """Get all alerts, optionally filtered by symbol"""
        if symbol:
            return [a for a in self.alerts.values() if a.symbol == symbol.upper()]
        return list(self.alerts.values())
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if self.is_running:
            logger.warning("Monitoring already running")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Alert monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Alert monitoring stopped")
    
    def register_callback(self, callback: Callable):
        """Register callback function for when alerts trigger"""
        self.alert_callbacks.append(callback)
    
    def _monitor_loop(self):
        """Background loop that checks alerts"""
        while self.is_running:
            try:
                self._check_all_alerts()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in alert monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def _check_all_alerts(self):
        """Check all active alerts"""
        # Group by symbol for efficiency
        symbols = set(a.symbol for a in self.alerts.values() if a.is_active)
        
        for symbol in symbols:
            try:
                price = self._get_current_price(symbol)
                if price is None:
                    continue
                
                symbol_alerts = [a for a in self.alerts.values() 
                               if a.symbol == symbol and a.is_active]
                
                for alert in symbol_alerts:
                    self._check_alert(alert, price)
            except Exception as e:
                logger.error(f"Error checking alerts for {symbol}: {e}")
    
    def _check_alert(self, alert: Alert, current_price: float):
        """Check if an alert should trigger"""
        should_trigger = False
        
        if alert.alert_type == 'price_above':
            should_trigger = current_price >= alert.target_value
        elif alert.alert_type == 'price_below':
            should_trigger = current_price <= alert.target_value
        elif alert.alert_type == 'buy_signal':
            # Buy signal when price drops to target
            should_trigger = current_price <= alert.target_value
        elif alert.alert_type == 'sell_signal':
            # Sell signal when price rises to target
            should_trigger = current_price >= alert.target_value
        
        if should_trigger and alert.triggered_at is None:
            self._trigger_alert(alert, current_price)
    
    def _trigger_alert(self, alert: Alert, current_price: float):
        """Trigger an alert"""
        alert.triggered_at = datetime.now().isoformat()
        self._save_alerts()
        
        alert_data = {
            'alert': alert,
            'current_price': current_price,
            'message': f"🔔 Alert: {alert.symbol} {alert.alert_type} triggered at ${current_price:.2f}"
        }
        
        # Call all registered callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"Error calling alert callback: {e}")
        
        logger.warning(alert_data['message'])
    
    def reset_alert(self, alert_id: str):
        """Reset a triggered alert to monitor again"""
        if alert_id in self.alerts:
            self.alerts[alert_id].triggered_at = None
            self._save_alerts()
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.info
            price = data.get('regularMarketPrice') or data.get('currentPrice')
            return float(price) if price else None
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def _save_alerts(self):
        """Save alerts to database"""
        if not self.db:
            return
        
        try:
            alerts_json = json.dumps({
                aid: asdict(alert) for aid, alert in self.alerts.items()
            })
            # Store in database (implementation depends on DB schema)
            # For now, just log
            logger.debug(f"Alerts saved: {len(self.alerts)} alerts")
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")
    
    def _load_alerts(self):
        """Load alerts from database"""
        if not self.db:
            return
        
        try:
            # Load from database (implementation depends on DB schema)
            # For now, start with empty alerts
            logger.debug("Alerts loaded from database")
        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
    
    def get_alert_summary(self) -> Dict:
        """Get summary of all alerts"""
        total = len(self.alerts)
        active = sum(1 for a in self.alerts.values() if a.is_active)
        triggered = sum(1 for a in self.alerts.values() if a.triggered_at)
        
        by_type = {}
        for alert in self.alerts.values():
            alert_type = alert.alert_type
            if alert_type not in by_type:
                by_type[alert_type] = 0
            by_type[alert_type] += 1
        
        return {
            'total_alerts': total,
            'active_alerts': active,
            'triggered_alerts': triggered,
            'by_type': by_type
        }


class AlertWorker:
    """Worker thread for alert monitoring"""
    
    def __init__(self, alert_service: AlertService):
        self.alert_service = alert_service
        self.alert_triggered = None  # Will be set to Signal in GUI
    
    def set_signal(self, signal):
        """Set the PyQt signal for alert triggered"""
        self.alert_triggered = signal
    
    def notify_alert(self, alert_data: dict):
        """Notify when alert is triggered"""
        if self.alert_triggered:
            try:
                self.alert_triggered.emit(alert_data)
            except Exception as e:
                logger.error(f"Error emitting alert signal: {e}")
