"""
Backtesting GUI Tab
Interface for strategy backtesting and performance analysis
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QSpinBox, QDoubleSpinBox,
    QDateEdit, QGroupBox, QTabWidget, QMessageBox, QProgressBar,
    QCheckBox, QDialog, QFormLayout, QTextEdit
)
from PySide6.QtCore import Qt, QDate, QSize, QTimer, Signal, QThread
from PySide6.QtGui import QColor, QFont

from services.backtester import (
    Backtester, SimpleMovingAverageCrossover, RelativeStrengthIndex,
    BollingerBands, MACD
)


class BacktestWorker(QThread):
    """Worker thread for backtesting to prevent UI blocking"""
    
    progress = Signal(str)
    finished = Signal(object)  # BacktestResults
    error = Signal(str)
    
    def __init__(self, backtester, symbol, strategy, start_date, end_date):
        super().__init__()
        self.backtester = backtester
        self.symbol = symbol
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
    
    def run(self):
        try:
            self.progress.emit(f"Running backtest for {self.symbol}...")
            results = self.backtester.backtest(
                self.symbol,
                self.strategy,
                self.start_date,
                self.end_date
            )
            self.progress.emit("Backtest complete!")
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class BacktestTab(QWidget):
    """Main Backtesting Tab"""
    
    def __init__(self, db=None, cache=None):
        super().__init__()
        self.db = db
        self.cache = cache
        self.backtester = Backtester(initial_capital=10000.0)
        self.current_results = None
        self.backtest_worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_backtest_tab(), "🚀 Run Backtest")
        tabs.addTab(self._create_results_tab(), "📊 Results")
        tabs.addTab(self._create_comparison_tab(), "⚖️ Compare Strategies")
        tabs.addTab(self._create_optimization_tab(), "🔧 Optimize Strategy")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def _create_backtest_tab(self) -> QWidget:
        """Create backtest execution tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Input section
        input_group = QGroupBox("Backtest Parameters")
        input_layout = QFormLayout()
        
        # Symbol
        self.bt_symbol = QLineEdit()
        self.bt_symbol.setText("AAPL")
        input_layout.addRow("Stock Symbol:", self.bt_symbol)
        
        # Strategy selector
        self.bt_strategy = QComboBox()
        self.bt_strategy.addItems([
            "SMA Crossover (20/50)",
            "RSI (14)",
            "Bollinger Bands (20)",
            "MACD (12/26/9)"
        ])
        input_layout.addRow("Strategy:", self.bt_strategy)
        
        # Date range
        today = QDate.currentDate()
        one_year_ago = today.addYears(-1)
        
        self.bt_start_date = QDateEdit()
        self.bt_start_date.setDate(one_year_ago)
        self.bt_start_date.setCalendarPopup(True)
        input_layout.addRow("Start Date:", self.bt_start_date)
        
        self.bt_end_date = QDateEdit()
        self.bt_end_date.setDate(today)
        self.bt_end_date.setCalendarPopup(True)
        input_layout.addRow("End Date:", self.bt_end_date)
        
        # Initial capital
        self.bt_capital = QDoubleSpinBox()
        self.bt_capital.setRange(100.0, 1000000.0)
        self.bt_capital.setValue(10000.0)
        self.bt_capital.setSingleStep(1000.0)
        input_layout.addRow("Initial Capital ($):", self.bt_capital)
        
        # Shares per trade
        self.bt_shares = QSpinBox()
        self.bt_shares.setRange(1, 1000)
        self.bt_shares.setValue(100)
        input_layout.addRow("Shares per Trade:", self.bt_shares)
        
        # Include buy & hold benchmark
        self.bt_benchmark = QCheckBox("Compare with Buy & Hold")
        self.bt_benchmark.setChecked(True)
        input_layout.addRow("Benchmark:", self.bt_benchmark)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Run button
        run_btn = QPushButton("🚀 Run Backtest")
        run_btn.clicked.connect(self._run_backtest)
        run_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(run_btn)
        
        # Progress section
        self.bt_progress = QProgressBar()
        self.bt_progress.setValue(0)
        self.bt_progress.setVisible(False)
        layout.addWidget(self.bt_progress)
        
        # Status
        self.bt_status = QLabel("Ready")
        self.bt_status.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.bt_status)
        
        widget.setLayout(layout)
        return widget
    
    def _create_results_tab(self) -> QWidget:
        """Create results display tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Summary metrics
        summary_group = QGroupBox("Performance Summary")
        summary_layout = QFormLayout()
        
        self.results_final_value = QLabel("-")
        self.results_total_return = QLabel("-")
        self.results_annual_return = QLabel("-")
        self.results_win_rate = QLabel("-")
        self.results_profit_factor = QLabel("-")
        self.results_sharpe = QLabel("-")
        self.results_max_dd = QLabel("-")
        self.results_num_trades = QLabel("-")
        
        summary_layout.addRow("Final Portfolio Value:", self.results_final_value)
        summary_layout.addRow("Total Return:", self.results_total_return)
        summary_layout.addRow("Annual Return:", self.results_annual_return)
        summary_layout.addRow("Win Rate:", self.results_win_rate)
        summary_layout.addRow("Profit Factor:", self.results_profit_factor)
        summary_layout.addRow("Sharpe Ratio:", self.results_sharpe)
        summary_layout.addRow("Max Drawdown:", self.results_max_dd)
        summary_layout.addRow("Number of Trades:", self.results_num_trades)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Trades table
        trades_group = QGroupBox("Trade History")
        trades_layout = QVBoxLayout()
        
        self.results_trades_table = QTableWidget()
        self.results_trades_table.setColumnCount(9)
        self.results_trades_table.setHorizontalHeaderLabels([
            "Entry Date", "Exit Date", "Type", "Entry Price", "Exit Price",
            "Shares", "Profit/Loss", "Return %", "Duration (days)"
        ])
        self.results_trades_table.setColumnWidth(0, 120)
        self.results_trades_table.setColumnWidth(1, 120)
        
        trades_layout.addWidget(self.results_trades_table)
        trades_group.setLayout(trades_layout)
        layout.addWidget(trades_group)
        
        widget.setLayout(layout)
        return widget
    
    def _create_comparison_tab(self) -> QWidget:
        """Create strategy comparison tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Comparison controls
        control_group = QGroupBox("Compare Strategies")
        control_layout = QFormLayout()
        
        self.comp_symbol = QLineEdit()
        self.comp_symbol.setText("AAPL")
        control_layout.addRow("Stock Symbol:", self.comp_symbol)
        
        today = QDate.currentDate()
        one_year_ago = today.addYears(-1)
        
        self.comp_start_date = QDateEdit()
        self.comp_start_date.setDate(one_year_ago)
        self.comp_start_date.setCalendarPopup(True)
        control_layout.addRow("Start Date:", self.comp_start_date)
        
        self.comp_end_date = QDateEdit()
        self.comp_end_date.setDate(today)
        self.comp_end_date.setCalendarPopup(True)
        control_layout.addRow("End Date:", self.comp_end_date)
        
        self.comp_capital = QDoubleSpinBox()
        self.comp_capital.setRange(100.0, 1000000.0)
        self.comp_capital.setValue(10000.0)
        control_layout.addRow("Initial Capital ($):", self.comp_capital)
        
        # Strategy checkboxes
        self.comp_sma = QCheckBox("SMA Crossover")
        self.comp_sma.setChecked(True)
        self.comp_rsi = QCheckBox("RSI")
        self.comp_rsi.setChecked(True)
        self.comp_bb = QCheckBox("Bollinger Bands")
        self.comp_bb.setChecked(True)
        self.comp_macd = QCheckBox("MACD")
        self.comp_macd.setChecked(True)
        self.comp_bh = QCheckBox("Buy & Hold (Benchmark)")
        self.comp_bh.setChecked(True)
        
        control_layout.addRow("Include:", self.comp_sma)
        control_layout.addRow("", self.comp_rsi)
        control_layout.addRow("", self.comp_bb)
        control_layout.addRow("", self.comp_macd)
        control_layout.addRow("", self.comp_bh)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Compare button
        compare_btn = QPushButton("⚖️ Compare Strategies")
        compare_btn.clicked.connect(self._compare_strategies)
        compare_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(compare_btn)
        
        # Comparison results table
        results_group = QGroupBox("Comparison Results")
        results_layout = QVBoxLayout()
        
        self.comp_results_table = QTableWidget()
        self.comp_results_table.setColumnCount(8)
        self.comp_results_table.setHorizontalHeaderLabels([
            "Strategy", "Total Return %", "Annual Return %", "Win Rate %",
            "Sharpe Ratio", "Max Drawdown %", "# Trades", "Profit Factor"
        ])
        
        results_layout.addWidget(self.comp_results_table)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        widget.setLayout(layout)
        return widget
    
    def _create_optimization_tab(self) -> QWidget:
        """Create strategy optimization tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Optimization controls
        opt_group = QGroupBox("Optimize Strategy Parameters")
        opt_layout = QFormLayout()
        
        self.opt_symbol = QLineEdit()
        self.opt_symbol.setText("AAPL")
        opt_layout.addRow("Stock Symbol:", self.opt_symbol)
        
        self.opt_strategy = QComboBox()
        self.opt_strategy.addItems([
            "SMA Crossover",
            "RSI",
            "Bollinger Bands",
            "MACD"
        ])
        opt_layout.addRow("Strategy to Optimize:", self.opt_strategy)
        
        today = QDate.currentDate()
        one_year_ago = today.addYears(-1)
        
        self.opt_start_date = QDateEdit()
        self.opt_start_date.setDate(one_year_ago)
        self.opt_start_date.setCalendarPopup(True)
        opt_layout.addRow("Start Date:", self.opt_start_date)
        
        self.opt_end_date = QDateEdit()
        self.opt_end_date.setDate(today)
        self.opt_end_date.setCalendarPopup(True)
        opt_layout.addRow("End Date:", self.opt_end_date)
        
        self.opt_metric = QComboBox()
        self.opt_metric.addItems([
            "sharpe_ratio",
            "total_return_pct",
            "win_rate_pct",
            "profit_factor"
        ])
        opt_layout.addRow("Optimize For:", self.opt_metric)
        
        opt_group.setLayout(opt_layout)
        layout.addWidget(opt_group)
        
        # Optimize button
        optimize_btn = QPushButton("🔧 Run Optimization")
        optimize_btn.clicked.connect(self._optimize_strategy)
        optimize_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(optimize_btn)
        
        # Optimization results
        results_group = QGroupBox("Optimization Results")
        results_layout = QVBoxLayout()
        
        self.opt_results_text = QTextEdit()
        self.opt_results_text.setReadOnly(True)
        self.opt_results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        
        results_layout.addWidget(self.opt_results_text)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        widget.setLayout(layout)
        return widget
    
    def _run_backtest(self):
        """Run backtest in background thread"""
        try:
            symbol = self.bt_symbol.text().upper()
            strategy_name = self.bt_strategy.currentText()
            start_date = self.bt_start_date.date().toPython()
            end_date = self.bt_end_date.date().toPython()
            capital = self.bt_capital.value()
            shares = self.bt_shares.value()
            
            # Validate inputs
            if not symbol:
                QMessageBox.warning(self, "Input Error", "Please enter a stock symbol")
                return
            
            if start_date >= end_date:
                QMessageBox.warning(self, "Date Error", "Start date must be before end date")
                return
            
            # Create strategy based on selection
            if "SMA" in strategy_name:
                strategy = SimpleMovingAverageCrossover(20, 50)
            elif "RSI" in strategy_name:
                strategy = RelativeStrengthIndex(14)
            elif "Bollinger" in strategy_name:
                strategy = BollingerBands(20)
            elif "MACD" in strategy_name:
                strategy = MACD(12, 26, 9)
            else:
                strategy = SimpleMovingAverageCrossover(20, 50)
            
            # Create backtester with current capital
            self.backtester = Backtester(initial_capital=capital)
            
            # Show progress
            self.bt_progress.setVisible(True)
            self.bt_progress.setValue(50)
            self.bt_status.setText("Running backtest...")
            
            # Run in background
            self.backtest_worker = BacktestWorker(
                self.backtester, symbol, strategy, start_date, end_date
            )
            self.backtest_worker.progress.connect(self._update_status)
            self.backtest_worker.finished.connect(self._on_backtest_complete)
            self.backtest_worker.error.connect(self._on_backtest_error)
            self.backtest_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run backtest: {str(e)}")
    
    def _on_backtest_complete(self, results):
        """Handle backtest completion"""
        self.current_results = results
        self.bt_progress.setValue(100)
        self.bt_status.setText("Backtest complete!")
        
        # Display results
        self._display_results(results)
        
        # Reset progress after 2 seconds
        QTimer.singleShot(2000, lambda: self.bt_progress.setVisible(False))
    
    def _on_backtest_error(self, error_msg):
        """Handle backtest error"""
        self.bt_progress.setVisible(False)
        QMessageBox.critical(self, "Backtest Error", error_msg)
        self.bt_status.setText(f"Error: {error_msg}")
    
    def _update_status(self, message):
        """Update status message"""
        self.bt_status.setText(message)
    
    def _display_results(self, results):
        """Display backtest results"""
        # Summary metrics
        final_value = results.equity_curve[-1] if results.equity_curve else results.initial_capital
        
        self.results_final_value.setText(f"${final_value:,.2f}")
        self.results_final_value.setStyleSheet(
            "color: #4CAF50;" if final_value >= results.initial_capital else "color: #f44336;"
        )
        
        self.results_total_return.setText(f"{results.total_return_pct:.2f}%")
        self.results_annual_return.setText(f"{results.annual_return_pct:.2f}%")
        self.results_win_rate.setText(f"{results.win_rate_pct:.1f}%")
        self.results_profit_factor.setText(f"{results.profit_factor:.2f}")
        self.results_sharpe.setText(f"{results.sharpe_ratio:.2f}")
        self.results_max_dd.setText(f"{results.max_drawdown_pct:.2f}%")
        
        closed_trades = len([t for t in results.trades if t.exit_price is not None])
        self.results_num_trades.setText(str(closed_trades))
        
        # Populate trades table
        self.results_trades_table.setRowCount(len(results.trades))
        
        for row, trade in enumerate(results.trades):
            self.results_trades_table.setItem(row, 0, QTableWidgetItem(
                trade.entry_date.strftime("%Y-%m-%d")
            ))
            
            exit_date = trade.exit_date.strftime("%Y-%m-%d") if trade.exit_date else "OPEN"
            self.results_trades_table.setItem(row, 1, QTableWidgetItem(exit_date))
            
            self.results_trades_table.setItem(row, 2, QTableWidgetItem(
                trade.position_type.value.upper()
            ))
            
            self.results_trades_table.setItem(row, 3, QTableWidgetItem(
                f"${trade.entry_price:.2f}"
            ))
            
            exit_price_str = f"${trade.exit_price:.2f}" if trade.exit_price else "-"
            self.results_trades_table.setItem(row, 4, QTableWidgetItem(exit_price_str))
            
            self.results_trades_table.setItem(row, 5, QTableWidgetItem(
                f"{trade.shares:.0f}"
            ))
            
            pl_str = f"${trade.profit_loss:,.2f}" if trade.exit_price else "-"
            pl_item = QTableWidgetItem(pl_str)
            if trade.exit_price and trade.profit_loss > 0:
                pl_item.setForeground(QColor("#4CAF50"))
            elif trade.exit_price and trade.profit_loss < 0:
                pl_item.setForeground(QColor("#f44336"))
            self.results_trades_table.setItem(row, 6, pl_item)
            
            ret_str = f"{trade.profit_loss_pct:.2f}%" if trade.exit_price else "-"
            self.results_trades_table.setItem(row, 7, QTableWidgetItem(ret_str))
            
            duration_str = f"{trade.duration_days}" if trade.exit_price else "-"
            self.results_trades_table.setItem(row, 8, QTableWidgetItem(duration_str))
    
    def _compare_strategies(self):
        """Compare multiple strategies"""
        try:
            symbol = self.comp_symbol.text().upper()
            start_date = self.comp_start_date.date().toPython()
            end_date = self.comp_end_date.date().toPython()
            capital = self.comp_capital.value()
            
            backtester = Backtester(initial_capital=capital)
            strategies = []
            
            if self.comp_sma.isChecked():
                strategies.append(SimpleMovingAverageCrossover(20, 50))
            if self.comp_rsi.isChecked():
                strategies.append(RelativeStrengthIndex(14))
            if self.comp_bb.isChecked():
                strategies.append(BollingerBands(20))
            if self.comp_macd.isChecked():
                strategies.append(MACD(12, 26, 9))
            
            self.bt_status.setText("Comparing strategies...")
            
            # Run comparisons
            results_dict = backtester.compare_strategies(symbol, strategies, start_date, end_date)
            
            # Add buy & hold if selected
            if self.comp_bh.isChecked():
                bh_results = backtester.buy_and_hold(symbol, start_date, end_date)
                results_dict["Buy & Hold"] = bh_results
            
            # Display results
            self.comp_results_table.setRowCount(len(results_dict))
            
            for row, (strategy_name, results) in enumerate(results_dict.items()):
                if results is None:
                    continue
                
                self.comp_results_table.setItem(row, 0, QTableWidgetItem(strategy_name))
                self.comp_results_table.setItem(row, 1, QTableWidgetItem(f"{results.total_return_pct:.2f}%"))
                self.comp_results_table.setItem(row, 2, QTableWidgetItem(f"{results.annual_return_pct:.2f}%"))
                self.comp_results_table.setItem(row, 3, QTableWidgetItem(f"{results.win_rate_pct:.1f}%"))
                self.comp_results_table.setItem(row, 4, QTableWidgetItem(f"{results.sharpe_ratio:.2f}"))
                self.comp_results_table.setItem(row, 5, QTableWidgetItem(f"{results.max_drawdown_pct:.2f}%"))
                
                closed = len([t for t in results.trades if t.exit_price is not None])
                self.comp_results_table.setItem(row, 6, QTableWidgetItem(str(closed)))
                self.comp_results_table.setItem(row, 7, QTableWidgetItem(f"{results.profit_factor:.2f}"))
            
            self.bt_status.setText("Comparison complete!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to compare strategies: {str(e)}")
    
    def _optimize_strategy(self):
        """Optimize strategy parameters"""
        try:
            symbol = self.opt_symbol.text().upper()
            strategy_name = self.opt_strategy.currentText()
            start_date = self.opt_start_date.date().toPython()
            end_date = self.opt_end_date.date().toPython()
            metric = self.opt_metric.currentText()
            
            self.bt_status.setText("Optimizing strategy (this may take a minute)...")
            
            backtester = Backtester(initial_capital=10000.0)
            
            # Define parameter grids
            if "SMA" in strategy_name:
                param_grid = {
                    'fast_period': [10, 15, 20, 25],
                    'slow_period': [40, 50, 60, 70]
                }
                best_params, best_results = backtester.optimize_strategy(
                    symbol, SimpleMovingAverageCrossover, param_grid, start_date, end_date, metric
                )
            elif "RSI" in strategy_name:
                param_grid = {
                    'period': [7, 14, 21],
                    'oversold': [20, 30, 40],
                    'overbought': [60, 70, 80]
                }
                best_params, best_results = backtester.optimize_strategy(
                    symbol, RelativeStrengthIndex, param_grid, start_date, end_date, metric
                )
            elif "Bollinger" in strategy_name:
                param_grid = {
                    'period': [15, 20, 25],
                    'num_std': [1.5, 2.0, 2.5]
                }
                best_params, best_results = backtester.optimize_strategy(
                    symbol, BollingerBands, param_grid, start_date, end_date, metric
                )
            elif "MACD" in strategy_name:
                param_grid = {
                    'fast_period': [10, 12],
                    'slow_period': [24, 26],
                    'signal_period': [7, 9]
                }
                best_params, best_results = backtester.optimize_strategy(
                    symbol, MACD, param_grid, start_date, end_date, metric
                )
            else:
                return
            
            # Display results
            results_text = f"""
╔════════════════════════════════════════════════════════╗
║             OPTIMIZATION RESULTS                       ║
╚════════════════════════════════════════════════════════╝

BEST PARAMETERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{format_params(best_params)}

BEST PERFORMANCE (Optimized for: {metric}):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Return:        {best_results.total_return_pct:.2f}%
Annual Return:       {best_results.annual_return_pct:.2f}%
Win Rate:            {best_results.win_rate_pct:.1f}%
Sharpe Ratio:        {best_results.sharpe_ratio:.2f}
Max Drawdown:        {best_results.max_drawdown_pct:.2f}%
Profit Factor:       {best_results.profit_factor:.2f}
Number of Trades:    {len([t for t in best_results.trades if t.exit_price is not None])}
"""
            
            self.opt_results_text.setText(results_text)
            self.bt_status.setText("Optimization complete!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to optimize strategy: {str(e)}")


def format_params(params: Dict) -> str:
    """Format parameters for display"""
    lines = []
    for key, value in params.items():
        lines.append(f"{key:.<30} {value}")
    return "\n".join(lines)
