"""Portfolio management - refactored version using BaseService"""

import csv
from typing import List, Dict, Optional
from datetime import datetime
import yfinance as yf

from utils.base_service import BaseService
from utils.data_models import Position
from utils.validators import validate_symbol, ValidationError


class Portfolio:
    """User portfolio tracking"""
    
    def __init__(self, name: str = "My Portfolio"):
        self.name = name
        self.holdings: Dict[str, Holding] = {}
        self.created_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()
    
    def add_holding(self, holding: Holding) -> bool:
        """Add a holding to portfolio"""
        if holding.symbol in self.holdings:
            logger.warning(f"Holding {holding.symbol} already exists, merging...")
            # Merge with existing holding
            existing = self.holdings[holding.symbol]
            total_shares = existing.shares + holding.shares
            avg_cost = ((existing.shares * existing.cost_basis) + 
                       (holding.shares * holding.cost_basis)) / total_shares
            
            merged = Holding(
                symbol=holding.symbol,
                shares=total_shares,
                cost_basis=avg_cost,
                date_purchased=existing.date_purchased,
                notes=f"{existing.notes}; {holding.notes}"
            )
            self.holdings[holding.symbol] = merged
        else:
            self.holdings[holding.symbol] = holding
        
        self.last_updated = datetime.now().isoformat()
        return True
    
    def remove_holding(self, symbol: str) -> bool:
        """Remove a holding from portfolio"""
        if symbol in self.holdings:
            del self.holdings[symbol]
            self.last_updated = datetime.now().isoformat()
            return True
        return False
    
    def update_prices(self) -> bool:
        """Update current prices for all holdings"""
        try:
            for symbol, holding in self.holdings.items():
                price = self._get_current_price(symbol)
                if price:
                    holding.current_price = price
                    holding.current_value = holding.shares * price
                    holding.gain_loss = holding.current_value - holding.total_cost
                    holding.gain_loss_percent = (holding.gain_loss / holding.total_cost * 100) if holding.total_cost else 0
            
            self.last_updated = datetime.now().isoformat()
            return True
        except Exception as e:
            logger.error(f"Error updating prices: {e}")
            return False
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary statistics"""
        total_cost = sum(h.total_cost for h in self.holdings.values())
        total_value = sum(h.current_value for h in self.holdings.values())
        total_gain_loss = total_value - total_cost
        total_return_pct = (total_gain_loss / total_cost * 100) if total_cost else 0
        
        return {
            'num_holdings': len(self.holdings),
            'total_invested': total_cost,
            'current_value': total_value,
            'total_gain_loss': total_gain_loss,
            'total_return_pct': total_return_pct,
            'last_updated': self.last_updated
        }
    
    def get_holdings(self) -> List[Holding]:
        """Get all holdings sorted by value"""
        return sorted(
            self.holdings.values(),
            key=lambda h: h.current_value,
            reverse=True
        )
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.info
            price = data.get('regularMarketPrice') or data.get('currentPrice')
            return float(price) if price else None
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None


class PortfolioImporter:
    """Import portfolio from CSV files"""
    
    # Expected CSV format:
    # Symbol,Shares,CostBasis,DatePurchased,Notes
    # AAPL,100,150.50,2023-01-15,Initial investment
    
    @staticmethod
    def import_from_csv(file_path: str) -> Optional[Portfolio]:
        """
        Import portfolio from CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Portfolio object or None if import fails
        """
        try:
            portfolio = Portfolio()
            
            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    try:
                        holding = Holding(
                            symbol=row['Symbol'].upper().strip(),
                            shares=float(row['Shares']),
                            cost_basis=float(row['CostBasis']),
                            date_purchased=row.get('DatePurchased', datetime.now().isoformat()),
                            notes=row.get('Notes', '')
                        )
                        
                        portfolio.add_holding(holding)
                        logger.info(f"Imported holding: {holding.symbol} - {holding.shares} shares")
                        
                    except (ValueError, KeyError) as e:
                        logger.error(f"Error parsing row {row}: {e}")
                        continue
            
            logger.info(f"Successfully imported portfolio with {len(portfolio.holdings)} holdings")
            return portfolio
            
        except Exception as e:
            logger.error(f"Error importing portfolio from CSV: {e}")
            return None
    
    @staticmethod
    def export_to_csv(portfolio: Portfolio, file_path: str) -> bool:
        """
        Export portfolio to CSV file
        
        Args:
            portfolio: Portfolio object
            file_path: Path to save CSV
            
        Returns:
            True if successful
        """
        try:
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = [
                    'Symbol', 'Shares', 'CostBasis', 'DatePurchased',
                    'CurrentPrice', 'CurrentValue', 'GainLoss', 'GainLossPercent', 'Notes'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for holding in portfolio.get_holdings():
                    writer.writerow({
                        'Symbol': holding.symbol,
                        'Shares': f"{holding.shares:.2f}",
                        'CostBasis': f"{holding.cost_basis:.2f}",
                        'DatePurchased': holding.date_purchased,
                        'CurrentPrice': f"{holding.current_price:.2f}",
                        'CurrentValue': f"{holding.current_value:.2f}",
                        'GainLoss': f"{holding.gain_loss:.2f}",
                        'GainLossPercent': f"{holding.gain_loss_percent:.2f}",
                        'Notes': holding.notes
                    })
            
            logger.info(f"Successfully exported portfolio to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting portfolio to CSV: {e}")
            return False
