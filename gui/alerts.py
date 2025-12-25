"""Alerts tab - Real-time price and signal monitoring"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QMessageBox, QDialog, QFormLayout, QStatusBar
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor
from services.alert_service import AlertService
import logging

logger = logging.getLogger(__name__)


class CreateAlertDialog(QDialog):
    """Dialog for creating a new alert"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Alert")
        self.setGeometry(100, 100, 400, 300)
        self.result_data = None
        
        layout = QFormLayout()
        
        # Symbol input
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("e.g., AAPL")
        layout.addRow("Stock Symbol:", self.symbol_input)
        
        # Alert type
        self.alert_type = QComboBox()
        self.alert_type.addItems([
            "Price Above",
            "Price Below",
            "Buy Signal",
            "Sell Signal"
        ])
        self.alert_type.currentTextChanged.connect(self._update_label)
        layout.addRow("Alert Type:", self.alert_type)
        
        # Target value
        self.target_value = QDoubleSpinBox()
        self.target_value.setRange(0, 10000)
        self.target_value.setDecimals(2)
        self.target_value.setValue(0)
        self.target_value_label = QLabel("Price Target ($):")
        layout.addRow(self.target_value_label, self.target_value)
        
        # Notes
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Optional notes...")
        layout.addRow("Notes:", self.notes_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Alert")
        create_btn.clicked.connect(self.create_alert)
        button_layout.addWidget(create_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    def _update_label(self, text):
        """Update target value label based on alert type"""
        if "Price" in text:
            self.target_value_label.setText("Price Target ($):")
        else:
            self.target_value_label.setText("Threshold Value:")
    
    def create_alert(self):
        """Validate and create alert"""
        symbol = self.symbol_input.text().strip().upper()
        alert_type_map = {
            "Price Above": "price_above",
            "Price Below": "price_below",
            "Buy Signal": "buy_signal",
            "Sell Signal": "sell_signal"
        }
        alert_type = alert_type_map[self.alert_type.currentText()]
        target = self.target_value.value()
        notes = self.notes_input.text()
        
        if not symbol:
            QMessageBox.warning(self, "Error", "Please enter a stock symbol")
            return
        
        if target <= 0:
            QMessageBox.warning(self, "Error", "Please enter a valid target value")
            return
        
        self.result_data = {
            'symbol': symbol,
            'alert_type': alert_type,
            'target_value': target,
            'notes': notes
        }
        
        self.accept()


class AlertsTab(QWidget):
    """Tab for managing real-time alerts"""
    
    alert_triggered = Signal(dict)
    
    def __init__(self, db, cache):
        super().__init__()
        self.db = db
        self.cache = cache
        self.alert_service = AlertService(db, check_interval=60)  # Check every minute
        self.alert_service.register_callback(self.on_alert_triggered)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🔔 Real-Time Alerts")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Add Alert")
        self.add_btn.clicked.connect(self.create_alert)
        button_layout.addWidget(self.add_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.clicked.connect(self.delete_alert)
        button_layout.addWidget(self.delete_btn)
        
        self.reset_btn = QPushButton("🔄 Reset Alert")
        self.reset_btn.clicked.connect(self.reset_alert)
        button_layout.addWidget(self.reset_btn)
        
        self.start_btn = QPushButton("▶️ Start Monitoring")
        self.start_btn.clicked.connect(self.start_monitoring)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop Monitoring")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        button_layout.addWidget(self.stop_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Alerts table
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(6)
        self.alerts_table.setHorizontalHeaderLabels([
            "Symbol", "Type", "Target", "Status", "Triggered", "Notes"
        ])
        self.alerts_table.setColumnWidth(0, 80)
        self.alerts_table.setColumnWidth(1, 120)
        self.alerts_table.setColumnWidth(2, 100)
        self.alerts_table.setColumnWidth(3, 80)
        self.alerts_table.setColumnWidth(4, 150)
        layout.addWidget(self.alerts_table)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready to monitor alerts")
        self.status_label.setStyleSheet("color: #AAAAAA; font-size: 9pt;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.summary_label = QLabel("Alerts: 0 total, 0 active, 0 triggered")
        self.summary_label.setStyleSheet("color: #AAAAAA; font-size: 9pt;")
        status_layout.addWidget(self.summary_label)
        
        layout.addLayout(status_layout)
        
        # Timer to refresh table
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_alerts)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
        # Signal for alerts
        self.alert_triggered.connect(self.on_alert_received)
        
        # Load initial alerts
        self.refresh_alerts()
    
    def create_alert(self):
        """Open dialog to create new alert"""
        dialog = CreateAlertDialog(self)
        if dialog.exec() == QDialog.Accepted and dialog.result_data:
            data = dialog.result_data
            self.alert_service.add_alert(
                symbol=data['symbol'],
                alert_type=data['alert_type'],
                target_value=data['target_value'],
                notes=data['notes']
            )
            self.refresh_alerts()
            self.status_label.setText(f"✓ Alert created for {data['symbol']}")
    
    def delete_alert(self):
        """Delete selected alert"""
        selected = self.alerts_table.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, "Error", "Please select an alert to delete")
            return
        
        row = selected[0].row()
        alert_id = self.alerts_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        self.alert_service.remove_alert(alert_id)
        self.refresh_alerts()
        self.status_label.setText("✓ Alert deleted")
    
    def reset_alert(self):
        """Reset a triggered alert"""
        selected = self.alerts_table.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, "Error", "Please select an alert to reset")
            return
        
        row = selected[0].row()
        alert_id = self.alerts_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        self.alert_service.reset_alert(alert_id)
        self.refresh_alerts()
        self.status_label.setText("✓ Alert reset")
    
    def start_monitoring(self):
        """Start alert monitoring"""
        self.alert_service.start_monitoring()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("🟢 Monitoring active")
    
    def stop_monitoring(self):
        """Stop alert monitoring"""
        self.alert_service.stop_monitoring()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("🔴 Monitoring stopped")
    
    def refresh_alerts(self):
        """Refresh alerts table"""
        alerts = self.alert_service.get_alerts()
        self.alerts_table.setRowCount(len(alerts))
        
        for row, alert in enumerate(alerts):
            # Symbol
            symbol_item = QTableWidgetItem(alert.symbol)
            symbol_item.setData(Qt.ItemDataRole.UserRole, alert.id)
            self.alerts_table.setItem(row, 0, symbol_item)
            
            # Type
            type_text = alert.alert_type.replace('_', ' ').title()
            self.alerts_table.setItem(row, 1, QTableWidgetItem(type_text))
            
            # Target
            self.alerts_table.setItem(row, 2, QTableWidgetItem(f"${alert.target_value:.2f}"))
            
            # Status
            status_text = "🟢 Active" if alert.is_active else "🔴 Inactive"
            self.alerts_table.setItem(row, 3, QTableWidgetItem(status_text))
            
            # Triggered
            triggered_text = "✓ Yes" if alert.triggered_at else "✗ No"
            triggered_item = QTableWidgetItem(triggered_text)
            if alert.triggered_at:
                triggered_item.setBackground(QColor("#2d5016"))  # Green background
            self.alerts_table.setItem(row, 4, triggered_item)
            
            # Notes
            self.alerts_table.setItem(row, 5, QTableWidgetItem(alert.notes))
        
        # Update summary
        summary = self.alert_service.get_alert_summary()
        self.summary_label.setText(
            f"Alerts: {summary['total_alerts']} total, "
            f"{summary['active_alerts']} active, "
            f"{summary['triggered_alerts']} triggered"
        )
    
    def on_alert_triggered(self, alert_data: dict):
        """Called by alert service when alert triggers"""
        self.alert_triggered.emit(alert_data)
    
    def on_alert_received(self, alert_data: dict):
        """Handle received alert notification"""
        alert = alert_data['alert']
        message = alert_data['message']
        
        # Show notification
        QMessageBox.information(self, "Alert Triggered", message)
        
        # Refresh table
        self.refresh_alerts()
    
    def closeEvent(self, event):
        """Cleanup on close"""
        self.refresh_timer.stop()
        self.alert_service.stop_monitoring()
        super().closeEvent(event)
