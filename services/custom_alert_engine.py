"""
Custom Alert Engine Service
Advanced alert conditions with AND/OR logic and multi-channel notifications
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import sqlite3
import hashlib
import threading
import time

from utils.base_service import BaseService
from utils.data_models import (
    AlertCondition, AlertTemplate, AlertRule, AlertEvent,
    AlertConditionType, LogicOperator, NotificationChannel, AlertSeverity
)
from services.notification_handlers import NotificationHandler, EmailNotificationHandler, WebhookNotificationHandler, PushNotificationHandler, InAppNotificationHandler


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
        
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
    
    def evaluate_condition(self, condition: AlertCondition, 
                         values: Dict = None) -> tuple[bool, Dict]:
        """Evaluate if condition is met. Returns: (is_met, triggered_values)"""
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
                old_price, new_price = history[0], history[-1]
                percent_change = ((new_price - old_price) / old_price) * 100
                threshold = params.get('percent', 0)
                direction = params.get('direction', 'either')
                
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
                is_met = False
                triggered_values = {'keyword': keyword}
            
            else:
                is_met = False
            
            return is_met, triggered_values
        except Exception as e:
            return False, {}


class CustomAlertEngine(BaseService):
    """Main alert engine with rule management and notifications"""
    
    def __init__(self, db_path: str = "alerts.db"):
        super().__init__("CustomAlertEngine")
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
                id TEXT PRIMARY KEY, template_id TEXT, symbol TEXT,
                enabled BOOLEAN, triggered_count INTEGER, last_triggered TIMESTAMP,
                cooldown_minutes INTEGER, created_at TIMESTAMP)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_events (
                id TEXT PRIMARY KEY, rule_id TEXT, symbol TEXT, severity TEXT,
                message TEXT, triggered_at TIMESTAMP, triggered_values TEXT,
                read BOOLEAN, acknowledged BOOLEAN)
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
        template = AlertTemplate(id=template_id, name=name, description=description,
                                conditions=conditions, logic_operator=logic,
                                severity=severity, notification_channels=channels)
        self.templates[template_id] = template
        return template
    
    def create_alert_rule(self, template: AlertTemplate, symbol: str,
                         cooldown_minutes: int = 30) -> AlertRule:
        """Create an active alert rule"""
        rule_id = hashlib.md5(f"{template.id}{symbol}{datetime.now()}".encode()).hexdigest()
        rule = AlertRule(id=rule_id, template=template, symbol=symbol,
                        enabled=True, cooldown_minutes=cooldown_minutes)
        self.rules[rule_id] = rule
        self._save_rule_to_db(rule)
        return rule
    
    def evaluate_rule(self, rule: AlertRule) -> Optional[AlertEvent]:
        """Evaluate if a rule should trigger"""
        if not rule.enabled or rule.is_in_cooldown():
            return None
        
        template = rule.template
        results = [self.evaluator.evaluate_condition(c)[0] 
                  for c in template.conditions if c.enabled]
        
        rule_triggered = (all(results) if results else False) if template.logic_operator == LogicOperator.AND else (any(results) if results else False)
        
        if rule_triggered:
            event_id = hashlib.md5(f"{rule.id}{datetime.now()}".encode()).hexdigest()
            event = AlertEvent(id=event_id, rule_id=rule.id, symbol=rule.symbol,
                             severity=template.severity,
                             message=f"Alert: {rule.symbol} - {template.name}",
                             triggered_at=datetime.now())
            
            rule.triggered_count += 1
            rule.last_triggered = datetime.now()
            
            self.alert_events.append(event)
            self._save_event_to_db(event)
            
            for channel in template.notification_channels:
                handler = self.handlers.get(channel)
                if handler:
                    handler.send(event, "user@example.com")
            
            return event
        
        return None
    
    def get_alert_history(self, symbol: Optional[str] = None,
                         hours: int = 24) -> List[AlertEvent]:
        """Get alert history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        events = [e for e in self.alert_events if e.triggered_at > cutoff_time]
        return sorted([e for e in events if not symbol or e.symbol == symbol],
                     key=lambda e: e.triggered_at, reverse=True)
    
    def acknowledge_alert(self, event_id: str):
        """Mark alert as acknowledged"""
        for event in self.alert_events:
            if event.id == event_id:
                event.acknowledged = True
                break
    
    def start_monitoring(self, check_interval: int = 60):
        """Start monitoring alerts"""
        self.is_running = True
        self.check_thread = threading.Thread(target=self._monitoring_loop,
                                            args=(check_interval,), daemon=True)
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
        cursor.execute("INSERT OR REPLACE INTO alert_rules VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (rule.id, rule.template.id, rule.symbol, rule.enabled,
                       rule.triggered_count, rule.last_triggered,
                       rule.cooldown_minutes, rule.created_at))
        conn.commit()
        conn.close()
    
    def _save_event_to_db(self, event: AlertEvent):
        """Save event to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO alert_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (event.id, event.rule_id, event.symbol, event.severity.value,
                       event.message, event.triggered_at,
                       json.dumps(event.triggered_values), event.read, event.acknowledged))
        conn.commit()
        conn.close()
    
    def get_alert_templates(self) -> List[AlertTemplate]:
        """Get all alert templates"""
        return list(self.templates.values())
    
    def get_alert_rules(self, symbol: Optional[str] = None) -> List[AlertRule]:
        """Get alert rules"""
        rules = list(self.rules.values())
        return [r for r in rules if not symbol or r.symbol == symbol]
    
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alert_rules WHERE id = ?", (rule_id,))
            conn.commit()
            conn.close()
            return True
        return False
    
    def get_statistics(self) -> Dict:
        """Get alert statistics"""
        return {
            'total_events': len(self.alert_events),
            'unread_count': len(self.get_unread_alerts()),
            'triggered_today': sum(1 for e in self.alert_events
                                  if (datetime.now() - e.triggered_at).days < 1),
            'active_rules': sum(1 for r in self.rules.values() if r.enabled),
            'severity_distribution': {s.value: sum(1 for e in self.alert_events if e.severity == s)
                                     for s in AlertSeverity}
        }
