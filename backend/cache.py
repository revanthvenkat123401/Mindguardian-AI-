"""Caching utilities using Redis"""
import json
import logging
from typing import Any, Optional
import redis.asyncio as redis
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheService:
    """Redis caching service"""
    
    _redis: Optional[redis.Redis] = None
    
    @classmethod
    async def init(cls):
        """Initialize Redis connection"""
        try:
            cls._redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await cls._redis.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
    
    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls._redis:
            await cls._redis.close()
            logger.info("Redis connection closed")
    
    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not cls._redis:
            return None
        
        try:
            value = await cls._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    @classmethod
    async def set(
        cls,
        key: str,
        value: Any,
        expire: int = None
    ) -> bool:
        """Set value in cache"""
        if not cls._redis:
            return False
        
        try:
            expire = expire or settings.REDIS_CACHE_EXPIRE
            await cls._redis.setex(
                key,
                expire,
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    @classmethod
    async def delete(cls, key: str) -> bool:
        """Delete value from cache"""
        if not cls._redis:
            return False
        
        try:
            await cls._redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    @classmethod
    async def clear_pattern(cls, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not cls._redis:
            return 0
        
        try:
            keys = await cls._redis.keys(pattern)
            if keys:
                return await cls._redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
