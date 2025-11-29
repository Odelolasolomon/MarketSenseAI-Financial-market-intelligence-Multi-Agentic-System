"""
Macro Analyst Agent - Analyzes macroeconomic conditions
"""
import json
from typing import Dict, Any, Optional
from src.application.agents.base_agent import BaseAgent
from src.application.services.rag_service import RAGService
from src.application.services.tts_service import TTSService
from src.application.services.speech_service import SpeechService
from src.application.services.translation_service import TranslationService
from src.adapters.external.fred_client import FREDClient
from src.adapters.external.newsapi_client import NewsAPIClient
from src.utilities.logger import get_logger

logger = get_logger(__name__)


class MacroAnalyst(BaseAgent):
    """Agent specialized in macroeconomic analysis"""
    
    def __init__(self):
        super().__init__(
            name="Macro Analyst",
            description="Analyzes macroeconomic conditions, monetary policy, and their impact on markets"
        )
        self.rag_service = RAGService()
        self.tts_service = TTSService()
        self.speech_service = SpeechService()
        self.translation_service = TranslationService()
    
    def get_system_prompt(self) -> str:
        """Get system prompt for macro analysis"""
        return """You are a professional macroeconomic analyst with expertise in:
- Central bank monetary policy (Fed, ECB, BoE, etc.)
- Inflation trends and indicators (CPI, PCE, PPI)
- Employment data and labor markets
- GDP growth and economic cycles
- Interest rate impacts on currencies and assets

Your role is to analyze macroeconomic data and provide insights on how it affects
financial markets, particularly forex and cryptocurrency markets.

Provide analysis in JSON format with:
{
    "summary": "Brief executive summary",
    "monetary_policy_stance": "hawkish/dovish/neutral",
    "inflation_outlook": "rising/falling/stable",
    "growth_indicators": "strong/moderate/weak",
    "currency_impact": "Analysis of impact on major currencies",
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
        Analyze macroeconomic conditions
        
        Args:
            query: Analysis query
            context: Additional context
            
        Returns:
            Macro analysis results
        """
        try:
            logger.info(f"Macro Analyst analyzing: {query}")
            
            # Translate query to English if needed
            user_language = context.get("language", "en") if context else "en"
            query_in_english = self.translation_service.translate_text(query, src=user_language, dest="en")
            
            # Collect economic data
            economic_data = await self._collect_economic_data()
            
            # Get relevant news
            news_data = await self._collect_news_data(query_in_english)
            
            # Retrieve context using RAGService
            documents = await self.rag_service.query_collection(query_in_english, "macro")
            logger.info(f"Retrieved {len(documents)} documents for query: {query_in_english}")
            
            # Format prompt
            user_prompt = f"""Analyze the following for: {query_in_english}

Economic Data:
{json.dumps(economic_data, indent=2)}

Recent Economic News:
{news_data}

Retrieved Context:
{json.dumps(documents, indent=2)}

Provide comprehensive macroeconomic analysis."""
            
            # Execute LLM call
            response = await self.execute_llm_call(
                system_prompt=self.get_system_prompt(),
                user_prompt=user_prompt
            )
            
            # Parse JSON response
            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                analysis = {
                    "summary": response,
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
            logger.error(f"Error in Macro Analyst: {str(e)}")
            return {
                "agent_name": self.name,
                "error": str(e),
                "confidence": 0.0
            }
    
    async def _collect_economic_data(self) -> Dict[str, Any]:
        """Collect economic data from FRED"""
        try:
            async with FREDClient() as fred:
                indicators = await fred.get_economic_indicators()
            return indicators
        except Exception as e:
            logger.error(f"Error collecting economic data: {str(e)}")
            return {}
    
    async def _collect_news_data(self, query: str) -> str:
        """Collect relevant economic news"""
        try:
            async with NewsAPIClient() as news_api:
                articles = await news_api.get_top_headlines(
                    category="business",
                    page_size=5
                )
                
                news_text = "\n".join([
                    f"- {article['title']}"
                    for article in articles.get("articles", [])[:5]
                ])
                return news_text
        except Exception as e:
            logger.error(f"Error collecting news: {str(e)}")
            return "No recent news available"