from sqlalchemy import select
from app.models.activity_log import ActivityLog
from app.services.exports.export_pipeline import generate_csv_export

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

    return generate_csv_export(
        filename_prefix="activity_logs_export",
        headers=headers,
        fetch_page=fetch_page,
        progress_callback=progress_callback,
    )