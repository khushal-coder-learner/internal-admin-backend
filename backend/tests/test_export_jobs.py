import pytest
from app.models.export import ExportJob, ExportStatus
from app.services.export_service import process_job, recover_stuck_jobs
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_export_job_success(db, redis_client):
    # Create job
    job = ExportJob(status=ExportStatus.pending)
    db.add(job)
    db.commit()
    db.refresh(job)

    await redis_client.rpush("queue:exports", job.id)

    # Simulate worker pop
    job_id = await redis_client.brpoplpush(
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
async def test_recover_stuck_job(db, redis_client):
    job = ExportJob(
        status=ExportStatus.processing,
        processing_started_at=datetime.now() - timedelta(seconds=1000)
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    await redis_client.rpush("queue:processing", job.id)

    await recover_stuck_jobs(db, redis_client)

    db.refresh(job)

    assert job.status == ExportStatus.pending

    queue = await redis_client.lrange("queue:exports", 0, -1)
    assert str(job.id) in queue

@pytest.mark.asyncio
async def test_completed_job_removed_from_processing(db, redis_client):
    job = ExportJob(status=ExportStatus.completed)
    db.add(job)
    db.commit()
    db.refresh(job)

    await redis_client.rpush("queue:processing", job.id)

    await recover_stuck_jobs(db, redis_client)

    queue = await redis_client.lrange("queue:processing", 0, -1)
    assert str(job.id) not in queue