import pytest

from tests.helpers import create_test_user
from app.models.job import Job, JobStatus
from app.models.user import User
from app.jobs.types import JobType
from app.services.job_service import process_job

@pytest.mark.asyncio
async def test_bulk_email_dispatch_creates_jobs(db, test_redis):

    assert db.query(User).count() == 0

    for _ in range(5):
        create_test_user(db)

    job = Job(
        type=JobType.bulk_user_email_dispatch,
        payload={
            "subject": "Hello",
            "body": "Test email"
        }
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    await process_job(db=db, redis=test_redis, job_id=job.id)

    db.refresh(job)
    assert job.status == JobStatus.completed

    email_jobs = db.query(Job).filter(Job.type == JobType.send_email).all()

    assert len(email_jobs) == 5

@pytest.mark.asyncio
async def test_bulk_dispatch_pushes_jobs_to_queue(db, test_redis):

    for _ in range(3):
        create_test_user(db)

    job = Job(
        type=JobType.bulk_user_email_dispatch,
        payload={"subject": "Hi", "body": "Body"}
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    await process_job(db=db, redis=test_redis, job_id=job.id)

    queue_length = await test_redis.llen("queue:jobs")

    assert queue_length == 3

@pytest.mark.asyncio
async def test_send_email_job_completes(db, test_redis):

    user = create_test_user(db)

    job = Job(
        type=JobType.send_email,
        payload={
            "user_id": str(user.id),
            "subject": "Test",
            "body": "Hello"
        }
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    await process_job(db=db, redis=test_redis, job_id=job.id)

    db.refresh(job)

    assert job.status == JobStatus.completed