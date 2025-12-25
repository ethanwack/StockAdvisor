"""
Custom Alert Engine Service
Advanced alert conditions with AND/OR logic, webhooks, and multi-channel notifications
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
import json
import requests
from abc import ABC, abstractmethod
import threading
import time
import sqlite3
import hashlib


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
class AlertTemplate:
    """Reusable alert template"""
    id: str
    name: str
    description: str
    conditions: List[AlertCondition]
    logic_operator: LogicOperator
    severity: AlertSeverity
    notification_channels: List[NotificationChannel]
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'conditions': [c.to_dict() for c in self.conditions],
            'logic_operator': self.logic_operator.value,
            'severity': self.severity.value,
            'notification_channels': [ch.value for ch in self.notification_channels],
            'created_at': self.created_at.isoformat()
        }


@dataclass
class AlertRule:
    """Active alert rule"""
    id: str
    template: AlertTemplate
    symbol: str
    enabled: bool
    triggered_count: int = 0
    last_triggered: Optional[datetime] = None
    cooldown_minutes: int = 0  # Prevent alert spam
    created_at: datetime = field(default_factory=datetime.now)
    
    def is_in_cooldown(self) -> bool:
        """Check if rule is in cooldown period"""
        if not self.last_triggered or self.cooldown_minutes == 0:
            return False
        
        cooldown_end = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
        return datetime.now() < cooldown_end
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'template_id': self.template.id,
            'symbol': self.symbol,
            'enabled': self.enabled,
            'triggered_count': self.triggered_count,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'cooldown_minutes': self.cooldown_minutes,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class AlertEvent:
    """Triggered alert event"""
    id: str
    rule_id: str
    symbol: str
    severity: AlertSeverity
    message: str
    triggered_at: datetime
    triggered_values: Dict = field(default_factory=dict)
    read: bool = False
    acknowledged: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'symbol': self.symbol,
            'severity': self.severity.value,
            'message': self.message,
            'triggered_at': self.triggered_at.isoformat(),
            'triggered_values': self.triggered_values,
            'read': self.read,
            'acknowledged': self.acknowledged
        }


class NotificationHandler(ABC):
    """Base class for notification handlers"""
    
    @abstractmethod
    def send(self, alert_event: AlertEvent, recipient: str) -> bool:
        """Send notification"""
        pass


class EmailNotificationHandler(NotificationHandler):
    """Send notifications via email"""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = 587):
        self.smtp_server = smtp_server or "smtp.gmail.com"
        self.smtp_port = smtp_port
        self.enabled = True
    
    def send(self, alert_event: AlertEvent, recipient: str) -> bool:
        """Send email notification"""
        try:
            # In production, would use actual SMTP
            # For now, just log
            print(f"📧 Email sent to {recipient}")
            print(f"   Subject: Alert: {alert_event.symbol}")
            print(f"   Message: {alert_event.message}")
            return True
        except Exception as e:
            print(f"❌ Email send failed: {e}")
            return False


class WebhookNotificationHandler(NotificationHandler):
    """Send notifications via webhook"""
    
    def __init__(self):
        self.enabled = True
    
    def send(self, alert_event: AlertEvent, recipient: str) -> bool:
        """Send webhook notification"""
        try:
            payload = alert_event.to_dict()
            response = requests.post(recipient, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Webhook send failed: {e}")
            return False


class PushNotificationHandler(NotificationHandler):
    """Send push notifications"""
    
    def __init__(self):
        self.enabled = True
    
    def send(self, alert_event: AlertEvent, recipient: str) -> bool:
        """Send push notification"""
        try:
            # In production, would use Firebase, OneSignal, etc.
            print(f"📱 Push notification sent to device: {recipient}")
            return True
        except Exception as e:
            print(f"❌ Push send failed: {e}")
            return False


class InAppNotificationHandler(NotificationHandler):
    """In-app notifications"""
    
    def __init__(self):
        self.enabled = True
        self.notifications: List[AlertEvent] = []
    
    def send(self, alert_event: AlertEvent, recipient: str) -> bool:
        """Store in-app notification"""
        self.notifications.append(alert_event)
        return True


class ConditionEvaluator:
    """Evaluates alert conditions against current data"""
    
    def __init__(self):
        self.current_prices: Dict[str, float] = {}
        self.price_history: Dict[str, List[float]] = {}
        self.volumes: Dict[str, float] = {}
    
    def update_price(self, symbol: str, price: float, volume: float = 0):
        """Update current price and volume"""
        self.current_prices[symbol] = price
        self.volumes[symbol] = volume
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(price)
        
        # Keep only last 100 prices
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
    
    def evaluate_condition(self, condition: AlertCondition, 
                         values: Dict = None) -> tuple[bool, Dict]:
        """
        Evaluate if condition is met
        Returns: (is_met, triggered_values)
        """
        symbol = condition.symbol
        params = condition.parameters
        triggered_values = {}
        
        try:
            if condition.type == AlertConditionType.PRICE_ABOVE:
                current = self.current_prices.get(symbol, 0)
                threshold = params.get('threshold', 0)
                is_met = current > threshold
                triggered_values = {'current_price': current, 'threshold': threshold}
            
            elif condition.type == AlertConditionType.PRICE_BELOW:
                current = self.current_prices.get(symbol, 0)
                threshold = params.get('threshold', 0)
                is_met = current < threshold
                triggered_values = {'current_price': current, 'threshold': threshold}
            
            elif condition.type == AlertConditionType.PRICE_CHANGE_PERCENT:
                history = self.price_history.get(symbol, [])
                if len(history) < 2:
                    return False, {}
                
                old_price = history[0]
                new_price = history[-1]
                percent_change = ((new_price - old_price) / old_price) * 100
                threshold = params.get('percent', 0)
                direction = params.get('direction', 'either')  # 'up', 'down', 'either'
                
                if direction == 'up':
                    is_met = percent_change > threshold
                elif direction == 'down':
                    is_met = percent_change < -threshold
                else:
                    is_met = abs(percent_change) > threshold
                
                triggered_values = {'percent_change': percent_change, 'threshold': threshold}
            
            elif condition.type == AlertConditionType.VOLUME_SPIKE:
                history = self.price_history.get(symbol, [])
                volumes = [self.volumes.get(symbol, 0)] * len(history)
                
                if len(volumes) < 20:
                    return False, {}
                
                avg_volume = sum(volumes[:-1]) / (len(volumes) - 1)
                current_volume = volumes[-1]
                multiplier = params.get('multiplier', 2)
                
                is_met = current_volume > (avg_volume * multiplier)
                triggered_values = {'current_volume': current_volume, 'avg_volume': avg_volume}
            
            elif condition.type == AlertConditionType.RSI_OVERSOLD:
                rsi = params.get('rsi_value', 0)
                threshold = params.get('threshold', 30)
                is_met = rsi < threshold
                triggered_values = {'rsi': rsi, 'threshold': threshold}
            
            elif condition.type == AlertConditionType.RSI_OVERBOUGHT:
                rsi = params.get('rsi_value', 0)
                threshold = params.get('threshold', 70)
                is_met = rsi > threshold
                triggered_values = {'rsi': rsi, 'threshold': threshold}
            
            elif condition.type == AlertConditionType.NEWS_KEYWORD:
                keyword = params.get('keyword', '')
                is_met = False  # Would check news API in production
                triggered_values = {'keyword': keyword}
            
            else:
                is_met = False
            
            return is_met, triggered_values
        
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return False, {}


class CustomAlertEngine:
    """Main alert engine"""
    
    def __init__(self, db_path: str = "alerts.db"):
        self.db_path = db_path
        self.rules: Dict[str, AlertRule] = {}
        self.templates: Dict[str, AlertTemplate] = {}
        self.alert_events: List[AlertEvent] = []
        self.evaluator = ConditionEvaluator()
        
        # Notification handlers
        self.handlers = {
            NotificationChannel.EMAIL: EmailNotificationHandler(),
            NotificationChannel.WEBHOOK: WebhookNotificationHandler(),
            NotificationChannel.PUSH: PushNotificationHandler(),
            NotificationChannel.IN_APP: InAppNotificationHandler(),
        }
        
        self.is_running = False
        self.check_thread = None
        
        self._init_db()
    
    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_rules (
                id TEXT PRIMARY KEY,
                template_id TEXT,
                symbol TEXT,
                enabled BOOLEAN,
                triggered_count INTEGER,
                last_triggered TIMESTAMP,
                cooldown_minutes INTEGER,
                created_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_events (
                id TEXT PRIMARY KEY,
                rule_id TEXT,
                symbol TEXT,
                severity TEXT,
                message TEXT,
                triggered_at TIMESTAMP,
                triggered_values TEXT,
                read BOOLEAN,
                acknowledged BOOLEAN
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_alert_template(self, name: str, description: str,
                            conditions: List[AlertCondition],
                            logic: LogicOperator,
                            severity: AlertSeverity,
                            channels: List[NotificationChannel]) -> AlertTemplate:
        """Create an alert template"""
        template_id = hashlib.md5(f"{name}{datetime.now()}".encode()).hexdigest()
        template = AlertTemplate(
            id=template_id,
            name=name,
            description=description,
            conditions=conditions,
            logic_operator=logic,
            severity=severity,
            notification_channels=channels
        )
        
        self.templates[template_id] = template
        return template
    
    def create_alert_rule(self, template: AlertTemplate, symbol: str,
                         cooldown_minutes: int = 30) -> AlertRule:
        """Create an active alert rule"""
        rule_id = hashlib.md5(f"{template.id}{symbol}{datetime.now()}".encode()).hexdigest()
        rule = AlertRule(
            id=rule_id,
            template=template,
            symbol=symbol,
            enabled=True,
            cooldown_minutes=cooldown_minutes
        )
        
        self.rules[rule_id] = rule
        self._save_rule_to_db(rule)
        return rule
    
    def evaluate_rule(self, rule: AlertRule) -> Optional[AlertEvent]:
        """Evaluate if a rule should trigger"""
        if not rule.enabled or rule.is_in_cooldown():
            return None
        
        template = rule.template
        conditions = template.conditions
        results = []
        triggered_values = {}
        
        # Evaluate all conditions
        for condition in conditions:
            if not condition.enabled:
                continue
            
            is_met, values = self.evaluator.evaluate_condition(condition)
            results.append(is_met)
            triggered_values.update(values)
        
        # Apply logic operator
        if template.logic_operator == LogicOperator.AND:
            rule_triggered = all(results) if results else False
        else:  # OR
            rule_triggered = any(results) if results else False
        
        if rule_triggered:
            # Create alert event
            event_id = hashlib.md5(f"{rule.id}{datetime.now()}".encode()).hexdigest()
            event = AlertEvent(
                id=event_id,
                rule_id=rule.id,
                symbol=rule.symbol,
                severity=template.severity,
                message=f"Alert triggered for {rule.symbol}: {template.name}",
                triggered_at=datetime.now(),
                triggered_values=triggered_values
            )
            
            rule.triggered_count += 1
            rule.last_triggered = datetime.now()
            
            self.alert_events.append(event)
            self._save_event_to_db(event)
            
            # Send notifications
            for channel in template.notification_channels:
                self._send_notification(event, channel)
            
            return event
        
        return None
    
    def _send_notification(self, event: AlertEvent, channel: NotificationChannel):
        """Send notification via specified channel"""
        handler = self.handlers.get(channel)
        if handler:
            # In production, would get actual recipient from user settings
            handler.send(event, "user@example.com")
    
    def get_alert_history(self, symbol: Optional[str] = None,
                         hours: int = 24) -> List[AlertEvent]:
        """Get alert history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        events = [e for e in self.alert_events if e.triggered_at > cutoff_time]
        
        if symbol:
            events = [e for e in events if e.symbol == symbol]
        
        return sorted(events, key=lambda e: e.triggered_at, reverse=True)
    
    def acknowledge_alert(self, event_id: str):
        """Mark alert as acknowledged"""
        for event in self.alert_events:
            if event.id == event_id:
                event.acknowledged = True
                break
    
    def start_monitoring(self, check_interval: int = 60):
        """Start monitoring alerts"""
        self.is_running = True
        self.check_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(check_interval,),
            daemon=True
        )
        self.check_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring alerts"""
        self.is_running = False
    
    def _monitoring_loop(self, check_interval: int):
        """Main monitoring loop"""
        while self.is_running:
            for rule in self.rules.values():
                self.evaluate_rule(rule)
            
            time.sleep(check_interval)
    
    def _save_rule_to_db(self, rule: AlertRule):
        """Save rule to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO alert_rules 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rule.id,
            rule.template.id,
            rule.symbol,
            rule.enabled,
            rule.triggered_count,
            rule.last_triggered,
            rule.cooldown_minutes,
            rule.created_at
        ))
        
        conn.commit()
        conn.close()
    
    def _save_event_to_db(self, event: AlertEvent):
        """Save event to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alert_events 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.id,
            event.rule_id,
            event.symbol,
            event.severity.value,
            event.message,
            event.triggered_at,
            json.dumps(event.triggered_values),
            event.read,
            event.acknowledged
        ))
        
        conn.commit()
        conn.close()
    
    def get_alert_templates(self) -> List[AlertTemplate]:
        """Get all alert templates"""
        return list(self.templates.values())
    
    def get_alert_rules(self, symbol: Optional[str] = None) -> List[AlertRule]:
        """Get all alert rules"""
        rules = list(self.rules.values())
        if symbol:
            rules = [r for r in rules if r.symbol == symbol]
        return rules
    
    def get_unread_alerts(self) -> List[AlertEvent]:
        """Get unread alerts"""
        return [e for e in self.alert_events if not e.read]
    
    def mark_alert_read(self, event_id: str):
        """Mark alert as read"""
        for event in self.alert_events:
            if event.id == event_id:
                event.read = True
                break
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete an alert rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            
            # Delete from DB
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alert_rules WHERE id = ?", (rule_id,))
            conn.commit()
            conn.close()
            
            return True
        return False
    
    def get_statistics(self) -> Dict:
        """Get alert statistics"""
        total_events = len(self.alert_events)
        unread = len(self.get_unread_alerts())
        triggered_today = sum(
            1 for e in self.alert_events
            if (datetime.now() - e.triggered_at).days < 1
        )
        
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = sum(
                1 for e in self.alert_events if e.severity == severity
            )
        
        return {
            'total_events': total_events,
            'unread_count': unread,
            'triggered_today': triggered_today,
            'active_rules': sum(1 for r in self.rules.values() if r.enabled),
            'severity_distribution': severity_counts
        }
