import pytest
from backend.app.models.job import ExportJob, ExportStatus
from backend.app.services.job_service import process_job, recover_stuck_jobs
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_export_job_success(db, test_redis):
    # Create job
    job = ExportJob(status=ExportStatus.pending)
    db.add(job)
    db.commit()
    db.refresh(job)

    await test_redis.rpush("queue:exports", job.id)

    # Simulate worker pop
    job_id = await test_redis.brpoplpush(
        "queue:exports",
        "queue:processing"
    )

    await process_job(db, int(job_id))

    db.refresh(job)

    assert job.status == ExportStatus.completed
    assert job.file_path is not None

@pytest.mark.asyncio
async def test_process_job_idempotent(db):
    job = ExportJob(status=ExportStatus.completed)
    db.add(job)
    db.commit()
    db.refresh(job)

    await process_job(db, job.id)

    # Should not change state
    db.refresh(job)
    assert job.status == ExportStatus.completed


@pytest.mark.asyncio
async def test_recover_stuck_job(db, test_redis):
    job = ExportJob(
        status=ExportStatus.processing,
        processing_started_at=datetime.now() - timedelta(seconds=1000)
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    await test_redis.rpush("queue:processing", job.id)

    await recover_stuck_jobs(db, test_redis)

    db.refresh(job)

    assert job.status == ExportStatus.pending

    queue = await test_redis.lrange("queue:exports", 0, -1)
    assert str(job.id) in queue

@pytest.mark.asyncio
async def test_completed_job_removed_from_processing(db, test_redis):
    job = ExportJob(status=ExportStatus.completed)
    db.add(job)
    db.commit()
    db.refresh(job)

    await test_redis.rpush("queue:processing", job.id)

    await recover_stuck_jobs(db, test_redis)

    queue = await test_redis.lrange("queue:processing", 0, -1)
    assert str(job.id) not in queue