from sqlalchemy import select
from app.models.record import Record
from app.services.exports.export_pipeline import generate_csv_export


def generate_records_csv(db, progress_callback=None):

    headers = ["id", "title", "description", "status", "assigned_to", "created_by", "is_deleted", "created_at", "updated_at"]

    def fetch_page(offset: int, limit: int):
        return db.execute(
            select(
                Record.id,
                Record.title,
                Record.description,
                Record.status,
                Record.assigned_to,
                Record.created_by,
                Record.is_deleted,
                Record.created_at,
                Record.updated_at,
            )
            .order_by(Record.created_at.asc(), Record.id.asc())
            .offset(offset)
            .limit(limit)
        ).all()

    return generate_csv_export(
        filename_prefix="records_export",
        headers=headers,
        fetch_page=fetch_page,
        progress_callback=progress_callback,
    )
