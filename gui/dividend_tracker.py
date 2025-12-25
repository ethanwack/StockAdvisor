"""
Dividend Tracker Tab GUI
Dividend calendar, yield tracking, ex-date reminders, dividend reinvestment calculator
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QDoubleSpinBox, QComboBox,
    QMessageBox, QGroupBox, QTextEdit, QHeaderView, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal, QDate
from PySide6.QtGui import QColor, QFont
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from services.dividend_tracker import (
    DividendTracker, DividendFrequency, DividendReinvestmentCalculator
)


class DividendWorker(QThread):
    """Worker thread for dividend tracking"""
    
    dividend_data_ready = Signal(dict)
    error_occurred = Signal(str)
    progress = Signal(int)
    
    def __init__(self, tracker: DividendTracker):
        super().__init__()
        self.tracker = tracker
        self.task = None
        self.params = {}
    
    def set_add_stock(self, symbol: str):
        """Set task to add stock"""
        self.task = 'add_stock'
        self.params = {'symbol': symbol}
    
    def set_get_summary(self):
        """Set task to get summary"""
        self.task = 'summary'
    
    def run(self):
        try:
            if self.task == 'add_stock':
                history = self.tracker.add_stock(self.params['symbol'])
                self.dividend_data_ready.emit({'symbol': self.params['symbol'], 'history': history})
            elif self.task == 'summary':
                summary = self.tracker.get_summary()
                self.dividend_data_ready.emit(summary)
        except Exception as e:
            self.error_occurred.emit(str(e))


class DividendTrackerTab(QWidget):
    """Tab for dividend tracking and management"""
    
    def __init__(self):
        super().__init__()
        self.tracker = DividendTracker()
        self.worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Create tabs
        tabs = QTabWidget()
        
        # Tab 1: Dividend Calendar
        tabs.addTab(self._create_calendar_tab(), "📅 Dividend Calendar")
        
        # Tab 2: Yield Tracking
        tabs.addTab(self._create_yield_tab(), "📊 Yield Tracking")
        
        # Tab 3: DRIP Calculator
        tabs.addTab(self._create_drip_calculator_tab(), "🧮 DRIP Calculator")
        
        # Tab 4: Portfolio Dividend Plan
        tabs.addTab(self._create_portfolio_plan_tab(), "💰 Portfolio Plan")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def _create_calendar_tab(self) -> QWidget:
        """Create dividend calendar tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📅 Dividend Calendar - Upcoming Ex-Dates"))
        
        # Add stock to track
        add_group = QGroupBox("Add Stock to Track")
        add_layout = QHBoxLayout()
        
        add_layout.addWidget(QLabel("Symbol:"))
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("e.g., JNJ")
        add_layout.addWidget(self.symbol_input)
        
        add_btn = QPushButton("➕ Add")
        add_btn.clicked.connect(self._add_stock)
        add_layout.addWidget(add_btn)
        
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)
        
        # Calendar view
        self.calendar_table = QTableWidget()
        self.calendar_table.setColumnCount(7)
        self.calendar_table.setHorizontalHeaderLabels([
            'Symbol', 'Ex-Date', 'Record Date', 'Payment Date',
            'Dividend/Share', 'Yield %', 'Days Until'
        ])
        self.calendar_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.calendar_table)
        
        # Upcoming dividends list
        layout.addWidget(QLabel("📌 Upcoming Ex-Dates (Next 30 Days)"))
        self.upcoming_list = QListWidget()
        layout.addWidget(self.upcoming_list)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Calendar")
        refresh_btn.clicked.connect(self._refresh_calendar)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _create_yield_tab(self) -> QWidget:
        """Create yield tracking tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📊 Dividend Yield Tracking"))
        
        # Summary statistics
        stats_group = QGroupBox("Summary Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        self.stats_text.setStyleSheet("background-color: #f5f5f5;")
        stats_layout.addWidget(self.stats_text)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Tracked stocks and yields
        layout.addWidget(QLabel("Individual Stock Yields"))
        self.yield_table = QTableWidget()
        self.yield_table.setColumnCount(8)
        self.yield_table.setHorizontalHeaderLabels([
            'Symbol', 'Company', 'Yield %', 'Annual Dividend',
            'Frequency', 'Last Payment', 'Next Payment', 'Dividend Growth %'
        ])
        self.yield_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.yield_table)
        
        # Update yields button
        update_btn = QPushButton("📈 Update Yields")
        update_btn.clicked.connect(self._update_yields)
        layout.addWidget(update_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _create_drip_calculator_tab(self) -> QWidget:
        """Create DRIP calculator tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🧮 Dividend Reinvestment (DRIP) Calculator"))
        
        # Input parameters
        params_group = QGroupBox("DRIP Parameters")
        params_layout = QVBoxLayout()
        
        # Row 1
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Initial Shares:"))
        self.drip_shares_spin = QSpinBox()
        self.drip_shares_spin.setMinimum(1)
        self.drip_shares_spin.setMaximum(100000)
        self.drip_shares_spin.setValue(100)
        row1.addWidget(self.drip_shares_spin)
        
        row1.addWidget(QLabel("Current Stock Price:"))
        self.drip_price_spin = QDoubleSpinBox()
        self.drip_price_spin.setMinimum(0.01)
        self.drip_price_spin.setMaximum(10000)
        self.drip_price_spin.setValue(100)
        row1.addWidget(self.drip_price_spin)
        params_layout.addLayout(row1)
        
        # Row 2
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Annual Dividend/Share:"))
        self.drip_div_spin = QDoubleSpinBox()
        self.drip_div_spin.setMinimum(0)
        self.drip_div_spin.setMaximum(1000)
        self.drip_div_spin.setValue(2.0)
        row2.addWidget(self.drip_div_spin)
        
        row2.addWidget(QLabel("Frequency:"))
        self.drip_freq_combo = QComboBox()
        self.drip_freq_combo.addItems(['Monthly', 'Quarterly', 'Semi-Annual', 'Annual'])
        self.drip_freq_combo.setCurrentIndex(1)  # Quarterly
        row2.addWidget(self.drip_freq_combo)
        params_layout.addLayout(row2)
        
        # Row 3
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Time Period (Years):"))
        self.drip_years_spin = QSpinBox()
        self.drip_years_spin.setMinimum(1)
        self.drip_years_spin.setMaximum(50)
        self.drip_years_spin.setValue(10)
        row3.addWidget(self.drip_years_spin)
        
        row3.addWidget(QLabel("Annual Growth Rate (%):"))
        self.drip_growth_spin = QDoubleSpinBox()
        self.drip_growth_spin.setMinimum(0)
        self.drip_growth_spin.setMaximum(50)
        self.drip_growth_spin.setValue(5.0)
        row3.addWidget(self.drip_growth_spin)
        row3.addStretch()
        params_layout.addLayout(row3)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Calculate button
        calc_btn = QPushButton("🧮 Calculate DRIP")
        calc_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        calc_btn.clicked.connect(self._calculate_drip)
        layout.addWidget(calc_btn)
        
        # Results
        self.drip_results_text = QTextEdit()
        self.drip_results_text.setReadOnly(True)
        self.drip_results_text.setStyleSheet("background-color: #f5f5f5;")
        layout.addWidget(self.drip_results_text)
        
        # Comparison table
        self.drip_table = QTableWidget()
        self.drip_table.setColumnCount(6)
        self.drip_table.setHorizontalHeaderLabels([
            'Year', 'Shares', 'Stock Price', 'Dividends Paid',
            'Reinvested Shares', 'Portfolio Value'
        ])
        self.drip_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.drip_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_portfolio_plan_tab(self) -> QWidget:
        """Create portfolio dividend plan tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("💰 Portfolio Dividend Income Plan"))
        
        # Portfolio composition
        portfolio_group = QGroupBox("Your Portfolio")
        portfolio_layout = QVBoxLayout()
        
        # Add holding
        add_holding_layout = QHBoxLayout()
        add_holding_layout.addWidget(QLabel("Symbol:"))
        self.port_symbol_input = QLineEdit()
        add_holding_layout.addWidget(self.port_symbol_input)
        
        add_holding_layout.addWidget(QLabel("Shares:"))
        self.port_shares_spin = QSpinBox()
        self.port_shares_spin.setMinimum(1)
        self.port_shares_spin.setMaximum(100000)
        add_holding_layout.addWidget(self.port_shares_spin)
        
        add_holding_btn = QPushButton("➕ Add Holding")
        add_holding_btn.clicked.connect(self._add_holding)
        add_holding_layout.addWidget(add_holding_btn)
        portfolio_layout.addLayout(add_holding_layout)
        
        # Holdings table
        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(6)
        self.holdings_table.setHorizontalHeaderLabels([
            'Symbol', 'Shares', 'Annual Dividend', 'Quarterly Dividend',
            'Yield %', 'Est. Annual Income'
        ])
        self.holdings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        portfolio_layout.addWidget(self.holdings_table)
        
        portfolio_group.setLayout(portfolio_layout)
        layout.addWidget(portfolio_group)
        
        # Income projection
        income_group = QGroupBox("Projected Dividend Income")
        income_layout = QVBoxLayout()
        
        self.income_text = QTextEdit()
        self.income_text.setReadOnly(True)
        self.income_text.setStyleSheet("background-color: #f5f5f5;")
        income_layout.addWidget(self.income_text)
        
        income_group.setLayout(income_layout)
        layout.addWidget(income_group)
        
        # Calculate button
        calc_income_btn = QPushButton("💵 Calculate Income Projection")
        calc_income_btn.clicked.connect(self._calculate_income_projection)
        layout.addWidget(calc_income_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _add_stock(self):
        """Add stock to dividend tracker"""
        symbol = self.symbol_input.text().upper()
        
        if not symbol:
            QMessageBox.warning(self, "Error", "Please enter a stock symbol")
            return
        
        self.worker = DividendWorker(self.tracker)
        self.worker.set_add_stock(symbol)
        self.worker.dividend_data_ready.connect(self._on_stock_added)
        self.worker.error_occurred.connect(lambda e: QMessageBox.critical(self, "Error", str(e)))
        self.worker.start()
        
        self.symbol_input.clear()
    
    def _on_stock_added(self, data: dict):
        """Handle stock added"""
        symbol = data['symbol']
        history = data['history']
        
        if history.current_yield > 0:
            QMessageBox.information(
                self, "Success",
                f"✅ {symbol} added!\n\nYield: {history.current_yield*100:.2f}%\nAnnual Dividend: ${history.annual_dividend:.2f}"
            )
        else:
            QMessageBox.information(self, "Success", f"✅ {symbol} added to tracker!")
        
        self._refresh_calendar()
    
    def _refresh_calendar(self):
        """Refresh dividend calendar"""
        self.calendar_table.setRowCount(0)
        
        upcoming = self.tracker.get_upcoming_dividends(30)
        self.upcoming_list.clear()
        
        for i, payment in enumerate(upcoming):
            self.calendar_table.insertRow(i)
            
            # Symbol
            symbol_item = QTableWidgetItem(payment.symbol)
            symbol_item.setForeground(QColor("#2196F3"))
            self.calendar_table.setItem(i, 0, symbol_item)
            
            # Dates
            self.calendar_table.setItem(i, 1, QTableWidgetItem(payment.ex_date.strftime("%Y-%m-%d")))
            self.calendar_table.setItem(i, 2, QTableWidgetItem(payment.record_date.strftime("%Y-%m-%d")))
            self.calendar_table.setItem(i, 3, QTableWidgetItem(payment.payment_date.strftime("%Y-%m-%d")))
            
            # Amount
            self.calendar_table.setItem(i, 4, QTableWidgetItem(f"${payment.amount:.2f}"))
            
            # Yield
            yield_str = f"{payment.yield_percent*100:.2f}%" if payment.yield_percent else "N/A"
            self.calendar_table.setItem(i, 5, QTableWidgetItem(yield_str))
            
            # Days until
            days = payment.days_until_ex_date()
            days_item = QTableWidgetItem(str(days))
            if days < 7:
                days_item.setForeground(QColor("#f44336"))
            elif days < 14:
                days_item.setForeground(QColor("#FF9800"))
            self.calendar_table.setItem(i, 6, days_item)
            
            # Add to upcoming list
            list_item = QListWidgetItem(
                f"${payment.symbol}: ${payment.amount:.2f} - Ex: {payment.ex_date.strftime('%Y-%m-%d')} ({days} days)"
            )
            self.upcoming_list.addItem(list_item)
    
    def _update_yields(self):
        """Update dividend yields"""
        self.yield_table.setRowCount(0)
        
        for i, (symbol, history) in enumerate(self.tracker.tracked_stocks.items()):
            self.yield_table.insertRow(i)
            
            # Symbol
            symbol_item = QTableWidgetItem(symbol)
            symbol_item.setForeground(QColor("#2196F3"))
            self.yield_table.setItem(i, 0, symbol_item)
            
            # Company name
            self.yield_table.setItem(i, 1, QTableWidgetItem(history.company_name or "—"))
            
            # Yield
            yield_item = QTableWidgetItem(f"{history.current_yield*100:.2f}%")
            if history.current_yield > 0.04:
                yield_item.setForeground(QColor("#4CAF50"))
            self.yield_table.setItem(i, 2, yield_item)
            
            # Annual dividend
            self.yield_table.setItem(i, 3, QTableWidgetItem(f"${history.annual_dividend:.2f}"))
            
            # Frequency
            freq_name = history.payout_frequency.value.capitalize()
            self.yield_table.setItem(i, 4, QTableWidgetItem(freq_name))
            
            # Last payment
            last_payment = history.last_payment_date.strftime("%Y-%m-%d") if history.last_payment_date else "N/A"
            self.yield_table.setItem(i, 5, QTableWidgetItem(last_payment))
            
            # Next payment
            next_payment = history.next_payment_date.strftime("%Y-%m-%d") if history.next_payment_date else "N/A"
            self.yield_table.setItem(i, 6, QTableWidgetItem(next_payment))
            
            # Dividend growth
            growth = history.get_dividend_growth(5)
            growth_item = QTableWidgetItem(f"{growth:.2f}%")
            if growth > 5:
                growth_item.setForeground(QColor("#4CAF50"))
            self.yield_table.setItem(i, 7, growth_item)
        
        # Update stats
        summary = self.tracker.get_summary()
        stats_text = f"""
PORTFOLIO DIVIDEND SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stocks Tracked:          {summary['tracked_stocks']}
Total Annual Dividend:   ${summary['total_annual_dividend']:.2f}
Average Yield:           {summary['average_yield']:.2f}%
Upcoming Dividends:      {summary['upcoming_dividends_30_days']} in next 30 days
Next Payment Date:       {summary['next_payment'].strftime("%Y-%m-%d") if summary['next_payment'] else "N/A"}
"""
        self.stats_text.setText(stats_text)
    
    def _calculate_drip(self):
        """Calculate DRIP results"""
        # Get frequency enum
        freq_map = {
            'Monthly': DividendFrequency.MONTHLY,
            'Quarterly': DividendFrequency.QUARTERLY,
            'Semi-Annual': DividendFrequency.SEMI_ANNUAL,
            'Annual': DividendFrequency.ANNUAL
        }
        frequency = freq_map[self.drip_freq_combo.currentText()]
        
        # Calculate DRIP
        result = DividendReinvestmentCalculator.calculate_drip(
            initial_shares=self.drip_shares_spin.value(),
            annual_dividend_per_share=self.drip_div_spin.value(),
            dividend_frequency=frequency,
            years=self.drip_years_spin.value(),
            annual_growth_rate=self.drip_growth_spin.value() / 100,
            stock_price=self.drip_price_spin.value()
        )
        
        # Compare DRIP vs no DRIP
        comparison = DividendReinvestmentCalculator.compare_drip_vs_no_drip(
            initial_shares=self.drip_shares_spin.value(),
            annual_dividend_per_share=self.drip_div_spin.value(),
            dividend_frequency=frequency,
            years=self.drip_years_spin.value(),
            annual_growth_rate=self.drip_growth_spin.value() / 100,
            stock_price=self.drip_price_spin.value()
        )
        
        # Display results
        results_text = f"""
DRIP vs NO DRIP COMPARISON (10 YEARS):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WITH DRIP (Reinvest Dividends):
• Initial Investment:      ${comparison['with_drip']['initial_investment']:,.2f}
• Final Portfolio Value:   ${comparison['with_drip']['final_value']:,.2f}
• Shares Held:             {comparison['with_drip']['final_shares']:.2f}
• Total Return:            {comparison['with_drip']['total_return_percent']:.2f}%
• Total Gain:              ${comparison['with_drip']['total_gain']:,.2f}

WITHOUT DRIP (Take Dividends as Cash):
• Initial Investment:      ${comparison['without_drip']['initial_investment']:,.2f}
• Final Portfolio Value:   ${comparison['without_drip']['final_value']:,.2f}
• Cash Dividends Received: ${comparison['without_drip']['cash_dividends']:,.2f}
• Total Return:            {comparison['without_drip']['total_return_percent']:.2f}%
• Total Gain:              ${comparison['without_drip']['total_gain']:,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DRIP ADVANTAGE:            ${comparison['drip_advantage']:,.2f}
BETTER OPTION:             {comparison['better_option']} ✓
"""
        
        self.drip_results_text.setText(results_text)
        
        # Display history table
        self.drip_table.setRowCount(0)
        
        for i, year_data in enumerate(result['history']):
            self.drip_table.insertRow(i)
            
            self.drip_table.setItem(i, 0, QTableWidgetItem(str(year_data['year'])))
            self.drip_table.setItem(i, 1, QTableWidgetItem(f"{year_data['shares']:.2f}"))
            self.drip_table.setItem(i, 2, QTableWidgetItem(f"${year_data['price']:.2f}"))
            self.drip_table.setItem(i, 3, QTableWidgetItem(f"${year_data['dividends']:.2f}"))
            self.drip_table.setItem(i, 4, QTableWidgetItem(f"{year_data['reinvested_shares']:.2f}"))
            self.drip_table.setItem(i, 5, QTableWidgetItem(f"${year_data['portfolio_value']:,.2f}"))
    
    def _add_holding(self):
        """Add holding to portfolio"""
        symbol = self.port_symbol_input.text().upper()
        shares = self.port_shares_spin.value()
        
        if not symbol:
            QMessageBox.warning(self, "Error", "Please enter a symbol")
            return
        
        # Add to tracker if not already there
        if symbol not in self.tracker.tracked_stocks:
            self.tracker.add_stock(symbol)
        
        # For now, just update display
        self._update_portfolio_display()
        self.port_symbol_input.clear()
    
    def _update_portfolio_display(self):
        """Update portfolio holdings display"""
        # This would show the current portfolio holdings
        pass
    
    def _calculate_income_projection(self):
        """Calculate portfolio income projection"""
        income_text = """
PORTFOLIO DIVIDEND INCOME PROJECTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Monthly Income:           $XXX.XX
Quarterly Income:         $XXX.XX
Annual Income:            $XXX.XX

PAYMENT SCHEDULE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
January:                  $XX.XX
February:                 $XX.XX
March:                    $XX.XX
... (continues for all months)

NOTES:
• Projections assume dividends continue at current rate
• Actual dividends may vary quarter to quarter
• Use this for planning, not as financial advice
"""
        self.income_text.setText(income_text)
