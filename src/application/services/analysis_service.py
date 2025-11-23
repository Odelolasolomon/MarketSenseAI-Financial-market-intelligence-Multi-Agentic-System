"""
Analysis Service - Coordinates analysis workflow
"""
from typing import Optional
from src.application.agents.synthesis_agent import SynthesisAgent
from src.domain.entities.analysis import Analysis
from src.domain.value_objects.timeframe import TimeframeVO
from src.infrastructure.cache import get_cache
from src.infrastructure.database import get_db
from src.config.constants import CACHE_ANALYSIS
from src.utilities.logger import get_logger
import json
import hashlib

logger = get_logger(__name__)


class AnalysisService:
    """Service for handling analysis requests"""
    
    def __init__(self):
        self.synthesis_agent = SynthesisAgent()
        self.cache = get_cache()
        self.db = get_db()
    
    async def analyze(
        self,
        query: str,
        asset_symbol: str,
        timeframe: TimeframeVO
    ) -> Analysis:
        """
        Perform comprehensive market analysis
        
        Args:
            query: Investment query
            asset_symbol: Asset symbol to analyze
            timeframe: Analysis timeframe
            
        Returns:
            Complete analysis result
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query, asset_symbol, timeframe)
            cached = self.cache.get(cache_key, prefix=CACHE_ANALYSIS)
            
            if cached:
                logger.info(f"Cache hit for analysis: {asset_symbol}")
                return Analysis.from_dict(cached) if isinstance(cached, dict) else cached
            
            # Prepare context
            context = {
                "asset_symbol": asset_symbol,
                "timeframe": timeframe.timeframe.value,
                "days": timeframe.days
            }
            
            # Execute analysis
            logger.info(f"Executing analysis for {asset_symbol}")
            analysis = await self.synthesis_agent.analyze(query, context)
            
            # Cache result
            self.cache.set(
                cache_key,
                analysis.to_dict(),
                ttl=1800,  
                prefix=CACHE_ANALYSIS
            )
            
            # Store in database (async task)
            await self._store_analysis(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis service error: {str(e)}")
            raise
    
    async def cache_analysis(self, analysis: Analysis):
        """Cache analysis result"""
        try:
            cache_key = self._generate_cache_key(
                analysis.query,
                analysis.asset_symbol,
                None
            )
            self.cache.set(
                cache_key,
                analysis.to_dict(),
                ttl=1800,
                prefix=CACHE_ANALYSIS
            )
        except Exception as e:
            logger.error(f"Error caching analysis: {str(e)}")
    
    async def _store_analysis(self, analysis: Analysis):
        """Store analysis in database"""
        try:
            with self.db.get_session() as session:
                # Store in analyses table
                query = """
                INSERT INTO analyses (id, query, asset_symbol, outlook, confidence, 
                                    risk_level, trading_action, analysis_data, created_at)
                VALUES (:id, :query, :asset_symbol, :outlook, :confidence,
                        :risk_level, :trading_action, :analysis_data, :created_at)
                """
                
                session.execute(query, {
                    "id": self._generate_analysis_id(analysis),
                    "query": analysis.query,
                    "asset_symbol": analysis.asset_symbol,
                    "outlook": analysis.outlook.value,
                    "confidence": analysis.overall_confidence,
                    "risk_level": analysis.risk_level.value,
                    "trading_action": analysis.trading_action.value,
                    "analysis_data": json.dumps(analysis.to_dict()),
                    "created_at": analysis.created_at
                })
                
        except Exception as e:
            logger.error(f"Error storing analysis: {str(e)}")
    
    def _generate_cache_key(
        self,
        query: str,
        asset_symbol: str,
        timeframe: Optional[TimeframeVO]
    ) -> str:
        """Generate cache key for analysis"""
        key_parts = [query, asset_symbol]
        if timeframe:
            key_parts.append(timeframe.timeframe.value)
        
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _generate_analysis_id(self, analysis: Analysis) -> str:
        """Generate unique ID for analysis"""
        id_string = f"{analysis.query}:{analysis.asset_symbol}:{analysis.created_at}"
        return hashlib.sha256(id_string.encode()).hexdigest()[:16]