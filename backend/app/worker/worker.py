import asyncio
from typing import Tuple, cast
from redis.asyncio import Redis
from app.db.session import SessionLocal
from app.services.job_service import process_job, recover_stuck_jobs
from app.core.config import settings
from app.jobs.scheduler import enqueue_scheduled_jobs

QUEUE_NAME = "queue:jobs"
QUEUE_PROCESSING = "queue:processing"

async def worker():
    redis = Redis.from_url(settings.redis_url)
    with SessionLocal() as db:
        await recover_stuck_jobs(db, redis)

    while True:
        await enqueue_scheduled_jobs(db, redis)

        job_id = await redis.brpoplpush(
            QUEUE_NAME,
            QUEUE_PROCESSING
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
                await process_job(db=db, job_id=int(job_id), redis=redis) # type: ignore
            await redis.lrem(QUEUE_PROCESSING, 0, job_id) # type: ignore
        finally:
            await redis.delete(lock_key)

if __name__ == "__main__":
    asyncio.run(worker())