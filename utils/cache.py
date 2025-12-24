"""Cache management - Store scraped data temporarily"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Manage caching of scraped data"""
    
    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 4):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached data if still valid"""
        try:
            cache_file = self.cache_dir / f"{key}.json"
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check if cache is still valid
            created_at = datetime.fromisoformat(data.get('timestamp', ''))
            if datetime.now() - created_at > self.ttl:
                cache_file.unlink()  # Delete expired cache
                return None
            
            return data.get('data')
        except Exception as e:
            logger.error(f"Error reading cache for {key}: {e}")
            return None
    
    def set(self, key: str, data: Dict):
        """Store data in cache"""
        try:
            cache_file = self.cache_dir / f"{key}.json"
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            logger.error(f"Error writing cache for {key}: {e}")
    
    def clear(self, key: str = None):
        """Clear cache"""
        try:
            if key:
                cache_file = self.cache_dir / f"{key}.json"
                if cache_file.exists():
                    cache_file.unlink()
            else:
                # Clear all cache
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
