"""
Base Service Class
Common initialization and patterns for all services
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import sqlite3


class BaseService:
    """Base class for all services with common patterns"""
    
    def __init__(self, db_path: Optional[str] = None, cache_ttl: int = 3600):
        """
        Initialize base service
        
        Args:
            db_path: Path to SQLite database
            cache_ttl: Cache time-to-live in seconds (default 1 hour)
        """
        self.logger = self._setup_logger()
        self.db_path = db_path
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple] = {}  # {key: (data, timestamp)}
        self._db_connection = None
        
        if db_path:
            self._connect_db()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for this service"""
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
    
    def _connect_db(self) -> None:
        """Connect to database"""
        try:
            self._db_connection = sqlite3.connect(self.db_path)
            self._db_connection.row_factory = sqlite3.Row
            self.logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    @property
    def db(self) -> sqlite3.Connection:
        """Get database connection"""
        if self._db_connection is None:
            raise RuntimeError("Database not initialized. Set db_path in __init__")
        return self._db_connection
    
    def _cache_get(self, key: str) -> Optional[Any]:
        """Get from cache if not expired"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return data
            else:
                del self._cache[key]
        return None
    
    def _cache_set(self, key: str, data: Any) -> None:
        """Set cache with timestamp"""
        self._cache[key] = (data, datetime.now())
    
    def _cache_clear(self, pattern: Optional[str] = None) -> None:
        """Clear cache by pattern or completely"""
        if pattern is None:
            self._cache.clear()
        else:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for k in keys_to_delete:
                del self._cache[k]
    
    def close(self) -> None:
        """Close database connection"""
        if self._db_connection:
            self._db_connection.close()
            self.logger.info("Database connection closed")
