"""
Sentiment Value Object
"""
from dataclasses import dataclass
from typing import Optional
from src.config.constants import (
    SENTIMENT_EXTREMELY_BEARISH,
    SENTIMENT_BEARISH,
    SENTIMENT_NEUTRAL,
    SENTIMENT_BULLISH,
    SENTIMENT_EXTREMELY_BULLISH
)


@dataclass(frozen=True)
class SentimentVO:
    """Sentiment value object - immutable"""
    
    score: float
    label: Optional[str] = None
    
    def __post_init__(self):
        """Validate sentiment score"""
        if not 0 <= self.score <= 100:
            raise ValueError("Sentiment score must be between 0 and 100")
    
    @property
    def sentiment_label(self) -> str:
        """Get sentiment label based on score"""
        if self.label:
            return self.label
        
        if self.score < SENTIMENT_EXTREMELY_BEARISH:
            return "extremely_bearish"
        elif self.score < SENTIMENT_BEARISH:
            return "bearish"
        elif self.score < SENTIMENT_NEUTRAL:
            return "neutral"
        elif self.score < SENTIMENT_BULLISH:
            return "bullish"
        else:
            return "extremely_bullish"
    
    @property
    def is_bullish(self) -> bool:
        """Check if sentiment is bullish"""
        return self.score >= SENTIMENT_NEUTRAL
    
    @property
    def is_bearish(self) -> bool:
        """Check if sentiment is bearish"""
        return self.score < SENTIMENT_NEUTRAL
    
    @property
    def is_extreme(self) -> bool:
        """Check if sentiment is extreme"""
        return (
            self.score < SENTIMENT_EXTREMELY_BEARISH or
            self.score > SENTIMENT_BULLISH
        )
    
    @classmethod
    def from_score(cls, score: float) -> "SentimentVO":
        """Create from score"""
        return cls(score=score)
    
    @classmethod
    def bullish(cls, strength: str = "moderate") -> "SentimentVO":
        """Create bullish sentiment"""
        scores = {"weak": 60, "moderate": 70, "strong": 85}
        return cls(score=scores.get(strength, 70))
    
    @classmethod
    def bearish(cls, strength: str = "moderate") -> "SentimentVO":
        """Create bearish sentiment"""
        scores = {"weak": 40, "moderate": 30, "strong": 15}
        return cls(score=scores.get(strength, 30))