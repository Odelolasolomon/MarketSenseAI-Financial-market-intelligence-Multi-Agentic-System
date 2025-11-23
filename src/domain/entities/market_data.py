"""
Market Data Entity - Represents market data for an asset
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class MarketData:
    """Market data domain entity"""
    
    asset_symbol: str
    timestamp: datetime
    price: float
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    volume: Optional[float] = None
    volume_quote: Optional[float] = None
    market_cap: Optional[float] = None
    circulating_supply: Optional[float] = None
    change_24h: Optional[float] = None
    change_7d: Optional[float] = None
    change_30d: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    active_addresses: Optional[int] = None
    transaction_count: Optional[int] = None
    whale_holdings: Optional[float] = None
    exchange_netflow: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    data_source: Optional[str] = None
    
    def __post_init__(self):
        """Validate market data"""
        if self.price <= 0:
            raise ValueError("Price must be greater than 0")
    
    @property
    def is_bullish(self) -> bool:
        """Check if price action is bullish"""
        if self.change_24h is None:
            return False
        return self.change_24h > 0
    
    @property
    def volatility_indicator(self) -> str:
        """Get volatility indicator"""
        if self.change_24h is None:
            return "unknown"
        
        abs_change = abs(self.change_24h)
        if abs_change < 2:
            return "low"
        elif abs_change < 5:
            return "moderate"
        else:
            return "high"
    
    @property
    def trend_signal(self) -> str:
        """Get trend signal based on moving averages"""
        if self.sma_50 is None or self.sma_200 is None:
            return "neutral"
        
        if self.sma_50 > self.sma_200:
            return "bullish"
        elif self.sma_50 < self.sma_200:
            return "bearish"
        return "neutral"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "asset_symbol": self.asset_symbol,
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
            "open_price": self.open_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "close_price": self.close_price,
            "volume": self.volume,
            "volume_quote": self.volume_quote,
            "market_cap": self.market_cap,
            "change_24h": self.change_24h,
            "change_7d": self.change_7d,
            "rsi": self.rsi,
            "macd": self.macd,
            "sma_50": self.sma_50,
            "sma_200": self.sma_200,
            "is_bullish": self.is_bullish,
            "volatility": self.volatility_indicator,
            "trend": self.trend_signal,
            "data_source": self.data_source
        }