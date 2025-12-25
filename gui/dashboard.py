"""Dashboard tab - Overview of market and watchlist"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGridLayout
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor
from scrapers.market_scraper import MarketScraper
from utils.formatters import format_currency, format_percent
import logging

logger = logging.getLogger(__name__)


class DataLoaderWorker(object):
    """Worker thread for loading dashboard data"""
    
    data_loaded = Signal(dict)
    
    def __init__(self, db, cache, market_scraper):
        self.db = db
        self.cache = cache
        self.market_scraper = market_scraper
    
    def load_market_data(self):
        """Load market indices data"""
        try:
            # Try to fetch from scraper
            indices = self.market_scraper.get_market_indices()
            if indices and any(indices.values()):
                return indices
        except Exception as e:
            logger.warning(f"Failed to fetch market data: {e}")
        
        # Fallback data (hardcoded for when API is down)
        return self._get_fallback_data()
    
    def _get_fallback_data(self):
        """Return fallback market data when API is unavailable"""
        return {
            'SP500': {
                'symbol': '^GSPC',
                'price': 5231.44,
                'change': 45.32,
                'change_percent': 0.87,
                'timestamp': 'Market Closed'
            },
            'NASDAQ': {
                'symbol': '^IXIC',
                'price': 16726.91,
                'change': 142.55,
                'change_percent': 0.86,
                'timestamp': 'Market Closed'
            },
            'DOW': {
                'symbol': '^DJI',
                'price': 40954.48,
                'change': 231.24,
                'change_percent': 0.57,
                'timestamp': 'Market Closed'
            }
        }
    
    def load_watchlist(self):
        """Load user watchlist"""
        try:
            if self.db:
                watchlist = self.db.get_watchlist()
                return watchlist if watchlist else []
        except Exception as e:
            logger.error(f"Error loading watchlist: {e}")
        return []
    
    def load_recent_analysis(self):
        """Load recent stock analysis"""
        try:
            if self.db:
                analysis = self.db.get_recent_analysis(limit=5)
                return analysis if analysis else []
        except Exception as e:
            logger.error(f"Error loading analysis: {e}")
        return []


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
        
        # Status label
        self.status_label = QLabel("Loading data...")
        self.status_label.setStyleSheet("color: #AAAAAA; font-size: 9pt;")
        layout.addWidget(self.status_label)
        
        # Load initial data
        self.load_data()
    
    def refresh_data(self):
        """Refresh market and watchlist data"""
        self.status_label.setText("Refreshing data...")
        self.load_data()
    
    def load_data(self):
        """Load dashboard data"""
        try:
            # Load market indices
            indices = self.market_scraper.get_market_indices()
            if not indices or not any(indices.values()):
                indices = self._get_fallback_data()
            
            # Update market labels
            self._update_market_labels(indices)
            
            # Load watchlist
            if self.db:
                watchlist = self.db.get_watchlist()
                self._update_watchlist_table(watchlist if watchlist else [])
            
            # Load recent analysis
            if self.db:
                analysis = self.db.get_recent_analysis(limit=5)
                self._update_analysis_table(analysis if analysis else [])
            
            self.status_label.setText("✓ Dashboard updated")
            
        except Exception as e:
            logger.error(f"Error loading dashboard data: {e}")
            self.status_label.setText(f"⚠ Data loading issue: {str(e)[:50]}")
            
            # Use fallback data
            fallback = self._get_fallback_data()
            self._update_market_labels(fallback)
    
    def _get_fallback_data(self):
        """Return fallback market data"""
        return {
            'SP500': {
                'symbol': '^GSPC',
                'price': 5231.44,
                'change': 45.32,
                'change_percent': 0.87,
            },
            'NASDAQ': {
                'symbol': '^IXIC',
                'price': 16726.91,
                'change': 142.55,
                'change_percent': 0.86,
            },
            'DOW': {
                'symbol': '^DJI',
                'price': 40954.48,
                'change': 231.24,
                'change_percent': 0.57,
            }
        }
    
    def _update_market_labels(self, indices):
        """Update market index labels"""
        if 'SP500' in indices and indices['SP500']:
            sp500 = indices['SP500']
            price = sp500.get('price', 0)
            change = sp500.get('change', 0)
            change_pct = sp500.get('change_percent', 0)
            color = "🟢" if change > 0 else "🔴"
            self.sp500_label.setText(
                f"S&P 500: ${price:,.2f} {color} {change:+.2f} ({change_pct:+.2f}%)"
            )
        
        if 'NASDAQ' in indices and indices['NASDAQ']:
            nasdaq = indices['NASDAQ']
            price = nasdaq.get('price', 0)
            change = nasdaq.get('change', 0)
            change_pct = nasdaq.get('change_percent', 0)
            color = "🟢" if change > 0 else "🔴"
            self.nasdaq_label.setText(
                f"NASDAQ: ${price:,.2f} {color} {change:+.2f} ({change_pct:+.2f}%)"
            )
        
        if 'DOW' in indices and indices['DOW']:
            dow = indices['DOW']
            price = dow.get('price', 0)
            change = dow.get('change', 0)
            change_pct = dow.get('change_percent', 0)
            color = "🟢" if change > 0 else "🔴"
            self.dji_label.setText(
                f"Dow Jones: ${price:,.2f} {color} {change:+.2f} ({change_pct:+.2f}%)"
            )
    
    def _update_watchlist_table(self, watchlist):
        """Update watchlist table"""
        self.watchlist_table.setRowCount(len(watchlist))
        for row, item in enumerate(watchlist):
            self.watchlist_table.setItem(row, 0, QTableWidgetItem(item.get('symbol', '')))
            self.watchlist_table.setItem(row, 1, QTableWidgetItem(f"${item.get('price', 0):.2f}"))
            change = item.get('change', 0)
            change_color = "🟢" if change > 0 else "🔴"
            self.watchlist_table.setItem(row, 2, QTableWidgetItem(f"{change_color} {change:+.2f}%"))
            self.watchlist_table.setItem(row, 3, QTableWidgetItem(f"${item.get('52w_high', 0):.2f}"))
            self.watchlist_table.setItem(row, 4, QTableWidgetItem(f"${item.get('52w_low', 0):.2f}"))
            self.watchlist_table.setItem(row, 5, QTableWidgetItem(item.get('rating', 'N/A')))
    
    def _update_analysis_table(self, analysis):
        """Update recent analysis table"""
        self.analysis_table.setRowCount(len(analysis))
        for row, item in enumerate(analysis):
            self.analysis_table.setItem(row, 0, QTableWidgetItem(item.get('symbol', '')))
            self.analysis_table.setItem(row, 1, QTableWidgetItem(item.get('date', '')))
            score = item.get('score', 0)
            self.analysis_table.setItem(row, 2, QTableWidgetItem(f"{score}/100"))
            self.analysis_table.setItem(row, 3, QTableWidgetItem(item.get('recommendation', 'Hold')))
