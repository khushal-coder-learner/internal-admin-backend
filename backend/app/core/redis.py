from redis.asyncio import Redis
from app.core.config import settings

_redis: Redis | None = None


async def init_redis() -> None:
    global _redis
    _redis = Redis.from_url(
        settings.test_redis_url,
        decode_responses=True,
    )


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


def get_redis_client() -> Redis:
    if _redis is None:
        raise RuntimeError("Redis client not initialized")
    return _redis
