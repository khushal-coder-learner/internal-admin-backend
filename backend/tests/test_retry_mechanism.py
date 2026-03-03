import pytest
from datetime import datetime, timedelta
from app.models.export import ExportJob, ExportStatus
from app.services.export_service import process_job, recover_stuck_jobs

@pytest.mark.asyncio
async def test_retry_schedules_backoff(db, monkeypatch):

    job = ExportJob(
        status=ExportStatus.pending,
        attempts=0,
        max_attempts=3
    )
    db.add(job)
    db.commit()

    def fake_generate(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "app.services.export_service.generate_csv",
        fake_generate
    )

    await process_job(db, job.id)

    db.refresh(job)

    assert job.status == ExportStatus.pending
    assert job.attempts == 1
    assert job.next_run_at is not None
    assert job.last_error == "boom"

@pytest.mark.asyncio
async def test_job_fails_after_max_attempts(db, monkeypatch):

    job = ExportJob(
        status=ExportStatus.pending,
        attempts=2,
        max_attempts=3
    )
    db.add(job)
    db.commit()

    def fake_generate(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr('app.services.export_service.generate_csv', fake_generate)

    await process_job(db, job.id)

    db.refresh(job)

    assert job.status == ExportStatus.failed
    assert job.attempts == 3

@pytest.mark.asyncio
async def test_no_double_counts_on_crash(db, test_redis):

    job = ExportJob(
        status=ExportStatus.processing,
        attempts=1,
        max_attempts=3,
        processing_started_at=datetime.now() - timedelta(seconds=600)
    )

    db.add(job)
    db.commit()

    await test_redis.lpush('queue:processing', job.id)

    await recover_stuck_jobs(db, test_redis)

    assert job.attempts == 1
    assert job.status == ExportStatus.pending
    assert job.next_run_at is not None

@pytest.mark.asyncio
async def test_no_retries_on_recovery_after_max_attempts(db, test_redis):

    job = ExportJob(
        status=ExportStatus.processing,
        attempts=3,
        max_attempts=3,
        processing_started_at=datetime.now() - timedelta(seconds=600)
    )

    db.add(job)
    db.commit()

    await test_redis.lpush('queue:processing', job.id)

    await recover_stuck_jobs(db, test_redis)

    processing_queue = await test_redis.lrange('queue:processing', 0, -1)

    assert job.status == ExportStatus.failed
    assert job.id not in processing_queue
