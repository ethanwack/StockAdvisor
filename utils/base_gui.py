"""
Base GUI Widget Class
Common patterns for all GUI tabs
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PySide6.QtCore import Qt, QThread
from typing import Optional, Dict, Any
import logging


class BaseTabWidget(QWidget):
    """Base class for all GUI tabs with common patterns"""
    
    def __init__(self, db=None, cache=None):
        """
        Initialize base tab widget
        
        Args:
            db: Database connection
            cache: Cache object
        """
        super().__init__()
        self.db = db
        self.cache = cache
        self.logger = self._setup_logger()
        self.workers = []  # Track worker threads
        
        self.init_ui()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for this widget"""
        logger = logging.getLogger(self.__class__.__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def init_ui(self):
        """Initialize UI - override in subclass"""
        layout = QVBoxLayout()
        self.setLayout(layout)
    
    def show_info(self, title: str, message: str):
        """Show information dialog"""
        QMessageBox.information(self, title, message)
    
    def show_error(self, title: str, message: str):
        """Show error dialog"""
        QMessageBox.critical(self, title, message)
    
    def show_warning(self, title: str, message: str):
        """Show warning dialog"""
        QMessageBox.warning(self, title, message)
    
    def show_confirm(self, title: str, message: str) -> bool:
        """Show confirmation dialog"""
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def add_worker(self, worker: QThread):
        """Add worker thread to track"""
        self.workers.append(worker)
    
    def cleanup_workers(self):
        """Wait for all workers to finish"""
        for worker in self.workers:
            if worker.isRunning():
                worker.quit()
                worker.wait()
    
    def closeEvent(self, event):
        """Clean up when tab closes"""
        self.cleanup_workers()
        super().closeEvent(event)
