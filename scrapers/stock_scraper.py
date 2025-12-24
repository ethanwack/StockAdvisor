"""Stock data scraper - Yahoo Finance, SEC filings, analyst ratings"""

import requests
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class StockScraper:
    """Scrape stock data from multiple sources"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.base_urls = {
            'yahoo': 'https://finance.yahoo.com',
            'marketwatch': 'https://www.marketwatch.com',
            'seeking_alpha': 'https://seekingalpha.com',
            'nasdaq': 'https://www.nasdaq.com'
        }
    
    def get_quote(self, symbol: str) -> Dict:
        """Get current stock quote using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.info
            
            return {
                'symbol': symbol,
                'price': data.get('currentPrice', 0),
                'change': data.get('regularMarketChange', 0),
                'change_percent': data.get('regularMarketChangePercent', 0),
                'bid': data.get('bid', 0),
                'ask': data.get('ask', 0),
                'volume': data.get('volume', 0),
                'market_cap': data.get('marketCap', 0),
                '52w_high': data.get('fiftyTwoWeekHigh', 0),
                '52w_low': data.get('fiftyTwoWeekLow', 0),
                'dividend_yield': data.get('dividendYield', 0),
                'pe_ratio': data.get('trailingPE', 0),
                'forward_pe': data.get('forwardPE', 0),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return {}
    
    def get_financial_data(self, symbol: str) -> Dict:
        """Get financial statements from yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get quarterly financials
            income_stmt = ticker.quarterly_financials
            balance_sheet = ticker.quarterly_balance_sheet
            cash_flow = ticker.quarterly_cashflow
            
            latest_quarter = income_stmt.columns[0]
            
            return {
                'symbol': symbol,
                'revenue': income_stmt.loc['Total Revenue', latest_quarter] if 'Total Revenue' in income_stmt.index else 0,
                'net_income': income_stmt.loc['Net Income', latest_quarter] if 'Net Income' in income_stmt.index else 0,
                'operating_income': income_stmt.loc['Operating Income', latest_quarter] if 'Operating Income' in income_stmt.index else 0,
                'total_assets': balance_sheet.loc['Total Assets', latest_quarter] if 'Total Assets' in balance_sheet.index else 0,
                'total_liabilities': balance_sheet.loc['Total Liabilities', latest_quarter] if 'Total Liabilities' in balance_sheet.index else 0,
                'shareholders_equity': balance_sheet.loc['Shareholders Equity', latest_quarter] if 'Shareholders Equity' in balance_sheet.index else 0,
                'operating_cash_flow': cash_flow.loc['Operating Cash Flow', latest_quarter] if 'Operating Cash Flow' in cash_flow.index else 0,
                'capex': cash_flow.loc['Capital Expenditure', latest_quarter] if 'Capital Expenditure' in cash_flow.index else 0,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching financials for {symbol}: {e}")
            return {}
    
    def get_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            return hist
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_analyst_ratings(self, symbol: str) -> List[Dict]:
        """Scrape analyst ratings from MarketWatch"""
        try:
            url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}/research"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'lxml')
            
            ratings = []
            # Parse analyst ratings from page
            # This is a simplified example - actual implementation would need 
            # to handle the specific HTML structure of MarketWatch
            
            return ratings
        except Exception as e:
            logger.error(f"Error scraping analyst ratings for {symbol}: {e}")
            return []
    
    def get_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get recent news articles about stock"""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            articles = []
            for article in news[:limit]:
                articles.append({
                    'title': article.get('title', ''),
                    'link': article.get('link', ''),
                    'source': article.get('source', ''),
                    'timestamp': article.get('providerPublishTime', 0)
                })
            
            return articles
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    def search_stocks(self, query: str) -> List[Dict]:
        """Search for stocks by symbol or company name"""
        try:
            # This would use a stock search API
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return []
