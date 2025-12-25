"""Stock search tab - Find and research stocks"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor
from scrapers.stock_scraper import StockScraper


class StockSearchTab(QWidget):
    """Search for stocks and view quick analysis"""
    
    def __init__(self, db, cache):
        super().__init__()
        self.db = db
        self.cache = cache
        self.stock_scraper = StockScraper()
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🔍 Stock Search")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Search bar
        search_layout = QHBoxLayout()
        
        search_label = QLabel("Search by symbol or company:")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("e.g., AAPL, Apple, MSFT...")
        self.search_input.returnPressed.connect(self.search)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.clicked.connect(self.search)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Min P/E:"))
        self.min_pe = QSpinBox()
        self.min_pe.setValue(0)
        filter_layout.addWidget(self.min_pe)
        
        filter_layout.addWidget(QLabel("Max P/E:"))
        self.max_pe = QSpinBox()
        self.max_pe.setValue(100)
        filter_layout.addWidget(self.max_pe)
        
        filter_layout.addWidget(QLabel("Dividend Yield Min:"))
        self.min_yield = QSpinBox()
        self.min_yield.setValue(0)
        filter_layout.addWidget(self.min_yield)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Results table
        results_label = QLabel("Search Results")
        results_font = QFont()
        results_font.setPointSize(12)
        results_font.setBold(True)
        results_label.setFont(results_font)
        layout.addWidget(results_label)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "Symbol", "Company", "Price", "P/E Ratio", "Dividend Yield", 
            "Market Cap", "Rating", "Action"
        ])
        self.results_table.itemDoubleClicked.connect(self.on_stock_selected)
        layout.addWidget(self.results_table)
    
    def search(self):
        """Perform stock search"""
        query = self.search_input.text().strip()
        if query:
            # Search logic would go here
            pass
    
    def on_stock_selected(self, item):
        """Handle stock selection"""
        row = item.row()
        # Navigate to analysis tab with selected stock
        pass
