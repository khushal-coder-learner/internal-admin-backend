import os
from datetime import datetime, timedelta
from sqlalchemy import select

from app.models.job import Job, JobType, JobStatus


RETENTION_SECONDS = 600


async def execute_cleanup_exports(db, redis, job):
    cutoff = datetime.now() - timedelta(seconds=RETENTION_SECONDS)

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
                print("File removed: ", file_path)
            except FileNotFoundError:
                print("File not found!")
        else:
            print(f"Skipping export job {export_job.id}: missing file_path")

        db.delete(export_job)

    db.commit()

    return "Cleaned up exports"
