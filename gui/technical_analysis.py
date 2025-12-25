"""
Technical Analysis Tab GUI
Advanced charting, pattern recognition, volume analysis, trend identification
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QGroupBox, QTextEdit,
    QHeaderView, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont
from typing import Optional

from services.technical_analysis import (
    TechnicalAnalyzer, PatternRecognition, VolumeAnalyzer, TrendDirection
)


class AnalysisWorker(QThread):
    """Worker thread for technical analysis"""
    
    analysis_ready = Signal(dict)
    error_occurred = Signal(str)
    progress = Signal(int)
    
    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol
        self.analyzer = TechnicalAnalyzer(symbol)
    
    def run(self):
        try:
            self.progress.emit(10)
            
            # Fetch data
            self.analyzer.fetch_data('1y')
            self.progress.emit(30)
            
            # Calculate indicators
            self.analyzer.calculate_indicators()
            self.progress.emit(60)
            
            # Detect patterns
            self.analyzer.detect_patterns()
            self.progress.emit(80)
            
            # Get summary
            summary = self.analyzer.get_summary()
            self.progress.emit(100)
            
            self.analysis_ready.emit(summary)
        
        except Exception as e:
            self.error_occurred.emit(str(e))


class TechnicalAnalysisTab(QWidget):
    """Tab for technical analysis"""
    
    def __init__(self):
        super().__init__()
        self.analyzer: Optional[TechnicalAnalyzer] = None
        self.worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Stock selection
        select_group = QGroupBox("Stock Selection")
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Symbol:"))
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("e.g., AAPL")
        select_layout.addWidget(self.symbol_input)
        self.analyze_btn = QPushButton("📊 Analyze")
        self.analyze_btn.clicked.connect(self._analyze_stock)
        select_layout.addWidget(self.analyze_btn)
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Overview
        self.tabs.addTab(self._create_overview_tab(), "📋 Overview")
        
        # Tab 2: Indicators
        self.tabs.addTab(self._create_indicators_tab(), "📈 Indicators")
        
        # Tab 3: Patterns
        self.tabs.addTab(self._create_patterns_tab(), "🎯 Patterns")
        
        # Tab 4: Support/Resistance
        self.tabs.addTab(self._create_support_resistance_tab(), "📍 Support/Resistance")
        
        # Tab 5: Volume
        self.tabs.addTab(self._create_volume_tab(), "📊 Volume")
        
        # Tab 6: Fibonacci
        self.tabs.addTab(self._create_fibonacci_tab(), "🔢 Fibonacci")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def _create_overview_tab(self) -> QWidget:
        """Create overview tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📋 Technical Analysis Overview"))
        
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        self.overview_text.setStyleSheet("background-color: #f5f5f5;")
        layout.addWidget(self.overview_text)
        
        widget.setLayout(layout)
        return widget
    
    def _create_indicators_tab(self) -> QWidget:
        """Create indicators tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📈 Technical Indicators"))
        
        # Indicator selection
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Select Indicator:"))
        self.indicator_combo = QComboBox()
        self.indicator_combo.addItems([
            'Moving Averages (SMA/EMA)',
            'Bollinger Bands',
            'RSI (Relative Strength Index)',
            'MACD (Moving Average Convergence)',
            'Stochastic Oscillator',
            'ADX (Average Directional Index)',
            'ATR (Average True Range)',
            'OBV (On-Balance Volume)'
        ])
        select_layout.addWidget(self.indicator_combo)
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # Indicators table
        self.indicators_table = QTableWidget()
        self.indicators_table.setColumnCount(4)
        self.indicators_table.setHorizontalHeaderLabels(['Indicator', 'Current', 'Signal', 'Description'])
        self.indicators_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.indicators_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_patterns_tab(self) -> QWidget:
        """Create patterns tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🎯 Chart Patterns & Candlesticks"))
        
        # Pattern info
        info_text = """
Chart patterns detected in recent price action:

Hammer: Bullish reversal signal after downtrend
Shooting Star: Bearish reversal signal after uptrend
Double Top/Bottom: Major reversal patterns
Head & Shoulders: Trend reversal pattern
Triangles: Continuation/reversal patterns
Wedges: Reversal patterns with decreasing volume
Flags: Continuation patterns after strong moves
"""
        layout.addWidget(QLabel(info_text))
        
        # Patterns table
        self.patterns_table = QTableWidget()
        self.patterns_table.setColumnCount(5)
        self.patterns_table.setHorizontalHeaderLabels(['Date', 'Pattern', 'Type', 'Reliability', 'Description'])
        self.patterns_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.patterns_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_support_resistance_tab(self) -> QWidget:
        """Create support/resistance tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📍 Support & Resistance Levels"))
        
        # Info
        info_text = """
Support: Price level where buying interest emerges, preventing further decline
Resistance: Price level where selling pressure emerges, preventing further rise
Fibonacci: Key retracement levels at 23.6%, 38.2%, 50%, 61.8%, 78.6%
Strength: How many times price has bounced off this level
"""
        layout.addWidget(QLabel(info_text))
        
        # Levels table
        self.levels_table = QTableWidget()
        self.levels_table.setColumnCount(5)
        self.levels_table.setHorizontalHeaderLabels(['Price', 'Type', 'Touches', 'Strength %', 'Last Touch'])
        self.levels_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.levels_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_volume_tab(self) -> QWidget:
        """Create volume tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📊 Volume Analysis"))
        
        self.volume_text = QTextEdit()
        self.volume_text.setReadOnly(True)
        self.volume_text.setStyleSheet("background-color: #f5f5f5;")
        layout.addWidget(self.volume_text)
        
        widget.setLayout(layout)
        return widget
    
    def _create_fibonacci_tab(self) -> QWidget:
        """Create Fibonacci tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🔢 Fibonacci Retracement Levels"))
        
        # Info
        info_text = """
Fibonacci retracement levels are derived from the Fibonacci sequence.
They show where price might find support or resistance during a correction.

Key Levels:
• 23.6% - Minor retracement
• 38.2% - Moderate retracement
• 50.0% - Medium retracement
• 61.8% - Major retracement (strongest)
• 78.6% - Deep retracement

These levels are often used in conjunction with other indicators.
"""
        layout.addWidget(QLabel(info_text))
        
        # Fibonacci levels table
        self.fibonacci_table = QTableWidget()
        self.fibonacci_table.setColumnCount(3)
        self.fibonacci_table.setHorizontalHeaderLabels(['Level %', 'Price', 'Type'])
        self.fibonacci_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.fibonacci_table)
        
        widget.setLayout(layout)
        return widget
    
    def _analyze_stock(self):
        """Analyze selected stock"""
        symbol = self.symbol_input.text().upper()
        
        if not symbol:
            QMessageBox.warning(self, "Error", "Please enter a stock symbol")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.analyze_btn.setEnabled(False)
        
        # Start analysis in worker thread
        self.worker = AnalysisWorker(symbol)
        self.worker.analysis_ready.connect(self._on_analysis_complete)
        self.worker.error_occurred.connect(self._on_analysis_error)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.start()
    
    def _on_analysis_complete(self, summary: dict):
        """Handle analysis complete"""
        self.analyzer = TechnicalAnalyzer(summary['symbol'])
        self.analyzer.fetch_data('1y')
        self.analyzer.calculate_indicators()
        self.analyzer.detect_patterns()
        
        # Display overview
        self._display_overview(summary)
        
        # Display indicators
        self._display_indicators()
        
        # Display patterns
        self._display_patterns()
        
        # Display support/resistance
        self._display_support_resistance()
        
        # Display volume
        self._display_volume(summary.get('volume'))
        
        # Display Fibonacci
        self._display_fibonacci()
        
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        QMessageBox.information(self, "Success", f"✅ Analysis complete for {summary['symbol']}!")
    
    def _on_analysis_error(self, error: str):
        """Handle analysis error"""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Analysis failed: {error}")
    
    def _display_overview(self, summary: dict):
        """Display overview information"""
        text = f"""
╔════════════════════════════════════════════════════════╗
║          TECHNICAL ANALYSIS OVERVIEW                   ║
╚════════════════════════════════════════════════════════╝

SYMBOL:          {summary['symbol']}
PRICE:           ${summary['current_price']:.2f}

TREND ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Direction:     {summary['trend'].upper()}
• Strength:      {summary['trend_strength'].upper()}
• ADX:           {summary['adx']:.1f} {"(Strong)" if summary['adx'] > 25 else "(Weak)"}

MOMENTUM INDICATORS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• RSI:           {summary['rsi']:.1f} ({summary['rsi_signal'].upper()})
• MACD Signal:   {summary['macd_signal'].upper()}

PATTERNS DETECTED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for pattern in summary['patterns']:
            text += f"• {pattern}\n"
        
        text += """
INTERPRETATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Use this analysis in conjunction with other indicators
• Technical analysis is not foolproof
• Always manage risk with proper position sizing
• Consider fundamental analysis alongside technical
"""
        
        self.overview_text.setText(text)
    
    def _display_indicators(self):
        """Display technical indicators"""
        if not self.analyzer:
            return
        
        indicators = self.analyzer.indicators
        self.indicators_table.setRowCount(0)
        
        # Moving averages
        if 'sma_20' in indicators:
            sma20 = indicators['sma_20'].iloc[-1]
            sma50 = indicators['sma_50'].iloc[-1]
            current = self.analyzer.data['Close'].iloc[-1]
            
            row = 0
            self.indicators_table.insertRow(row)
            self.indicators_table.setItem(row, 0, QTableWidgetItem("SMA 20"))
            self.indicators_table.setItem(row, 1, QTableWidgetItem(f"${sma20:.2f}"))
            signal = "Bullish" if current > sma20 else "Bearish"
            self.indicators_table.setItem(row, 2, QTableWidgetItem(signal))
            self.indicators_table.setItem(row, 3, QTableWidgetItem("20-period average"))
        
        # RSI
        if 'rsi' in indicators:
            rsi = indicators['rsi'].iloc[-1]
            row = 1
            self.indicators_table.insertRow(row)
            self.indicators_table.setItem(row, 0, QTableWidgetItem("RSI (14)"))
            self.indicators_table.setItem(row, 1, QTableWidgetItem(f"{rsi:.1f}"))
            signal = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
            self.indicators_table.setItem(row, 2, QTableWidgetItem(signal))
            self.indicators_table.setItem(row, 3, QTableWidgetItem("Momentum indicator"))
        
        # MACD
        if 'macd' in indicators:
            macd_val = indicators['macd']['histogram'].iloc[-1]
            row = 2
            self.indicators_table.insertRow(row)
            self.indicators_table.setItem(row, 0, QTableWidgetItem("MACD"))
            self.indicators_table.setItem(row, 1, QTableWidgetItem(f"{macd_val:.4f}"))
            signal = "Bullish" if macd_val > 0 else "Bearish"
            self.indicators_table.setItem(row, 2, QTableWidgetItem(signal))
            self.indicators_table.setItem(row, 3, QTableWidgetItem("Trend & momentum"))
    
    def _display_patterns(self):
        """Display detected patterns"""
        if not self.analyzer:
            return
        
        self.patterns_table.setRowCount(0)
        
        for i, pattern in enumerate(self.analyzer.patterns[:10]):
            self.patterns_table.insertRow(i)
            
            self.patterns_table.setItem(i, 0, QTableWidgetItem(pattern.date.strftime("%Y-%m-%d")))
            self.patterns_table.setItem(i, 1, QTableWidgetItem(pattern.name))
            
            ptype = "Bullish" if pattern.bullish else "Bearish"
            self.patterns_table.setItem(i, 2, QTableWidgetItem(ptype))
            
            self.patterns_table.setItem(i, 3, QTableWidgetItem(f"{pattern.reliability*100:.0f}%"))
            self.patterns_table.setItem(i, 4, QTableWidgetItem(pattern.description))
    
    def _display_support_resistance(self):
        """Display support/resistance levels"""
        if not self.analyzer:
            return
        
        levels = self.analyzer.get_support_resistance_levels(5)
        self.levels_table.setRowCount(0)
        
        for i, level in enumerate(levels):
            self.levels_table.insertRow(i)
            
            self.levels_table.setItem(i, 0, QTableWidgetItem(f"${level.price:.2f}"))
            self.levels_table.setItem(i, 1, QTableWidgetItem(level.type.upper()))
            self.levels_table.setItem(i, 2, QTableWidgetItem(str(level.touches)))
            
            strength_item = QTableWidgetItem(f"{level.strength}%")
            if level.strength > 70:
                strength_item.setForeground(QColor("#4CAF50"))
            self.levels_table.setItem(i, 3, strength_item)
            
            last_touch = level.last_touch.strftime("%Y-%m-%d") if level.last_touch else "N/A"
            self.levels_table.setItem(i, 4, QTableWidgetItem(last_touch))
    
    def _display_volume(self, volume_analysis):
        """Display volume analysis"""
        if not volume_analysis:
            text = "Volume analysis not available"
        else:
            text = f"""
VOLUME ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Volume:         {volume_analysis.current_volume:,.0f}
20-Day Average:         {volume_analysis.average_volume:,.0f}
Volume Ratio:           {volume_analysis.volume_ratio:.2f}x

Volume Trend:           {volume_analysis.volume_trend.upper()}
On-Balance Volume:      {volume_analysis.on_balance_volume:,.0f}
Price-Volume Trend:     {volume_analysis.price_volume_trend:.2f}

INTERPRETATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Higher volume = More conviction behind price move
• Volume should increase on trend direction
• Volume breakouts signal potential breakout trades
• Divergences (price up, volume down) can signal weakness
"""
        
        self.volume_text.setText(text)
    
    def _display_fibonacci(self):
        """Display Fibonacci levels"""
        if not self.analyzer:
            return
        
        fib = self.analyzer.get_fibonacci_levels(52)
        self.fibonacci_table.setRowCount(0)
        
        level_names = {
            '0.0': 'Low (0%)',
            '0.236': 'Minor (23.6%)',
            '0.382': 'Moderate (38.2%)',
            '0.5': 'Medium (50%)',
            '0.618': 'Major (61.8%)',
            '0.786': 'Deep (78.6%)',
            '1.0': 'High (100%)'
        }
        
        for i, (level_pct, price) in enumerate(fib.levels.items()):
            self.fibonacci_table.insertRow(i)
            
            self.fibonacci_table.setItem(i, 0, QTableWidgetItem(level_pct))
            self.fibonacci_table.setItem(i, 1, QTableWidgetItem(f"${price:.2f}"))
            self.fibonacci_table.setItem(i, 2, QTableWidgetItem(level_names.get(level_pct, '')))
