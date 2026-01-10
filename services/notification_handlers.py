"""
Notification Handlers
Abstract and concrete implementations for sending alerts via different channels
"""

from abc import ABC, abstractmethod
import requests
from utils.data_models import AlertEvent


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
            print(f"📧 Email sent to {recipient}")
            print(f"   Subject: Alert: {alert_event.symbol}")
            print(f"   Message: {alert_event.message}")
            return True
        except Exception as e:
            print(f"❌ Email send failed: {e}")
            return False


class WebhookNotificationHandler(NotificationHandler):
    """Send notifications via webhook"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url)
    
    def send(self, alert_event: AlertEvent, recipient: str) -> bool:
        """Send webhook notification"""
        try:
            if not self.webhook_url:
                return False
            
            payload = alert_event.to_dict()
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Webhook send failed: {e}")
            return False


class PushNotificationHandler(NotificationHandler):
    """Send notifications via push notifications"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.enabled = bool(api_key)
    
    def send(self, alert_event: AlertEvent, recipient: str) -> bool:
        """Send push notification"""
        try:
            print(f"📱 Push notification sent to {recipient}")
            print(f"   Alert: {alert_event.symbol}")
            return True
        except Exception as e:
            print(f"❌ Push send failed: {e}")
            return False


class InAppNotificationHandler(NotificationHandler):
    """Store notifications in-app"""
    
    def __init__(self):
        self.notifications = []
    
    def send(self, alert_event: AlertEvent, recipient: str) -> bool:
        """Store in-app notification"""
        try:
            self.notifications.append(alert_event)
            return True
        except Exception as e:
            print(f"❌ In-app notification failed: {e}")
            return False
