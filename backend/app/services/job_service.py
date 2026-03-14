import asyncio

from app.models.job import Job, JobStatus
from app.utils.job_utils import schedule_retry_or_fail
from app.jobs.registry import JOB_REGISTRY
from sqlalchemy.orm import Session
from redis.asyncio import Redis
from datetime import datetime, timedelta

JOB_TIMEOUT_SECONDS = 300
QUEUE_PROCESSING = "queue:processing"
QUEUE_PENDING = "queue:jobs"

async def process_job(*, db: Session, job_id: int, redis: Redis):
    
    job = db.get(Job, job_id)

    if not job:
        return  # orphaned job

    if job.status != JobStatus.pending:
        return  # idempotency guard

    job.status = JobStatus.processing
    job.attempts += 1
    job.processing_started_at = datetime.now()
    db.flush()

    executor = JOB_REGISTRY[job.type]

    try:
        result = executor(db, redis, job)
        if asyncio.iscoroutine(result):
            await result

        job.status = JobStatus.completed
        job.next_run_at = None
        job.last_error = None
    except Exception as e:
        job.last_error = str(e)
        schedule_retry_or_fail(job)

    db.commit()

async def recover_stuck_jobs(db, redis: Redis):
    processing_jobs = await redis.lrange(QUEUE_PROCESSING, 0, -1) # type: ignore

    for job_id in processing_jobs:
        job = db.get(Job, int(job_id))
        if not job:
            continue

        # Already completed? Clean Redis
        if job.status == JobStatus.completed:
            await redis.lrem(QUEUE_PROCESSING, 0, job_id) # type: ignore
            continue

        # Timed out?
        if (
            job.status == JobStatus.processing
            and job.processing_started_at
            and job.processing_started_at
            < datetime.now() - timedelta(seconds=JOB_TIMEOUT_SECONDS)
        ):
            print(f"Requeuing stuck job {job_id}")

            await redis.lrem(QUEUE_PROCESSING, 0, job_id) # type: ignore

            # Simulate failed execution
            job.last_error = "Job timed out"

            schedule_retry_or_fail(job)

            if job.status == JobStatus.pending:
                await redis.lpush(QUEUE_PENDING, job_id) # type: ignore

            db.commit()