"""
Application Constants
"""
from enum import Enum


class AssetType(str, Enum):
    """Asset type enumeration"""
    CRYPTO = "crypto"
    FOREX = "forex"
    STOCK = "stock"
    COMMODITY = "commodity"


class Timeframe(str, Enum):
    """Analysis timeframe enumeration"""
    SHORT = "short"      # Days to weeks
    MEDIUM = "medium"    # Weeks to months
    LONG = "long"        # Months to years


class MarketOutlook(str, Enum):
    """Market outlook enumeration"""
    EXTREMELY_BEARISH = "extremely_bearish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BULLISH = "bullish"
    EXTREMELY_BULLISH = "extremely_bullish"


class TradingAction(str, Enum):
    """Trading action recommendation"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"
    WAIT = "wait"


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class DataSource(str, Enum):
    """Data source enumeration"""
    FRED = "fred"
    BINANCE = "binance"
    COINGECKO = "coingecko"
    NEWSAPI = "newsapi"
    YAHOO_FINANCE = "yahoo_finance"


# API Constants
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Cache Keys
CACHE_PREFIX = "multiasset:"
CACHE_MARKET_DATA = f"{CACHE_PREFIX}market:"
CACHE_ANALYSIS = f"{CACHE_PREFIX}analysis:"
CACHE_NEWS = f"{CACHE_PREFIX}news:"

# Rate Limits
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 

# Collection Names
CHROMA_COLLECTION_MACRO = "macro_data"
CHROMA_COLLECTION_CRYPTO = "crypto_data"
CHROMA_COLLECTION_NEWS = "news_sentiment"

# Agent Names
AGENT_MACRO = "Macro Analyst"
AGENT_TECHNICAL = "Technical Analyst"
AGENT_SENTIMENT = "Sentiment Analyst"
AGENT_SYNTHESIS = "Synthesis Agent"

# Popular Trading Pairs
CRYPTO_PAIRS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "SOL/USDT",
    "XRP/USDT", "DOT/USDT", "DOGE/USDT", "AVAX/USDT", "MATIC/USDT"
]

FOREX_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD",
    "USD/CAD", "NZD/USD", "EUR/GBP", "EUR/JPY", "GBP/JPY"
]

# Technical Indicators
TECHNICAL_INDICATORS = [
    "RSI", "MACD", "SMA_50", "SMA_200", "EMA_12", "EMA_26",
    "BB_UPPER", "BB_LOWER", "ATR", "STOCH", "ADX"
]

# Sentiment Thresholds
SENTIMENT_EXTREMELY_BEARISH = 20
SENTIMENT_BEARISH = 40
SENTIMENT_NEUTRAL = 60
SENTIMENT_BULLISH = 80
SENTIMENT_EXTREMELY_BULLISH = 100