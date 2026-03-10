import pytest 
from app.models.job import Job
from app.jobs.types import JobType
from datetime import datetime, timedelta
from app.jobs.scheduler import enqueue_scheduled_jobs

@pytest.mark.asyncio
async def test_scheduler_enqueues_ready_job(db, test_redis):

    job = Job(
        type=JobType.export,
        payload={},
        next_run_at=datetime.now() - timedelta(seconds=1)
    )

    db.add(job)
    db.commit()

    await enqueue_scheduled_jobs(db, test_redis)

    queue_length = await test_redis.llen("queue:jobs")

    assert queue_length == 1

@pytest.mark.asyncio
async def test_scheduler_skips_future_job(db, test_redis):

    job = Job(
        type=JobType.export,
        payload={},
        next_run_at=datetime.now() + timedelta(minutes=5)
    )

    db.add(job)
    db.commit()

    await enqueue_scheduled_jobs(db, test_redis)

    queue_length = await test_redis.llen("queue:jobs")

    assert queue_length == 0

@pytest.mark.asyncio
async def test_scheduler_clears_next_run_at(db, test_redis):

    job = Job(
        type=JobType.export,
        payload={},
        next_run_at=datetime.now() - timedelta(seconds=1)
    )

    db.add(job)
    db.commit()

    await enqueue_scheduled_jobs(db, test_redis)

    db.refresh(job)

    assert job.next_run_at is None