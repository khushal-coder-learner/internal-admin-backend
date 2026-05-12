from sqlalchemy import select
from app.models.user import User
from app.services.exports.export_pipeline import generate_csv_export

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

    return generate_csv_export(
        filename_prefix="users_export",
        headers=headers,
        fetch_page=fetch_page,
        progress_callback=progress_callback,
    )
