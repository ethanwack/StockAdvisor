"""
Broker Integration GUI Tab
Interface for connecting to brokers and executing trades
"""

from datetime import datetime
from typing import Optional, Dict, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QSpinBox, QDoubleSpinBox,
    QGroupBox, QTabWidget, QMessageBox, QProgressBar, QCheckBox, QDialog,
    QFormLayout, QTextEdit
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QColor, QFont

from services.broker_integration import (
    BrokerManager, AlpacaBroker, TDAmeritradeBroker, OrderSide, OrderType,
    OrderStatus, PositionSide, Account, Position, Order
)


class BrokerWorker(QThread):
    """Worker thread for broker operations"""
    
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, operation, manager, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.manager = manager
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            if self.operation == "account":
                result = self.manager.get_account()
            elif self.operation == "positions":
                result = self.manager.get_positions()
            elif self.operation == "orders":
                result = self.manager.get_orders()
            elif self.operation == "place_order":
                result = self.manager.place_order(*self.args, **self.kwargs)
            else:
                result = None
            
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class BrokerConnectionDialog(QDialog):
    """Dialog for connecting to a broker"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to Broker")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QFormLayout()
        
        # Broker selection
        self.broker_combo = QComboBox()
        self.broker_combo.addItems(["Alpaca", "TD Ameritrade"])
        layout.addRow("Broker:", self.broker_combo)
        
        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter API key")
        layout.addRow("API Key:", self.api_key_input)
        
        # Secret Key
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText("Enter secret key")
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Secret Key:", self.secret_key_input)
        
        # Connection name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Primary Account")
        layout.addRow("Connection Name:", self.name_input)
        
        # Sandbox toggle
        self.sandbox_check = QCheckBox("Use Paper Trading (Sandbox)")
        self.sandbox_check.setChecked(True)
        layout.addRow("", self.sandbox_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.accept)
        button_layout.addWidget(connect_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
    
    def get_connection_data(self) -> Dict:
        """Get connection data"""
        return {
            'broker': self.broker_combo.currentText(),
            'api_key': self.api_key_input.text(),
            'secret_key': self.secret_key_input.text(),
            'name': self.name_input.text() or self.broker_combo.currentText(),
            'sandbox': self.sandbox_check.isChecked()
        }


class BrokerTab(QWidget):
    """Main Broker Integration Tab"""
    
    def __init__(self, db=None, cache=None):
        super().__init__()
        self.db = db
        self.cache = cache
        self.manager = BrokerManager()
        self.broker_worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_connections_tab(), "🔌 Connections")
        tabs.addTab(self._create_account_tab(), "💼 Account")
        tabs.addTab(self._create_positions_tab(), "📊 Positions")
        tabs.addTab(self._create_orders_tab(), "📋 Orders")
        tabs.addTab(self._create_trading_tab(), "💹 Trade")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def _create_connections_tab(self) -> QWidget:
        """Create broker connections tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Connection controls
        control_group = QGroupBox("Broker Connections")
        control_layout = QHBoxLayout()
        
        connect_btn = QPushButton("➕ Add Broker")
        connect_btn.clicked.connect(self._add_broker_connection)
        connect_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        control_layout.addWidget(connect_btn)
        
        disconnect_btn = QPushButton("❌ Disconnect")
        disconnect_btn.clicked.connect(self._disconnect_broker)
        disconnect_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        control_layout.addWidget(disconnect_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_connections)
        control_layout.addWidget(refresh_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Connections list
        list_group = QGroupBox("Connected Brokers")
        list_layout = QVBoxLayout()
        
        self.connections_table = QTableWidget()
        self.connections_table.setColumnCount(4)
        self.connections_table.setHorizontalHeaderLabels([
            "Broker", "Status", "Active", "Type"
        ])
        self.connections_table.setMaximumHeight(200)
        
        list_layout.addWidget(self.connections_table)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Connection info
        info_group = QGroupBox("Connection Details")
        info_layout = QVBoxLayout()
        
        self.connection_info_text = QTextEdit()
        self.connection_info_text.setReadOnly(True)
        self.connection_info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }
        """)
        
        info_layout.addWidget(self.connection_info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        widget.setLayout(layout)
        return widget
    
    def _create_account_tab(self) -> QWidget:
        """Create account information tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Account Info")
        refresh_btn.clicked.connect(self._refresh_account)
        refresh_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(refresh_btn)
        
        # Account metrics
        metrics_group = QGroupBox("Account Summary")
        metrics_layout = QFormLayout()
        
        self.account_id = QLabel("-")
        self.account_type = QLabel("-")
        self.cash = QLabel("-")
        self.buying_power = QLabel("-")
        self.portfolio_value = QLabel("-")
        self.total_value = QLabel("-")
        self.equity = QLabel("-")
        self.return_pct = QLabel("-")
        
        metrics_layout.addRow("Account ID:", self.account_id)
        metrics_layout.addRow("Account Type:", self.account_type)
        metrics_layout.addRow("Cash Available:", self.cash)
        metrics_layout.addRow("Buying Power:", self.buying_power)
        metrics_layout.addRow("Portfolio Value:", self.portfolio_value)
        metrics_layout.addRow("Total Value:", self.total_value)
        metrics_layout.addRow("Equity:", self.equity)
        metrics_layout.addRow("Return %:", self.return_pct)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_positions_tab(self) -> QWidget:
        """Create positions tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Positions")
        refresh_btn.clicked.connect(self._refresh_positions)
        refresh_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(refresh_btn)
        
        # Positions table
        positions_group = QGroupBox("Open Positions")
        positions_layout = QVBoxLayout()
        
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(8)
        self.positions_table.setHorizontalHeaderLabels([
            "Symbol", "Side", "Quantity", "Entry Price", "Current Price",
            "Market Value", "Gain/Loss", "Return %"
        ])
        
        positions_layout.addWidget(self.positions_table)
        positions_group.setLayout(positions_layout)
        layout.addWidget(positions_group)
        
        widget.setLayout(layout)
        return widget
    
    def _create_orders_tab(self) -> QWidget:
        """Create orders tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Orders")
        refresh_btn.clicked.connect(self._refresh_orders)
        refresh_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(refresh_btn)
        
        # Orders table
        orders_group = QGroupBox("Orders")
        orders_layout = QVBoxLayout()
        
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(9)
        self.orders_table.setHorizontalHeaderLabels([
            "Order ID", "Symbol", "Type", "Side", "Quantity", "Price",
            "Status", "Created", "Filled"
        ])
        
        orders_layout.addWidget(self.orders_table)
        orders_group.setLayout(orders_layout)
        layout.addWidget(orders_group)
        
        # Cancel order button
        cancel_btn = QPushButton("❌ Cancel Selected Order")
        cancel_btn.clicked.connect(self._cancel_selected_order)
        cancel_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(cancel_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _create_trading_tab(self) -> QWidget:
        """Create trading/order placement tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Order input section
        order_group = QGroupBox("Place Order")
        order_layout = QFormLayout()
        
        # Symbol
        self.trade_symbol = QLineEdit()
        self.trade_symbol.setPlaceholderText("e.g., AAPL")
        self.trade_symbol.setText("AAPL")
        order_layout.addRow("Symbol:", self.trade_symbol)
        
        # Side
        self.trade_side = QComboBox()
        self.trade_side.addItems(["BUY", "SELL"])
        order_layout.addRow("Side:", self.trade_side)
        
        # Quantity
        self.trade_quantity = QSpinBox()
        self.trade_quantity.setRange(1, 10000)
        self.trade_quantity.setValue(100)
        order_layout.addRow("Quantity:", self.trade_quantity)
        
        # Order type
        self.trade_order_type = QComboBox()
        self.trade_order_type.addItems(["MARKET", "LIMIT", "STOP", "STOP_LIMIT"])
        self.trade_order_type.currentTextChanged.connect(self._on_order_type_changed)
        order_layout.addRow("Order Type:", self.trade_order_type)
        
        # Limit price
        self.trade_limit_price = QDoubleSpinBox()
        self.trade_limit_price.setRange(0.01, 10000.0)
        self.trade_limit_price.setSingleStep(0.01)
        self.trade_limit_price.setVisible(False)
        order_layout.addRow("Limit Price:", self.trade_limit_price)
        
        # Stop price
        self.trade_stop_price = QDoubleSpinBox()
        self.trade_stop_price.setRange(0.01, 10000.0)
        self.trade_stop_price.setSingleStep(0.01)
        self.trade_stop_price.setVisible(False)
        order_layout.addRow("Stop Price:", self.trade_stop_price)
        
        order_group.setLayout(order_layout)
        layout.addWidget(order_group)
        
        # Place order button
        place_btn = QPushButton("💹 Place Order")
        place_btn.clicked.connect(self._place_order)
        place_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(place_btn)
        
        # Order confirmation
        self.order_confirm_text = QTextEdit()
        self.order_confirm_text.setReadOnly(True)
        self.order_confirm_text.setMaximumHeight(150)
        self.order_confirm_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.order_confirm_text)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _add_broker_connection(self):
        """Add a new broker connection"""
        dialog = BrokerConnectionDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_connection_data()
            
            try:
                if data['broker'] == "Alpaca":
                    broker = AlpacaBroker(
                        api_key=data['api_key'],
                        secret_key=data['secret_key'],
                        sandbox=data['sandbox']
                    )
                elif data['broker'] == "TD Ameritrade":
                    broker = TDAmeritradeBroker(
                        api_key=data['api_key'],
                        secret_key=data['secret_key'],
                        sandbox=data['sandbox']
                    )
                else:
                    QMessageBox.warning(self, "Error", "Unknown broker")
                    return
                
                if self.manager.add_broker(data['name'], broker):
                    QMessageBox.information(self, "Success", f"Connected to {data['broker']}")
                    self._refresh_connections()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to connect to {data['broker']}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Connection failed: {str(e)}")
    
    def _disconnect_broker(self):
        """Disconnect from broker"""
        brokers = self.manager.list_brokers()
        
        if not brokers:
            QMessageBox.information(self, "Info", "No brokers connected")
            return
        
        if len(brokers) == 1:
            broker = brokers[0]
        else:
            # TODO: Show selection dialog
            broker = brokers[0]
        
        if self.manager.remove_broker(broker):
            QMessageBox.information(self, "Success", f"Disconnected from {broker}")
            self._refresh_connections()
    
    def _refresh_connections(self):
        """Refresh connections list"""
        info = self.manager.get_broker_info()
        
        self.connections_table.setRowCount(len(info))
        
        for row, (name, data) in enumerate(info.items()):
            self.connections_table.setItem(row, 0, QTableWidgetItem(data['broker']))
            
            status = "🟢 Connected" if data['connected'] else "🔴 Disconnected"
            self.connections_table.setItem(row, 1, QTableWidgetItem(status))
            
            active = "✓ Active" if data['active'] else ""
            self.connections_table.setItem(row, 2, QTableWidgetItem(active))
            
            self.connections_table.setItem(row, 3, QTableWidgetItem(name))
        
        # Update connection info
        info_text = "Connected Brokers:\n\n"
        for name, data in info.items():
            info_text += f"• {name} ({data['broker']})\n"
            info_text += f"  Status: {'Connected' if data['connected'] else 'Disconnected'}\n"
            info_text += f"  Active: {'Yes' if data['active'] else 'No'}\n\n"
        
        self.connection_info_text.setText(info_text)
    
    def _refresh_account(self):
        """Refresh account information"""
        account = self.manager.get_account()
        
        if account:
            self.account_id.setText(account.account_id)
            self.account_type.setText(account.account_type)
            self.cash.setText(f"${account.cash:,.2f}")
            self.buying_power.setText(f"${account.buying_power:,.2f}")
            self.portfolio_value.setText(f"${account.portfolio_value:,.2f}")
            self.total_value.setText(f"${account.total_value:,.2f}")
            self.equity.setText(f"${account.equity:,.2f}")
            self.return_pct.setText(f"{account.portfolio_return_pct:.2f}%")
            
            # Color code return
            if account.portfolio_return_pct >= 0:
                self.return_pct.setStyleSheet("color: #4CAF50;")
            else:
                self.return_pct.setStyleSheet("color: #f44336;")
        else:
            QMessageBox.warning(self, "Error", "No broker connected")
    
    def _refresh_positions(self):
        """Refresh positions"""
        positions = self.manager.get_positions()
        
        self.positions_table.setRowCount(len(positions))
        
        for row, pos in enumerate(positions):
            self.positions_table.setItem(row, 0, QTableWidgetItem(pos.symbol))
            self.positions_table.setItem(row, 1, QTableWidgetItem(pos.side.value.upper()))
            self.positions_table.setItem(row, 2, QTableWidgetItem(f"{pos.quantity:.0f}"))
            self.positions_table.setItem(row, 3, QTableWidgetItem(f"${pos.entry_price:.2f}"))
            self.positions_table.setItem(row, 4, QTableWidgetItem(f"${pos.current_price:.2f}"))
            self.positions_table.setItem(row, 5, QTableWidgetItem(f"${pos.market_value:,.2f}"))
            
            pl_item = QTableWidgetItem(f"${pos.unrealized_gain_loss:,.2f}")
            if pos.unrealized_gain_loss > 0:
                pl_item.setForeground(QColor("#4CAF50"))
            elif pos.unrealized_gain_loss < 0:
                pl_item.setForeground(QColor("#f44336"))
            self.positions_table.setItem(row, 6, pl_item)
            
            ret_item = QTableWidgetItem(f"{pos.unrealized_gain_loss_pct:.2f}%")
            if pos.unrealized_gain_loss_pct > 0:
                ret_item.setForeground(QColor("#4CAF50"))
            elif pos.unrealized_gain_loss_pct < 0:
                ret_item.setForeground(QColor("#f44336"))
            self.positions_table.setItem(row, 7, ret_item)
    
    def _refresh_orders(self):
        """Refresh orders"""
        orders = self.manager.get_orders()
        
        self.orders_table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            self.orders_table.setItem(row, 0, QTableWidgetItem(order.order_id))
            self.orders_table.setItem(row, 1, QTableWidgetItem(order.symbol))
            self.orders_table.setItem(row, 2, QTableWidgetItem(order.order_type.value))
            self.orders_table.setItem(row, 3, QTableWidgetItem(order.side.value.upper()))
            self.orders_table.setItem(row, 4, QTableWidgetItem(f"{order.quantity:.0f}"))
            
            price_str = f"${order.price:.2f}" if order.price else "-"
            self.orders_table.setItem(row, 5, QTableWidgetItem(price_str))
            
            self.orders_table.setItem(row, 6, QTableWidgetItem(order.status.value))
            self.orders_table.setItem(row, 7, QTableWidgetItem(
                order.created_at.strftime("%Y-%m-%d %H:%M") if isinstance(order.created_at, datetime) else str(order.created_at)
            ))
            
            filled_str = f"{order.filled_quantity:.0f} @ ${order.average_fill_price:.2f}" if order.filled_quantity > 0 else "-"
            self.orders_table.setItem(row, 8, QTableWidgetItem(filled_str))
    
    def _cancel_selected_order(self):
        """Cancel selected order"""
        selected_row = self.orders_table.currentRow()
        
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select an order to cancel")
            return
        
        order_id = self.orders_table.item(selected_row, 0).text()
        
        if self.manager.cancel_order(order_id):
            QMessageBox.information(self, "Success", f"Order {order_id} cancelled")
            self._refresh_orders()
        else:
            QMessageBox.critical(self, "Error", "Failed to cancel order")
    
    def _on_order_type_changed(self):
        """Handle order type change"""
        order_type = self.trade_order_type.currentText()
        
        self.trade_limit_price.setVisible(order_type in ["LIMIT", "STOP_LIMIT"])
        self.trade_stop_price.setVisible(order_type in ["STOP", "STOP_LIMIT"])
    
    def _place_order(self):
        """Place an order"""
        symbol = self.trade_symbol.text().upper()
        side = OrderSide.BUY if self.trade_side.currentText() == "BUY" else OrderSide.SELL
        quantity = self.trade_quantity.value()
        order_type_str = self.trade_order_type.currentText()
        
        if not symbol:
            QMessageBox.warning(self, "Error", "Please enter a symbol")
            return
        
        try:
            order_type = OrderType[order_type_str.upper().replace("_", "")]
        except KeyError:
            QMessageBox.warning(self, "Error", "Invalid order type")
            return
        
        limit_price = self.trade_limit_price.value() if self.trade_limit_price.isVisible() else None
        stop_price = self.trade_stop_price.value() if self.trade_stop_price.isVisible() else None
        
        # Confirmation
        confirm_text = f"""
ORDER CONFIRMATION:

Symbol:       {symbol}
Side:         {side.value.upper()}
Quantity:     {quantity}
Order Type:   {order_type.value}
"""
        
        if limit_price:
            confirm_text += f"Limit Price:  ${limit_price:.2f}\n"
        if stop_price:
            confirm_text += f"Stop Price:   ${stop_price:.2f}\n"
        
        self.order_confirm_text.setText(confirm_text)
        
        # Place order
        try:
            order = self.manager.place_order(
                symbol=symbol,
                quantity=quantity,
                side=side,
                order_type=order_type,
                limit_price=limit_price,
                stop_price=stop_price
            )
            
            if order:
                QMessageBox.information(
                    self, "Success",
                    f"Order placed!\nOrder ID: {order.order_id}\nStatus: {order.status.value}"
                )
                self._refresh_orders()
            else:
                QMessageBox.critical(self, "Error", "Failed to place order")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Order placement failed: {str(e)}")
