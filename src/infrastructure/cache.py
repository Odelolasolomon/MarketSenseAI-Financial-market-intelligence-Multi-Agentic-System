"""
Cache Management with Redis
"""
import json
import pickle
from typing import Optional, Any
import redis
from datetime import timedelta
from src.config.settings import get_settings
from src.config.constants import CACHE_PREFIX
from src.utilities.logger import get_logger
from src.error_trace.exceptions import CacheError

logger = get_logger(__name__)
settings = get_settings()


class CacheManager:
    """Manages Redis cache operations"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_url
        try:
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info(f"Redis cache initialized: {self.redis_url.split('@')[-1]}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise CacheError(f"Redis connection failed: {str(e)}")
    
    def _make_key(self, key: str, prefix: str = CACHE_PREFIX) -> str:
        """Create prefixed cache key"""
        return f"{prefix}{key}"
    
    def get(self, key: str, prefix: str = CACHE_PREFIX) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            prefix: Key prefix
            
        Returns:
            Cached value or None
        """
        try:
            full_key = self._make_key(key, prefix)
            data = self.client.get(full_key)
            
            if data is None:
                return None
            
            # Try to deserialize as pickle first, then JSON
            try:
                return pickle.loads(data)
            except:
                try:
                    return json.loads(data.decode('utf-8'))
                except:
                    return data.decode('utf-8')
                    
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        prefix: str = CACHE_PREFIX
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            prefix: Key prefix
            
        Returns:
            Success status
        """
        try:
            full_key = self._make_key(key, prefix)
            ttl = ttl or settings.cache_ttl
            
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value).encode('utf-8')
            elif isinstance(value, str):
                serialized = value.encode('utf-8')
            else:
                serialized = pickle.dumps(value)
            
            if ttl:
                self.client.setex(full_key, ttl, serialized)
            else:
                self.client.set(full_key, serialized)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str, prefix: str = CACHE_PREFIX) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
            prefix: Key prefix
            
        Returns:
            Success status
        """
        try:
            full_key = self._make_key(key, prefix)
            self.client.delete(full_key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    def exists(self, key: str, prefix: str = CACHE_PREFIX) -> bool:
        """Check if key exists in cache"""
        try:
            full_key = self._make_key(key, prefix)
            return bool(self.client.exists(full_key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {str(e)}")
            return False
    
    def clear_prefix(self, prefix: str = CACHE_PREFIX) -> int:
        """
        Clear all keys with given prefix
        
        Returns:
            Number of keys deleted
        """
        try:
            pattern = f"{prefix}*"
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear error for prefix {prefix}: {str(e)}")
            return 0
    
    def get_ttl(self, key: str, prefix: str = CACHE_PREFIX) -> int:
        """Get TTL for key in seconds"""
        try:
            full_key = self._make_key(key, prefix)
            return self.client.ttl(full_key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {str(e)}")
            return -1
    
    def health_check(self) -> bool:
        """Check Redis health"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return False


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Get cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
