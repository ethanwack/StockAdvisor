"""
Personalization Tab GUI
UI for user preferences, learned preferences, and personalized recommendations
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QSlider,
    QCheckBox, QPushButton, QListWidget, QListWidgetItem, QComboBox,
    QSpinBox, QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox,
    QMessageBox, QDialog, QFormLayout, QLineEdit
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QColor, QFont, QIcon
from enum import Enum
import sys

# Import ML personalization
from services.ml_personalization import (
    MLPersonalizationEngine, RiskProfile, InteractionType, UserInteraction
)


class PersonalizationWorker(QThread):
    """Worker thread for personalization tasks"""
    
    recommendations_ready = Signal(list)
    insights_ready = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, engine: MLPersonalizationEngine, user_id: str):
        super().__init__()
        self.engine = engine
        self.user_id = user_id
        self.task = None
        self.candidates = []
    
    def set_get_recommendations(self, candidates: list, limit: int = 10):
        """Set task to get recommendations"""
        self.task = 'recommendations'
        self.candidates = candidates
        self.limit = limit
    
    def set_get_insights(self):
        """Set task to get insights"""
        self.task = 'insights'
    
    def run(self):
        try:
            if self.task == 'recommendations':
                recs = self.engine.get_recommendations(
                    self.user_id,
                    self.candidates,
                    self.limit
                )
                self.recommendations_ready.emit(recs)
            elif self.task == 'insights':
                insights = self.engine.get_profile_insights(self.user_id)
                self.insights_ready.emit(insights)
        except Exception as e:
            self.error_occurred.emit(str(e))


class PersonalizationTab(QWidget):
    """Tab for personalization settings and ML recommendations"""
    
    def __init__(self):
        super().__init__()
        self.engine = MLPersonalizationEngine()
        self.user_id = "default_user"
        self.profile = self.engine.get_or_create_user(self.user_id)
        self.worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Tab 1: Profile & Preferences
        tabs.addTab(self._create_profile_tab(), "👤 Profile")
        
        # Tab 2: Learned Preferences
        tabs.addTab(self._create_learning_tab(), "📚 Learning")
        
        # Tab 3: Recommendations
        tabs.addTab(self._create_recommendations_tab(), "🎯 Recommendations")
        
        # Tab 4: Interaction History
        tabs.addTab(self._create_history_tab(), "📋 History")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def _create_profile_tab(self) -> QWidget:
        """Create profile/preferences tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Risk Profile Section
        risk_group = QGroupBox("Risk Profile")
        risk_layout = QVBoxLayout()
        
        # Risk slider
        risk_label = QLabel("Risk Tolerance: Moderate")
        risk_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.risk_slider = QSlider(Qt.Horizontal)
        self.risk_slider.setMinimum(0)
        self.risk_slider.setMaximum(2)
        self.risk_slider.setValue(1)
        self.risk_slider.setTickPosition(QSlider.TicksBelow)
        self.risk_slider.setTickInterval(1)
        self.risk_slider.valueChanged.connect(lambda: self._on_risk_changed(risk_label))
        
        risk_layout.addWidget(QLabel("Conservative ← → Aggressive"))
        risk_layout.addWidget(self.risk_slider)
        risk_layout.addWidget(risk_label)
        
        risk_group.setLayout(risk_layout)
        layout.addWidget(risk_group)
        
        # Favorite Sectors
        sectors_group = QGroupBox("Favorite Sectors")
        sectors_layout = QVBoxLayout()
        
        sectors = [
            "Technology", "Healthcare", "Finance", "Energy",
            "Consumer", "Industrials", "Materials", "Utilities",
            "Real Estate", "Communications"
        ]
        
        self.sector_checkboxes = {}
        for sector in sectors:
            cb = QCheckBox(sector)
            cb.stateChanged.connect(self._on_sectors_changed)
            self.sector_checkboxes[sector] = cb
            sectors_layout.addWidget(cb)
        
        sectors_group.setLayout(sectors_layout)
        layout.addWidget(sectors_group)
        
        # Watchlist Management
        watchlist_group = QGroupBox("Watchlist")
        watchlist_layout = QVBoxLayout()
        
        # Add to watchlist
        add_layout = QHBoxLayout()
        self.watchlist_input = QLineEdit()
        self.watchlist_input.setPlaceholderText("Enter symbol (e.g., AAPL)")
        add_btn = QPushButton("Add to Watchlist")
        add_btn.clicked.connect(self._add_to_watchlist)
        add_layout.addWidget(self.watchlist_input)
        add_layout.addWidget(add_btn)
        watchlist_layout.addLayout(add_layout)
        
        # Watchlist display
        self.watchlist_widget = QListWidget()
        self._update_watchlist_display()
        watchlist_layout.addWidget(QLabel("Your Watchlist:"))
        watchlist_layout.addWidget(self.watchlist_widget)
        
        watchlist_group.setLayout(watchlist_layout)
        layout.addWidget(watchlist_group)
        
        # Save button
        save_btn = QPushButton("💾 Save Preferences")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        save_btn.clicked.connect(self._save_preferences)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_learning_tab(self) -> QWidget:
        """Create learning/preferences tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Insights
        layout.addWidget(QLabel("📊 Learned Preferences"))
        
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setStyleSheet("background-color: #f5f5f5;")
        layout.addWidget(self.insights_text)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Insights")
        refresh_btn.clicked.connect(self._refresh_insights)
        layout.addWidget(refresh_btn)
        
        # Clear history button
        clear_btn = QPushButton("🗑️ Clear Interaction History")
        clear_btn.setStyleSheet("background-color: #f44336; color: white;")
        clear_btn.clicked.connect(self._clear_history)
        layout.addWidget(clear_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_recommendations_tab(self) -> QWidget:
        """Create recommendations tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instructions
        layout.addWidget(QLabel("🎯 Personalized Recommendations"))
        instructions = QLabel(
            "Based on your preferences and interaction history, "
            "here are personalized stock recommendations."
        )
        instructions.setStyleSheet("color: #666;")
        layout.addWidget(instructions)
        
        # Recommendations table
        self.recommendations_table = QTableWidget()
        self.recommendations_table.setColumnCount(6)
        self.recommendations_table.setHorizontalHeaderLabels(
            ["Symbol", "Score", "Confidence", "Risk", "Reason", "Return %"]
        )
        self.recommendations_table.setColumnWidth(0, 80)
        self.recommendations_table.setColumnWidth(1, 80)
        self.recommendations_table.setColumnWidth(2, 100)
        self.recommendations_table.setColumnWidth(3, 80)
        self.recommendations_table.setColumnWidth(4, 300)
        self.recommendations_table.setColumnWidth(5, 100)
        layout.addWidget(self.recommendations_table)
        
        # Generate recommendations button
        gen_btn = QPushButton("🚀 Generate Recommendations")
        gen_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        gen_btn.clicked.connect(self._generate_recommendations)
        layout.addWidget(gen_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_history_tab(self) -> QWidget:
        """Create interaction history tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📋 Interaction History"))
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(
            ["Timestamp", "Type", "Symbol", "Details"]
        )
        self.history_table.setColumnWidth(0, 150)
        self.history_table.setColumnWidth(1, 150)
        self.history_table.setColumnWidth(2, 80)
        self.history_table.setColumnWidth(3, 300)
        
        # Add sample interactions
        self._update_history_display()
        
        layout.addWidget(self.history_table)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        self._update_stats()
        stats_layout.addWidget(self.stats_text)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        widget.setLayout(layout)
        return widget
    
    def _on_risk_changed(self, label: QLabel):
        """Handle risk slider change"""
        risk_map = {0: "Conservative", 1: "Moderate", 2: "Aggressive"}
        label.setText(f"Risk Tolerance: {risk_map[self.risk_slider.value()]}")
    
    def _on_sectors_changed(self):
        """Handle sector checkbox changes"""
        pass  # Will be saved when user clicks save
    
    def _add_to_watchlist(self):
        """Add symbol to watchlist"""
        symbol = self.watchlist_input.text().upper()
        if symbol and symbol not in self.profile.watchlist:
            self.profile.watchlist.append(symbol)
            self.watchlist_input.clear()
            self._update_watchlist_display()
            
            # Record interaction
            interaction = UserInteraction(
                interaction_type=InteractionType.ADDED_TO_WATCHLIST,
                symbol=symbol
            )
            self.engine.record_interaction(self.user_id, interaction)
    
    def _update_watchlist_display(self):
        """Update watchlist display"""
        self.watchlist_widget.clear()
        for symbol in self.profile.watchlist:
            item = QListWidgetItem(f"${symbol}")
            item.setForeground(QColor("#2196F3"))
            self.watchlist_widget.addItem(item)
            
            # Add remove button functionality (right-click)
            item.setFlags(item.flags() | Qt.ItemIsSelectable)
    
    def _save_preferences(self):
        """Save user preferences"""
        # Get risk profile
        risk_idx = self.risk_slider.value()
        risk_map = {0: RiskProfile.CONSERVATIVE, 1: RiskProfile.MODERATE, 2: RiskProfile.AGGRESSIVE}
        risk_profile = risk_map[risk_idx]
        
        # Get favorite sectors
        favorite_sectors = [
            sector for sector, cb in self.sector_checkboxes.items()
            if cb.isChecked()
        ]
        
        # Update profile
        self.engine.update_user_profile(
            self.user_id,
            risk_profile=risk_profile,
            favorite_sectors=favorite_sectors,
            watchlist=self.profile.watchlist
        )
        
        QMessageBox.information(self, "Success", "✅ Preferences saved successfully!")
    
    def _refresh_insights(self):
        """Refresh learned insights"""
        self.worker = PersonalizationWorker(self.engine, self.user_id)
        self.worker.set_get_insights()
        self.worker.insights_ready.connect(self._on_insights_ready)
        self.worker.start()
    
    def _on_insights_ready(self, insights: dict):
        """Handle insights ready"""
        text = f"""
╔════════════════════════════════════════════════════════╗
║         YOUR LEARNED PREFERENCES                       ║
╚════════════════════════════════════════════════════════╝

PROFILE SUMMARY:
• Risk Profile:      {insights['risk_profile'].upper()}
• Total Interactions: {insights['interaction_count']}
• Watchlist Size:     {insights['watchlist_size']}

FAVORITE SYMBOLS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for symbol in insights['favorite_symbols'][:5]:
            text += f"  • {symbol}\n"
        
        prefs = insights['preferences']
        text += f"""
TOP SECTORS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for sector, count in prefs.get('sector_preferences', [])[:5]:
            text += f"  • {sector} ({count} interactions)\n"
        
        text += f"""
INFERRED PROFILE:
• Risk Profile:  {prefs.get('inferred_risk_profile', 'moderate').upper()}

This profile is learned from your behavior. You can override
it in the Profile tab above.
"""
        
        self.insights_text.setText(text)
    
    def _clear_history(self):
        """Clear interaction history"""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all interaction history?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.profile.interactions.clear()
            self._update_history_display()
            self._update_stats()
            QMessageBox.information(self, "Success", "✅ History cleared!")
    
    def _update_history_display(self):
        """Update history table display"""
        self.history_table.setRowCount(0)
        
        for i, interaction in enumerate(reversed(self.profile.interactions[-50:])):
            self.history_table.insertRow(i)
            
            # Timestamp
            timestamp_item = QTableWidgetItem(
                interaction.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            )
            self.history_table.setItem(i, 0, timestamp_item)
            
            # Type
            type_item = QTableWidgetItem(interaction.interaction_type.value.replace('_', ' ').title())
            self.history_table.setItem(i, 1, type_item)
            
            # Symbol
            symbol_item = QTableWidgetItem(interaction.symbol or "—")
            if interaction.symbol:
                symbol_item.setForeground(QColor("#2196F3"))
            self.history_table.setItem(i, 2, symbol_item)
            
            # Metadata
            metadata_str = ", ".join(f"{k}:{v}" for k, v in interaction.metadata.items())
            details_item = QTableWidgetItem(metadata_str or "—")
            self.history_table.setItem(i, 3, details_item)
    
    def _update_stats(self):
        """Update statistics"""
        total_interactions = len(self.profile.interactions)
        
        # Count by type
        type_counts = {}
        for interaction in self.profile.interactions:
            key = interaction.interaction_type.value
            type_counts[key] = type_counts.get(key, 0) + 1
        
        stats_text = f"""
INTERACTION STATISTICS:
• Total:              {total_interactions}
• Watchlist Adds:     {type_counts.get('added_to_watchlist', 0)}
• Stocks Viewed:      {type_counts.get('viewed_stock', 0)}
• Analysis Views:     {type_counts.get('viewed_analysis', 0)}
• Alerts Set:         {type_counts.get('set_alert', 0)}
"""
        
        self.stats_text.setText(stats_text)
    
    def _generate_recommendations(self):
        """Generate personalized recommendations"""
        # For now, use sample candidates
        candidates = [
            {
                'symbol': 'AAPL',
                'rsi': 35,
                'macd_signal': 1.5,
                'momentum_pct': 2.5,
                'pe_ratio': 22,
                'dividend_yield': 0.006,
                'volatility': 0.22,
                'sector': 'Technology',
                'sentiment_score': 0.6,
                'predicted_return': 3.5
            },
            {
                'symbol': 'MSFT',
                'rsi': 40,
                'macd_signal': 2.1,
                'momentum_pct': 3.2,
                'pe_ratio': 25,
                'dividend_yield': 0.008,
                'volatility': 0.20,
                'sector': 'Technology',
                'sentiment_score': 0.7,
                'predicted_return': 4.2
            },
            {
                'symbol': 'JNJ',
                'rsi': 28,
                'macd_signal': -0.5,
                'momentum_pct': -1.2,
                'pe_ratio': 18,
                'dividend_yield': 0.028,
                'volatility': 0.15,
                'sector': 'Healthcare',
                'sentiment_score': 0.4,
                'predicted_return': 2.1
            },
            {
                'symbol': 'XOM',
                'rsi': 32,
                'macd_signal': 1.2,
                'momentum_pct': 1.8,
                'pe_ratio': 12,
                'dividend_yield': 0.035,
                'volatility': 0.28,
                'sector': 'Energy',
                'sentiment_score': 0.3,
                'predicted_return': 1.5
            },
            {
                'symbol': 'GOOGL',
                'rsi': 45,
                'macd_signal': 0.8,
                'momentum_pct': 2.1,
                'pe_ratio': 24,
                'dividend_yield': 0.0,
                'volatility': 0.23,
                'sector': 'Technology',
                'sentiment_score': 0.5,
                'predicted_return': 3.8
            }
        ]
        
        # Get recommendations
        recs = self.engine.get_recommendations(self.user_id, candidates, 10)
        
        # Display in table
        self.recommendations_table.setRowCount(0)
        for i, rec in enumerate(recs):
            self.recommendations_table.insertRow(i)
            
            # Symbol
            symbol_item = QTableWidgetItem(rec.symbol)
            symbol_item.setForeground(QColor("#2196F3"))
            self.recommendations_table.setItem(i, 0, symbol_item)
            
            # Score
            score_item = QTableWidgetItem(f"{rec.score:.1f}")
            if rec.score > 70:
                score_item.setForeground(QColor("#4CAF50"))
            elif rec.score > 50:
                score_item.setForeground(QColor("#FF9800"))
            else:
                score_item.setForeground(QColor("#f44336"))
            self.recommendations_table.setItem(i, 1, score_item)
            
            # Confidence
            conf_item = QTableWidgetItem(f"{rec.confidence*100:.0f}%")
            self.recommendations_table.setItem(i, 2, conf_item)
            
            # Risk
            risk_item = QTableWidgetItem(rec.risk_level.capitalize())
            self.recommendations_table.setItem(i, 3, risk_item)
            
            # Reason
            reason_item = QTableWidgetItem("; ".join(rec.reasons[:2]))
            self.recommendations_table.setItem(i, 4, reason_item)
            
            # Predicted return
            if rec.predicted_return:
                ret_item = QTableWidgetItem(f"{rec.predicted_return:.2f}%")
                if rec.predicted_return > 0:
                    ret_item.setForeground(QColor("#4CAF50"))
                self.recommendations_table.setItem(i, 5, ret_item)
    
    def record_interaction(self, interaction_type: InteractionType, symbol: str = None, metadata: dict = None):
        """Record user interaction (called from other tabs)"""
        interaction = UserInteraction(
            interaction_type=interaction_type,
            symbol=symbol,
            metadata=metadata or {}
        )
        self.engine.record_interaction(self.user_id, interaction)
