import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Optional

from redis.asyncio import Redis
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.core.logging import get_logger
from app.jobs.registry import JOB_REGISTRY
from app.models.user import User
from app.schemas.user import UserRole
from app.models.job import Job, JobStatus
from app.jobs.types import JobType
from app.utils.job_utils import schedule_retry_or_fail

JOB_TIMEOUT_SECONDS = 300
QUEUE_PROCESSING = "queue:processing"
QUEUE_PENDING = "queue:jobs"
logger = get_logger(__name__)

async def get_user_jobs(
    db: Session,
    current_user: User,
    status: Optional[JobStatus],
    job_type: Optional[JobType],
    limit: int,
    offset: int,
    sort_order: str = "desc",
):
    # 🧠 Build filters explicitly
    if current_user.role == UserRole.ADMIN:
        filters = []
    else:
        filters = [Job.user_id == current_user.id]

    if status:
        filters.append(Job.status == status)

    if job_type:
        filters.append(Job.type == job_type)

    # 📊 Total count (filtered)
    total = db.scalar(
        select(func.count()).select_from(Job).where(*filters)
    ) or 0

    # 🔽 Sorting
    order_expr = (
        Job.created_at.desc()
        if sort_order == "desc"
        else Job.created_at.asc()
    )

    # 📄 Main query
    stmt = (
        select(Job)
        .where(*filters)
        .order_by(order_expr)
        .limit(limit)
        .offset(offset)
    )

    items = db.execute(stmt).scalars().all()

    return {
        "items": items,
        "total": total,
    }

async def process_job(*, db: Session, job_id: str | uuid.UUID, redis: Redis):
    job_id = str(job_id)
    job = db.get(Job, job_id)

    if not job:
        logger.warning("Skipping orphaned job", extra={"job_id": job_id})
        return  # orphaned job

    if job.status != JobStatus.pending:
        logger.warning(
            "Skipping job with unexpected status",
            extra={
                "job_id": job_id,
                "job_status": job.status.value,
            },
        )
        return  # idempotency guard

    job.status = JobStatus.processing
    job.attempts += 1
    job.processing_started_at = datetime.now()
    db.flush()

    logger.info(
        "Job processing started",
        extra={
            "job_id": job_id,
            "job_type": job.type.value,
            "attempt": job.attempts,
            "max_attempts": job.max_attempts,
            "request_id": job.request_id
        },
    )

    executor = JOB_REGISTRY[job.type]

    try:
        result = executor(db, redis, job)
        if asyncio.iscoroutine(result):
            await result

        job.status = JobStatus.completed
        job.next_run_at = None
        job.last_error = None
        logger.info(
            "Job processing completed",
            extra={
                "job_id": job_id,
                "job_type": job.type.value,
                "attempt": job.attempts,
                "request_id": job.request_id
            },
        )
    except Exception as e:
        logger.error(
            "Job processing failed",
            extra={
                "job_id": job_id,
                "job_type": job.type.value,
                "attempt": job.attempts,
                "request_id": job.request_id
            },
            exc_info=True
        )
        job.last_error = str(e)
        schedule_retry_or_fail(job)
        logger.warning(
            "Job retry state updated",
            extra={
                "job_id": job_id,
                "job_type": job.type.value,
                "job_status": job.status.value,
                "next_run_at": job.next_run_at,
                "attempt": job.attempts,
                "max_attempts": job.max_attempts,
                "request_id": job.request_id
            },
        )

    db.commit()

async def recover_stuck_jobs(db, redis: Redis):
    processing_jobs = await redis.lrange(QUEUE_PROCESSING, 0, -1) # type: ignore

    for job_id in processing_jobs:
        if isinstance(job_id, bytes):
            job_id = job_id.decode("utf-8")

        job = db.get(Job, job_id)
        if not job:
            logger.warning("Found missing processing job during recovery", extra={"job_id": job_id})
            continue

        # Already completed? Clean Redis
        if job.status == JobStatus.completed:
            logger.info(
                "Removed completed job from processing queue",
                extra={"job_id": job_id, "job_type": job.type.value, "request_id": job.request_id},
            )
            await redis.lrem(QUEUE_PROCESSING, 0, job_id) # type: ignore
            continue

        # Timed out?
        if (
            job.status == JobStatus.processing
            and job.processing_started_at
            and job.processing_started_at
            < datetime.now() - timedelta(seconds=JOB_TIMEOUT_SECONDS)
        ):
            logger.warning(
                "Recovering stuck job",
                extra={
                    "job_id": job_id,
                    "job_type": job.type.value,
                    "processing_started_at": job.processing_started_at,
                    "request_id": job.request_id
                },
            )

            await redis.lrem(QUEUE_PROCESSING, 0, job_id) # type: ignore

            # Simulate failed execution
            job.last_error = "Job timed out"

            schedule_retry_or_fail(job)

            if job.status == JobStatus.pending:
                await redis.lpush(QUEUE_PENDING, job_id) # type: ignore
                logger.info(
                    "Requeued recovered job",
                    extra={
                        "job_id": job_id,
                        "job_type": job.type.value,
                        "next_run_at": job.next_run_at,
                        "request_id": job.request_id
                    },
                )
            else:
                logger.warning(
                    "Recovered job exhausted retries",
                    extra={
                        "job_id": job_id,
                        "job_type": job.type.value,
                        "job_status": job.status.value,
                        "request_id": job.request_id
                    },
                )

            db.commit()

            db.commit()
