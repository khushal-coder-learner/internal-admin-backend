import os
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from tests.helpers import create_test_user, create_completed_export_job, create_test_job

from app.jobs.executors.cleanup_exports import RETENTION_SECONDS, execute_cleanup_exports
from app.core.dependencies import get_current_user
from app.main import app
from app.models.record import Record
from app.models.activity_log import ActivityLog
from app.models.job import Job, JobStatus, JobType
from app.services.job_service import (
    process_job,
    recover_stuck_jobs,
    QUEUE_PENDING,
    QUEUE_PROCESSING,
)

@pytest.mark.asyncio
async def test_export_job_success(db, test_redis):
    job = create_test_job(
        db,
        job_type=JobType.export,
        status=JobStatus.pending,
        payload={"export_type": "records"},
    )

    await test_redis.rpush(QUEUE_PENDING, job.id)

    # Simulate worker pop
    job_id = await test_redis.brpoplpush(
        QUEUE_PENDING,
        QUEUE_PROCESSING,
    )

    await process_job(db=db, job_id=job_id, redis=test_redis)

    db.refresh(job)

    assert job.status == JobStatus.completed
    assert isinstance(job.payload, dict)
    assert "file_path" in job.payload
    assert Path(job.payload["file_path"]).exists()

@pytest.mark.asyncio
async def test_process_job_idempotent(db, test_redis):
    job = create_test_job(db, job_type=JobType.export, status=JobStatus.completed)

    await process_job(db=db, job_id=job.id, redis=test_redis)

    # Should not change state
    db.refresh(job)
    assert job.status == JobStatus.completed


@pytest.mark.asyncio
async def test_recover_stuck_job(db, test_redis):
    job = create_test_job(
        db,
        job_type=JobType.export,
        status=JobStatus.processing,
        processing_started_at=datetime.now() - timedelta(seconds=1000),
    )

    await test_redis.rpush(QUEUE_PROCESSING, job.id)

    await recover_stuck_jobs(db, test_redis)

    db.refresh(job)

    assert job.status == JobStatus.pending

    queue = await test_redis.lrange(QUEUE_PENDING, 0, -1)
    assert str(job.id) in queue

@pytest.mark.asyncio
async def test_completed_job_removed_from_processing(db, test_redis):
    job = create_test_job(db, job_type=JobType.export, status=JobStatus.completed)

    await test_redis.rpush(QUEUE_PROCESSING, job.id)

    await recover_stuck_jobs(db, test_redis)

    queue = await test_redis.lrange(QUEUE_PROCESSING, 0, -1)
    assert str(job.id) not in queue

@pytest.mark.asyncio
async def test_records_export_job(db, test_redis):

    user = create_test_user(db)

    # create test records
    record1 = Record(title="Test1", status="open", created_by=user.id)
    record2 = Record(title="Test2", status="closed", created_by=user.id)

    db.add_all([record1, record2])
    db.commit()

    job = create_test_job(
        db,
        user=user,
        job_type=JobType.export,
        payload={"export_type": "records"},
    )

    await process_job(db=db, redis=test_redis, job_id=job.id)

    db.refresh(job)

    file_path = job.payload["file_path"]

    assert os.path.exists(file_path)

    with open(file_path) as f:
        content = f.read()

    assert "Test1" in content
    assert "Test2" in content

@pytest.mark.asyncio
async def test_users_export_job(db, test_redis):

    user = create_test_user(db)

    db.add(user)
    db.commit()

    job = create_test_job(
        db,
        user=user,
        job_type=JobType.export,
        payload={"export_type": "users"},
    )

    await process_job(db=db, redis=test_redis, job_id=job.id)

    db.refresh(job)

    assert "file_path" in job.payload

@pytest.mark.asyncio
async def test_activity_logs_export_job(client, db, test_redis,):
    user = create_test_user(db)

    # create export job
    job = create_test_job(
        db,
        user=user,
        job_type=JobType.export,
        payload={"export_type": "activity_logs"},
    )

    await process_job(db=db, redis=test_redis, job_id=job.id)

    db.refresh(job)

    assert "file_path" in job.payload

    file_path = job.payload["file_path"]

    assert os.path.exists(file_path)

@pytest.mark.asyncio
async def test_cleanup_exports_removes_expired_files_and_jobs(db, test_redis, export_dir):
    export_file = export_dir / "expired-export.csv"
    export_file.write_text("id,name\n1,test\n", encoding="utf-8")

    job = create_test_job(
        db,
        job_type=JobType.export,
        status=JobStatus.completed,
        payload={"export_type": "records", "file_path": str(export_file)},
        updated_at=datetime.now() - timedelta(seconds=RETENTION_SECONDS + 1),
    )
    job_id = job.id

    result = await execute_cleanup_exports(db, test_redis, job)

    assert result == "Cleaned up exports"
    assert not export_file.exists()
    assert db.get(Job, job_id) is None

@pytest.mark.asyncio
async def test_export_download(client, db, test_redis):
    user = create_test_user(db)
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        job = await create_completed_export_job(db, test_redis)
        job.user_id = user.id
        db.commit()
        db.refresh(job)

        response = client.get(f"/jobs/{job.id}")

        assert response.status_code == 200, response.text

        url = response.json()["download_url"]

        download = client.get(url)

        assert download.status_code == 200
        assert "text/csv" in download.headers["content-type"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)
