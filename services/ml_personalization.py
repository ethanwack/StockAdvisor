"""
Machine Learning & Personalization Service
Personalized stock recommendations using ML and user interaction tracking
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import os
import numpy as np


class InteractionType(Enum):
    """User interaction types"""
    VIEWED_STOCK = "viewed_stock"
    SEARCHED_STOCK = "searched_stock"
    ADDED_TO_WATCHLIST = "added_to_watchlist"
    REMOVED_FROM_WATCHLIST = "removed_from_watchlist"
    SET_ALERT = "set_alert"
    VIEWED_ANALYSIS = "viewed_analysis"
    USED_SCREENER = "used_screener"
    EXECUTED_TRADE = "executed_trade"
    BACKTEST_STRATEGY = "backtest_strategy"
    VIEWED_OPTION = "viewed_option"


class RiskProfile(Enum):
    """User risk profile"""
    CONSERVATIVE = "conservative"  # Low risk, stable income
    MODERATE = "moderate"          # Balanced growth
    AGGRESSIVE = "aggressive"      # High growth, high risk


@dataclass
class UserInteraction:
    """User interaction record"""
    interaction_type: InteractionType
    symbol: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'interaction_type': self.interaction_type.value,
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class UserProfile:
    """User preference profile"""
    user_id: str
    risk_profile: RiskProfile = RiskProfile.MODERATE
    favorite_sectors: List[str] = field(default_factory=list)
    favorite_symbols: List[str] = field(default_factory=list)
    watchlist: List[str] = field(default_factory=list)
    interactions: List[UserInteraction] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def add_interaction(self, interaction: UserInteraction):
        """Add user interaction"""
        self.interactions.append(interaction)
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'risk_profile': self.risk_profile.value,
            'favorite_sectors': self.favorite_sectors,
            'favorite_symbols': self.favorite_symbols,
            'watchlist': self.watchlist,
            'interactions': [i.to_dict() for i in self.interactions],
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }


@dataclass
class RecommendationScore:
    """Score for a recommendation"""
    symbol: str
    score: float  # 0-100
    confidence: float  # 0-1
    reasons: List[str] = field(default_factory=list)
    risk_level: str = "moderate"
    sector: Optional[str] = None
    predicted_return: Optional[float] = None
    
    def __lt__(self, other):
        """For sorting by score"""
        return self.score < other.score


class PreferenceEngine:
    """Engine for learning user preferences"""
    
    def __init__(self):
        self.sector_preferences = {}
        self.symbol_preferences = {}
        self.risk_preference = RiskProfile.MODERATE
    
    def analyze_interactions(self, interactions: List[UserInteraction]) -> Dict:
        """
        Analyze user interactions to learn preferences
        
        Args:
            interactions: List of user interactions
            
        Returns:
            Dict with preference analysis
        """
        # Count interaction types
        type_counts = {}
        for interaction in interactions:
            key = interaction.interaction_type.value
            type_counts[key] = type_counts.get(key, 0) + 1
        
        # Count symbol views
        symbol_counts = {}
        for interaction in interactions:
            if interaction.symbol:
                symbol_counts[interaction.symbol] = symbol_counts.get(interaction.symbol, 0) + 1
        
        # Sector preferences
        sector_counts = {}
        for interaction in interactions:
            if 'sector' in interaction.metadata:
                sector = interaction.metadata['sector']
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        # Calculate risk profile from interactions
        risk_indicators = {
            'backtest_strategy': 3,  # 3x weight for backtesting
            'viewed_option': 2,      # 2x weight for options
            'set_alert': 0.5,        # 0.5x weight for alerts
        }
        
        risk_score = sum(
            risk_indicators.get(itype, 1) for itype in type_counts.keys()
        ) / max(len(interactions), 1)
        
        if risk_score > 2.0:
            self.risk_preference = RiskProfile.AGGRESSIVE
        elif risk_score < 1.0:
            self.risk_preference = RiskProfile.CONSERVATIVE
        else:
            self.risk_preference = RiskProfile.MODERATE
        
        return {
            'interaction_types': type_counts,
            'favorite_symbols': sorted(
                symbol_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'sector_preferences': sorted(
                sector_counts.items(),
                key=lambda x: x[1],
                reverse=True
            ),
            'inferred_risk_profile': self.risk_preference.value
        }


class RecommendationEngine:
    """Engine for generating personalized recommendations"""
    
    def __init__(self, user_profile: UserProfile):
        self.user_profile = user_profile
        self.preference_engine = PreferenceEngine()
    
    def generate_recommendations(self, candidates: List[Dict],
                                limit: int = 10) -> List[RecommendationScore]:
        """
        Generate personalized recommendations
        
        Args:
            candidates: List of candidate stocks with data
            limit: Number of recommendations to return
            
        Returns:
            List of RecommendationScore sorted by score
        """
        recommendations = []
        
        # Learn preferences from history
        preferences = self.preference_engine.analyze_interactions(
            self.user_profile.interactions
        )
        
        # Score each candidate
        for candidate in candidates:
            symbol = candidate.get('symbol')
            
            # Base score from technical/fundamental metrics
            score = self._calculate_base_score(candidate)
            
            # Boost if in watchlist
            if symbol in self.user_profile.watchlist:
                score += 15
            
            # Boost based on sector preference
            sector = candidate.get('sector')
            if sector and any(s[0] == sector for s in preferences.get('sector_preferences', [])):
                score += 10
            
            # Adjust for risk profile
            risk_adjustment = self._get_risk_adjustment(candidate)
            score += risk_adjustment
            
            # Calculate confidence (0-1)
            confidence = self._calculate_confidence(candidate, preferences)
            
            # Get predicted return
            predicted_return = candidate.get('predicted_return', 0.0)
            
            # Collect reasons
            reasons = self._generate_reasons(candidate, preferences)
            
            rec = RecommendationScore(
                symbol=symbol,
                score=max(0, min(100, score)),  # Clamp 0-100
                confidence=confidence,
                reasons=reasons,
                risk_level=self._get_risk_level(candidate),
                sector=sector,
                predicted_return=predicted_return
            )
            
            recommendations.append(rec)
        
        # Sort by score and return top limit
        recommendations.sort(reverse=True, key=lambda x: (x.score, x.confidence))
        return recommendations[:limit]
    
    def _calculate_base_score(self, candidate: Dict) -> float:
        """
        Calculate base recommendation score from metrics
        
        Args:
            candidate: Stock data
            
        Returns:
            Base score (0-100)
        """
        score = 50.0  # Start with neutral score
        
        # Technical metrics
        if 'rsi' in candidate:
            rsi = candidate['rsi']
            if rsi < 30:
                score += 15  # Oversold = buy signal
            elif rsi > 70:
                score -= 15  # Overbought = sell signal
        
        if 'macd_signal' in candidate:
            if candidate['macd_signal'] > 0:
                score += 10
            else:
                score -= 10
        
        # Momentum
        if 'momentum_pct' in candidate:
            momentum = candidate['momentum_pct']
            score += momentum / 2  # Max +/- 50 from momentum
        
        # Fundamental metrics
        if 'pe_ratio' in candidate:
            pe = candidate['pe_ratio']
            if 10 < pe < 25:  # Reasonable range
                score += 5
            elif pe > 50:
                score -= 10  # Too expensive
        
        if 'dividend_yield' in candidate:
            if candidate['dividend_yield'] > 0.02:
                score += 5
        
        # Sentiment if available
        if 'sentiment_score' in candidate:
            sentiment = candidate['sentiment_score']  # -1 to 1
            score += sentiment * 20
        
        return score
    
    def _calculate_confidence(self, candidate: Dict, preferences: Dict) -> float:
        """Calculate confidence in recommendation (0-1)"""
        confidence = 0.5
        
        # More data = more confidence
        data_points = sum(1 for k in candidate.keys() if k != 'symbol' and candidate[k] is not None)
        confidence += (data_points / 20) * 0.3  # Up to +0.3
        
        # If user has history with this symbol, higher confidence
        if candidate.get('symbol') in self.user_profile.favorite_symbols:
            confidence += 0.15
        
        # Clamp to 0-1
        return max(0, min(1, confidence))
    
    def _get_risk_adjustment(self, candidate: Dict) -> float:
        """Get score adjustment based on user's risk profile"""
        if self.user_profile.risk_profile == RiskProfile.CONSERVATIVE:
            # Prefer stable, low-volatility stocks
            volatility = candidate.get('volatility', 0.25)
            if volatility < 0.20:
                return 10
            elif volatility > 0.40:
                return -15
            return 0
        
        elif self.user_profile.risk_profile == RiskProfile.AGGRESSIVE:
            # Prefer high-growth, higher-volatility stocks
            volatility = candidate.get('volatility', 0.25)
            if volatility > 0.40:
                return 10
            momentum = candidate.get('momentum_pct', 0)
            return momentum / 2
        
        else:  # MODERATE
            return 0
    
    def _get_risk_level(self, candidate: Dict) -> str:
        """Determine risk level of candidate"""
        volatility = candidate.get('volatility', 0.25)
        
        if volatility < 0.15:
            return "low"
        elif volatility > 0.40:
            return "high"
        else:
            return "moderate"
    
    def _generate_reasons(self, candidate: Dict, preferences: Dict) -> List[str]:
        """Generate human-readable reasons for recommendation"""
        reasons = []
        
        symbol = candidate.get('symbol', 'Stock')
        
        # Technical reasons
        if candidate.get('rsi', 50) < 30:
            reasons.append(f"{symbol} is oversold (RSI < 30)")
        
        if candidate.get('macd_signal', 0) > 0:
            reasons.append("MACD showing positive momentum")
        
        # Momentum
        momentum = candidate.get('momentum_pct', 0)
        if momentum > 5:
            reasons.append(f"{symbol} has strong upward momentum ({momentum:.1f}%)")
        elif momentum < -5:
            reasons.append(f"{symbol} has downward momentum ({momentum:.1f}%)")
        
        # Fundamental
        pe = candidate.get('pe_ratio')
        if pe and 10 < pe < 25:
            reasons.append(f"Reasonable P/E ratio ({pe:.1f})")
        
        dividend = candidate.get('dividend_yield', 0)
        if dividend > 0.02:
            reasons.append(f"Good dividend yield ({dividend*100:.2f}%)")
        
        # Watchlist
        if symbol in self.user_profile.watchlist:
            reasons.append("In your watchlist")
        
        # Return default if no reasons
        if not reasons:
            reasons = [f"{symbol} meets technical criteria"]
        
        return reasons[:5]  # Limit to 5 reasons
    
    def explain_recommendation(self, recommendation: RecommendationScore) -> str:
        """Generate human-readable explanation for a recommendation"""
        explanation = f"""
╔════════════════════════════════════════════════════════╗
║          PERSONALIZED RECOMMENDATION                   ║
╚════════════════════════════════════════════════════════╝

SYMBOL:              {recommendation.symbol}
SCORE:               {recommendation.score:.1f}/100
CONFIDENCE:          {recommendation.confidence*100:.0f}%
RISK LEVEL:          {recommendation.risk_level.upper()}

SECTOR:              {recommendation.sector or 'N/A'}
PREDICTED RETURN:    {recommendation.predicted_return:.2f}% if recommendation.predicted_return else 'N/A'

REASONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for i, reason in enumerate(recommendation.reasons, 1):
            explanation += f"  {i}. {reason}\n"
        
        explanation += f"""
USER PROFILE:
• Risk Profile: {self.user_profile.risk_profile.value.upper()}
• Watchlist Size: {len(self.user_profile.watchlist)} stocks
• Interactions: {len(self.user_profile.interactions)} recorded

DISCLAIMER:
This recommendation is based on historical data and ML analysis.
Always conduct your own research before making investment decisions.
Past performance does not guarantee future results.
"""
        
        return explanation


class MLPersonalizationEngine:
    """Main engine combining ML and personalization"""
    
    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.recommendation_engines: Dict[str, RecommendationEngine] = {}
    
    def get_or_create_user(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
            self.recommendation_engines[user_id] = RecommendationEngine(
                self.user_profiles[user_id]
            )
        return self.user_profiles[user_id]
    
    def record_interaction(self, user_id: str, interaction: UserInteraction):
        """Record user interaction"""
        profile = self.get_or_create_user(user_id)
        profile.add_interaction(interaction)
    
    def update_user_profile(self, user_id: str, risk_profile: Optional[RiskProfile] = None,
                           favorite_sectors: Optional[List[str]] = None,
                           watchlist: Optional[List[str]] = None):
        """Update user preferences"""
        profile = self.get_or_create_user(user_id)
        
        if risk_profile:
            profile.risk_profile = risk_profile
        if favorite_sectors:
            profile.favorite_sectors = favorite_sectors
        if watchlist:
            profile.watchlist = watchlist
        
        profile.last_updated = datetime.now()
    
    def get_recommendations(self, user_id: str, candidates: List[Dict],
                           limit: int = 10) -> List[RecommendationScore]:
        """Get personalized recommendations for user"""
        profile = self.get_or_create_user(user_id)
        engine = self.recommendation_engines[user_id]
        return engine.generate_recommendations(candidates, limit)
    
    def get_profile_insights(self, user_id: str) -> Dict:
        """Get insights about user's trading preferences"""
        profile = self.get_or_create_user(user_id)
        engine = self.recommendation_engines[user_id]
        preferences = engine.preference_engine.analyze_interactions(profile.interactions)
        
        return {
            'user_id': user_id,
            'risk_profile': profile.risk_profile.value,
            'interaction_count': len(profile.interactions),
            'favorite_symbols': profile.favorite_symbols,
            'watchlist_size': len(profile.watchlist),
            'preferences': preferences
        }
    
    def save_profile(self, user_id: str, filepath: str):
        """Save user profile to file"""
        profile = self.get_or_create_user(user_id)
        
        with open(filepath, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
    
    def load_profile(self, user_id: str, filepath: str):
        """Load user profile from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            profile = UserProfile(user_id=user_id)
            profile.risk_profile = RiskProfile(data.get('risk_profile', 'moderate'))
            profile.favorite_sectors = data.get('favorite_sectors', [])
            profile.favorite_symbols = data.get('favorite_symbols', [])
            profile.watchlist = data.get('watchlist', [])
            
            # Load interactions
            for interaction_data in data.get('interactions', []):
                interaction = UserInteraction(
                    interaction_type=InteractionType(interaction_data['interaction_type']),
                    symbol=interaction_data.get('symbol'),
                    metadata=interaction_data.get('metadata', {})
                )
                profile.interactions.append(interaction)
            
            self.user_profiles[user_id] = profile
            self.recommendation_engines[user_id] = RecommendationEngine(profile)
            
            return profile
        
        return None
