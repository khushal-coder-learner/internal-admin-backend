from sqlalchemy import select
from app.models.record import Record
from .csv_writer import write_csv
from .paths import get_export_dir
from uuid import uuid4


def generate_records_csv(db, progress_callback=None):

    headers = ["id", "title", "description", "status", "assigned_to", "created_by", "is_deleted", "created_at", "updated_at"]

    rows = db.execute(
        select(
            Record.id,
            Record.title,
            Record.description,
            Record.status,
            Record.assigned_to,
            Record.created_by,
            Record.is_deleted,
            Record.created_at,
            Record.updated_at
        )
    ).yield_per(1000)

    file_path = get_export_dir() / f"records_export_{uuid4()}.csv"

    write_csv(file_path, headers, rows, progress_callback=progress_callback)

    return str(file_path)
