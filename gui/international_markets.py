"""
International Markets Tab GUI
Support for major exchanges, currency conversion, foreign tax considerations
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QDoubleSpinBox, QMessageBox,
    QGroupBox, QTextEdit, QHeaderView, QSpinBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont
from typing import Optional

from services.international_markets import (
    InternationalStockFetcher, InternationalPortfolioManager, 
    InternationalMarketAnalyzer, Exchange, Currency, ExchangeDatabase
)


class InternationalWorker(QThread):
    """Worker thread for international market operations"""
    
    data_ready = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.task = None
        self.params = {}
    
    def set_fetch_stock(self, symbol: str, exchange: Exchange):
        """Set task to fetch stock"""
        self.task = 'fetch_stock'
        self.params = {'symbol': symbol, 'exchange': exchange}
    
    def set_get_rates(self, currencies: list):
        """Set task to get currency rates"""
        self.task = 'currency_rates'
        self.params = {'currencies': currencies}
    
    def run(self):
        try:
            if self.task == 'fetch_stock':
                fetcher = InternationalStockFetcher()
                stock = fetcher.fetch_stock(
                    self.params['symbol'],
                    self.params['exchange']
                )
                self.data_ready.emit({'stock': stock})
            elif self.task == 'currency_rates':
                # Would fetch rates here
                self.data_ready.emit({'rates': {}})
        except Exception as e:
            self.error_occurred.emit(str(e))


class InternationalMarketsTab(QWidget):
    """Tab for international markets and currency conversion"""
    
    def __init__(self):
        super().__init__()
        self.fetcher = InternationalStockFetcher()
        self.portfolio_manager = InternationalPortfolioManager()
        self.analyzer = InternationalMarketAnalyzer()
        self.worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Create tabs
        tabs = QTabWidget()
        
        # Tab 1: International Stock Search
        tabs.addTab(self._create_stock_search_tab(), "🌍 Stock Search")
        
        # Tab 2: Currency Converter
        tabs.addTab(self._create_currency_tab(), "💱 Currency Converter")
        
        # Tab 3: Exchange Comparison
        tabs.addTab(self._create_exchange_comparison_tab(), "📊 Exchanges")
        
        # Tab 4: International Portfolio
        tabs.addTab(self._create_portfolio_tab(), "💼 Portfolio")
        
        # Tab 5: Tax Planning
        tabs.addTab(self._create_tax_planning_tab(), "📋 Tax Planning")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def _create_stock_search_tab(self) -> QWidget:
        """Create international stock search tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🌍 Search Stocks Globally"))
        
        # Search parameters
        search_group = QGroupBox("Search Stock")
        search_layout = QVBoxLayout()
        
        param_row = QHBoxLayout()
        param_row.addWidget(QLabel("Symbol:"))
        self.int_symbol_input = QLineEdit()
        self.int_symbol_input.setPlaceholderText("e.g., ASML")
        param_row.addWidget(self.int_symbol_input)
        
        param_row.addWidget(QLabel("Exchange:"))
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems([
            'NYSE', 'NASDAQ', 'LSE', 'TSE', 'ASX', 'TSX', 'EURONEXT'
        ])
        param_row.addWidget(self.exchange_combo)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.clicked.connect(self._search_international_stock)
        param_row.addWidget(search_btn)
        search_layout.addLayout(param_row)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Results
        self.intl_stock_table = QTableWidget()
        self.intl_stock_table.setColumnCount(8)
        self.intl_stock_table.setHorizontalHeaderLabels([
            'Symbol', 'Company', 'Exchange', 'Currency', 'Local Price',
            'Market Cap', 'P/E Ratio', 'Dividend Yield'
        ])
        self.intl_stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.intl_stock_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_currency_tab(self) -> QWidget:
        """Create currency converter tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("💱 Currency Converter"))
        
        # Converter
        converter_group = QGroupBox("Convert Currency")
        converter_layout = QVBoxLayout()
        
        # Row 1: Amount input
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Amount:"))
        self.currency_amount_spin = QDoubleSpinBox()
        self.currency_amount_spin.setMinimum(0.01)
        self.currency_amount_spin.setMaximum(999999999)
        self.currency_amount_spin.setValue(1000)
        row1.addWidget(self.currency_amount_spin)
        converter_layout.addLayout(row1)
        
        # Row 2: From and To currencies
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("From:"))
        self.from_currency_combo = QComboBox()
        self.from_currency_combo.addItems(['USD', 'GBP', 'JPY', 'AUD', 'CAD', 'EUR', 'HKD'])
        row2.addWidget(self.from_currency_combo)
        
        row2.addWidget(QLabel("To:"))
        self.to_currency_combo = QComboBox()
        self.to_currency_combo.addItems(['USD', 'GBP', 'JPY', 'AUD', 'CAD', 'EUR', 'HKD'])
        self.to_currency_combo.setCurrentIndex(1)  # Default to different currency
        row2.addWidget(self.to_currency_combo)
        
        convert_btn = QPushButton("Convert")
        convert_btn.clicked.connect(self._convert_currency)
        row2.addWidget(convert_btn)
        
        converter_layout.addLayout(row2)
        
        converter_group.setLayout(converter_layout)
        layout.addWidget(converter_group)
        
        # Results
        self.conversion_text = QTextEdit()
        self.conversion_text.setReadOnly(True)
        self.conversion_text.setStyleSheet("background-color: #f5f5f5;")
        layout.addWidget(self.conversion_text)
        
        widget.setLayout(layout)
        return widget
    
    def _create_exchange_comparison_tab(self) -> QWidget:
        """Create exchange comparison tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📊 Global Stock Exchange Comparison"))
        
        # Exchange comparison table
        self.exchange_table = QTableWidget()
        self.exchange_table.setColumnCount(9)
        self.exchange_table.setHorizontalHeaderLabels([
            'Exchange', 'Country', 'Currency', 'Settlement', 'Dividend Tax',
            'Capital Gains Tax', 'Min. Market Cap', 'Trading Hours (UTC)', 'Timezone'
        ])
        self.exchange_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Populate exchanges
        row = 0
        for exchange_info in ExchangeDatabase.get_all_exchanges():
            self.exchange_table.insertRow(row)
            
            self.exchange_table.setItem(row, 0, QTableWidgetItem(exchange_info.exchange.value))
            self.exchange_table.setItem(row, 1, QTableWidgetItem(exchange_info.country))
            self.exchange_table.setItem(row, 2, QTableWidgetItem(exchange_info.currency.value))
            self.exchange_table.setItem(row, 3, QTableWidgetItem(f"T+{exchange_info.settlement_days}"))
            
            div_tax = QTableWidgetItem(f"{exchange_info.dividend_tax_rate*100:.1f}%")
            self.exchange_table.setItem(row, 4, div_tax)
            
            cap_tax = QTableWidgetItem(f"{exchange_info.capital_gains_tax_rate*100:.1f}%")
            self.exchange_table.setItem(row, 5, cap_tax)
            
            self.exchange_table.setItem(
                row, 6,
                QTableWidgetItem(f"${exchange_info.market_cap_requirement/1e6:.0f}M")
            )
            
            hours = f"{exchange_info.trading_hours_open}-{exchange_info.trading_hours_close}"
            self.exchange_table.setItem(row, 7, QTableWidgetItem(hours))
            
            self.exchange_table.setItem(row, 8, QTableWidgetItem(exchange_info.timezone))
            
            row += 1
        
        layout.addWidget(self.exchange_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_portfolio_tab(self) -> QWidget:
        """Create international portfolio tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("💼 International Portfolio Manager"))
        
        # Add holding
        add_group = QGroupBox("Add International Holding")
        add_layout = QVBoxLayout()
        
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Symbol:"))
        self.port_intl_symbol = QLineEdit()
        row1.addWidget(self.port_intl_symbol)
        
        row1.addWidget(QLabel("Exchange:"))
        self.port_exchange_combo = QComboBox()
        self.port_exchange_combo.addItems(['NYSE', 'NASDAQ', 'LSE', 'TSE', 'ASX', 'TSX'])
        row1.addWidget(self.port_exchange_combo)
        add_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Shares:"))
        self.port_intl_shares = QSpinBox()
        self.port_intl_shares.setMinimum(1)
        self.port_intl_shares.setMaximum(100000)
        row2.addWidget(self.port_intl_shares)
        
        row2.addWidget(QLabel("Cost Basis (local):"))
        self.port_intl_cost = QDoubleSpinBox()
        self.port_intl_cost.setMinimum(0.01)
        self.port_intl_cost.setMaximum(100000)
        self.port_intl_cost.setValue(100)
        row2.addWidget(self.port_intl_cost)
        
        add_btn = QPushButton("➕ Add Holding")
        add_btn.clicked.connect(self._add_intl_holding)
        row2.addWidget(add_btn)
        add_layout.addLayout(row2)
        
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)
        
        # Portfolio holdings
        layout.addWidget(QLabel("Your International Holdings"))
        self.intl_holdings_table = QTableWidget()
        self.intl_holdings_table.setColumnCount(7)
        self.intl_holdings_table.setHorizontalHeaderLabels([
            'Symbol', 'Exchange', 'Currency', 'Shares', 'Value (Local)',
            'Value (Base Currency)', 'Yield %'
        ])
        self.intl_holdings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.intl_holdings_table)
        
        # Base currency selection
        base_row = QHBoxLayout()
        base_row.addWidget(QLabel("Base Currency:"))
        self.base_currency_combo = QComboBox()
        self.base_currency_combo.addItems(['USD', 'GBP', 'AUD', 'CAD', 'EUR'])
        base_row.addWidget(self.base_currency_combo)
        base_row.addStretch()
        layout.addLayout(base_row)
        
        # Portfolio summary
        self.portfolio_summary_text = QTextEdit()
        self.portfolio_summary_text.setReadOnly(True)
        self.portfolio_summary_text.setStyleSheet("background-color: #f5f5f5;")
        self.portfolio_summary_text.setMaximumHeight(150)
        layout.addWidget(self.portfolio_summary_text)
        
        widget.setLayout(layout)
        return widget
    
    def _create_tax_planning_tab(self) -> QWidget:
        """Create tax planning tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📋 International Tax Planning"))
        
        # Tax information
        info_text = """
INTERNATIONAL TAX CONSIDERATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WITHHOLDING TAXES:
Different countries impose different withholding taxes on dividends:
• US: 0% (no withholding on dividends)
• UK: 20% withholding tax (reduced under tax treaties)
• Japan: 20% withholding tax
• Australia: 15% withholding tax

CAPITAL GAINS TAXES:
• Long-term (>1 year): Generally 15% in US, 20% in UK
• Short-term: Usually taxed as ordinary income
• Australia: 50% CGT discount for long-term gains

TAX TREATIES:
Many countries have tax treaties to avoid double taxation.
Check the specific treaty between your country and the stock's country.

W-8BEN FORM:
Non-US investors may need to file Form W-8BEN to reduce withholding taxes.
This is required when opening US brokerage accounts.

FOREIGN TAX CREDITS:
You may be able to claim foreign taxes paid as a credit on your home country taxes.
Consult with a tax professional about your specific situation.
"""
        
        tax_info = QTextEdit()
        tax_info.setText(info_text)
        tax_info.setReadOnly(True)
        tax_info.setStyleSheet("background-color: #f5f5f5;")
        layout.addWidget(tax_info)
        
        # Tax report
        tax_report_group = QGroupBox("Your Tax Report")
        tax_report_layout = QVBoxLayout()
        
        self.tax_report_text = QTextEdit()
        self.tax_report_text.setReadOnly(True)
        self.tax_report_text.setMaximumHeight(200)
        tax_report_layout.addWidget(self.tax_report_text)
        
        generate_btn = QPushButton("📄 Generate Tax Report")
        generate_btn.clicked.connect(self._generate_tax_report)
        tax_report_layout.addWidget(generate_btn)
        
        tax_report_group.setLayout(tax_report_layout)
        layout.addWidget(tax_report_group)
        
        widget.setLayout(layout)
        return widget
    
    def _search_international_stock(self):
        """Search for international stock"""
        symbol = self.int_symbol_input.text().upper()
        exchange_name = self.exchange_combo.currentText()
        
        if not symbol:
            QMessageBox.warning(self, "Error", "Please enter a symbol")
            return
        
        # Convert string to Exchange enum
        try:
            exchange = Exchange[exchange_name]
        except:
            exchange = Exchange.NYSE
        
        self.worker = InternationalWorker()
        self.worker.set_fetch_stock(symbol, exchange)
        self.worker.data_ready.connect(self._on_stock_fetched)
        self.worker.error_occurred.connect(lambda e: QMessageBox.critical(self, "Error", str(e)))
        self.worker.start()
    
    def _on_stock_fetched(self, data: dict):
        """Handle stock fetched"""
        stock = data.get('stock')
        if stock:
            self.intl_stock_table.setRowCount(0)
            self.intl_stock_table.insertRow(0)
            
            self.intl_stock_table.setItem(0, 0, QTableWidgetItem(stock.symbol))
            self.intl_stock_table.setItem(0, 1, QTableWidgetItem(stock.company_name))
            self.intl_stock_table.setItem(0, 2, QTableWidgetItem(stock.exchange.value))
            self.intl_stock_table.setItem(0, 3, QTableWidgetItem(stock.currency.value))
            
            price_item = QTableWidgetItem(f"{stock.price_local:.2f}")
            price_item.setForeground(QColor("#2196F3"))
            self.intl_stock_table.setItem(0, 4, price_item)
            
            market_cap = f"${stock.market_cap/1e9:.1f}B" if stock.market_cap else "—"
            self.intl_stock_table.setItem(0, 5, QTableWidgetItem(market_cap))
            
            pe = f"{stock.pe_ratio:.1f}" if stock.pe_ratio else "—"
            self.intl_stock_table.setItem(0, 6, QTableWidgetItem(pe))
            
            div_yield = f"{stock.dividend_yield*100:.2f}%" if stock.dividend_yield else "—"
            self.intl_stock_table.setItem(0, 7, QTableWidgetItem(div_yield))
    
    def _convert_currency(self):
        """Convert currency"""
        amount = self.currency_amount_spin.value()
        from_curr = self.from_currency_combo.currentText()
        to_curr = self.to_currency_combo.currentText()
        
        try:
            from_currency = Currency[from_curr]
            to_currency = Currency[to_curr]
            
            converted = self.fetcher.converter.convert(amount, from_currency, to_currency)
            
            if converted:
                text = f"""
CURRENCY CONVERSION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Original Amount:    {amount:,.2f} {from_curr}
Converted Amount:   {converted:,.2f} {to_curr}
Exchange Rate:      1 {from_curr} = {converted/amount:.4f} {to_curr}

Note: Rates are updated daily from Yahoo Finance.
Actual rates may vary with your bank or brokerage.
"""
                self.conversion_text.setText(text)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _add_intl_holding(self):
        """Add international holding"""
        symbol = self.port_intl_symbol.text().upper()
        exchange_name = self.port_exchange_combo.currentText()
        shares = self.port_intl_shares.value()
        cost_basis = self.port_intl_cost.value()
        
        if not symbol:
            QMessageBox.warning(self, "Error", "Please enter a symbol")
            return
        
        try:
            exchange = Exchange[exchange_name]
            success = self.portfolio_manager.add_holding(symbol, exchange, shares, cost_basis)
            
            if success:
                QMessageBox.information(self, "Success", f"✅ Added {shares} shares of {symbol}")
                self.port_intl_symbol.clear()
            else:
                QMessageBox.warning(self, "Error", "Failed to add holding")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _generate_tax_report(self):
        """Generate tax report"""
        if not self.portfolio_manager.holdings:
            self.tax_report_text.setText("No holdings to report on")
            return
        
        report = self.portfolio_manager.get_tax_report()
        
        text = f"""
TAX REPORT FOR INTERNATIONAL HOLDINGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total After-Tax Gains:      ${report['total_after_tax_gains']:,.2f}
Est. Annual Dividend Taxes: ${report['estimated_annual_taxes']:,.2f}

POSITION DETAILS:
"""
        
        for position in report['positions'][:5]:
            text += f"""
{position['symbol']} ({position['exchange']}):
  • After-Tax Gain:  ${position['after_tax_gain']:,.2f}
  • Dividend Tax Rate: {position['dividend_tax_rate']*100:.0f}%
  • Est. Annual Tax:  ${position['estimated_dividend_tax']:,.2f}
"""
        
        text += """
DISCLAIMER:
This is for informational purposes only. Consult with a tax professional
for specific tax advice. Tax rates and treaties vary by jurisdiction.
"""
        
        self.tax_report_text.setText(text)
