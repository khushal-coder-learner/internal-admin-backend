from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException
from redis.asyncio import Redis
from app.core.dependencies import get_db, get_redis
from app.models.export import ExportJob, ExportStatus

QUEUE_NAME = "queue:exports"

router = APIRouter()

@router.post("/exports")
async def create_export(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):

    job = ExportJob(status=ExportStatus.pending)

    db.add(job)
    db.commit()
    db.refresh(job)

    await redis.lpush(QUEUE_NAME, job.id) # type: ignore

    return {"job_id": job.id}

@router.get("/exports/{job_id}")
def get_export(job_id: int, db: Session = Depends(get_db)):
    job = db.get(ExportJob, job_id)
    if not job:
        raise HTTPException(404)

    return {
        "status": job.status,
        "file_path": job.file_path
    }