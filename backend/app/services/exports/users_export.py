from sqlalchemy import select
from app.models.user import User
from .csv_writer import write_csv_paged
from .paths import get_export_dir
from uuid import uuid4

def generate_users_csv(db, progress_callback=None):

    headers = ["id", "email", "role", "is_active", "created_at", "updated_at"]

    def fetch_page(offset: int, limit: int):
        return db.execute(
            select(
                User.id,
                User.email,
                User.role,
                User.is_active,
                User.created_at,
                User.updated_at,
            )
            .order_by(User.created_at.asc(), User.id.asc())
            .offset(offset)
            .limit(limit)
        ).all()

    file_path = get_export_dir() / f"users_export_{uuid4()}.csv"

    write_csv_paged(
        file_path,
        headers,
        fetch_page,
        progress_callback=progress_callback,
        progress_step=100,
        page_size=1000,
    )

    return str(file_path)
