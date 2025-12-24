"""Market data scraper - Indices, trends, market overview"""

import requests
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class MarketScraper:
    """Scrape market-wide data and indices"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def get_market_indices(self) -> Dict:
        """Get major market indices"""
        try:
            indices = {
                'SP500': self._get_index_data('^GSPC'),
                'NASDAQ': self._get_index_data('^IXIC'),
                'DOW': self._get_index_data('^DJI'),
                'VIX': self._get_index_data('^VIX')
            }
            return indices
        except Exception as e:
            logger.error(f"Error fetching market indices: {e}")
            return {}
    
    def _get_index_data(self, symbol: str) -> Dict:
        """Get data for a single index"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.info
            
            return {
                'symbol': symbol,
                'price': data.get('regularMarketPrice', 0),
                'change': data.get('regularMarketChange', 0),
                'change_percent': data.get('regularMarketChangePercent', 0),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return {}
    
    def get_trending_stocks(self, limit: int = 20) -> List[Dict]:
        """Get trending stocks from market"""
        # This would scrape trending data from financial websites
        try:
            # Using yfinance to get some popular stocks
            popular = ['^GSPC', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META']
            trending = []
            
            for symbol in popular:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.info
                    trending.append({
                        'symbol': symbol,
                        'price': data.get('currentPrice', 0),
                        'change_percent': data.get('regularMarketChangePercent', 0),
                        'volume': data.get('volume', 0),
                        'market_cap': data.get('marketCap', 0)
                    })
                except:
                    pass
            
            return trending[:limit]
        except Exception as e:
            logger.error(f"Error fetching trending stocks: {e}")
            return []
    
    def get_sector_performance(self) -> Dict:
        """Get sector performance data"""
        try:
            sectors = {
                'Technology': yf.Ticker('XLK').info.get('regularMarketChangePercent', 0),
                'Healthcare': yf.Ticker('XLV').info.get('regularMarketChangePercent', 0),
                'Financials': yf.Ticker('XLF').info.get('regularMarketChangePercent', 0),
                'Energy': yf.Ticker('XLE').info.get('regularMarketChangePercent', 0),
                'Consumer': yf.Ticker('XLY').info.get('regularMarketChangePercent', 0),
            }
            return sectors
        except Exception as e:
            logger.error(f"Error fetching sector performance: {e}")
            return {}
