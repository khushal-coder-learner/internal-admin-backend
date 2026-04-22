from sqlalchemy import select
from app.models.activity_log import ActivityLog
from .csv_writer import write_csv_paged
from .paths import get_export_dir
from uuid import uuid4

def generate_activity_logs_csv(db, progress_callback=None):

    headers = ["id", "entity_type", "entity_id", "action", "performed_by", "details", "created_at", "updated_at"]

    def fetch_page(offset: int, limit: int):
        return db.execute(
            select(
                ActivityLog.id,
                ActivityLog.entity_type,
                ActivityLog.entity_id,
                ActivityLog.action,
                ActivityLog.performed_by,
                ActivityLog.details,
                ActivityLog.created_at,
                ActivityLog.updated_at,
            )
            .order_by(ActivityLog.created_at.asc(), ActivityLog.id.asc())
            .offset(offset)
            .limit(limit)
        ).all()

    file_path = get_export_dir() / f"activity_logs_export_{uuid4()}.csv"

    write_csv_paged(
        file_path,
        headers,
        fetch_page,
        progress_callback=progress_callback,
        progress_step=100,
        page_size=1000,
    )

    return str(file_path)
