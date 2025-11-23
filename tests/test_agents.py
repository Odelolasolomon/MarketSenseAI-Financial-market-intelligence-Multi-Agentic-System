"""
Tests for AI Agents
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.application.agents.macro_analyst import MacroAnalyst
from src.application.agents.technical_analyst import TechnicalAnalyst
from src.application.agents.sentiment_analyst import SentimentAnalyst
from src.application.agents.synthesis_agent import SynthesisAgent


@pytest.fixture
def mock_response():
    """Mock API response"""
    return {
        "summary": "Test analysis summary",
        "confidence": 0.75,
        "key_factors": ["factor1", "factor2"],
        "risks": ["risk1"]
    }


class TestMacroAnalyst:
    """Tests for Macro Analyst Agent"""
    
    @pytest.mark.asyncio
    async def test_macro_analyst_initialization(self):
        """Test agent initialization"""
        agent = MacroAnalyst()
        assert agent.name == "Macro Analyst"
        assert agent.model == "gpt-4"
    
    @pytest.mark.asyncio
    @patch('src.application.agents.macro_analyst.FREDClient')
    @patch('src.application.agents.macro_analyst.NewsAPIClient')
    async def test_macro_analyst_analyze(self, mock_news, mock_fred, mock_openai_response):
        """Test macro analysis"""
        # Setup mocks
        mock_fred_instance = AsyncMock()
        mock_fred_instance.get_economic_indicators = AsyncMock(return_value={
            "fed_funds_rate": {"value": 5.33},
            "inflation_cpi": {"value": 3.2}
        })
        mock_fred.return_value.__aenter__.return_value = mock_fred_instance
        
        mock_news_instance = AsyncMock()
        mock_news_instance.get_top_headlines = AsyncMock(return_value={
            "articles": [{"title": "Economic news"}]
        })
        mock_news.return_value.__aenter__.return_value = mock_news_instance
        
        agent = MacroAnalyst()
        
        # Mock LLM call
        with patch.object(agent, 'execute_llm_call', new=AsyncMock(
            return_value='{"summary": "Test", "confidence": 0.8, "key_factors": []}'
        )):
            result = await agent.analyze("Analyze USD outlook")
            
            assert "agent_name" in result
            assert result["agent_name"] == "Macro Analyst"
            assert "confidence" in result


class TestTechnicalAnalyst:
    """Tests for Technical Analyst Agent"""
    
    @pytest.mark.asyncio
    async def test_technical_analyst_initialization(self):
        """Test agent initialization"""
        agent = TechnicalAnalyst()
        assert agent.name == "Technical Analyst"
    
    @pytest.mark.asyncio
    @patch('src.application.agents.technical_analyst.BinanceClient')
    async def test_technical_analyst_analyze(self, mock_binance):
        """Test technical analysis"""
        # Setup mock
        mock_binance_instance = AsyncMock()
        mock_binance_instance.get_24h_ticker = AsyncMock(return_value={
            "lastPrice": "45000",
            "priceChangePercent": "2.5",
            "volume": "1000000",
            "highPrice": "46000",
            "lowPrice": "44000"
        })
        mock_binance_instance.get_klines = AsyncMock(return_value=[
            [1234567890, "45000", "46000", "44000", "45500", "1000", None, None, None, None, None, None]
        ] * 200)
        mock_binance.return_value.__aenter__.return_value = mock_binance_instance
        
        agent = TechnicalAnalyst()
        
        with patch.object(agent, 'execute_llm_call', new=AsyncMock(
            return_value='{"summary": "Bullish", "confidence": 0.75, "key_factors": []}'
        )):
            result = await agent.analyze("Analyze BTC", {"asset_symbol": "BTC"})
            
            assert "agent_name" in result
            assert result["agent_name"] == "Technical Analyst"


class TestSentimentAnalyst:
    """Tests for Sentiment Analyst Agent"""
    
    @pytest.mark.asyncio
    @patch('src.application.agents.sentiment_analyst.NewsAPIClient')
    async def test_sentiment_analyst_analyze(self, mock_news):
        """Test sentiment analysis"""
        # Setup mock
        mock_news_instance = AsyncMock()
        mock_news_instance.search_crypto_news = AsyncMock(return_value=[
            {"title": "Bitcoin rises", "source": {"name": "CoinDesk"}}
        ])
        mock_news.return_value.__aenter__.return_value = mock_news_instance
        
        agent = SentimentAnalyst()
        
        with patch.object(agent, 'execute_llm_call', new=AsyncMock(
            return_value='{"summary": "Positive", "sentiment_score": 65, "confidence": 0.7, "key_factors": []}'
        )):
            result = await agent.analyze("Market sentiment", {"asset_symbol": "BTC"})
            
            assert "agent_name" in result
            assert result["agent_name"] == "Sentiment Analyst"


class TestSynthesisAgent:
    """Tests for Synthesis Agent"""
    
    @pytest.mark.asyncio
    async def test_synthesis_agent_initialization(self):
        """Test synthesis agent initialization"""
        agent = SynthesisAgent()
        assert agent.name == "Synthesis Agent"
        assert agent.macro_analyst is not None
        assert agent.technical_analyst is not None
        assert agent.sentiment_analyst is not None
    
    @pytest.mark.asyncio
    async def test_synthesis_agent_coordination(self):
        """Test agent coordination"""
        agent = SynthesisAgent()
        
        # Mock specialist agents
        mock_result = {
            "agent_name": "Test Agent",
            "summary": "Test summary",
            "confidence": 0.75,
            "key_factors": ["factor1"],
            "data_sources": ["source1"],
            "detailed_analysis": {}
        }
        
        with patch.object(agent.macro_analyst, 'analyze', new=AsyncMock(return_value=mock_result)):
            with patch.object(agent.technical_analyst, 'analyze', new=AsyncMock(return_value=mock_result)):
                with patch.object(agent.sentiment_analyst, 'analyze', new=AsyncMock(return_value=mock_result)):
                    with patch.object(agent, 'execute_llm_call', new=AsyncMock(
                        return_value='{"executive_summary": "Test", "outlook": "bullish", "trading_action": "buy", "confidence": 0.75}'
                    )):
                        result = await agent.analyze("Test query", {"asset_symbol": "BTC"})
                        
                        assert result is not None
                        assert result.asset_symbol == "BTC"
                        assert result.macro_analysis is not None
                        assert result.technical_analysis is not None
                        assert result.sentiment_analysis is not None

