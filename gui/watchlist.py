"""Watchlist tab - Manage tracked stocks"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


class WatchlistTab(QWidget):
    """Manage watchlist of tracked stocks"""
    
    def __init__(self, db, cache):
        super().__init__()
        self.db = db
        self.cache = cache
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("⭐ My Watchlist")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Add to watchlist
        add_layout = QHBoxLayout()
        
        add_layout.addWidget(QLabel("Add Stock:"))
        self.add_symbol = QLineEdit()
        self.add_symbol.setPlaceholderText("e.g., AAPL")
        add_layout.addWidget(self.add_symbol)
        
        add_btn = QPushButton("➕ Add to Watchlist")
        add_btn.clicked.connect(self.add_to_watchlist)
        add_layout.addWidget(add_btn)
        
        add_layout.addStretch()
        layout.addLayout(add_layout)
        
        # Watchlist table
        watchlist_label = QLabel("Your Tracked Stocks")
        watchlist_font = QFont()
        watchlist_font.setPointSize(12)
        watchlist_font.setBold(True)
        watchlist_label.setFont(watchlist_font)
        layout.addWidget(watchlist_label)
        
        self.watchlist_table = QTableWidget()
        self.watchlist_table.setColumnCount(8)
        self.watchlist_table.setHorizontalHeaderLabels([
            "Symbol", "Price", "Change", "Target", "Score", "Notes", "Date Added", "Action"
        ])
        self.watchlist_table.itemDoubleClicked.connect(self.on_stock_selected)
        layout.addWidget(self.watchlist_table)
        
        # Notes section
        notes_label = QLabel("Notes for Selected Stock")
        notes_font = QFont()
        notes_font.setPointSize(11)
        notes_font.setBold(True)
        notes_label.setFont(notes_font)
        layout.addWidget(notes_label)
        
        notes_layout = QHBoxLayout()
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(100)
        notes_layout.addWidget(self.notes_text)
        
        save_btn = QPushButton("💾 Save Notes")
        save_btn.clicked.connect(self.save_notes)
        notes_layout.addWidget(save_btn)
        
        layout.addLayout(notes_layout)
    
    def add_to_watchlist(self):
        """Add stock to watchlist"""
        symbol = self.add_symbol.text().strip().upper()
        if symbol:
            # Add to database
            pass
    
    def on_stock_selected(self, item):
        """Handle stock selection"""
        pass
    
    def save_notes(self):
        """Save notes for selected stock"""
        pass
