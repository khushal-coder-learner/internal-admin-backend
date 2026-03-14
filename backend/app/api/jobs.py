from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import FileResponse
from redis.asyncio import Redis
from app.core.dependencies import get_db, get_redis
from app.models.job import Job, JobStatus
from app.jobs.types import JobType
from app.core.security import settings
from app.utils.file_utils import generate_signed_download_url

import os
import time
import hmac
import hashlib

QUEUE_NAME = "queue:jobs"

router = APIRouter()

@router.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404)
    
    download_url = None

    if job.status == JobStatus.completed and job.payload.get("file_path"):
        download_url = generate_signed_download_url(job.payload["file_path"])

    return {
        "status": job.status,
        "payload": job.payload,
        "progress": job.payload.get("progress", 0),
        "download_url": download_url
    }

@router.post("/jobs/export")
async def create_export(
    export_type: str,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):

    job = Job(
        type = JobType.export,
        status=JobStatus.pending,
        payload = {"export_type": export_type})

    db.add(job)
    db.commit()
    db.refresh(job)

    await redis.lpush(QUEUE_NAME, job.id) # type: ignore

    return {"job_id": job.id}

@router.get("/exports/download")
def download_export(path: str, expires: int, sig: str):

    now = int(time.time())

    if now > expires:
        raise HTTPException(403, "Download link expired")

    message = f"{path}:{expires}".encode()

    expected_sig = hmac.new(
        settings.secret_key.encode(),
        message,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(sig, expected_sig):
        raise HTTPException(403, "Invalid signature")

    if not os.path.exists(path):
        raise HTTPException(404, "File not found")

    return FileResponse(
        path,
        filename=os.path.basename(path),
        media_type="text/csv"
    )

@router.post("/jobs/send-announcement")
async def send_announcement(
    subject: str,
    body: str,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):

    job = Job(
        type=JobType.bulk_user_email_dispatch,
        payload={
            "subject": subject,
            "body": body
        }
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    await redis.lpush("queue:jobs", job.id) # type: ignore

    return {"job_id": job.id}