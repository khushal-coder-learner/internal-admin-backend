from app.utils.csv_generator import generate_csv
from app.models.job import Job
from sqlalchemy.orm import Session
from redis.asyncio import Redis

def execute_export(db: Session, job: Job, redis: Redis | None = None):
    file_path = generate_csv(db, job.id)
    job.payload = {"file_path": file_path}