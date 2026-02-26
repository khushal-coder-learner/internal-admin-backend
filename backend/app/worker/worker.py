import asyncio
from typing import Tuple, cast
from redis.asyncio import Redis
from app.db.session import SessionLocal
from app.services.export_service import process_job, recover_stuck_jobs
from app.core.config import settings

QUEUE_NAME = "queue:exports"

async def worker():
    redis = Redis.from_url(settings.redis_url)
    with SessionLocal() as db:
        await recover_stuck_jobs(db, redis)

    while True:
        job_id = await redis.brpoplpush(
            "queue:exports",
            "queue:processing"
        ) # type: ignore

        lock_key = f"lock:job:{job_id}"

        acquired = await redis.set(
            lock_key,
            "1",
            nx=True,
            ex=300
        )

        if not acquired:
            continue

        try:
            with SessionLocal() as db:
                await process_job(db, int(job_id)) # type: ignore
            await redis.lrem("queue:processing", 0, job_id) # type: ignore
        finally:
            await redis.delete(lock_key)

if __name__ == "__main__":
    asyncio.run(worker())