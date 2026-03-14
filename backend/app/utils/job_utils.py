from datetime import datetime, timedelta
from app.models.job import Job, JobStatus
from sqlalchemy.orm.attributes import flag_modified

def compute_backoff(attempts: int) -> timedelta:
    base = 10          # seconds
    cap = 300          # 5 minutes
    delay = min(base * (2 ** (attempts - 1)), cap)
    return timedelta(seconds=delay)

def schedule_retry_or_fail(job: Job):
    if job.attempts >= job.max_attempts:
        job.status = JobStatus.failed
        job.next_run_at = None
    else:
        delay = compute_backoff(job.attempts)
        job.status = JobStatus.pending
        job.next_run_at = datetime.now() + delay