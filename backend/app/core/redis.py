"""Redis configuration for caching and pub/sub"""
import json
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings

redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis connection"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    r = await get_redis()
    value = await r.get(key)
    if value:
        return json.loads(value)
    return None


async def cache_set(key: str, value: Any, expire: int = 300) -> None:
    """Set value in cache with expiration"""
    r = await get_redis()
    await r.set(key, json.dumps(value), ex=expire)


async def publish_event(channel: str, data: dict) -> None:
    """Publish event to Redis pub/sub"""
    r = await get_redis()
    await r.publish(channel, json.dumps(data))
