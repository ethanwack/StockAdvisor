"""Fundamental analysis - Calculate financial metrics and scores"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FundamentalAnalyzer:
    """Analyze stocks based on fundamental metrics"""
    
    def __init__(self):
        # Quality score weights
        self.weights = {
            'valuation': 0.25,
            'profitability': 0.25,
            'growth': 0.20,
            'financial_health': 0.20,
            'dividend': 0.10
        }
    
    def calculate_valuation_score(self, quote: Dict, financials: Dict) -> Tuple[float, str]:
        """Calculate valuation score (0-100)"""
        try:
            pe_ratio = quote.get('pe_ratio', 0)
            forward_pe = quote.get('forward_pe', 0)
            price_to_book = self._calculate_pb_ratio(quote, financials)
            
            # Score based on valuation metrics
            pe_score = self._score_pe_ratio(pe_ratio, forward_pe)
            pb_score = self._score_pb_ratio(price_to_book)
            
            score = (pe_score + pb_score) / 2
            analysis = self._valuation_analysis(score, pe_ratio)
            
            return score, analysis
        except Exception as e:
            logger.error(f"Error calculating valuation score: {e}")
            return 0, "Unable to calculate"
    
    def calculate_profitability_score(self, quote: Dict, financials: Dict) -> Tuple[float, str]:
        """Calculate profitability score (0-100)"""
        try:
            revenue = financials.get('revenue', 0)
            net_income = financials.get('net_income', 0)
            operating_income = financials.get('operating_income', 0)
            
            if revenue == 0:
                return 0, "Insufficient data"
            
            # Profit margins
            net_margin = (net_income / revenue) * 100 if revenue > 0 else 0
            operating_margin = (operating_income / revenue) * 100 if revenue > 0 else 0
            
            # Score based on margins
            score = min((net_margin + 5) * 5 + (operating_margin + 5) * 3, 100)
            analysis = f"Net margin: {net_margin:.1f}%, Operating margin: {operating_margin:.1f}%"
            
            return max(0, min(score, 100)), analysis
        except Exception as e:
            logger.error(f"Error calculating profitability score: {e}")
            return 0, "Unable to calculate"
    
    def calculate_financial_health_score(self, quote: Dict, financials: Dict) -> Tuple[float, str]:
        """Calculate financial health score (0-100)"""
        try:
            total_assets = financials.get('total_assets', 1)
            total_liabilities = financials.get('total_liabilities', 0)
            shareholders_equity = financials.get('shareholders_equity', 1)
            
            # Debt ratio
            debt_ratio = total_liabilities / total_assets if total_assets > 0 else 0
            
            # Equity ratio
            equity_ratio = shareholders_equity / total_assets if total_assets > 0 else 0
            
            # Score: Lower debt is better
            score = (1 - debt_ratio) * 100
            
            analysis = f"Debt ratio: {debt_ratio:.2%}, Equity ratio: {equity_ratio:.2%}"
            
            return max(0, min(score, 100)), analysis
        except Exception as e:
            logger.error(f"Error calculating financial health score: {e}")
            return 0, "Unable to calculate"
    
    def calculate_quality_score(self, quote: Dict, financials: Dict, historical: pd.DataFrame) -> Tuple[float, str]:
        """Calculate overall quality score (0-100)"""
        try:
            scores = {
                'valuation': self.calculate_valuation_score(quote, financials)[0],
                'profitability': self.calculate_profitability_score(quote, financials)[0],
                'financial_health': self.calculate_financial_health_score(quote, financials)[0],
            }
            
            # Calculate weighted score
            weighted_score = sum(scores[key] * self.weights[key] for key in scores) / sum(self.weights[k] for k in self.weights if k in scores)
            
            # Determine quality level
            if weighted_score >= 80:
                level = "Excellent"
            elif weighted_score >= 60:
                level = "Good"
            elif weighted_score >= 40:
                level = "Fair"
            else:
                level = "Poor"
            
            return weighted_score, level
        except Exception as e:
            logger.error(f"Error calculating quality score: {e}")
            return 0, "Unable to calculate"
    
    def generate_investment_thesis(self, symbol: str, quote: Dict, financials: Dict) -> str:
        """Generate investment thesis based on analysis"""
        try:
            quality_score, quality_level = self.calculate_quality_score(quote, financials, pd.DataFrame())
            valuation_score, valuation_analysis = self.calculate_valuation_score(quote, financials)
            profitability_score, profitability_analysis = self.calculate_profitability_score(quote, financials)
            health_score, health_analysis = self.calculate_financial_health_score(quote, financials)
            
            thesis = f"""
INVESTMENT THESIS FOR {symbol}

QUALITY ASSESSMENT: {quality_level} ({quality_score:.1f}/100)

VALUATION ANALYSIS:
{valuation_analysis}
Score: {valuation_score:.1f}/100

PROFITABILITY:
{profitability_analysis}
Score: {profitability_score:.1f}/100

FINANCIAL HEALTH:
{health_analysis}
Score: {health_score:.1f}/100

RECOMMENDATION:
Based on the fundamental analysis, {symbol} rates {quality_level} quality.
This indicates {'strong' if quality_score >= 70 else 'moderate' if quality_score >= 50 else 'weak'} investment potential.

PRICE POINT: ${quote.get('price', 0):.2f}
P/E RATIO: {quote.get('pe_ratio', 'N/A')}
52W HIGH: ${quote.get('52w_high', 0):.2f}
52W LOW: ${quote.get('52w_low', 0):.2f}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            return thesis
        except Exception as e:
            logger.error(f"Error generating investment thesis: {e}")
            return "Unable to generate thesis"
    
    def _calculate_pb_ratio(self, quote: Dict, financials: Dict) -> float:
        """Calculate price-to-book ratio"""
        try:
            price = quote.get('price', 0)
            equity = financials.get('shareholders_equity', 1)
            # This is simplified; real calculation needs shares outstanding
            return price / (equity / 1e9) if equity > 0 else 0
        except:
            return 0
    
    def _score_pe_ratio(self, pe: float, forward_pe: float) -> float:
        """Score P/E ratio (lower is better, but not too low)"""
        if pe <= 0:
            return 50
        if pe < 15:
            return 80
        elif pe < 25:
            return 70
        elif pe < 35:
            return 50
        else:
            return 30
    
    def _score_pb_ratio(self, pb: float) -> float:
        """Score P/B ratio"""
        if pb <= 0:
            return 50
        if pb < 1.5:
            return 80
        elif pb < 2.5:
            return 60
        else:
            return 40
    
    def _valuation_analysis(self, score: float, pe: float) -> str:
        """Generate valuation analysis text"""
        if score >= 75:
            return f"Stock appears undervalued (P/E: {pe:.1f})"
        elif score >= 50:
            return f"Stock appears fairly valued (P/E: {pe:.1f})"
        else:
            return f"Stock appears overvalued (P/E: {pe:.1f})"
