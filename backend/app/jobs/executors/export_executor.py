from app.utils.csv_generator import generate_csv
from app.models.job import Job
from sqlalchemy.orm import Session

def execute_export(db: Session, job: Job):
    file_path = generate_csv(db, job.id)
    job.payload = {"file_path": file_path}