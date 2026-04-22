import asyncio
import time

from redis.asyncio import Redis

from app.core.logging import configure_logging, get_logger
from app.core.config import settings
from app.db.session import SessionLocal
from app.jobs.executors.cleanup_exports import execute_cleanup_exports
from app.jobs.scheduler import enqueue_scheduled_jobs
from app.services.job_service import process_job, recover_stuck_jobs

QUEUE_NAME = "queue:jobs"
QUEUE_PROCESSING = "queue:processing"

CLEANUP_INTERVAL = 60*60*24
QUEUE_BLOCK_TIMEOUT = 5

configure_logging(service="worker")
logger = get_logger(__name__)


async def worker():
    logger.info("Starting worker process")
    redis = Redis.from_url(settings.redis_url)
    with SessionLocal() as db:
        await recover_stuck_jobs(db, redis)

    last_cleanup = 0.0

    while True:
        now = time.time()

        with SessionLocal() as db:
            await enqueue_scheduled_jobs(db, redis)

            if now - last_cleanup >= CLEANUP_INTERVAL:
                await execute_cleanup_exports(db=db, redis=redis, job=None)
                last_cleanup = now

        job_id = await redis.brpoplpush(
            QUEUE_NAME,
            QUEUE_PROCESSING,
            timeout=QUEUE_BLOCK_TIMEOUT,
        ) # type: ignore

        if job_id is None:
            continue

        if isinstance(job_id, bytes):
            job_id = job_id.decode("utf-8")

        lock_key = f"lock:job:{job_id}"

        acquired = await redis.set(
            lock_key,
            "1",
            nx=True,
            ex=300
        )

        if not acquired:
            logger.warning("Skipped locked job", extra={"job_id": job_id})
            continue

        try:
            logger.info("Picked up job", extra={"job_id": job_id})
            with SessionLocal() as db:
                await process_job(db=db, job_id=job_id, redis=redis)

            await redis.lrem(QUEUE_PROCESSING, 0, job_id) # type: ignore

        finally:
            await redis.delete(lock_key)

if __name__ == "__main__":
    asyncio.run(worker())
