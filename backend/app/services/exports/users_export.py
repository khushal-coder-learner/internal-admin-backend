from sqlalchemy import select
from app.models.user import User
from .csv_writer import write_csv
from .paths import get_export_dir
from uuid import uuid4

def generate_users_csv(db, progress_callback=None):

    headers = ["id", "email", "role", "is_active", "created_at", "updated_at"]

    rows = db.execute(
        select(
            User.id,
            User.email,
            User.role,
            User.is_active,
            User.created_at,
            User.updated_at
        )
    ).yield_per(1000)

    file_path = get_export_dir() / f"users_export_{uuid4()}.csv"

    write_csv(file_path, headers, rows, progress_callback=progress_callback)

    return str(file_path)
