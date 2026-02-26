import csv
from sqlalchemy import select
from sqlalchemy.orm import Session
from pathlib import Path
from app.models.record import Record

EXPORT_DIR = Path("storage/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def generate_csv(db: Session, job_id: int) -> str:
    rows = db.execute(select(Record)).scalars().all()

    file_path = EXPORT_DIR / f"export_{job_id}.csv"

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "title", "description", "status", "assigned_to", "created_by", "is_deleted", "created_at", "updated_at"])

        for row in rows:
            writer.writerow([
                row.id,
                row.title,
                row.description,
                row.status,
                row.assigned_to,
                row.created_by,
                row.is_deleted,
                row.created_at,
                row.updated_at
            ])

    return str(file_path)