"""
Sentiment Analyst Agent - Analyzes market sentiment and news
"""
import json
from typing import Dict, Any, Optional
from src.application.agents.base_agent import BaseAgent
from src.application.services.rag_service import RAGService
from src.application.services.tts_service import TTSService
from src.application.services.speech_service import SpeechService
from src.application.services.translation_service import TranslationService
from src.adapters.external.newsapi_client import NewsAPIClient
from src.utilities.logger import get_logger

logger = get_logger(__name__)


class SentimentAnalyst(BaseAgent):
    """Agent specialized in sentiment analysis"""
    
    def __init__(self):
        super().__init__(
            name="Sentiment Analyst",
            description="Analyzes market sentiment from news and social signals"
        )
        self.rag_service = RAGService()
        self.tts_service = TTSService()
        self.speech_service = SpeechService()
        self.translation_service = TranslationService()
    
    def get_system_prompt(self) -> str:
        """Get system prompt for sentiment analysis"""
        return """You are an expert sentiment analyst specializing in:
- News sentiment analysis
- Market narratives and themes
- Fear & Greed indicators
- Social media sentiment trends
- Contrarian indicators

Analyze sentiment from news and provide insights in JSON format:
{
    "summary": "Brief sentiment summary",
    "sentiment_score": 0-100 (0=extremely bearish, 50=neutral, 100=extremely bullish),
    "sentiment_label": "extremely_bearish/bearish/neutral/bullish/extremely_bullish",
    "dominant_narratives": {
        "bullish": ["narrative1", ...],
        "bearish": ["narrative1", ...]
    },
    "news_flow": "positive/negative/mixed",
    "contrarian_signals": ["signal1", ...],
    "key_factors": ["factor1", "factor2", ...],
    "confidence": 0.0-1.0,
    "risks": ["risk1", "risk2", ...]
}"""
    
    async def analyze(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze market sentiment
        
        Args:
            query: Analysis query
            context: Additional context with asset info
            
        Returns:
            Sentiment analysis results
        """
        try:
            # Translate query to English if needed
            user_language = context.get("language", "en") if context else "en"
            query_in_english = self.translation_service.translate_text(query, src=user_language, dest="en")
            
            asset = context.get("asset_symbol", "market") if context else "market"
            logger.info(f"Sentiment Analyst analyzing: {asset}")
            
            # Collect news data
            news_data = await self._collect_news_sentiment(asset)
            
            # Retrieve context using RAGService
            documents = await self.rag_service.query_collection(query_in_english, "news")
            logger.info(f"Retrieved {len(documents)} documents for query: {query_in_english}")
            
            # Format prompt
            user_prompt = f"""Analyze market sentiment for {asset}: {query_in_english}

Recent News and Headlines:
{news_data}

Retrieved Context:
{json.dumps(documents, indent=2)}

Provide comprehensive sentiment analysis with specific narratives and signals."""
            
            # Execute LLM call
            response = await self.execute_llm_call(
                system_prompt=self.get_system_prompt(),
                user_prompt=user_prompt
            )
            
            # Parse response
            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                analysis = {
                    "summary": response,
                    "sentiment_score": 50,
                    "confidence": 0.6,
                    "key_factors": []
                }
            
            # Translate response back to user's language
            translated_summary = self.translation_service.translate_text(
                analysis.get("summary", ""), src="en", dest=user_language
            )
            analysis["summary"] = translated_summary
            
            # Convert response to speech if requested
            if context.get("audio_output", False):
                audio_path = self.tts_service.text_to_speech(translated_summary, language=user_language)
                analysis["audio_path"] = audio_path
            
            return self.format_output(
                analysis=analysis,
                confidence=analysis.get("confidence", 0.7),
                key_factors=analysis.get("key_factors", [])
            )
            
        except Exception as e:
            logger.error(f"Error in Sentiment Analyst: {str(e)}")
            return {
                "agent_name": self.name,
                "error": str(e),
                "confidence": 0.0
            }
    
    async def _collect_news_sentiment(self, asset: str) -> str:
        """Collect and format news data"""
        try:
            async with NewsAPIClient() as news_api:
                if asset.upper() in ["BTC", "ETH", "CRYPTO", "BITCOIN", "ETHEREUM"]:
                    articles = await news_api.search_crypto_news(asset, days=3, page_size=10)
                else:
                    result = await news_api.get_everything(
                        query=asset,
                        page_size=10
                    )
                    articles = result.get("articles", [])
                
                # Format news
                news_text = "\n".join([
                    f"- [{article.get('source', {}).get('name', 'Unknown')}] {article.get('title', '')}"
                    for article in articles[:10]
                ])
                
                return news_text if news_text else "No recent news available"
                
        except Exception as e:
            logger.error(f"Error collecting news sentiment: {str(e)}")
            return "Unable to fetch news data"