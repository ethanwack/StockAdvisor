"""Dashboard tab - Overview of market and watchlist"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGridLayout
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor
from scrapers.market_scraper import MarketScraper
from utils.formatters import format_currency, format_percent


class DashboardTab(QWidget):
    """Dashboard showing market overview and watchlist summary"""
    
    def __init__(self, db, cache):
        super().__init__()
        self.db = db
        self.cache = cache
        self.market_scraper = MarketScraper()
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📊 Market Dashboard")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Market overview
        overview_layout = QHBoxLayout()
        
        self.sp500_label = QLabel("S&P 500: Loading...")
        self.nasdaq_label = QLabel("NASDAQ: Loading...")
        self.dji_label = QLabel("Dow Jones: Loading...")
        
        overview_layout.addWidget(self.sp500_label)
        overview_layout.addWidget(self.nasdaq_label)
        overview_layout.addWidget(self.dji_label)
        overview_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        overview_layout.addWidget(refresh_btn)
        
        layout.addLayout(overview_layout)
        
        # Watchlist summary
        watchlist_label = QLabel("Your Watchlist Summary")
        watchlist_font = QFont()
        watchlist_font.setPointSize(12)
        watchlist_font.setBold(True)
        watchlist_label.setFont(watchlist_font)
        layout.addWidget(watchlist_label)
        
        self.watchlist_table = QTableWidget()
        self.watchlist_table.setColumnCount(6)
        self.watchlist_table.setHorizontalHeaderLabels([
            "Symbol", "Price", "Change", "52W High", "52W Low", "Analyst Rating"
        ])
        layout.addWidget(self.watchlist_table)
        
        # Recent analysis
        analysis_label = QLabel("Recent Analysis")
        analysis_font = QFont()
        analysis_font.setPointSize(12)
        analysis_font.setBold(True)
        analysis_label.setFont(analysis_font)
        layout.addWidget(analysis_label)
        
        self.analysis_table = QTableWidget()
        self.analysis_table.setColumnCount(4)
        self.analysis_table.setHorizontalHeaderLabels([
            "Stock", "Analysis Date", "Score", "Recommendation"
        ])
        layout.addWidget(self.analysis_table)
        
        # Load initial data
        self.load_data()
    
    def refresh_data(self):
        """Refresh market and watchlist data"""
        self.load_data()
    
    def load_data(self):
        """Load dashboard data in background thread"""
        # This would fetch from scrapers
        pass
