"""
Options Trading GUI Tab
Interface for options pricing, Greeks analysis, and strategy building
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
import math

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QSpinBox, QDoubleSpinBox,
    QDateEdit, QGroupBox, QTabWidget, QMessageBox, QProgressBar,
    QCheckBox, QDialog, QFormLayout, QSlider, QFrame
)
from PySide6.QtCore import Qt, QDate, QSize, QTimer, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import QPointF

try:
    from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
    CHART_AVAILABLE = True
except ImportError:
    CHART_AVAILABLE = False

from services.options_analyzer import (
    OptionsAnalyzer, OptionType, StrategyType, Option, Strategy
)


class OptionsTab(QWidget):
    """Main Options Trading Tab"""
    
    def __init__(self, db=None, cache=None):
        super().__init__()
        self.db = db
        self.cache = cache
        self.analyzer = OptionsAnalyzer()
        self.current_option: Optional[Option] = None
        self.current_strategy: Optional[Strategy] = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Create tabs for different analysis modes
        tabs = QTabWidget()
        tabs.addTab(self._create_pricer_tab(), "📊 Option Pricer")
        tabs.addTab(self._create_strategy_builder_tab(), "🎯 Strategy Builder")
        tabs.addTab(self._create_strategy_analyzer_tab(), "📈 Strategy Analysis")
        tabs.addTab(self._create_greeks_tab(), "🔢 Greeks Dashboard")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def _create_pricer_tab(self) -> QWidget:
        """Create single option pricing tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Input section
        input_group = QGroupBox("Option Parameters")
        input_layout = QFormLayout()
        
        # Symbol
        self.pricer_symbol = QLineEdit()
        self.pricer_symbol.setPlaceholderText("e.g., AAPL")
        self.pricer_symbol.setText("AAPL")
        input_layout.addRow("Stock Symbol:", self.pricer_symbol)
        
        # Option type
        self.pricer_option_type = QComboBox()
        self.pricer_option_type.addItems(["CALL", "PUT"])
        input_layout.addRow("Option Type:", self.pricer_option_type)
        
        # Strike price
        self.pricer_strike = QDoubleSpinBox()
        self.pricer_strike.setRange(0.01, 10000.0)
        self.pricer_strike.setValue(150.0)
        self.pricer_strike.setSingleStep(1.0)
        input_layout.addRow("Strike Price:", self.pricer_strike)
        
        # Days to expiration
        self.pricer_days = QSpinBox()
        self.pricer_days.setRange(0, 730)  # Up to 2 years
        self.pricer_days.setValue(30)
        input_layout.addRow("Days to Expiration:", self.pricer_days)
        
        # Volatility
        self.pricer_volatility = QDoubleSpinBox()
        self.pricer_volatility.setRange(0.01, 5.0)
        self.pricer_volatility.setValue(0.25)
        self.pricer_volatility.setSingleStep(0.01)
        self.pricer_volatility.setDecimals(4)
        input_layout.addRow("Volatility (%):", self.pricer_volatility)
        
        # Risk-free rate
        self.pricer_rate = QDoubleSpinBox()
        self.pricer_rate.setRange(0.0, 1.0)
        self.pricer_rate.setValue(0.05)
        self.pricer_rate.setSingleStep(0.01)
        self.pricer_rate.setDecimals(4)
        input_layout.addRow("Risk-Free Rate (%):", self.pricer_rate)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Price button
        price_btn = QPushButton("📊 Price Option")
        price_btn.clicked.connect(self._price_option)
        price_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(price_btn)
        
        # Results section
        results_group = QGroupBox("Option Pricing Results")
        results_layout = QVBoxLayout()
        
        # Results display
        self.pricer_results_text = self._create_results_text_widget()
        results_layout.addWidget(self.pricer_results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        widget.setLayout(layout)
        return widget
    
    def _create_strategy_builder_tab(self) -> QWidget:
        """Create strategy builder tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Strategy selector
        builder_group = QGroupBox("Strategy Builder")
        builder_layout = QFormLayout()
        
        # Symbol
        self.builder_symbol = QLineEdit()
        self.builder_symbol.setText("AAPL")
        builder_layout.addRow("Stock Symbol:", self.builder_symbol)
        
        # Market outlook
        self.builder_outlook = QComboBox()
        self.builder_outlook.addItems(["Bullish", "Bearish", "Neutral"])
        builder_layout.addRow("Market Outlook:", self.builder_outlook)
        
        # Max cost
        self.builder_max_cost = QDoubleSpinBox()
        self.builder_max_cost.setRange(100.0, 100000.0)
        self.builder_max_cost.setValue(5000.0)
        self.builder_max_cost.setSingleStep(500.0)
        builder_layout.addRow("Max Cost ($):", self.builder_max_cost)
        
        # Days to expiration
        self.builder_days = QSpinBox()
        self.builder_days.setRange(1, 365)
        self.builder_days.setValue(30)
        builder_layout.addRow("Days to Expiration:", self.builder_days)
        
        builder_group.setLayout(builder_layout)
        layout.addWidget(builder_group)
        
        # Build button
        build_btn = QPushButton("🎯 Build Strategy")
        build_btn.clicked.connect(self._build_strategy)
        build_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(build_btn)
        
        # Results
        results_group = QGroupBox("Strategy Recommendations")
        results_layout = QVBoxLayout()
        
        self.builder_results_text = self._create_results_text_widget()
        results_layout.addWidget(self.builder_results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        widget.setLayout(layout)
        return widget
    
    def _create_strategy_analyzer_tab(self) -> QWidget:
        """Create strategy analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Analysis controls
        control_group = QGroupBox("Strategy Analysis")
        control_layout = QFormLayout()
        
        # Strategy selector
        self.analyzer_strategy = QComboBox()
        strategies = [st.value.replace("_", " ").title() for st in StrategyType]
        self.analyzer_strategy.addItems(strategies)
        control_layout.addRow("Strategy Type:", self.analyzer_strategy)
        
        # Symbol
        self.analyzer_symbol = QLineEdit()
        self.analyzer_symbol.setText("AAPL")
        control_layout.addRow("Stock Symbol:", self.analyzer_symbol)
        
        # Analysis range
        self.analyzer_min_price = QDoubleSpinBox()
        self.analyzer_min_price.setRange(0.01, 10000.0)
        self.analyzer_min_price.setValue(100.0)
        control_layout.addRow("Min Price:", self.analyzer_min_price)
        
        self.analyzer_max_price = QDoubleSpinBox()
        self.analyzer_max_price.setRange(0.01, 10000.0)
        self.analyzer_max_price.setValue(200.0)
        control_layout.addRow("Max Price:", self.analyzer_max_price)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Analyze button
        analyze_btn = QPushButton("📈 Analyze Strategy")
        analyze_btn.clicked.connect(self._analyze_strategy)
        analyze_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(analyze_btn)
        
        # Chart area
        self.analyzer_chart = QChart()
        self.analyzer_chart.setTitle("Strategy P&L Diagram")
        self.analyzer_chart_view = QChartView(self.analyzer_chart)
        self.analyzer_chart_view.setRenderHint(self.analyzer_chart_view.RenderHint.Antialiasing)
        layout.addWidget(self.analyzer_chart_view)
        
        # Results
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout()
        
        self.analyzer_results_text = self._create_results_text_widget()
        results_layout.addWidget(self.analyzer_results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        widget.setLayout(layout)
        return widget
    
    def _create_greeks_tab(self) -> QWidget:
        """Create Greeks dashboard tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Greeks explanation
        info_group = QGroupBox("Greeks Explained")
        info_layout = QVBoxLayout()
        
        info_text = """
        <b>Greeks:</b> Sensitivity measures for option prices
        
        <b>Delta (Δ):</b> Price change per $1 move in underlying
        • Range: 0 to 1 (calls) or 0 to -1 (puts)
        • ATM option ≈ 0.5 delta
        
        <b>Gamma (Γ):</b> Rate of delta change
        • Highest at-the-money
        • Increases as expiration approaches
        
        <b>Theta (Θ):</b> Time decay per day
        • Positive for short options, negative for long
        • Accelerates as expiration nears
        
        <b>Vega (ν):</b> Volatility sensitivity per 1% change
        • Positive for long options
        • Highest at-the-money
        
        <b>Rho (ρ):</b> Interest rate sensitivity per 1% change
        • More important for longer-dated options
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Greeks visualization
        greeks_group = QGroupBox("Current Greeks")
        greeks_layout = QVBoxLayout()
        
        self.greeks_display_text = self._create_results_text_widget()
        greeks_layout.addWidget(self.greeks_display_text)
        
        greeks_group.setLayout(greeks_layout)
        layout.addWidget(greeks_group)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Show Last Priced Option Greeks")
        refresh_btn.clicked.connect(self._refresh_greeks)
        refresh_btn.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _create_results_text_widget(self):
        """Create a styled text display widget"""
        from PySide6.QtWidgets import QTextEdit
        text = QTextEdit()
        text.setReadOnly(True)
        text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        return text
    
    def _price_option(self):
        """Price a single option"""
        try:
            symbol = self.pricer_symbol.text().upper()
            option_type = OptionType.CALL if self.pricer_option_type.currentText() == "CALL" else OptionType.PUT
            strike = self.pricer_strike.value()
            days = self.pricer_days.value()
            volatility = self.pricer_volatility.value() / 100.0
            risk_free_rate = self.pricer_rate.value() / 100.0
            
            # Create expiration date
            expiration = datetime.now() + timedelta(days=days)
            
            # Price the option
            option = self.analyzer.price_option(
                symbol=symbol,
                option_type=option_type,
                strike=strike,
                expiration=expiration,
                volatility=volatility
            )
            
            self.current_option = option
            
            # Display results
            results = f"""
╔════════════════════════════════════════════════════════╗
║            OPTION PRICING ANALYSIS                     ║
╚════════════════════════════════════════════════════════╝

OPTION DETAILS:
  Symbol:              {symbol}
  Type:                {option_type.value.upper()}
  Strike Price:        ${strike:.2f}
  Current Stock:       ${option.underlying_price:.2f}
  Expiration:          {expiration.strftime('%Y-%m-%d')} ({days} days)

PRICING:
  Option Price:        ${option.price:.2f}
  Intrinsic Value:     ${option.intrinsic_value:.2f}
  Time Value:          ${option.time_value:.2f}
  Moneyness:           {option.moneyness:.4f}

GREEKS (Sensitivity Measures):
  Delta (Δ):           {option.greeks.delta:>10.4f}   (Price sensitivity)
  Gamma (Γ):           {option.greeks.gamma:>10.6f}   (Delta acceleration)
  Theta (Θ):           {option.greeks.theta:>10.4f}   (Time decay/day)
  Vega (ν):            {option.greeks.vega:>10.4f}    (Volatility sensitivity)
  Rho (ρ):             {option.greeks.rho:>10.4f}    (Interest rate sensitivity)

VOLATILITY:
  Input Volatility:    {volatility*100:.2f}%
  Risk-Free Rate:      {risk_free_rate*100:.2f}%
"""
            
            self.pricer_results_text.setText(results)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to price option: {str(e)}")
    
    def _build_strategy(self):
        """Build recommended strategy"""
        try:
            symbol = self.builder_symbol.text().upper()
            outlook = self.builder_outlook.currentText().lower()
            max_cost = self.builder_max_cost.value()
            
            # Get recommendations
            recommendations = self.analyzer.suggest_strategy(symbol, outlook, max_cost)
            
            # Format results
            results = f"""
╔════════════════════════════════════════════════════════╗
║        STRATEGY RECOMMENDATIONS                        ║
╚════════════════════════════════════════════════════════╝

Symbol:              {symbol}
Current Price:       ${recommendations['current_price']:.2f}
Market Outlook:      {outlook.upper()}
Expiration:          {recommendations['expiration']}
Max Cost:            ${max_cost:.2f}

RECOMMENDED STRATEGIES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            
            for i, rec in enumerate(recommendations.get('recommendations', []), 1):
                results += f"""
{i}. {rec['description'].upper()}
   Strategy Type:      {rec['strategy'].replace('_', ' ').title()}
   Total Cost:         ${rec['cost']:.2f}
   Max Profit:         ${rec['max_profit']:.2f}
   Max Loss:           ${rec['max_loss']:.2f}
   Breakeven(s):       {', '.join([f"${be:.2f}" for be in rec['breakevens']]) if rec['breakevens'] else 'N/A'}

"""
            
            self.builder_results_text.setText(results)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to build strategy: {str(e)}")
    
    def _analyze_strategy(self):
        """Analyze strategy P&L"""
        try:
            strategy_type_str = self.analyzer_strategy.currentText().lower().replace(" ", "_")
            strategy_type = StrategyType[strategy_type_str.upper()]
            symbol = self.analyzer_symbol.text().upper()
            min_price = self.analyzer_min_price.value()
            max_price = self.analyzer_max_price.value()
            
            # Get current stock price
            from services.options_analyzer import yf
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
            
            # Create a simple strategy for analysis
            expiration = datetime.now() + timedelta(days=30)
            
            # Configure legs based on strategy type
            legs_config = self._get_strategy_legs(strategy_type, current_price)
            
            strategy = self.analyzer.create_strategy(
                strategy_type=strategy_type,
                symbol=symbol,
                legs_config=legs_config,
                expiration=expiration
            )
            
            self.current_strategy = strategy
            
            # Analyze strategy
            analysis = self.analyzer.analyze_strategy_range(
                strategy,
                (min_price, max_price)
            )
            
            # Plot results
            self._plot_strategy_analysis(analysis)
            
            # Display results
            results = f"""
╔════════════════════════════════════════════════════════╗
║            STRATEGY ANALYSIS                           ║
╚════════════════════════════════════════════════════════╝

STRATEGY:            {analysis['strategy_name']}
Total Cost:          ${analysis['total_cost']:.2f}

PROFIT/LOSS ANALYSIS:
  Max Profit:        ${analysis['max_profit']:.2f}
  Max Loss:          ${analysis['max_loss']:.2f}
  Risk/Reward Ratio: {abs(analysis['max_profit']/analysis['max_loss']) if analysis['max_loss'] != 0 else float('inf'):.2f}

BREAKEVEN POINTS:
  {', '.join([f"${be:.2f}" for be in analysis['breakevens']]) if analysis['breakevens'] else 'N/A'}

PRICE RANGE:
  Min: ${min_price:.2f}
  Max: ${max_price:.2f}
"""
            
            self.analyzer_results_text.setText(results)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to analyze strategy: {str(e)}")
    
    def _plot_strategy_analysis(self, analysis: Dict):
        """Plot strategy P&L diagram"""
        try:
            # Clear chart
            self.analyzer_chart.removeAllSeries()
            
            # Create profit series
            series = QLineSeries()
            series.setName("P&L")
            
            prices = analysis['prices']
            profits = analysis['profits']
            
            for price, profit in zip(prices, profits):
                series.append(QPointF(price, profit))
            
            # Clear and set new chart
            self.analyzer_chart.removeAllSeries()
            self.analyzer_chart.addSeries(series)
            
            # Create axes
            from PySide6.QtChart import QValueAxis
            
            axis_x = QValueAxis()
            axis_x.setTitleText("Stock Price")
            axis_x.setRange(min(prices), max(prices))
            
            axis_y = QValueAxis()
            axis_y.setTitleText("Profit/Loss ($)")
            axis_y.setRange(min(profits) * 1.1, max(profits) * 1.1)
            
            self.analyzer_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            self.analyzer_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)
            
        except Exception as e:
            print(f"Error plotting strategy: {e}")
    
    def _get_strategy_legs(self, strategy_type: StrategyType, current_price: float) -> List[Dict]:
        """Get leg configuration for strategy type"""
        if strategy_type == StrategyType.LONG_CALL:
            return [{'option_type': OptionType.CALL, 'strike': current_price}]
        elif strategy_type == StrategyType.LONG_PUT:
            return [{'option_type': OptionType.PUT, 'strike': current_price}]
        elif strategy_type == StrategyType.SHORT_CALL:
            return [{'option_type': OptionType.CALL, 'strike': current_price}]
        elif strategy_type == StrategyType.SHORT_PUT:
            return [{'option_type': OptionType.PUT, 'strike': current_price}]
        elif strategy_type == StrategyType.BULL_CALL_SPREAD:
            return [
                {'option_type': OptionType.CALL, 'strike': current_price},
                {'option_type': OptionType.CALL, 'strike': current_price * 1.05}
            ]
        elif strategy_type == StrategyType.BEAR_CALL_SPREAD:
            return [
                {'option_type': OptionType.CALL, 'strike': current_price},
                {'option_type': OptionType.CALL, 'strike': current_price * 1.05}
            ]
        elif strategy_type == StrategyType.BULL_PUT_SPREAD:
            return [
                {'option_type': OptionType.PUT, 'strike': current_price},
                {'option_type': OptionType.PUT, 'strike': current_price * 0.95}
            ]
        elif strategy_type == StrategyType.BEAR_PUT_SPREAD:
            return [
                {'option_type': OptionType.PUT, 'strike': current_price},
                {'option_type': OptionType.PUT, 'strike': current_price * 0.95}
            ]
        elif strategy_type == StrategyType.IRON_CONDOR:
            return [
                {'option_type': OptionType.CALL, 'strike': current_price * 1.05},
                {'option_type': OptionType.CALL, 'strike': current_price * 1.10},
                {'option_type': OptionType.PUT, 'strike': current_price * 0.95},
                {'option_type': OptionType.PUT, 'strike': current_price * 0.90}
            ]
        elif strategy_type == StrategyType.BUTTERFLY:
            return [
                {'option_type': OptionType.CALL, 'strike': current_price},
                {'option_type': OptionType.CALL, 'strike': current_price * 1.05},
                {'option_type': OptionType.CALL, 'strike': current_price * 1.05}
            ]
        elif strategy_type == StrategyType.STRADDLE:
            return [
                {'option_type': OptionType.CALL, 'strike': current_price},
                {'option_type': OptionType.PUT, 'strike': current_price}
            ]
        elif strategy_type == StrategyType.STRANGLE:
            return [
                {'option_type': OptionType.CALL, 'strike': current_price * 1.05},
                {'option_type': OptionType.PUT, 'strike': current_price * 0.95}
            ]
        else:
            return [{'option_type': OptionType.CALL, 'strike': current_price}]
    
    def _refresh_greeks(self):
        """Display Greeks from last priced option"""
        if self.current_option:
            greeks_text = f"""
╔════════════════════════════════════════════════════════╗
║               GREEKS ANALYSIS                          ║
╚════════════════════════════════════════════════════════╝

OPTION:              {self.current_option.symbol} {self.current_option.option_type.value.upper()}
Strike:              ${self.current_option.strike:.2f}
Current Stock:       ${self.current_option.underlying_price:.2f}
Days to Expiration:  {self.current_option.days_to_expiration:.1f}

GREEKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Delta (Δ):           {self.current_option.greeks.delta:>10.4f}
  → Price changes by ${self.current_option.greeks.delta:.2f} per $1 move in stock

Gamma (Γ):           {self.current_option.greeks.gamma:>10.6f}
  → Delta changes by {self.current_option.greeks.gamma:.6f} per $1 move in stock

Theta (Θ):           {self.current_option.greeks.theta:>10.4f}
  → Option loses ${abs(self.current_option.greeks.theta):.2f} per day (time decay)

Vega (ν):            {self.current_option.greeks.vega:>10.4f}
  → Price changes by ${self.current_option.greeks.vega:.2f} per 1% volatility change

Rho (ρ):             {self.current_option.greeks.rho:>10.4f}
  → Price changes by ${self.current_option.greeks.rho:.2f} per 1% rate change

INTERPRETATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For every $1 the stock moves:
  • Option moves approximately ${self.current_option.greeks.delta:.2f}
  • Delta changes by approximately {self.current_option.greeks.gamma:.6f}

Time decay impact:
  • Option loses approximately ${abs(self.current_option.greeks.theta):.2f} per day

Volatility impact:
  • Each 1% volatility increase adds ${self.current_option.greeks.vega:.2f} to price
"""
            
            self.greeks_display_text.setText(greeks_text)
        else:
            QMessageBox.information(self, "No Option", "Price an option first to see Greeks")
