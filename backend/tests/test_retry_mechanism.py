import pytest
from datetime import datetime, timedelta

from app.models.job import Job, JobStatus, JobType
from app.services.job_service import process_job, recover_stuck_jobs, QUEUE_PROCESSING

@pytest.mark.asyncio
async def test_retry_schedules_backoff(db, test_redis, monkeypatch):

    job = Job(
        type=JobType.export,
        status=JobStatus.pending,
        attempts=0,
        max_attempts=3,
        payload={"export_type": "records"},
    )
    db.add(job)
    db.commit()

    def fake_generate(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "app.jobs.executors.export.EXPORT_GENERATORS",
        {"records": fake_generate},
    )

    await process_job(db=db, job_id=job.id, redis=test_redis)

    db.refresh(job)

    assert job.status == JobStatus.pending
    assert job.attempts == 1
    assert job.next_run_at is not None
    assert job.last_error == "boom"

@pytest.mark.asyncio
async def test_job_fails_after_max_attempts(db, test_redis, monkeypatch):

    job = Job(
        type=JobType.export,
        status=JobStatus.pending,
        attempts=2,
        max_attempts=3,
        payload={"export_type": "records"},
    )
    db.add(job)
    db.commit()

    def fake_generate(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "app.jobs.executors.export.EXPORT_GENERATORS",
        {"records": fake_generate},
    )

    await process_job(db=db, job_id=job.id, redis=test_redis)

    db.refresh(job)

    assert job.status == JobStatus.failed
    assert job.attempts == 3

@pytest.mark.asyncio
async def test_no_double_counts_on_crash(db, test_redis):

    job = Job(
        type=JobType.export,
        status=JobStatus.processing,
        attempts=1,
        max_attempts=3,
        processing_started_at=datetime.now() - timedelta(seconds=600),
    )

    db.add(job)
    db.commit()

    await test_redis.lpush(QUEUE_PROCESSING, job.id)

    await recover_stuck_jobs(db, test_redis)

    assert job.attempts == 1
    assert job.status == JobStatus.pending
    assert job.next_run_at is not None

@pytest.mark.asyncio
async def test_no_retries_on_recovery_after_max_attempts(db, test_redis):

    job = Job(
        type=JobType.export,
        status=JobStatus.processing,
        attempts=3,
        max_attempts=3,
        processing_started_at=datetime.now() - timedelta(seconds=600),
    )

    db.add(job)
    db.commit()

    await test_redis.lpush(QUEUE_PROCESSING, job.id)

    await recover_stuck_jobs(db, test_redis)

    processing_queue = await test_redis.lrange(QUEUE_PROCESSING, 0, -1)

    assert job.status == JobStatus.failed
    assert job.id not in processing_queue
