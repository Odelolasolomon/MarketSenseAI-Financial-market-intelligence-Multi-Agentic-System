"""
Pytest Configuration and Fixtures
"""
import pytest
import os
from unittest.mock import MagicMock


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    os.environ["OPENAI_API_KEY"] = "test-key-123"
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"
    os.environ["REDIS_URL"] = "redis://localhost:6379/15"
    os.environ["DEBUG"] = "True"
    os.environ["ENVIRONMENT"] = "test"


@pytest.fixture
def mock_cache():
    """Mock cache manager"""
    cache = MagicMock()
    cache.get.return_value = None
    cache.set.return_value = True
    cache.delete.return_value = True
    cache.health_check.return_value = True
    return cache


@pytest.fixture
def mock_database():
    """Mock database manager"""
    db = MagicMock()
    db.health_check.return_value = True
    return db


@pytest.fixture
def sample_market_data():
    """Sample market data"""
    return {
        "asset_symbol": "BTC",
        "price": 45000.0,
        "volume": 1000000.0,
        "change_24h": 2.5,
        "high_price": 46000.0,
        "low_price": 44000.0
    }


@pytest.fixture
def sample_analysis():
    """Sample analysis result"""
    return {
        "query": "Should I buy Bitcoin?",
        "asset_symbol": "BTC",
        "outlook": "bullish",
        "confidence": 0.75,
        "trading_action": "buy",
        "risk_level": "medium"
    }