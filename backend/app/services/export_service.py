from app.models.export import ExportJob, ExportStatus
from app.utils.csv_generator import generate_csv
from app.utils.job_utils import schedule_retry_or_fail
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from redis.asyncio import Redis
from datetime import datetime, timedelta

JOB_TIMEOUT_SECONDS = 300
QUEUE_PROCESSING = "queue:processing"
QUEUE_PENDING = "queue:exports"

async def process_job(db: Session, job_id: int):
    
    job = db.get(ExportJob, job_id)

    if not job:
        return  # orphaned job

    if job.status != ExportStatus.pending:
        return  # idempotency guard

    job.status = ExportStatus.processing
    job.attempts += 1
    job.processing_started_at = datetime.now()
    db.flush()

    try:
        file_path = generate_csv(db, job_id)
        job.status = ExportStatus.completed
        job.file_path = file_path
        job.next_run_at = None
        job.last_error = None 
    except Exception as e:
        job.last_error = str(e)
        schedule_retry_or_fail(job)
        
    db.commit()

async def recover_stuck_jobs(db, redis: Redis):
    processing_jobs = await redis.lrange("queue:processing", 0, -1) # type: ignore

    for job_id in processing_jobs:
        job = db.get(ExportJob, int(job_id))
        if not job:
            continue

        # Already completed? Clean Redis
        if job.status == ExportStatus.completed:
            await redis.lrem("queue:processing", 0, job_id) # type: ignore
            continue

        # Timed out?
        if (
            job.status == ExportStatus.processing
            and job.processing_started_at
            and job.processing_started_at
            < datetime.now() - timedelta(seconds=JOB_TIMEOUT_SECONDS)
        ):
            print(f"Requeuing stuck job {job_id}")

            await redis.lrem(QUEUE_PROCESSING, 0, job_id) # type: ignore

            # Simulate failed execution
            job.last_error = "Job timed out"

            schedule_retry_or_fail(job)

            if job.status == ExportStatus.pending:
                await redis.lpush(QUEUE_PENDING, job_id) # type: ignore

            db.commit()