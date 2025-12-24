"""Database management - SQLite for watchlist, notes, analysis cache"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """SQLite database for storing watchlist and analysis"""
    
    def __init__(self, db_path: str = "stock_advisor.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Watchlist table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT UNIQUE NOT NULL,
                    company_name TEXT,
                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    target_price REAL,
                    notes TEXT,
                    quality_score REAL
                )
            """)
            
            # Analysis history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    quality_score REAL,
                    valuation_score REAL,
                    profitability_score REAL,
                    health_score REAL,
                    recommendation TEXT,
                    thesis TEXT
                )
            """)
            
            # Price history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    date TIMESTAMP NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER
                )
            """)
            
            # Reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT,
                    file_format TEXT,
                    report_type TEXT
                )
            """)
            
            conn.commit()
    
    def add_to_watchlist(self, symbol: str, company_name: str = None, target_price: float = None) -> bool:
        """Add stock to watchlist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO watchlist (symbol, company_name, target_price)
                    VALUES (?, ?, ?)
                """, (symbol.upper(), company_name, target_price))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            return False
    
    def remove_from_watchlist(self, symbol: str) -> bool:
        """Remove stock from watchlist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol.upper(),))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            return False
    
    def get_watchlist(self) -> List[Dict]:
        """Get all stocks in watchlist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT symbol, company_name, target_price, notes, quality_score FROM watchlist")
                rows = cursor.fetchall()
                return [
                    {
                        'symbol': row[0],
                        'company_name': row[1],
                        'target_price': row[2],
                        'notes': row[3],
                        'quality_score': row[4]
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error retrieving watchlist: {e}")
            return []
    
    def add_analysis(self, symbol: str, scores: Dict, recommendation: str, thesis: str) -> bool:
        """Store analysis results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO analysis_history 
                    (symbol, quality_score, valuation_score, profitability_score, health_score, recommendation, thesis)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol.upper(),
                    scores.get('quality', 0),
                    scores.get('valuation', 0),
                    scores.get('profitability', 0),
                    scores.get('health', 0),
                    recommendation,
                    thesis
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error storing analysis: {e}")
            return False
    
    def get_latest_analysis(self, symbol: str) -> Optional[Dict]:
        """Get latest analysis for a stock"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT quality_score, valuation_score, profitability_score, health_score, 
                           recommendation, thesis, analysis_date
                    FROM analysis_history
                    WHERE symbol = ?
                    ORDER BY analysis_date DESC
                    LIMIT 1
                """, (symbol.upper(),))
                row = cursor.fetchone()
                if row:
                    return {
                        'quality_score': row[0],
                        'valuation_score': row[1],
                        'profitability_score': row[2],
                        'health_score': row[3],
                        'recommendation': row[4],
                        'thesis': row[5],
                        'date': row[6]
                    }
        except Exception as e:
            logger.error(f"Error retrieving analysis: {e}")
        return None
    
    def update_watchlist_notes(self, symbol: str, notes: str, quality_score: float = None) -> bool:
        """Update notes for a watchlist item"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if quality_score is not None:
                    cursor.execute(
                        "UPDATE watchlist SET notes = ?, quality_score = ? WHERE symbol = ?",
                        (notes, quality_score, symbol.upper())
                    )
                else:
                    cursor.execute(
                        "UPDATE watchlist SET notes = ? WHERE symbol = ?",
                        (notes, symbol.upper())
                    )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating notes: {e}")
            return False
