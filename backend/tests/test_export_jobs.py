import pytest
from datetime import datetime, timedelta
from pathlib import Path

from app.models.job import Job, JobStatus, JobType
from app.services.job_service import (
    process_job,
    recover_stuck_jobs,
    QUEUE_PENDING,
    QUEUE_PROCESSING,
)

@pytest.mark.asyncio
async def test_export_job_success(db, test_redis):
    job = Job(type=JobType.export, status=JobStatus.pending)
    db.add(job)
    db.commit()
    db.refresh(job)

    await test_redis.rpush(QUEUE_PENDING, job.id)

    # Simulate worker pop
    job_id = await test_redis.brpoplpush(
        QUEUE_PENDING,
        QUEUE_PROCESSING,
    )

    await process_job(db=db, job_id=int(job_id), redis=test_redis)

    db.refresh(job)

    assert job.status == JobStatus.completed
    assert isinstance(job.payload, dict)
    assert "file_path" in job.payload
    assert Path(job.payload["file_path"]).exists()

@pytest.mark.asyncio
async def test_process_job_idempotent(db, test_redis):
    job = Job(type=JobType.export, status=JobStatus.completed)
    db.add(job)
    db.commit()
    db.refresh(job)

    await process_job(db=db, job_id=job.id, redis=test_redis)

    # Should not change state
    db.refresh(job)
    assert job.status == JobStatus.completed


@pytest.mark.asyncio
async def test_recover_stuck_job(db, test_redis):
    job = Job(
        type=JobType.export,
        status=JobStatus.processing,
        processing_started_at=datetime.now() - timedelta(seconds=1000),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    await test_redis.rpush(QUEUE_PROCESSING, job.id)

    await recover_stuck_jobs(db, test_redis)

    db.refresh(job)

    assert job.status == JobStatus.pending

    queue = await test_redis.lrange(QUEUE_PENDING, 0, -1)
    assert str(job.id) in queue

@pytest.mark.asyncio
async def test_completed_job_removed_from_processing(db, test_redis):
    job = Job(type=JobType.export, status=JobStatus.completed)
    db.add(job)
    db.commit()
    db.refresh(job)

    await test_redis.rpush(QUEUE_PROCESSING, job.id)

    await recover_stuck_jobs(db, test_redis)

    queue = await test_redis.lrange(QUEUE_PROCESSING, 0, -1)
    assert str(job.id) not in queue