from sqlalchemy import select
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from app.models.user import User
from app.models.job import Job
from app.models.job import JobType


async def execute_bulk_user_email_dispatch(db: Session, job, redis: Redis):

    payload = job.payload
    subject = payload["subject"]
    body = payload["body"]

    count = 0

    for user_id in db.execute(
        select(User.id).where(User.is_active.is_(True))
    ).scalars():

        new_job = Job(
            type=JobType.send_email,
            payload={
                "user_id": str(user_id),
                "subject": subject,
                "body": body,
            },
        )

        db.add(new_job)
        db.flush()  # assign an id so we can push it to Redis

        await redis.lpush("queue:jobs", new_job.id) # type: ignore

        count += 1

        if count % 500 == 0:
            db.flush()