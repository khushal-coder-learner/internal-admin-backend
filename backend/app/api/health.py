from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from redis.exceptions import ConnectionError
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.dependencies import get_redis, get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/redis")
async def redis_health(redis: Redis = Depends(get_redis)):
    try:
        pong = await redis.ping()  # type: ignore
        return {"redis": pong}
    except ConnectionError:
        return {"redis": False}


@router.get("/db")
def db_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"db": True}
    except Exception:
        return {"db": False}
