import os
from datetime import datetime, timedelta

from sqlalchemy import select

from app.core.logging import get_logger
from app.models.job import Job, JobType, JobStatus


RETENTION_SECONDS = 600
logger = get_logger(__name__)


async def execute_cleanup_exports(db, redis, job):
    cutoff = datetime.now() - timedelta(seconds=RETENTION_SECONDS)
    cleaned_count = 0
    trigger_job_id = getattr(job, "id", None) if job is not None else None

    jobs = db.execute(
        select(Job)
        .where(Job.type == JobType.export)
        .where(Job.status == JobStatus.completed)
        .where(Job.updated_at < cutoff)
        .limit(1000)
    ).scalars()

    for export_job in jobs:
        payload = export_job.payload or {}
        file_path = payload.get("file_path")

        if file_path:
            try:
                os.remove(file_path)
                logger.info(
                    "Removed exported file",
                    extra={"job_id": export_job.id, "file_path": file_path},
                )
            except FileNotFoundError:
                logger.warning(
                    "Export file already missing during cleanup",
                    extra={"job_id": export_job.id, "file_path": file_path},
                )
        else:
            logger.warning(
                "Skipping export cleanup because file path is missing",
                extra={"job_id": export_job.id},
            )

        db.delete(export_job)
        cleaned_count += 1

    db.commit()
    logger.info(
        "Completed export cleanup pass",
        extra={
            "job_id": trigger_job_id,
            "cleaned_jobs": cleaned_count,
        },
    )

    return "Cleaned up exports"
