"""
CoinGecko API Client
"""
from typing import Dict, Any, Optional, List
import aiohttp
from src.config.settings import get_settings
from src.utilities.logger import get_logger
from src.error_trace.exceptions import ExternalAPIError

logger = get_logger(__name__)
settings = get_settings()


class CoinGeckoClient:
    """Client for CoinGecko API"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.coingecko_api_key
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
    ) -> Any:
        """Make API request"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {}
        
        if self.api_key:
            headers["x-cg-pro-api-key"] = self.api_key
        
        try:
            async with self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 429:
                    raise ExternalAPIError(
                        message="CoinGecko rate limit exceeded",
                        api_name="coingecko",
                        status_code=429
                    )
                
                if response.status != 200:
                    text = await response.text()
                    raise ExternalAPIError(
                        message=f"CoinGecko API error: {text}",
                        api_name="coingecko",
                        status_code=response.status
                    )
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"CoinGecko API request error: {str(e)}")
            raise ExternalAPIError(
                message=f"CoinGecko connection error: {str(e)}",
                api_name="coingecko"
            )
    
    async def get_coin_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get comprehensive data for a coin
        
        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum')
            
        Returns:
            Coin data including price, market cap, volume, etc.
        """
        endpoint = f"/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "true",
            "developer_data": "false"
        }
        return await self._request(endpoint, params)
    
    async def get_simple_price(
        self,
        coin_ids: List[str],
        vs_currencies: List[str] = ["usd"],
        include_24h_change: bool = True,
        include_market_cap: bool = True,
        include_24h_volume: bool = True
    ) -> Dict[str, Any]:
        """
        Get simple price data for multiple coins
        
        Args:
            coin_ids: List of coin IDs
            vs_currencies: List of target currencies
            include_24h_change: Include 24h price change
            include_market_cap: Include market cap
            include_24h_volume: Include 24h volume
            
        Returns:
            Price data for requested coins
        """
        endpoint = "/simple/price"
        params = {
            "ids": ",".join(coin_ids),
            "vs_currencies": ",".join(vs_currencies),
            "include_24hr_change": str(include_24h_change).lower(),
            "include_market_cap": str(include_market_cap).lower(),
            "include_24hr_vol": str(include_24h_volume).lower()
        }
        return await self._request(endpoint, params)
    
    async def get_market_chart(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get historical market data
        
        Args:
            coin_id: CoinGecko coin ID
            vs_currency: Target currency
            days: Number of days of data
            
        Returns:
            Historical price, market cap, and volume data
        """
        endpoint = f"/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": days
        }
        return await self._request(endpoint, params)
    
    async def get_trending(self) -> Dict[str, Any]:
        """Get trending coins"""
        endpoint = "/search/trending"
        return await self._request(endpoint)
    
    async def get_global_data(self) -> Dict[str, Any]:
        """Get global cryptocurrency data"""
        endpoint = "/global"
        return await self._request(endpoint)
    
    def normalize_symbol(self, symbol: str) -> str:
        """
        Convert symbol to CoinGecko coin ID
        
        Args:
            symbol: Crypto symbol (e.g., BTC, ETH)
            
        Returns:
            CoinGecko coin ID
        """
        mapping = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "BNB": "binancecoin",
            "ADA": "cardano",
            "SOL": "solana",
            "XRP": "ripple",
            "DOT": "polkadot",
            "DOGE": "dogecoin",
            "AVAX": "avalanche-2",
            "MATIC": "matic-network",
            "LINK": "chainlink",
            "UNI": "uniswap"
        }
        return mapping.get(symbol.upper(), symbol.lower())
