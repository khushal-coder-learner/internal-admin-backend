from datetime import datetime
from sqlalchemy import select
from app.models.job import Job, JobStatus


async def enqueue_scheduled_jobs(db, redis):

    now = datetime.now()

    jobs = db.execute(
        select(Job)
        .where(Job.status == JobStatus.pending)
        .where(Job.next_run_at <= now)
        .order_by(Job.next_run_at)
        .limit(1000)
        .with_for_update(skip_locked=True)
    ).scalars()

    for job in jobs:
        job.next_run_at = None
        await redis.lpush("queue:jobs", job.id)

    db.commit()