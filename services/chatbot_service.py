"""AI-powered chatbot for stock recommendations and analysis"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import yfinance as yf
from scrapers.stock_scraper import StockScraper
from analyzers.fundamental_analyzer import FundamentalAnalyzer

logger = logging.getLogger(__name__)


class StockChatbot:
    """AI chatbot for stock recommendations and analysis"""
    
    def __init__(self, db=None, cache=None):
        """Initialize chatbot with database and cache"""
        self.db = db
        self.cache = cache
        self.scraper = StockScraper()
        self.analyzer = FundamentalAnalyzer()
        
        # Try to initialize OpenAI API
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.use_openai = False
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.use_openai = True
                logger.info("OpenAI API initialized successfully")
            except Exception as e:
                logger.warning(f"OpenAI API not available: {e}. Using rule-based responses.")
                self.use_openai = False
    
    def get_response(self, user_message: str) -> Dict:
        """
        Get chatbot response to user message
        
        Args:
            user_message: User's question or request
            
        Returns:
            Dictionary with response and metadata
        """
        user_message = user_message.strip().lower()
        
        # Try AI response first if OpenAI available
        if self.use_openai:
            try:
                return self._get_ai_response(user_message)
            except Exception as e:
                logger.error(f"Error getting AI response: {e}")
                # Fall back to rule-based
        
        # Rule-based responses
        return self._get_rule_based_response(user_message)
    
    def _get_ai_response(self, user_message: str) -> Dict:
        """Get response using OpenAI API"""
        from openai import OpenAI
        
        client = OpenAI(api_key=self.api_key)
        
        # Build context about stocks
        context = self._build_stock_context(user_message)
        
        system_prompt = """You are an expert financial advisor and stock analysis assistant. 
You help investors make informed decisions about stocks, portfolio management, and investment strategies.
Provide specific, actionable advice based on fundamental analysis and market trends.
Always include risk disclaimers in your responses.
When discussing specific stocks, provide analysis with reasoning."""
        
        user_prompt = f"""Stock Context:
{context}

User Question: {user_message}

Provide a helpful, detailed response focused on stock investments and analysis."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content
        
        return {
            "response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "is_ai": True,
            "stocks_mentioned": self._extract_stock_symbols(user_message)
        }
    
    def _get_rule_based_response(self, user_message: str) -> Dict:
        """Get response using rule-based logic"""
        response = ""
        stocks_mentioned = self._extract_stock_symbols(user_message)
        
        # Recommendation queries
        if any(word in user_message for word in ["recommend", "should i buy", "what stocks", "best stocks", "recommendations"]):
            response = self._get_recommendations()
        
        # Selling advice
        elif any(word in user_message for word in ["when to sell", "sell signals", "stop loss", "take profit"]):
            response = self._get_sell_advice()
        
        # Shorting advice
        elif any(word in user_message for word in ["short", "short sell", "bearish", "downside"]):
            response = self._get_short_advice()
        
        # Stock analysis
        elif any(word in user_message for word in ["analyze", "analysis", "fundamentals", "pe ratio", "earnings"]):
            if stocks_mentioned:
                response = self._analyze_stocks(stocks_mentioned)
            else:
                response = "Please mention a stock symbol (like AAPL, GOOGL, MSFT) for detailed analysis."
        
        # Portfolio advice
        elif any(word in user_message for word in ["portfolio", "diversif", "allocation", "balance"]):
            response = self._get_portfolio_advice()
        
        # Market trends
        elif any(word in user_message for word in ["market", "trend", "outlook", "fed", "interest rate", "inflation"]):
            response = self._get_market_analysis()
        
        # Risk management
        elif any(word in user_message for word in ["risk", "volatility", "downside", "protection", "hedging"]):
            response = self._get_risk_management_advice()
        
        # Default response
        else:
            response = self._get_default_response(user_message)
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "is_ai": False,
            "stocks_mentioned": stocks_mentioned
        }
    
    def _build_stock_context(self, query: str) -> str:
        """Build context about mentioned stocks"""
        symbols = self._extract_stock_symbols(query)
        context = ""
        
        for symbol in symbols[:3]:  # Limit to 3 stocks
            try:
                data = self.scraper.get_stock_data(symbol)
                analysis = self.analyzer.analyze_stock(symbol, data)
                
                context += f"\n{symbol}:"
                context += f"\n  Price: ${data.get('price', 'N/A')}"
                context += f"\n  52W High/Low: ${data.get('52w_high', 'N/A')} / ${data.get('52w_low', 'N/A')}"
                context += f"\n  P/E Ratio: {data.get('pe_ratio', 'N/A')}"
                context += f"\n  Analyst Score: {analysis.get('score', 'N/A')}/100"
            except Exception as e:
                logger.error(f"Error getting context for {symbol}: {e}")
        
        return context if context else "No specific stock data available"
    
    def _extract_stock_symbols(self, text: str) -> List[str]:
        """Extract stock symbols from text"""
        # Common stock symbols pattern
        symbols = []
        words = text.upper().split()
        
        # Check for common symbols
        common_symbols = {
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX',
            'MRNA', 'JNJ', 'PFE', 'V', 'MA', 'JPM', 'BAC', 'GS', 'SPY', 'QQQ',
            'IVV', 'VOO', 'VTI', 'BRK.B', 'BRKA', 'XOM', 'CVX', 'COP', 'MPC'
        }
        
        for word in words:
            word_clean = word.strip('.,!?;:')
            if word_clean in common_symbols and word_clean not in symbols:
                symbols.append(word_clean)
        
        return symbols
    
    def _get_recommendations(self) -> str:
        """Get stock recommendations"""
        return """
📊 **Stock Recommendations** (Based on Fundamental Analysis)

**Strong Buy (Momentum + Value):**
- Look for stocks with P/E ratios below 20 combined with strong earnings growth (>15% YoY)
- Consider companies with solid free cash flow and low debt-to-equity ratios
- Screen for insider buying activity

**Top Sectors to Watch:**
1. **Technology**: Monitor AI adoption, cloud growth, semiconductor demand
2. **Healthcare**: Biotech with FDA approvals, established pharma with moats
3. **Finance**: Banks with improving rates, insurance companies with pricing power
4. **Energy**: Oil/gas with disciplined capital allocation and renewable transitions

**Watchlist Strategy:**
- Create a list of 10-15 companies in industries you understand
- Monitor quarterly earnings and management guidance
- Track technical support/resistance levels
- Wait for pullbacks to buy (dollar-cost averaging)

⚠️ **Risk Disclaimer:** Past performance is not indicative of future results. Always do your own research and consider your risk tolerance before investing.
"""
    
    def _get_sell_advice(self) -> str:
        """Get selling strategy advice"""
        return """
📉 **When to Sell: Key Signals & Strategies**

**Fundamental Sell Signals:**
1. **Earnings Deterioration**: 2+ consecutive quarters of declining earnings or EPS beats turning into misses
2. **Industry Disruption**: Competitive advantages eroding or disruptive new entrants (e.g., streaming vs. cable)
3. **Management Changes**: Founder departure, CFO turnover, or loss of visionary leadership
4. **Debt Issues**: Increasing debt-to-equity ratio or credit rating downgrade
5. **Cash Flow Problems**: Free cash flow turning negative while stock is highly valued

**Technical Sell Signals:**
- Break below long-term moving average (200-day MA)
- Loss of support level with high volume
- Divergence between price and momentum indicators

**Profit-Taking Strategy:**
- **Trim Winners**: Sell 25-50% when stock doubles to lock in gains
- **Rebalance**: Sell if a position grows to >30% of portfolio
- **Tax Loss Harvesting**: Sell losers in December to offset gains

**Stop Loss Approach:**
- Set stop at 15-25% below entry depending on volatility
- Don't get emotionally attached to positions
- Review quarterly; exit if thesis changes

⚠️ **Selling is as important as buying. Protecting capital matters more than chasing gains.**
"""
    
    def _get_short_advice(self) -> str:
        """Get shorting strategy advice"""
        return """
🔻 **Shorting Strategy: When & How to Short Stocks**

**Valid Short Opportunities:**
1. **Overvaluation**: P/E > 50 with no earnings growth or negative revenue trends
2. **Accounting Red Flags**: Related-party transactions, aggressive accounting, restatements
3. **Business Model Disruption**: Incumbent facing technological obsolescence
4. **Deteriorating Fundamentals**: Negative FCF, rising debt, shrinking margins
5. **Fraud Signals**: Whistleblower reports, SEC investigations, founder selling heavily

**Technical Short Signals:**
- Stock breaking below support with high volume
- Moving below 50-day MA with declining RSI
- Lower highs and lower lows pattern (downtrend)

**Shorting Risks (Understand These!):**
- **Unlimited Loss Potential**: Price can rise indefinitely (vs. stocks max at $0)
- **Forced Buybacks**: Short squeeze when stock drops further = margin calls
- **Borrow Costs**: Lending fees can be 10-50%+ annually for hot shorts
- **Short Ladder Attacks**: Manipulative practices to shake out shorts
- **Reversals**: Beaten-down stocks can bounce 20-50% on any positive catalyst

**Best Practices:**
- Only short with money you can afford to lose entirely
- Always use stop losses (crucial!)
- Short theses on broken business models, not just valuation
- Smaller position sizes than longs (due to higher risk)
- Track why you shorted; exit if thesis fails

⚠️ **Shorting is high-risk. Consider puts or inverse ETFs as safer alternatives.**
"""
    
    def _analyze_stocks(self, symbols: List[str]) -> str:
        """Analyze specific stocks"""
        response = f"📈 **Analysis for: {', '.join(symbols)}**\n\n"
        
        for symbol in symbols[:3]:  # Limit to 3 stocks
            try:
                data = self.scraper.get_stock_data(symbol)
                if data:
                    analysis = self.analyzer.analyze_stock(symbol, data)
                    
                    response += f"**{symbol}**:\n"
                    response += f"- Price: ${data.get('price', 'N/A')}\n"
                    response += f"- Market Cap: ${data.get('market_cap', 'N/A')}\n"
                    response += f"- P/E Ratio: {data.get('pe_ratio', 'N/A')}\n"
                    response += f"- Dividend Yield: {data.get('dividend_yield', 'N/A')}%\n"
                    response += f"- Analysis Score: {analysis.get('score', 'N/A')}/100\n"
                    response += f"- Recommendation: {analysis.get('recommendation', 'Hold')}\n\n"
                else:
                    response += f"**{symbol}**: Unable to fetch data (rate limit or ticker not found)\n\n"
            except Exception as e:
                response += f"**{symbol}**: Error during analysis ({str(e)})\n\n"
        
        return response
    
    def _get_portfolio_advice(self) -> str:
        """Get portfolio management advice"""
        return """
💼 **Portfolio Management & Diversification Strategy**

**Asset Allocation (Age-Based Rule of Thumb):**
- **Age 20-30**: 80-90% stocks, 10-20% bonds/cash (high growth)
- **Age 30-40**: 70-80% stocks, 20-30% bonds/cash (balanced growth)
- **Age 40-50**: 60-70% stocks, 30-40% bonds/cash (moderate)
- **Age 50-60**: 40-60% stocks, 40-60% bonds/cash (conservative)
- **Age 60+**: 30-40% stocks, 60-70% bonds/cash (income-focused)

**Diversification Framework:**
1. **By Sector**: No single sector >30% of portfolio
   - Tech 15-25%, Healthcare 10-15%, Financials 10-15%, Energy 5-10%, etc.
2. **By Market Cap**: Mix large-cap, mid-cap, small-cap, international
3. **By Strategy**: Value (30%), Growth (30%), Dividends (20%), Defensive (20%)
4. **By Asset Class**: Stocks 60-80%, Bonds 15-30%, Cash/REITs 5-10%

**Core-Satellite Approach:**
- **Core (70-80%)**: Low-cost index funds (SPY, VTI, QQQ, BND)
- **Satellite (20-30%)**: Individual stock picks for outperformance

**Rebalancing Rules:**
- Rebalance quarterly or when any asset class drifts >5% from target
- Use new contributions to rebalance (no tax consequences)
- Don't chase performance - stick to your allocation

**Risk Management in Portfolio:**
- Position sizing: Never >5% in single stock, <2% in speculative plays
- Diversification reduces need for perfect stock picking
- Lower volatility = sleep at night = better long-term returns

⚠️ **The best portfolio is one you can stick with through market cycles.**
"""
    
    def _get_market_analysis(self) -> str:
        """Get current market analysis"""
        return """
🌍 **Current Market Analysis & Outlook**

**Key Economic Indicators to Watch:**
1. **Interest Rates**: Fed Fund Rate determines cost of capital, bond yields
   - Rising rates = headwinds for growth stocks, benefits bonds
   - Cutting rates = boosts equities, reduces bond yields

2. **Inflation**: CPI/PPI impacts purchasing power and Fed policy
   - High inflation = stagflation risk, benefits commodity stocks
   - Low inflation = supports growth stocks, aids consumer spending

3. **Employment**: Unemployment rate and job creation drive consumer confidence
   - Strong jobs = robust economy, supports stock valuations
   - Weak jobs = recession signal, warrant defensive positioning

4. **GDP Growth**: Economic expansion/contraction signal
   - >2% real growth = healthy, supports corporate earnings
   - <0% = recession, typically negative for stocks

5. **Yield Curve**: 10-yr vs 2-yr Treasury spread
   - Inverted = recession indicator (often followed by bear market)
   - Steep = reflation bet, benefits cyclicals

**Current Sector Rotation:**
- **Economic Strength**: Cyclicals (Industrials, Finance, Consumer Discretionary)
- **Inflation**: Energy, Materials, Commodities
- **Slowdown**: Defensives (Healthcare, Utilities, Consumer Staples)
- **Tech**: Sensitive to rates and growth expectations

**Market Timing Notes:**
- Historical: Bull markets last 4-8 years, bear markets 1-2 years
- Most returns come from staying invested (missing 10 best days = massive underperformance)
- Time IN market > timing the market
- Monitor sentiment, but don't make decisions based solely on fear/greed

⚠️ **Market cycles are normal. Dollar-cost averaging smooths returns.**
"""
    
    def _get_risk_management_advice(self) -> str:
        """Get risk management strategies"""
        return """
🛡️ **Risk Management & Portfolio Protection Strategies**

**Understanding Risk Types:**
1. **Market Risk**: Overall market decline (can't diversify away, only hedge)
2. **Company Risk**: Individual stock decline (diversification reduces this)
3. **Sector Risk**: Entire sector underperforms (hedge with opposite sectors)
4. **Currency Risk**: Foreign investments affected by exchange rates
5. **Liquidity Risk**: Cannot quickly exit a position

**Risk Management Techniques:**

**1. Stop Losses (Most Important)**
- Set at 15-25% below entry for growth stocks
- Set at 20-30% below entry for value stocks
- Move up as stock appreciates (protect profits)
- Use trailing stops to let winners run

**2. Position Sizing**
- Never put >5% in single stock
- Speculative plays <2% of portfolio
- Concentration kills portfolios in corrections

**3. Hedging Strategies**
- **Protective Puts**: Buy put options when concerned (expensive but effective)
- **Collar**: Sell covered calls, buy puts (free or profitable hedge)
- **Inverse ETFs**: -1x or -3x leverage on market/sector (hedge entire portfolio)
- **Bonds**: Natural hedge as stocks fall, bonds typically rise

**4. Volatility Management**
- VIX <15 = complacency, consider reducing exposure
- VIX >30 = fear, often creates buying opportunities
- High volatility = opportunity to trim winners, buy dips strategically

**5. Correlation Awareness**
- Stocks + bonds typically move opposite (diversification benefit)
- Small-cap + large-cap correlations rise in crashes (less diversification benefit)
- International stocks provide some diversification in US downturns

**Red Flags for Portfolio Concentration Risk:**
- Any single position >10% of portfolio
- More than 2-3 positions >5% each
- Industry concentration >40% in one sector
- All stocks in one country/geography

**The Barbell Approach:**
- 70% Very Safe (index funds, blue chips, bonds)
- 30% Calculated Risks (small caps, emerging markets, innovative companies)
- Provides stability + upside potential
- Avoids being "medium-risk" everywhere

⚠️ **Good risk management is about sleeping at night, not hitting homeruns.**
"""
    
    def _get_default_response(self, user_message: str) -> str:
        """Get response for general questions"""
        return f"""
💡 **Stock Advisor Pro - Chat Assistant**

I didn't quite understand your question: "{user_message}"

I can help you with:
- **Stock Recommendations**: "What stocks should I buy?"
- **Buy Signals**: "When should I buy stocks?" / "What are good entry points?"
- **Sell Signals**: "When should I sell?" / "Profit taking strategy"
- **Shorting**: "How to short?" / "Bearish stocks"
- **Analysis**: "Analyze AAPL" / "Stock fundamentals"
- **Portfolio**: "Portfolio diversification" / "Asset allocation"
- **Market**: "Market outlook" / "Fed policy impact"
- **Risk**: "Risk management" / "Hedging strategies"

Try asking a specific question above, or mention stock symbols (AAPL, MSFT, GOOGL, etc.) for analysis!
"""


# Thread worker for async chatbot responses
from PySide6.QtCore import QObject, Signal


class ChatbotWorker(QObject):
    """Worker thread for chatbot responses"""
    
    response_ready = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, chatbot: StockChatbot):
        super().__init__()
        self.chatbot = chatbot
    
    def process_message(self, message: str):
        """Process message and emit response"""
        try:
            response = self.chatbot.get_response(message)
            self.response_ready.emit(response)
        except Exception as e:
            logger.error(f"Error in chatbot worker: {e}")
            self.error_occurred.emit(str(e))
