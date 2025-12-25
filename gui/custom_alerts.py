"""
Custom Alert Engine GUI Tab
Create and manage advanced alert rules with AND/OR logic
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox, QDoubleSpinBox,
    QMessageBox, QGroupBox, QTextEdit, QHeaderView, QCheckBox, QListWidget,
    QListWidgetItem, QDialog, QFormLayout, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont
from typing import List, Dict, Optional

from services.custom_alert_engine import (
    CustomAlertEngine, AlertCondition, AlertConditionType, AlertTemplate,
    LogicOperator, NotificationChannel, AlertSeverity, AlertRule
)


class AlertWorker(QThread):
    """Worker thread for alert operations"""
    
    data_ready = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.task = None
        self.params = {}
    
    def set_evaluate_alerts(self, engine: CustomAlertEngine):
        """Set task to evaluate alerts"""
        self.task = 'evaluate'
        self.params = {'engine': engine}
    
    def run(self):
        try:
            if self.task == 'evaluate':
                engine = self.params['engine']
                results = {}
                for rule in engine.get_alert_rules():
                    event = engine.evaluate_rule(rule)
                    if event:
                        results[rule.id] = event.to_dict()
                self.data_ready.emit({'triggered': results})
        except Exception as e:
            self.error_occurred.emit(str(e))


class CreateConditionDialog(QDialog):
    """Dialog to create a new alert condition"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Alert Condition")
        self.setGeometry(100, 100, 500, 400)
        self.condition = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QFormLayout()
        
        # Symbol
        self.symbol_input = QLineEdit()
        layout.addRow("Symbol:", self.symbol_input)
        
        # Condition Type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            'Price Above', 'Price Below', 'Price Change %', 'Volume Spike',
            'RSI Oversold', 'RSI Overbought', 'News Keyword'
        ])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        layout.addRow("Condition Type:", self.type_combo)
        
        # Dynamic parameter fields
        self.param_widgets = {}
        
        # Threshold
        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setMinimum(0)
        self.threshold_input.setMaximum(100000)
        self.threshold_input.setValue(100)
        self.threshold_label = QLabel("Threshold ($):")
        layout.addRow(self.threshold_label, self.threshold_input)
        self.param_widgets['threshold'] = (self.threshold_label, self.threshold_input)
        
        # Direction
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(['Up', 'Down', 'Either'])
        self.direction_label = QLabel("Direction:")
        layout.addRow(self.direction_label, self.direction_combo)
        self.param_widgets['direction'] = (self.direction_label, self.direction_combo)
        self.direction_label.hide()
        self.direction_combo.hide()
        
        # Multiplier
        self.multiplier_spin = QDoubleSpinBox()
        self.multiplier_spin.setMinimum(1.0)
        self.multiplier_spin.setMaximum(10.0)
        self.multiplier_spin.setValue(2.0)
        self.multiplier_label = QLabel("Multiplier:")
        layout.addRow(self.multiplier_label, self.multiplier_spin)
        self.param_widgets['multiplier'] = (self.multiplier_label, self.multiplier_spin)
        self.multiplier_label.hide()
        self.multiplier_spin.hide()
        
        # Enabled
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(True)
        layout.addRow("Enabled:", self.enabled_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton("✅ Create Condition")
        create_btn.clicked.connect(self._create_condition)
        button_layout.addWidget(create_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    def _on_type_changed(self, type_name: str):
        """Handle condition type change"""
        # Hide all dynamic widgets
        for label, widget in self.param_widgets.values():
            label.hide()
            widget.hide()
        
        # Show relevant widgets based on type
        if 'Price' in type_name:
            self.threshold_label.setText("Price Threshold ($):")
            self.threshold_label.show()
            self.threshold_input.show()
            
            if '%' in type_name:
                self.threshold_label.setText("Percent Change (%):")
                self.direction_label.show()
                self.direction_combo.show()
        elif 'Volume' in type_name:
            self.multiplier_label.show()
            self.multiplier_spin.show()
        elif 'RSI' in type_name:
            self.threshold_label.setText("RSI Threshold:")
            self.threshold_input.setMinimum(0)
            self.threshold_input.setMaximum(100)
            self.threshold_label.show()
            self.threshold_input.show()
    
    def _create_condition(self):
        """Create condition from inputs"""
        symbol = self.symbol_input.text().upper()
        if not symbol:
            QMessageBox.warning(self, "Error", "Please enter symbol")
            return
        
        type_name = self.type_combo.currentText()
        type_map = {
            'Price Above': AlertConditionType.PRICE_ABOVE,
            'Price Below': AlertConditionType.PRICE_BELOW,
            'Price Change %': AlertConditionType.PRICE_CHANGE_PERCENT,
            'Volume Spike': AlertConditionType.VOLUME_SPIKE,
            'RSI Oversold': AlertConditionType.RSI_OVERSOLD,
            'RSI Overbought': AlertConditionType.RSI_OVERBOUGHT,
            'News Keyword': AlertConditionType.NEWS_KEYWORD,
        }
        
        condition_type = type_map.get(type_name, AlertConditionType.PRICE_ABOVE)
        
        parameters = {}
        if 'Price' in type_name:
            parameters['threshold'] = self.threshold_input.value()
            if '%' in type_name:
                direction_map = {'Up': 'up', 'Down': 'down', 'Either': 'either'}
                parameters['direction'] = direction_map[self.direction_combo.currentText()]
        elif 'Volume' in type_name:
            parameters['multiplier'] = self.multiplier_spin.value()
        elif 'RSI' in type_name:
            parameters['threshold'] = self.threshold_input.value()
        
        self.condition = AlertCondition(
            id=f"cond_{symbol}_{type_name}",
            type=condition_type,
            symbol=symbol,
            parameters=parameters,
            enabled=self.enabled_check.isChecked()
        )
        
        self.accept()


class CustomAlertsTab(QWidget):
    """Tab for custom alert engine"""
    
    def __init__(self):
        super().__init__()
        self.engine = CustomAlertEngine()
        self.worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Create tabs
        tabs = QTabWidget()
        
        # Tab 1: Create Alert Rules
        tabs.addTab(self._create_builder_tab(), "🛠️ Alert Builder")
        
        # Tab 2: Alert Rules List
        tabs.addTab(self._create_rules_tab(), "📋 Active Rules")
        
        # Tab 3: Alert History
        tabs.addTab(self._create_history_tab(), "📜 History")
        
        # Tab 4: Templates
        tabs.addTab(self._create_templates_tab(), "📦 Templates")
        
        # Tab 5: Statistics
        tabs.addTab(self._create_stats_tab(), "📊 Statistics")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def _create_builder_tab(self) -> QWidget:
        """Create alert builder tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🛠️ Build Custom Alert Rules"))
        
        # Template name and description
        config_group = QGroupBox("Alert Configuration")
        config_layout = QVBoxLayout()
        
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Name:"))
        self.alert_name_input = QLineEdit()
        self.alert_name_input.setPlaceholderText("e.g., 'Tech Stock Breakout'")
        row1.addWidget(self.alert_name_input)
        config_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Description:"))
        self.alert_desc_input = QLineEdit()
        self.alert_desc_input.setPlaceholderText("What does this alert do?")
        row2.addWidget(self.alert_desc_input)
        config_layout.addLayout(row2)
        
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Severity:"))
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(['Low', 'Medium', 'High', 'Critical'])
        row3.addWidget(self.severity_combo)
        config_layout.addLayout(row3)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Conditions
        conditions_group = QGroupBox("Alert Conditions")
        conditions_layout = QVBoxLayout()
        
        conditions_layout.addWidget(QLabel("Define conditions for this alert:"))
        
        self.conditions_list = QListWidget()
        conditions_layout.addWidget(self.conditions_list)
        
        cond_buttons = QHBoxLayout()
        
        add_cond_btn = QPushButton("➕ Add Condition")
        add_cond_btn.clicked.connect(self._add_condition)
        cond_buttons.addWidget(add_cond_btn)
        
        remove_cond_btn = QPushButton("➖ Remove Selected")
        remove_cond_btn.clicked.connect(self._remove_condition)
        cond_buttons.addWidget(remove_cond_btn)
        
        conditions_layout.addLayout(cond_buttons)
        
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Logic:"))
        self.logic_combo = QComboBox()
        self.logic_combo.addItems(['AND (All conditions)', 'OR (Any condition)'])
        row4.addWidget(self.logic_combo)
        conditions_layout.addLayout(row4)
        
        conditions_group.setLayout(conditions_layout)
        layout.addWidget(conditions_group)
        
        # Notifications
        notif_group = QGroupBox("Notification Channels")
        notif_layout = QVBoxLayout()
        
        self.email_check = QCheckBox("📧 Email")
        self.email_check.setChecked(True)
        notif_layout.addWidget(self.email_check)
        
        self.webhook_check = QCheckBox("🔗 Webhook")
        notif_layout.addWidget(self.webhook_check)
        
        self.push_check = QCheckBox("📱 Push Notification")
        notif_layout.addWidget(self.push_check)
        
        self.inapp_check = QCheckBox("💬 In-App")
        self.inapp_check.setChecked(True)
        notif_layout.addWidget(self.inapp_check)
        
        notif_group.setLayout(notif_layout)
        layout.addWidget(notif_group)
        
        # Create button
        create_template_btn = QPushButton("✅ Create Alert Template")
        create_template_btn.clicked.connect(self._create_template)
        layout.addWidget(create_template_btn)
        
        layout.addStretch()
        return widget
    
    def _create_rules_tab(self) -> QWidget:
        """Create active rules tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📋 Manage Active Alert Rules"))
        
        # Symbol filter
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Symbol:"))
        self.rules_symbol_input = QLineEdit()
        filter_row.addWidget(self.rules_symbol_input)
        
        filter_btn = QPushButton("🔍 Filter")
        filter_btn.clicked.connect(self._refresh_rules)
        filter_row.addWidget(filter_btn)
        filter_row.addStretch()
        
        layout.addLayout(filter_row)
        
        # Rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(7)
        self.rules_table.setHorizontalHeaderLabels([
            'Symbol', 'Alert Name', 'Severity', 'Status', 'Triggered',
            'Last Triggered', 'Actions'
        ])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.rules_table)
        
        # Activate rule
        apply_group = QGroupBox("Apply Template to Symbol")
        apply_layout = QVBoxLayout()
        
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Template:"))
        self.template_combo = QComboBox()
        row1.addWidget(self.template_combo)
        
        row1.addWidget(QLabel("Symbol:"))
        self.apply_symbol_input = QLineEdit()
        row1.addWidget(self.apply_symbol_input)
        
        apply_btn = QPushButton("✅ Apply Rule")
        apply_btn.clicked.connect(self._apply_rule)
        row1.addWidget(apply_btn)
        
        apply_layout.addLayout(row1)
        apply_group.setLayout(apply_layout)
        layout.addWidget(apply_group)
        
        return widget
    
    def _create_history_tab(self) -> QWidget:
        """Create alert history tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📜 Alert Trigger History"))
        
        # Filters
        filter_row = QHBoxLayout()
        
        filter_row.addWidget(QLabel("Symbol:"))
        self.history_symbol_input = QLineEdit()
        filter_row.addWidget(self.history_symbol_input)
        
        filter_row.addWidget(QLabel("Hours:"))
        self.history_hours_spin = QSpinBox()
        self.history_hours_spin.setValue(24)
        self.history_hours_spin.setMaximum(720)
        filter_row.addWidget(self.history_hours_spin)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_history)
        filter_row.addWidget(refresh_btn)
        filter_row.addStretch()
        
        layout.addLayout(filter_row)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            'Time', 'Symbol', 'Severity', 'Message', 'Values', 'Read'
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.history_table)
        
        # Details
        self.history_details_text = QTextEdit()
        self.history_details_text.setReadOnly(True)
        self.history_details_text.setMaximumHeight(150)
        layout.addWidget(self.history_details_text)
        
        return widget
    
    def _create_templates_tab(self) -> QWidget:
        """Create templates tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📦 Saved Alert Templates"))
        
        # Templates list
        self.templates_list = QListWidget()
        layout.addWidget(self.templates_list)
        
        # Template details
        self.template_details_text = QTextEdit()
        self.template_details_text.setReadOnly(True)
        self.template_details_text.setMaximumHeight(200)
        layout.addWidget(self.template_details_text)
        
        # Load templates
        load_btn = QPushButton("🔄 Load Templates")
        load_btn.clicked.connect(self._load_templates)
        layout.addWidget(load_btn)
        
        return widget
    
    def _create_stats_tab(self) -> QWidget:
        """Create statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📊 Alert Statistics & Monitoring"))
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("background-color: #f5f5f5;")
        layout.addWidget(self.stats_text)
        
        # Buttons
        button_row = QHBoxLayout()
        
        start_btn = QPushButton("▶️ Start Monitoring")
        start_btn.clicked.connect(self._start_monitoring)
        button_row.addWidget(start_btn)
        
        stop_btn = QPushButton("⏸️ Stop Monitoring")
        stop_btn.clicked.connect(self._stop_monitoring)
        button_row.addWidget(stop_btn)
        
        refresh_stats_btn = QPushButton("🔄 Refresh Stats")
        refresh_stats_btn.clicked.connect(self._refresh_stats)
        button_row.addWidget(refresh_stats_btn)
        
        layout.addLayout(button_row)
        
        self._refresh_stats()
        
        return widget
    
    def _add_condition(self):
        """Add condition to alert"""
        dialog = CreateConditionDialog(self)
        if dialog.exec() == QDialog.Accepted:
            condition = dialog.condition
            item = QListWidgetItem(
                f"{condition.symbol} - {condition.type.value.replace('_', ' ').title()}"
            )
            item.setData(Qt.UserRole, condition)
            self.conditions_list.addItem(item)
    
    def _remove_condition(self):
        """Remove selected condition"""
        current = self.conditions_list.currentRow()
        if current >= 0:
            self.conditions_list.takeItem(current)
    
    def _create_template(self):
        """Create alert template from configuration"""
        name = self.alert_name_input.text()
        description = self.alert_desc_input.text()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter alert name")
            return
        
        # Get conditions
        conditions = []
        for i in range(self.conditions_list.count()):
            item = self.conditions_list.item(i)
            condition = item.data(Qt.UserRole)
            conditions.append(condition)
        
        if not conditions:
            QMessageBox.warning(self, "Error", "Please add at least one condition")
            return
        
        # Get channels
        channels = []
        if self.email_check.isChecked():
            channels.append(NotificationChannel.EMAIL)
        if self.webhook_check.isChecked():
            channels.append(NotificationChannel.WEBHOOK)
        if self.push_check.isChecked():
            channels.append(NotificationChannel.PUSH)
        if self.inapp_check.isChecked():
            channels.append(NotificationChannel.IN_APP)
        
        severity_map = {'Low': AlertSeverity.LOW, 'Medium': AlertSeverity.MEDIUM,
                       'High': AlertSeverity.HIGH, 'Critical': AlertSeverity.CRITICAL}
        severity = severity_map[self.severity_combo.currentText()]
        
        logic = LogicOperator.AND if 'AND' in self.logic_combo.currentText() else LogicOperator.OR
        
        template = self.engine.create_alert_template(
            name=name,
            description=description,
            conditions=conditions,
            logic=logic,
            severity=severity,
            channels=channels
        )
        
        QMessageBox.information(self, "Success", f"✅ Template '{name}' created!")
        
        self.alert_name_input.clear()
        self.alert_desc_input.clear()
        self.conditions_list.clear()
        
        self._load_templates()
    
    def _apply_rule(self):
        """Apply template to symbol"""
        if self.template_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Error", "Please select a template")
            return
        
        symbol = self.apply_symbol_input.text().upper()
        if not symbol:
            QMessageBox.warning(self, "Error", "Please enter symbol")
            return
        
        templates = self.engine.get_alert_templates()
        if templates:
            template = templates[self.template_combo.currentIndex()]
            rule = self.engine.create_alert_rule(template, symbol)
            
            QMessageBox.information(self, "Success", f"✅ Rule created for {symbol}")
            self.apply_symbol_input.clear()
            self._refresh_rules()
    
    def _refresh_rules(self):
        """Refresh rules table"""
        symbol_filter = self.rules_symbol_input.text().upper()
        
        rules = self.engine.get_alert_rules(symbol_filter if symbol_filter else None)
        
        self.rules_table.setRowCount(0)
        for i, rule in enumerate(rules):
            self.rules_table.insertRow(i)
            
            self.rules_table.setItem(i, 0, QTableWidgetItem(rule.symbol))
            self.rules_table.setItem(i, 1, QTableWidgetItem(rule.template.name))
            self.rules_table.setItem(i, 2, QTableWidgetItem(rule.template.severity.value))
            
            status = "🟢 Active" if rule.enabled else "🔴 Inactive"
            self.rules_table.setItem(i, 3, QTableWidgetItem(status))
            
            self.rules_table.setItem(i, 4, QTableWidgetItem(str(rule.triggered_count)))
            
            last_triggered = rule.last_triggered.strftime('%Y-%m-%d %H:%M') if rule.last_triggered else "—"
            self.rules_table.setItem(i, 5, QTableWidgetItem(last_triggered))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.clicked.connect(lambda checked, rid=rule.id: self.engine.delete_rule(rid) or self._refresh_rules())
            self.rules_table.setCellWidget(i, 6, delete_btn)
    
    def _refresh_history(self):
        """Refresh alert history"""
        symbol_filter = self.history_symbol_input.text().upper()
        hours = self.history_hours_spin.value()
        
        events = self.engine.get_alert_history(symbol_filter if symbol_filter else None, hours)
        
        self.history_table.setRowCount(0)
        for i, event in enumerate(events):
            self.history_table.insertRow(i)
            
            time_str = event.triggered_at.strftime('%H:%M:%S')
            self.history_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.history_table.setItem(i, 1, QTableWidgetItem(event.symbol))
            
            severity_item = QTableWidgetItem(event.severity.value.upper())
            if event.severity == AlertSeverity.CRITICAL:
                severity_item.setForeground(QColor("red"))
            elif event.severity == AlertSeverity.HIGH:
                severity_item.setForeground(QColor("orange"))
            self.history_table.setItem(i, 2, severity_item)
            
            self.history_table.setItem(i, 3, QTableWidgetItem(event.message))
            self.history_table.setItem(i, 4, QTableWidgetItem(str(event.triggered_values)))
            
            read_status = "✓" if event.read else "—"
            self.history_table.setItem(i, 5, QTableWidgetItem(read_status))
    
    def _load_templates(self):
        """Load and display templates"""
        templates = self.engine.get_alert_templates()
        
        self.templates_list.clear()
        self.template_combo.clear()
        
        for template in templates:
            item = QListWidgetItem(f"{template.name} - {template.severity.value}")
            item.setData(Qt.UserRole, template.id)
            self.templates_list.addItem(item)
            self.template_combo.addItem(template.name)
    
    def _refresh_stats(self):
        """Refresh statistics display"""
        stats = self.engine.get_statistics()
        
        text = f"""
ALERT ENGINE STATISTICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Active Rules:          {stats['active_rules']}
Total Alert Events:    {stats['total_events']}
Unread Alerts:         {stats['unread_count']}
Triggered Today:       {stats['triggered_today']}

SEVERITY DISTRIBUTION:
  🟢 Low:              {stats['severity_distribution']['low']}
  🟡 Medium:           {stats['severity_distribution']['medium']}
  🟠 High:             {stats['severity_distribution']['high']}
  🔴 Critical:         {stats['severity_distribution']['critical']}

MONITORING STATUS:     {'▶️ Running' if self.engine.is_running else '⏸️ Stopped'}
"""
        
        self.stats_text.setText(text)
    
    def _start_monitoring(self):
        """Start alert monitoring"""
        self.engine.start_monitoring(check_interval=60)
        QMessageBox.information(self, "Monitoring", "✅ Alert monitoring started")
        self._refresh_stats()
    
    def _stop_monitoring(self):
        """Stop alert monitoring"""
        self.engine.stop_monitoring()
        QMessageBox.information(self, "Monitoring", "⏸️ Alert monitoring stopped")
        self._refresh_stats()
