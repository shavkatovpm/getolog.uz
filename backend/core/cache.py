import json
import logging

from redis.asyncio import Redis

logger = logging.getLogger(__name__)

_redis: Redis | None = None


def init_cache(redis: Redis):
    global _redis
    _redis = redis


async def cache_get(key: str) -> dict | None:
    if not _redis:
        return None
    try:
        data = await _redis.get(f"cache:{key}")
        if data:
            return json.loads(data)
    except Exception as e:
        logger.debug(f"Cache get error: {e}")
    return None


async def cache_set(key: str, value: dict, ttl: int = 60):
    if not _redis:
        return
    try:
        await _redis.setex(f"cache:{key}", ttl, json.dumps(value))
    except Exception as e:
        logger.debug(f"Cache set error: {e}")


async def cache_delete(pattern: str):
    if not _redis:
        return
    try:
        keys = []
        async for key in _redis.scan_iter(f"cache:{pattern}*"):
            keys.append(key)
        if keys:
            await _redis.delete(*keys)
    except Exception as e:
        logger.debug(f"Cache delete error: {e}")
