"""
Asset Entity - Represents a tradeable asset
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from src.config.constants import AssetType


@dataclass
class Asset:
    """Asset domain entity"""
    
    symbol: str
    name: str
    asset_type: AssetType
    base_currency: Optional[str] = None
    quote_currency: Optional[str] = None
    exchange: Optional[str] = None
    is_active: bool = True
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate asset after initialization"""
        if not self.symbol:
            raise ValueError("Asset symbol cannot be empty")
        
        self.symbol = self.symbol.upper().strip()
        
        if self.asset_type == AssetType.CRYPTO and "/" in self.symbol:
            parts = self.symbol.split("/")
            if len(parts) == 2:
                self.base_currency = parts[0]
                self.quote_currency = parts[1]
        
        elif self.asset_type == AssetType.FOREX:
            if "/" in self.symbol:
                parts = self.symbol.split("/")
                if len(parts) == 2:
                    self.base_currency = parts[0]
                    self.quote_currency = parts[1]
            elif len(self.symbol) == 6:
                self.base_currency = self.symbol[:3]
                self.quote_currency = self.symbol[3:]
    
    @property
    def display_name(self) -> str:
        """Get display name for asset"""
        if self.base_currency and self.quote_currency:
            return f"{self.base_currency}/{self.quote_currency}"
        return self.name or self.symbol
    
    @property
    def identifier(self) -> str:
        """Get unique identifier"""
        return f"{self.asset_type.value}:{self.symbol}"
    
    def update(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "asset_type": self.asset_type.value,
            "base_currency": self.base_currency,
            "quote_currency": self.quote_currency,
            "exchange": self.exchange,
            "is_active": self.is_active,
            "display_name": self.display_name,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }