import pytest

from tests.helpers import create_test_user, create_test_job
from app.models.job import Job, JobStatus
from app.models.user import User
from app.jobs.types import JobType
from app.services.job_service import process_job

@pytest.mark.asyncio
async def test_bulk_email_dispatch_creates_jobs(db, test_redis):
    initial_active_user_count = db.query(User).filter(User.is_active.is_(True)).count()
    initial_send_email_job_count = db.query(Job).filter(Job.type == JobType.send_email).count()

    for _ in range(5):
        create_test_user(db)

    owner = create_test_user(db)
    active_user_count = db.query(User).filter(User.is_active.is_(True)).count()

    job = create_test_job(
        db,
        user=owner,
        job_type=JobType.bulk_user_email_dispatch,
        payload={
            "subject": "Hello",
            "body": "Test email"
        },
    )

    await process_job(db=db, redis=test_redis, job_id=job.id)

    db.refresh(job)
    assert job.status == JobStatus.completed

    email_jobs = db.query(Job).filter(Job.type == JobType.send_email).all()

    assert active_user_count == initial_active_user_count + 6
    assert len(email_jobs) == initial_send_email_job_count + active_user_count

@pytest.mark.asyncio
async def test_bulk_dispatch_pushes_jobs_to_queue(db, test_redis, monkeypatch):

    for _ in range(3):
        create_test_user(db)

    owner = create_test_user(db)
    active_user_count = db.query(User).filter(User.is_active.is_(True)).count()
    queued_job_ids = []

    original_lpush = test_redis.lpush

    async def tracking_lpush(name, value):
        if name == "queue:jobs":
            queued_job_ids.append(value)
        return await original_lpush(name, value)

    monkeypatch.setattr(test_redis, "lpush", tracking_lpush)

    job = create_test_job(
        db,
        user=owner,
        job_type=JobType.bulk_user_email_dispatch,
        payload={"subject": "Hi", "body": "Body"},
    )

    await process_job(db=db, redis=test_redis, job_id=job.id)

    assert len(queued_job_ids) == active_user_count
    assert all(isinstance(job_id, str) for job_id in queued_job_ids)

@pytest.mark.asyncio
async def test_send_email_job_completes(db, test_redis):

    user = create_test_user(db)

    job = create_test_job(
        db,
        user=user,
        job_type=JobType.send_email,
        payload={
            "user_id": str(user.id),
            "subject": "Test",
            "body": "Hello"
        },
    )

    await process_job(db=db, redis=test_redis, job_id=job.id)

    db.refresh(job)

    assert job.status == JobStatus.completed
