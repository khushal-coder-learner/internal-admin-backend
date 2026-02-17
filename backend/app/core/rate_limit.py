from fastapi import HTTPException, status
from redis.asyncio import Redis


async def enforce_rate_limit(
    redis: Redis,
    *,
    key: str,
    limit: int,
    window_seconds: int,
):
    current = await redis.incr(key)

    if current == 1:
        # First request → set expiry
        await redis.expire(key, window_seconds)

    if current > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again later.",
        )
