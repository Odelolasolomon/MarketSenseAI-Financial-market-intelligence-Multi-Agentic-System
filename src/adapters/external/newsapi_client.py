"""
NewsAPI Client
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp
from src.config.settings import get_settings
from src.utilities.logger import get_logger
from src.error_trace.exceptions import ExternalAPIError

logger = get_logger(__name__)
settings = get_settings()


class NewsAPIClient:
    """Client for NewsAPI"""
    
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.newsapi_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make API request"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        params["apiKey"] = self.api_key
        
        try:
            async with self.session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                data = await response.json()
                
                if response.status != 200:
                    raise ExternalAPIError(
                        message=f"NewsAPI error: {data.get('message', 'Unknown error')}",
                        api_name="newsapi",
                        status_code=response.status,
                        response_data=data
                    )
                
                return data
                
        except aiohttp.ClientError as e:
            logger.error(f"NewsAPI request error: {str(e)}")
            raise ExternalAPIError(
                message=f"NewsAPI connection error: {str(e)}",
                api_name="newsapi"
            )
    
    async def get_everything(
        self,
        query: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Search for articles
        
        Args:
            query: Search query
            from_date: Start date
            to_date: End date
            language: Language code
            sort_by: Sort method (publishedAt, relevancy, popularity)
            page_size: Number of results
            
        Returns:
            Articles data
        """
        endpoint = "/everything"
        
        # Default to last 7 days if no date specified
        if not from_date:
            from_date = datetime.now() - timedelta(days=7)
        
        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": min(page_size, 100)  
        }
        
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        
        return await self._request(endpoint, params)
    
    async def get_top_headlines(
        self,
        category: Optional[str] = None,
        country: str = "us",
        query: Optional[str] = None,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Get top headlines
        
        Args:
            category: Category (business, technology, etc.)
            country: Country code
            query: Search query
            page_size: Number of results
            
        Returns:
            Top headlines data
        """
        endpoint = "/top-headlines"
        
        params = {
            "country": country,
            "pageSize": min(page_size, 100)
        }
        
        if category:
            params["category"] = category
        if query:
            params["q"] = query
        
        return await self._request(endpoint, params)
    
    async def search_crypto_news(
        self,
        coin: str,
        days: int = 7,
        page_size: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for cryptocurrency news
        
        Args:
            coin: Cryptocurrency name or symbol
            days: Number of days back
            page_size: Number of results
            
        Returns:
            List of articles
        """
        from_date = datetime.now() - timedelta(days=days)
        
        query = f"{coin} cryptocurrency OR {coin} crypto"
        
        result = await self.get_everything(
            query=query,
            from_date=from_date,
            sort_by="relevancy",
            page_size=page_size
        )
        
        return result.get("articles", [])
    
    async def search_forex_news(
        self,
        currency_pair: str,
        days: int = 7,
        page_size: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for forex news
        
        Args:
            currency_pair: Currency pair (e.g., EUR/USD)
            days: Number of days back
            page_size: Number of results
            
        Returns:
            List of articles
        """
        from_date = datetime.now() - timedelta(days=days)
        
        query = f"{currency_pair} forex OR currency exchange"
        
        result = await self.get_everything(
            query=query,
            from_date=from_date,
            sort_by="relevancy",
            page_size=page_size
        )
        
        return result.get("articles", [])

