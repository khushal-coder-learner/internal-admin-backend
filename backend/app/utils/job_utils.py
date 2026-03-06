from datetime import datetime, timedelta
from backend.app.models.job import ExportStatus, ExportJob

def compute_backoff(attempts: int) -> timedelta:
    base = 10          # seconds
    cap = 300          # 5 minutes
    delay = min(base * (2 ** (attempts - 1)), cap)
    return timedelta(seconds=delay)

def schedule_retry_or_fail(job: ExportJob):
    if job.attempts >= job.max_attempts:
        job.status = ExportStatus.failed
        job.next_run_at = None
    else:
        delay = compute_backoff(job.attempts)
        job.status = ExportStatus.pending
        job.next_run_at = datetime.now() + delay