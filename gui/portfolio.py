"""Portfolio tab - Upload and manage your stock holdings"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from services.portfolio_manager import Portfolio, PortfolioImporter
import logging

logger = logging.getLogger(__name__)


class PortfolioTab(QWidget):
    """Tab for portfolio management"""
    
    def __init__(self, db, cache):
        super().__init__()
        self.db = db
        self.cache = cache
        self.portfolio = None
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("💼 Portfolio Manager")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel(
            "Upload a CSV file with your stock holdings. Format: Symbol, Shares, CostBasis, DatePurchased, Notes"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #AAAAAA; font-size: 9pt;")
        layout.addWidget(instructions)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.upload_btn = QPushButton("📤 Upload CSV")
        self.upload_btn.clicked.connect(self.upload_portfolio)
        button_layout.addWidget(self.upload_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh Prices")
        self.refresh_btn.clicked.connect(self.refresh_prices)
        button_layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("💾 Export CSV")
        self.export_btn.clicked.connect(self.export_portfolio)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Summary section
        summary_layout = QHBoxLayout()
        
        self.summary_label = QLabel("No portfolio loaded")
        self.summary_label.setStyleSheet("color: #87CEEB; font-size: 11pt; font-weight: bold;")
        summary_layout.addWidget(self.summary_label)
        
        summary_layout.addStretch()
        layout.addLayout(summary_layout)
        
        # Holdings table
        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(9)
        self.holdings_table.setHorizontalHeaderLabels([
            "Symbol", "Shares", "Cost/Share", "Total Cost", 
            "Current Price", "Current Value", "Gain/Loss", "Return %", "Purchased"
        ])
        
        # Set column widths
        for i in range(9):
            self.holdings_table.setColumnWidth(i, 110)
        
        layout.addWidget(self.holdings_table)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status bar
        self.status_label = QLabel("Ready to upload portfolio")
        self.status_label.setStyleSheet("color: #AAAAAA; font-size: 9pt;")
        layout.addWidget(self.status_label)
        
        # Timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.auto_refresh_prices)
        self.update_timer.start(300000)  # Refresh every 5 minutes
    
    def upload_portfolio(self):
        """Upload portfolio from CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Portfolio CSV", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        self.status_label.setText("📥 Importing portfolio...")
        self.progress_bar.setVisible(True)
        
        try:
            portfolio = PortfolioImporter.import_from_csv(file_path)
            
            if portfolio and len(portfolio.holdings) > 0:
                self.portfolio = portfolio
                self.status_label.setText("📥 Updating prices...")
                self.progress_bar.setVisible(True)
                
                # Update prices in background
                if self.portfolio.update_prices():
                    self.display_portfolio()
                    self.export_btn.setEnabled(True)
                    self.status_label.setText(
                        f"✓ Portfolio loaded: {len(self.portfolio.holdings)} holdings"
                    )
                else:
                    QMessageBox.warning(
                        self, "Warning",
                        "Portfolio imported but some prices couldn't be fetched"
                    )
                    self.display_portfolio()
            else:
                QMessageBox.warning(self, "Error", "No holdings found in CSV file")
                self.status_label.setText("❌ Import failed")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import portfolio: {str(e)}")
            self.status_label.setText("❌ Import error")
        
        finally:
            self.progress_bar.setVisible(False)
    
    def display_portfolio(self):
        """Display portfolio in table"""
        if not self.portfolio:
            return
        
        holdings = self.portfolio.get_holdings()
        self.holdings_table.setRowCount(len(holdings))
        
        for row, holding in enumerate(holdings):
            # Symbol
            self.holdings_table.setItem(row, 0, QTableWidgetItem(holding.symbol))
            
            # Shares
            self.holdings_table.setItem(row, 1, QTableWidgetItem(f"{holding.shares:.2f}"))
            
            # Cost/Share
            self.holdings_table.setItem(row, 2, QTableWidgetItem(f"${holding.cost_basis:.2f}"))
            
            # Total Cost
            self.holdings_table.setItem(row, 3, QTableWidgetItem(f"${holding.total_cost:.2f}"))
            
            # Current Price
            price_item = QTableWidgetItem(f"${holding.current_price:.2f}")
            self.holdings_table.setItem(row, 4, price_item)
            
            # Current Value
            self.holdings_table.setItem(row, 5, QTableWidgetItem(f"${holding.current_value:.2f}"))
            
            # Gain/Loss
            gain_loss_item = QTableWidgetItem(f"${holding.gain_loss:.2f}")
            if holding.gain_loss >= 0:
                gain_loss_item.setForeground(QColor("#90EE90"))  # Green
            else:
                gain_loss_item.setForeground(QColor("#FF6B6B"))  # Red
            self.holdings_table.setItem(row, 6, gain_loss_item)
            
            # Return %
            return_item = QTableWidgetItem(f"{holding.gain_loss_percent:.2f}%")
            if holding.gain_loss_percent >= 0:
                return_item.setForeground(QColor("#90EE90"))  # Green
            else:
                return_item.setForeground(QColor("#FF6B6B"))  # Red
            self.holdings_table.setItem(row, 7, return_item)
            
            # Purchased
            self.holdings_table.setItem(row, 8, QTableWidgetItem(holding.date_purchased))
        
        # Update summary
        self._update_summary()
    
    def _update_summary(self):
        """Update portfolio summary"""
        if not self.portfolio:
            return
        
        summary = self.portfolio.get_portfolio_summary()
        
        summary_text = (
            f"💰 Invested: ${summary['total_invested']:,.2f} | "
            f"Current: ${summary['current_value']:,.2f} | "
            f"Gain/Loss: ${summary['total_gain_loss']:,.2f} ({summary['total_return_pct']:.2f}%)"
        )
        
        self.summary_label.setText(summary_text)
        
        # Color code the summary
        if summary['total_gain_loss'] >= 0:
            self.summary_label.setStyleSheet("color: #90EE90; font-size: 11pt; font-weight: bold;")
        else:
            self.summary_label.setStyleSheet("color: #FF6B6B; font-size: 11pt; font-weight: bold;")
    
    def refresh_prices(self):
        """Manually refresh all prices"""
        if not self.portfolio:
            QMessageBox.information(self, "Info", "Please upload a portfolio first")
            return
        
        self.status_label.setText("🔄 Updating prices...")
        self.progress_bar.setVisible(True)
        
        try:
            if self.portfolio.update_prices():
                self.display_portfolio()
                self.status_label.setText("✓ Prices updated")
            else:
                QMessageBox.warning(self, "Error", "Failed to update some prices")
        finally:
            self.progress_bar.setVisible(False)
    
    def auto_refresh_prices(self):
        """Auto-refresh prices on timer"""
        if self.portfolio:
            self.portfolio.update_prices()
            self.display_portfolio()
    
    def export_portfolio(self):
        """Export portfolio to CSV"""
        if not self.portfolio:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Portfolio CSV", "portfolio.csv", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        if PortfolioImporter.export_to_csv(self.portfolio, file_path):
            QMessageBox.information(self, "Success", f"Portfolio exported to {file_path}")
            self.status_label.setText("✓ Portfolio exported")
        else:
            QMessageBox.critical(self, "Error", "Failed to export portfolio")
    
    def closeEvent(self, event):
        """Cleanup on close"""
        self.update_timer.stop()
        super().closeEvent(event)
