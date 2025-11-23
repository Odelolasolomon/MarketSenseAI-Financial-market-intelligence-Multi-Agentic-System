"""
Binance API Client
"""
import hashlib
import hmac
import time
from typing import Dict, Any, Optional, List
import aiohttp
from src.config.settings import get_settings
from src.utilities.logger import get_logger
from src.error_trace.exceptions import ExternalAPIError

logger = get_logger(__name__)
settings = get_settings()


class BinanceClient:
    """Client for Binance API"""
    
    BASE_URL = "https://api.binance.com"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None
    ):
        self.api_key = api_key or settings.binance_api_key
        self.api_secret = api_secret or settings.binance_api_secret
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate HMAC SHA256 signature"""
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        signed: bool = False
    ) -> Dict[str, Any]:
        """Make API request"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {"X-MBX-APIKEY": self.api_key} if self.api_key else {}
        params = params or {}
        
        # Add signature for signed endpoints
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        try:
            async with self.session.request(
                method,
                url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                data = await response.json()
                
                if response.status != 200:
                    raise ExternalAPIError(
                        message=f"Binance API error: {data.get('msg', 'Unknown error')}",
                        api_name="binance",
                        status_code=response.status,
                        response_data=data
                    )
                
                return data
                
        except aiohttp.ClientError as e:
            logger.error(f"Binance API request error: {str(e)}")
            raise ExternalAPIError(
                message=f"Binance connection error: {str(e)}",
                api_name="binance"
            )
    
    async def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get latest price for a symbol
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            
        Returns:
            Price data
        """
        endpoint = "/api/v3/ticker/price"
        params = {"symbol": symbol.upper().replace("/", "")}
        return await self._request("GET", endpoint, params)
    
    async def get_24h_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get 24-hour price change statistics
        
        Args:
            symbol: Trading pair
            
        Returns:
            24h statistics
        """
        endpoint = "/api/v3/ticker/24hr"
        params = {"symbol": symbol.upper().replace("/", "")}
        return await self._request("GET", endpoint, params)
    
    async def get_klines(
        self,
        symbol: str,
        interval: str = "1d",
        limit: int = 100
    ) -> List[List]:
        """
        Get candlestick data
        
        Args:
            symbol: Trading pair
            interval: Timeframe (1m, 5m, 1h, 1d, etc.)
            limit: Number of candles
            
        Returns:
            List of OHLCV data
        """
        endpoint = "/api/v3/klines"
        params = {
            "symbol": symbol.upper().replace("/", ""),
            "interval": interval,
            "limit": limit
        }
        return await self._request("GET", endpoint, params)
    
    async def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get exchange trading rules and symbol information"""
        endpoint = "/api/v3/exchangeInfo"
        params = {"symbol": symbol.upper().replace("/", "")} if symbol else {}
        return await self._request("GET", endpoint, params)
    
    async def get_account(self) -> Dict[str, Any]:
        """Get account information (requires API key)"""
        endpoint = "/api/v3/account"
        return await self._request("GET", endpoint, signed=True)
