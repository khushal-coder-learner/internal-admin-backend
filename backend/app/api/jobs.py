from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import Request, Depends, APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from redis.asyncio import Redis
from typing import Optional
from app.core.permissions import Permission
from app.core.dependencies import get_db, get_redis, get_request_id, get_current_user, require_permission
from app.models.user import User
from app.models.job import Job, JobStatus
from app.jobs.types import JobType
from app.core.security import settings
from app.utils.file_utils import generate_signed_download_url
from app.core.logging import get_logger
from app.services.activity_service import log_activity
from app.services.job_service import get_user_jobs

import os
import uuid
import time
import hmac
import hashlib
from pathlib import Path


logger = get_logger(__name__)

QUEUE_NAME = "queue:jobs"

router = APIRouter()

@router.get("/jobs/me")
async def get_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[JobStatus] = Query(None),
    job_type: Optional[JobType] = Query(None),
    limit: int = Query(10, le=100),
    offset: int = Query(0),
    sort_order: str = Query("desc"),
):
    result = await get_user_jobs(
        db=db,
        current_user=current_user,
        status=status,
        job_type=job_type,
        limit=limit,
        offset=offset,
        sort_order=sort_order,
    )

    logger.info(
        "Fetched user jobs",
        extra={
            "user_id": current_user.id,
            "count": result["total"]
        }
    )

    items = []

    for job in result["items"]:
        download_url = None

        if job.status == JobStatus.completed and job.payload.get("file_path"):
            download_url = generate_signed_download_url(job.payload["file_path"])

        items.append({
            "id": job.id,
            "type": job.type,
            "status": job.status,
            "payload": job.payload,
            "created_at": job.created_at,
            "download_url": download_url,
        })

    return {
        "items": items,
        "total": result["total"],
        }

@router.get("/jobs/{job_id}", dependencies=[Depends(require_permission(Permission.JOB_VIEW))])
def get_job(job_id: str, db: Session = Depends(get_db)):
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

@router.post("/jobs/export", dependencies=[Depends(require_permission(Permission.EXPORT_JOB))])
async def create_export(
    export_type: str,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(get_current_user)
):

    job = Job(
        type = JobType.export,
        user_id = current_user.id,
        status=JobStatus.pending,
        payload = {"export_type": export_type},
        request_id = request_id)

    db.add(job)
    db.commit()
    db.refresh(job)

    logger.info(
        "Job created",
        extra={
            "job_id": job.id,
            "job_type": job.type,
            "request_id": request_id
        }
    )

    log_activity(
        db,
        entity_type="job",
        entity_id=job.id,
        action="export_requested",
        performed_by=current_user.id,  # IMPORTANT
        details={
            "job_type": job.type,
            "export_type": export_type,
            "request_id": request_id
        }
    )

    await redis.lpush(QUEUE_NAME, str(job.id)) # type: ignore

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
    
    BASE_DIR = Path("storage/exports").resolve()
    requested_path = Path(path).resolve()

    if not str(requested_path).startswith(str(BASE_DIR)):
        raise HTTPException(403, "Invalid path")

    if not os.path.exists(requested_path):
        raise HTTPException(404, "File not found")

    return FileResponse(
        path,
        filename=os.path.basename(path),
        media_type="text/csv"
    )

@router.post("/jobs/send-announcement", dependencies=[Depends(require_permission(Permission.SEND_ANNOUNCEMENT))])
async def send_announcement(
    subject: str,
    body: str,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    request_id: str = Depends(get_request_id),
    current_user: User = Depends(get_current_user)
):

    job = Job(
        type=JobType.bulk_user_email_dispatch,
        user_id = current_user.id,
        status = JobStatus.pending,
        payload={
            "subject": subject,
            "body": body
        },
        request_id = request_id
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    logger.info(
        "Job created",
        extra={
            "job_id": job.id,
            "job_type": job.type,
            "request_id": request_id
        }
    )

    log_activity(
        db,
        entity_type="job",
        entity_id=job.id,
        action="announcement_requested",
        performed_by=current_user.id,
        details={
            "job_type": job.type,
            "subject": subject,
            "request_id": request_id
        }
    )

    await redis.lpush("queue:jobs", str(job.id)) # type: ignore

    return {"job_id": job.id}