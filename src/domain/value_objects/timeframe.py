"""
Timeframe Value Object
"""
from dataclasses import dataclass
from src.config.constants import Timeframe


@dataclass(frozen=True)
class TimeframeVO:
    """Timeframe value object - immutable"""
    
    timeframe: Timeframe
    
    def __post_init__(self):
        """Validate timeframe"""
        if not isinstance(self.timeframe, Timeframe):
            raise ValueError("Invalid timeframe type")
    
    @property
    def days(self) -> int:
        """Get number of days for timeframe"""
        mapping = {
            Timeframe.SHORT: 30,
            Timeframe.MEDIUM: 90,
            Timeframe.LONG: 365
        }
        return mapping[self.timeframe]
    
    @property
    def description(self) -> str:
        """Get human-readable description"""
        descriptions = {
            Timeframe.SHORT: "Short-term (days to weeks)",
            Timeframe.MEDIUM: "Medium-term (weeks to months)",
            Timeframe.LONG: "Long-term (months to years)"
        }
        return descriptions[self.timeframe]
    
    @classmethod
    def from_string(cls, timeframe_str: str) -> "TimeframeVO":
        """Create from string"""
        try:
            tf = Timeframe(timeframe_str.lower())
            return cls(timeframe=tf)
        except ValueError:
            raise ValueError(f"Invalid timeframe: {timeframe_str}")
    
    @classmethod
    def short(cls) -> "TimeframeVO":
        """Create short-term timeframe"""
        return cls(timeframe=Timeframe.SHORT)
    
    @classmethod
    def medium(cls) -> "TimeframeVO":
        """Create medium-term timeframe"""
        return cls(timeframe=Timeframe.MEDIUM)
    
    @classmethod
    def long(cls) -> "TimeframeVO":
        """Create long-term timeframe"""
        return cls(timeframe=Timeframe.LONG)

