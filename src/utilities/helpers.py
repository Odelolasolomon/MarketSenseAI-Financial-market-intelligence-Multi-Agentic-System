"""
Helper Utility Functions
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import re
from src.config.constants import Timeframe, RiskLevel


def parse_timeframe_to_days(timeframe: str) -> int:
    """
    Convert timeframe string to number of days
    
    Args:
        timeframe: Timeframe string (short/medium/long)
        
    Returns:
        Number of days
    """
    mapping = {
        Timeframe.SHORT: 30,
        Timeframe.MEDIUM: 90,
        Timeframe.LONG: 365
    }
    
    try:
        tf = Timeframe(timeframe.lower())
        return mapping[tf]
    except (ValueError, KeyError):
        return 90  


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format value as percentage
    
    Args:
        value: Numeric value
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimals}f}%"


def format_currency(
    value: float,
    currency: str = "USD",
    decimals: int = 2
) -> str:
    """
    Format value as currency
    
    Args:
        value: Numeric value
        currency: Currency symbol
        decimals: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    return f"{currency} {value:,.{decimals}f}"


def normalize_asset_symbol(symbol: str) -> str:
    """
    Normalize asset symbol to standard format
    
    Args:
        symbol: Raw asset symbol
        
    Returns:
        Normalized symbol (uppercase, no spaces)
    """
    normalized = symbol.upper().strip()
    
    crypto_map = {
        "BITCOIN": "BTC",
        "ETHEREUM": "ETH",
        "RIPPLE": "XRP",
        "BINANCE COIN": "BNB",
        "CARDANO": "ADA",
        "SOLANA": "SOL",
        "DOGECOIN": "DOGE"
    }
    
    return crypto_map.get(normalized, normalized)


def calculate_risk_score(
    volatility: float,
    confidence: float,
    sentiment_score: float,
    market_conditions: Dict[str, Any]
) -> float:
    """
    Calculate overall risk score
    
    Args:
        volatility: Market volatility (0-1)
        confidence: Analysis confidence (0-1)
        sentiment_score: Market sentiment (0-100)
        market_conditions: Additional market data
        
    Returns:
        Risk score from 0-1 (higher = more risky)
    """
    normalized_sentiment = abs(sentiment_score - 50) / 50
    
    risk_score = (
        volatility * 0.4 +
        (1 - confidence) * 0.3 +
        normalized_sentiment * 0.3
    )
    
    return min(max(risk_score, 0.0), 1.0)


def get_risk_level(risk_score: float) -> RiskLevel:
    """
    Convert risk score to risk level
    
    Args:
        risk_score: Risk score (0-1)
        
    Returns:
        Risk level enum
    """
    if risk_score < 0.2:
        return RiskLevel.VERY_LOW
    elif risk_score < 0.4:
        return RiskLevel.LOW
    elif risk_score < 0.6:
        return RiskLevel.MEDIUM
    elif risk_score < 0.8:
        return RiskLevel.HIGH
    else:
        return RiskLevel.VERY_HIGH


def validate_asset_symbol(symbol: str) -> bool:
    """
    Validate asset symbol format
    
    Args:
        symbol: Asset symbol to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol or len(symbol) < 2 or len(symbol) > 10:
        return False
    
    pattern = r'^[A-Z0-9]+[/-]?[A-Z0-9]*$'
    return bool(re.match(pattern, symbol.upper()))


def get_date_range(days: int) -> tuple:
    """
    Get date range for data collection
    
    Args:
        days: Number of days back from now
        
    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers
    
    Args:
        numerator: Number to divide
        denominator: Number to divide by
        default: Default value if division fails
        
    Returns:
        Result of division or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default
