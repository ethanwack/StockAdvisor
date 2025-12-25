"""
Stock Screener Tab GUI
Advanced filtering, saved screens, and bulk analysis
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox,
    QListWidget, QListWidgetItem, QMessageBox, QDialog, QFormLayout, QLineEdit,
    QCheckBox, QTextEdit, QHeaderView
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont
from typing import List
import pandas as pd

from services.stock_screener import (
    StockScreener, FilterCriteria, ComparisonOperator, SortOrder, SortCriteria
)


class ScreenerWorker(QThread):
    """Worker thread for screening operations"""
    
    results_ready = Signal(list)
    error_occurred = Signal(str)
    progress = Signal(int)  # 0-100
    
    def __init__(self, screener: StockScreener):
        super().__init__()
        self.screener = screener
        self.task = None
        self.params = {}
    
    def set_run_screen(self, screen_name: str, universe: str = 'sp500'):
        """Set task to run a screen"""
        self.task = 'run_screen'
        self.params = {'screen_name': screen_name, 'universe': universe}
    
    def set_quick_screen(self, universe: str, filters: List[FilterCriteria], 
                        sort: any, limit: int):
        """Set task to quick screen"""
        self.task = 'quick_screen'
        self.params = {
            'universe': universe,
            'filters': filters,
            'sort': sort,
            'limit': limit
        }
    
    def run(self):
        try:
            if self.task == 'run_screen':
                results = self.screener.run_screen(
                    self.params['screen_name'],
                    self.params['universe']
                )
                self.results_ready.emit(results)
            elif self.task == 'quick_screen':
                results = self.screener.quick_screen(
                    self.params['universe'],
                    self.params['filters'],
                    self.params['sort'],
                    self.params['limit']
                )
                self.results_ready.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))


class AddFilterDialog(QDialog):
    """Dialog to add a filter"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Filter")
        self.setGeometry(200, 200, 500, 300)
        
        layout = QFormLayout()
        
        # Field selection
        self.field_combo = QComboBox()
        self.field_combo.addItems([
            'pe_ratio', 'market_cap', 'dividend_yield', 'earnings_growth',
            'revenue_growth', 'profit_margin', 'debt_to_equity', 'rsi', 'macd',
            'volume', 'sector', 'industry'
        ])
        layout.addRow("Field:", self.field_combo)
        
        # Operator selection
        self.operator_combo = QComboBox()
        self.operator_combo.addItems([op.value for op in ComparisonOperator])
        layout.addRow("Operator:", self.operator_combo)
        
        # Value inputs
        self.value1_input = QLineEdit()
        layout.addRow("Value:", self.value1_input)
        
        self.value2_input = QLineEdit()
        self.value2_input.setVisible(False)
        layout.addRow("Value 2 (for range):", self.value2_input)
        
        # Show value2 for IN_RANGE
        self.operator_combo.currentTextChanged.connect(
            lambda text: self.value2_input.setVisible(text == "in_range")
        )
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
    
    def get_filter(self) -> FilterCriteria:
        """Get the filter from inputs"""
        field = self.field_combo.currentText()
        operator = ComparisonOperator(self.operator_combo.currentText())
        value = self.value1_input.text()
        value2 = self.value2_input.text() if self.value2_input.isVisible() else None
        
        return FilterCriteria(field, operator, value, value2)


class ScreenerTab(QWidget):
    """Tab for stock screening and analysis"""
    
    def __init__(self):
        super().__init__()
        self.screener = StockScreener()
        self.worker = None
        self.current_results = []
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Tab 1: Quick Screen
        tabs.addTab(self._create_quick_screen_tab(), "⚡ Quick Screen")
        
        # Tab 2: Advanced Screen
        tabs.addTab(self._create_advanced_screen_tab(), "🔧 Advanced Screen")
        
        # Tab 3: Saved Screens
        tabs.addTab(self._create_saved_screens_tab(), "💾 Saved Screens")
        
        # Tab 4: Results & Analysis
        tabs.addTab(self._create_results_tab(), "📊 Results")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def _create_quick_screen_tab(self) -> QWidget:
        """Create quick screen tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instructions
        layout.addWidget(QLabel("🚀 Quick Screen - Fast filtering with preset criteria"))
        
        # Universe selection
        universe_group = QGroupBox("Stock Universe")
        universe_layout = QHBoxLayout()
        self.universe_combo = QComboBox()
        self.universe_combo.addItems(['sp500', 'tech', 'dividend', 'growth', 'value', 'small_cap'])
        universe_layout.addWidget(QLabel("Universe:"))
        universe_layout.addWidget(self.universe_combo)
        universe_layout.addStretch()
        universe_group.setLayout(universe_layout)
        layout.addWidget(universe_group)
        
        # Quick filter presets
        presets_group = QGroupBox("Quick Filter Presets")
        presets_layout = QVBoxLayout()
        
        # Preset buttons
        preset_row1 = QHBoxLayout()
        btn_dividend = QPushButton("💰 High Dividend (>2%)")
        btn_dividend.clicked.connect(lambda: self._apply_preset('dividend'))
        btn_growth = QPushButton("📈 Growth Stocks (>15% earnings)")
        btn_growth.clicked.connect(lambda: self._apply_preset('growth'))
        preset_row1.addWidget(btn_dividend)
        preset_row1.addWidget(btn_growth)
        presets_layout.addLayout(preset_row1)
        
        preset_row2 = QHBoxLayout()
        btn_value = QPushButton("💎 Value Stocks (PE <15)")
        btn_value.clicked.connect(lambda: self._apply_preset('value'))
        btn_oversold = QPushButton("📉 Oversold (RSI <30)")
        btn_oversold.clicked.connect(lambda: self._apply_preset('oversold'))
        preset_row2.addWidget(btn_value)
        preset_row2.addWidget(btn_oversold)
        presets_layout.addLayout(preset_row2)
        
        presets_group.setLayout(presets_layout)
        layout.addWidget(presets_group)
        
        # Results limit
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("Results Limit:"))
        self.quick_limit_spin = QSpinBox()
        self.quick_limit_spin.setMinimum(5)
        self.quick_limit_spin.setMaximum(200)
        self.quick_limit_spin.setValue(50)
        limit_layout.addWidget(self.quick_limit_spin)
        limit_layout.addStretch()
        layout.addLayout(limit_layout)
        
        # Run button
        run_btn = QPushButton("🔍 Run Quick Screen")
        run_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        run_btn.clicked.connect(self._run_quick_screen)
        layout.addWidget(run_btn)
        
        # Results display
        layout.addWidget(QLabel("Results:"))
        self.quick_results_table = QTableWidget()
        self.quick_results_table.setColumnCount(6)
        self.quick_results_table.setHorizontalHeaderLabels(
            ['Symbol', 'Price', 'P/E Ratio', 'Dividend %', 'Sector', 'Score']
        )
        layout.addWidget(self.quick_results_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_advanced_screen_tab(self) -> QWidget:
        """Create advanced screen tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🔧 Advanced Screen - Custom multi-criteria filtering"))
        
        # Universe selection
        universe_group = QGroupBox("Stock Universe")
        universe_layout = QHBoxLayout()
        self.adv_universe_combo = QComboBox()
        self.adv_universe_combo.addItems(['sp500', 'tech', 'dividend', 'growth', 'value', 'small_cap'])
        universe_layout.addWidget(QLabel("Universe:"))
        universe_layout.addWidget(self.adv_universe_combo)
        universe_layout.addStretch()
        universe_group.setLayout(universe_layout)
        layout.addWidget(universe_group)
        
        # Filter builder
        filter_group = QGroupBox("Add Filters")
        filter_layout = QVBoxLayout()
        
        # Active filters list
        filter_layout.addWidget(QLabel("Active Filters:"))
        self.filters_list = QListWidget()
        filter_layout.addWidget(self.filters_list)
        
        # Add filter button
        add_filter_btn = QPushButton("➕ Add Filter")
        add_filter_btn.clicked.connect(self._add_filter)
        
        # Remove filter button
        remove_filter_btn = QPushButton("🗑️ Remove Selected")
        remove_filter_btn.clicked.connect(self._remove_filter)
        
        button_row = QHBoxLayout()
        button_row.addWidget(add_filter_btn)
        button_row.addWidget(remove_filter_btn)
        filter_layout.addLayout(button_row)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Sort options
        sort_group = QGroupBox("Sort Results")
        sort_layout = QHBoxLayout()
        
        sort_layout.addWidget(QLabel("Sort by:"))
        self.sort_field_combo = QComboBox()
        self.sort_field_combo.addItems([
            'pe_ratio', 'price', 'dividend_yield', 'market_cap', 'rsi', 'volume'
        ])
        sort_layout.addWidget(self.sort_field_combo)
        
        sort_layout.addWidget(QLabel("Order:"))
        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItems(['Descending', 'Ascending'])
        sort_layout.addWidget(self.sort_order_combo)
        
        sort_layout.addStretch()
        sort_group.setLayout(sort_layout)
        layout.addWidget(sort_group)
        
        # Run button
        run_btn = QPushButton("🔍 Run Advanced Screen")
        run_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        run_btn.clicked.connect(self._run_advanced_screen)
        layout.addWidget(run_btn)
        
        # Results
        layout.addWidget(QLabel("Results:"))
        self.adv_results_table = QTableWidget()
        self.adv_results_table.setColumnCount(9)
        self.adv_results_table.setHorizontalHeaderLabels([
            'Symbol', 'Price', 'P/E', 'Yield %', 'Market Cap', 'RSI', 'Sector', 'Industry', 'Score'
        ])
        layout.addWidget(self.adv_results_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_saved_screens_tab(self) -> QWidget:
        """Create saved screens tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("💾 Saved Screens - Save and manage screening strategies"))
        
        # Create new screen
        new_group = QGroupBox("Create New Screen")
        new_layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Screen Name:"))
        self.screen_name_input = QLineEdit()
        name_layout.addWidget(self.screen_name_input)
        new_layout.addLayout(name_layout)
        
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.screen_desc_input = QTextEdit()
        self.screen_desc_input.setMaximumHeight(60)
        desc_layout.addWidget(self.screen_desc_input)
        new_layout.addLayout(desc_layout)
        
        create_btn = QPushButton("✅ Create Screen")
        create_btn.clicked.connect(self._create_screen)
        new_layout.addWidget(create_btn)
        
        new_group.setLayout(new_layout)
        layout.addWidget(new_group)
        
        # Saved screens list
        screens_group = QGroupBox("Your Saved Screens")
        screens_layout = QVBoxLayout()
        
        self.screens_list = QListWidget()
        self._update_screens_list()
        screens_layout.addWidget(self.screens_list)
        
        button_row = QHBoxLayout()
        run_saved_btn = QPushButton("▶️ Run Selected")
        run_saved_btn.clicked.connect(self._run_saved_screen)
        delete_saved_btn = QPushButton("🗑️ Delete Selected")
        delete_saved_btn.clicked.connect(self._delete_screen)
        button_row.addWidget(run_saved_btn)
        button_row.addWidget(delete_saved_btn)
        screens_layout.addLayout(button_row)
        
        screens_group.setLayout(screens_layout)
        layout.addWidget(screens_group)
        
        # Export button
        export_btn = QPushButton("📥 Export Results to CSV")
        export_btn.clicked.connect(self._export_results)
        layout.addWidget(export_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _create_results_tab(self) -> QWidget:
        """Create results and analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📊 Screen Results & Analysis"))
        
        # Results table
        layout.addWidget(QLabel("Detailed Results:"))
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(14)
        self.results_table.setHorizontalHeaderLabels([
            'Symbol', 'Name', 'Price', 'P/E', 'Market Cap', 'Yield %',
            'Earnings Growth', 'Revenue Growth', 'Profit Margin', 'D/E',
            'RSI', 'MACD', 'Sector', 'Score'
        ])
        layout.addWidget(self.results_table)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        stats_layout.addWidget(self.stats_text)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Action buttons
        button_row = QHBoxLayout()
        export_btn = QPushButton("📥 Export to CSV")
        export_btn.clicked.connect(self._export_results)
        copy_btn = QPushButton("📋 Copy Symbols")
        copy_btn.clicked.connect(self._copy_symbols)
        button_row.addWidget(export_btn)
        button_row.addWidget(copy_btn)
        layout.addLayout(button_row)
        
        widget.setLayout(layout)
        return widget
    
    def _apply_preset(self, preset_name: str):
        """Apply a quick filter preset"""
        filters = []
        
        if preset_name == 'dividend':
            filters = [FilterCriteria('dividend_yield', ComparisonOperator.GREATER_THAN, 0.02)]
        elif preset_name == 'growth':
            filters = [FilterCriteria('earnings_growth', ComparisonOperator.GREATER_THAN, 0.15)]
        elif preset_name == 'value':
            filters = [FilterCriteria('pe_ratio', ComparisonOperator.LESS_THAN, 15)]
        elif preset_name == 'oversold':
            filters = [FilterCriteria('rsi', ComparisonOperator.LESS_THAN, 30)]
        
        # Run quick screen
        universe = self.universe_combo.currentText()
        results = self.screener.quick_screen(
            universe=universe,
            filters=filters if filters else None,
            limit=self.quick_limit_spin.value()
        )
        
        self._display_quick_results(results)
    
    def _run_quick_screen(self):
        """Run quick screen without filters"""
        universe = self.universe_combo.currentText()
        results = self.screener.quick_screen(
            universe=universe,
            limit=self.quick_limit_spin.value()
        )
        self._display_quick_results(results)
    
    def _display_quick_results(self, results: list):
        """Display quick screen results"""
        self.current_results = results
        self.quick_results_table.setRowCount(0)
        
        for i, result in enumerate(results):
            self.quick_results_table.insertRow(i)
            
            # Symbol
            symbol_item = QTableWidgetItem(result.symbol)
            symbol_item.setForeground(QColor("#2196F3"))
            self.quick_results_table.setItem(i, 0, symbol_item)
            
            # Price
            price_item = QTableWidgetItem(f"${result.price:.2f}" if result.price else "—")
            self.quick_results_table.setItem(i, 1, price_item)
            
            # P/E
            pe_item = QTableWidgetItem(f"{result.pe_ratio:.1f}" if result.pe_ratio else "—")
            self.quick_results_table.setItem(i, 2, pe_item)
            
            # Dividend
            div_item = QTableWidgetItem(f"{result.dividend_yield*100:.2f}%" if result.dividend_yield else "—")
            self.quick_results_table.setItem(i, 3, div_item)
            
            # Sector
            sector_item = QTableWidgetItem(result.sector or "—")
            self.quick_results_table.setItem(i, 4, sector_item)
            
            # Score
            score_item = QTableWidgetItem(f"{result.score:.0f}")
            self.quick_results_table.setItem(i, 5, score_item)
        
        QMessageBox.information(self, "Success", f"✅ Found {len(results)} stocks!")
    
    def _add_filter(self):
        """Add a filter dialog"""
        dialog = AddFilterDialog()
        if dialog.exec() == QDialog.Accepted:
            filter_criteria = dialog.get_filter()
            item = QListWidgetItem(f"{filter_criteria.field} {filter_criteria.operator.value} {filter_criteria.value}")
            self.filters_list.addItem(item)
    
    def _remove_filter(self):
        """Remove selected filter"""
        self.filters_list.takeItem(self.filters_list.row(self.filters_list.currentItem()))
    
    def _run_advanced_screen(self):
        """Run advanced screen with custom filters"""
        # Collect filters
        filters = []
        # (In production would extract from filters_list)
        
        universe = self.adv_universe_combo.currentText()
        results = self.screener.quick_screen(
            universe=universe,
            filters=filters if filters else None
        )
        
        self._display_advanced_results(results)
    
    def _display_advanced_results(self, results: list):
        """Display advanced screen results"""
        self.current_results = results
        self.adv_results_table.setRowCount(0)
        
        for i, result in enumerate(results[:50]):
            self.adv_results_table.insertRow(i)
            
            cells = [
                result.symbol,
                f"${result.price:.2f}" if result.price else "—",
                f"{result.pe_ratio:.1f}" if result.pe_ratio else "—",
                f"{result.dividend_yield*100:.2f}%" if result.dividend_yield else "—",
                f"${result.market_cap/1e9:.1f}B" if result.market_cap else "—",
                f"{result.rsi:.0f}" if result.rsi else "—",
                result.sector or "—",
                result.industry or "—",
                f"{result.score:.0f}"
            ]
            
            for j, cell_text in enumerate(cells):
                item = QTableWidgetItem(str(cell_text))
                if j == 0:
                    item.setForeground(QColor("#2196F3"))
                self.adv_results_table.setItem(i, j, item)
    
    def _create_screen(self):
        """Create a new saved screen"""
        name = self.screen_name_input.text()
        desc = self.screen_desc_input.toPlainText()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter screen name")
            return
        
        self.screener.create_screen(name, desc)
        self.screen_name_input.clear()
        self.screen_desc_input.clear()
        self._update_screens_list()
        QMessageBox.information(self, "Success", f"✅ Screen '{name}' created!")
    
    def _update_screens_list(self):
        """Update saved screens list"""
        self.screens_list.clear()
        for screen in self.screener.get_saved_screens():
            item = QListWidgetItem(f"📋 {screen.name} ({screen.results_count} results)")
            self.screens_list.addItem(item)
    
    def _run_saved_screen(self):
        """Run selected saved screen"""
        selected = self.screens_list.currentItem()
        if selected:
            screen_name = selected.text().split(" ")[1]
            results = self.screener.run_screen(screen_name)
            self._display_advanced_results(results)
    
    def _delete_screen(self):
        """Delete selected screen"""
        selected = self.screens_list.currentItem()
        if selected:
            screen_name = selected.text().split(" ")[1]
            reply = QMessageBox.question(self, "Confirm", f"Delete screen '{screen_name}'?")
            if reply == QMessageBox.Yes:
                self.screener.delete_screen(screen_name)
                self._update_screens_list()
    
    def _export_results(self):
        """Export results to CSV"""
        if not self.current_results:
            QMessageBox.warning(self, "Error", "No results to export")
            return
        
        try:
            data = [r.to_dict() for r in self.current_results]
            df = pd.DataFrame(data)
            filepath = "/tmp/screener_results.csv"
            df.to_csv(filepath, index=False)
            QMessageBox.information(self, "Success", f"✅ Exported to {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
    
    def _copy_symbols(self):
        """Copy symbols to clipboard"""
        if not self.current_results:
            return
        
        symbols = ",".join([r.symbol for r in self.current_results])
        
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(symbols)
        QMessageBox.information(self, "Success", f"✅ Copied {len(self.current_results)} symbols to clipboard!")
