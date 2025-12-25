#!/usr/bin/env python3
"""
Stock Advisor Pro - Python GUI Application
Professional stock research and analysis tool inspired by Motley Fool
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QProgressBar, QMessageBox, QStatusBar, QSplitter, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import QDateTime

from gui.dashboard import DashboardTab
from gui.stock_search import StockSearchTab
from gui.stock_analysis import StockAnalysisTab
from gui.watchlist import WatchlistTab
from gui.reports import ReportsTab
from gui.chatbot import ChatbotTab
from utils.database import Database
from utils.cache import CacheManager

class StockAdvisorApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Advisor Pro - Investment Research Tool")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize database and cache
        self.db = Database()
        self.cache = CacheManager()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Add tabs
        self.dashboard_tab = DashboardTab(self.db, self.cache)
        self.search_tab = StockSearchTab(self.db, self.cache)
        self.analysis_tab = StockAnalysisTab(self.db, self.cache)
        self.watchlist_tab = WatchlistTab(self.db, self.cache)
        self.reports_tab = ReportsTab(self.db, self.cache)
        self.chatbot_tab = ChatbotTab(self.db, self.cache)
        
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        self.tabs.addTab(self.search_tab, "🔍 Stock Search")
        self.tabs.addTab(self.analysis_tab, "📈 Analysis")
        self.tabs.addTab(self.chatbot_tab, "💬 ChatBot")
        self.tabs.addTab(self.watchlist_tab, "⭐ Watchlist")
        self.tabs.addTab(self.reports_tab, "📄 Reports")
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Apply dark theme
        self.apply_dark_theme()
        
    def apply_dark_theme(self):
        """Apply professional dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 20px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0d47a1;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLineEdit, QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton {
                background-color: #0d47a1;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0c3aa3;
            }
            QTableWidget {
                background-color: #2d2d2d;
                alternate-background-color: #252525;
                gridline-color: #3c3c3c;
            }
            QHeaderView::section {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 5px;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #0d47a1;
                border-radius: 6px;
            }
        """)
    
    def closeEvent(self, event):
        """Handle window close event with proper cleanup"""
        try:
            # Attempt to clean up chatbot tab if it exists
            if hasattr(self, 'chatbot_tab') and hasattr(self.chatbot_tab, 'closeEvent'):
                try:
                    self.chatbot_tab.closeEvent(event)
                except:
                    pass
        except:
            pass
        
        super().closeEvent(event)


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    window = StockAdvisorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
