from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException
from redis.asyncio import Redis
from app.core.dependencies import get_db, get_redis
from app.models.job import Job, JobStatus
from app.jobs.types import JobType

QUEUE_NAME = "queue:jobs"

router = APIRouter()

@router.post("/jobs")
async def create_export(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):

    job = Job(
        type = JobType.export,
        status=JobStatus.pending,
        payload = {})

    db.add(job)
    db.commit()
    db.refresh(job)

    await redis.lpush(QUEUE_NAME, job.id) # type: ignore

    return {"job_id": job.id}

@router.get("/jobs/{job_id}")
def get_export(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404)

    return {
        "status": job.status,
        "payload": job.payload
    }