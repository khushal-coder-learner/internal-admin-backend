from .records_export import generate_records_csv
from .users_export import generate_users_csv
from .activity_logs_export import generate_activity_logs_csv
from sqlalchemy import select, func

from app.models.user import User
from app.models.record import Record
from app.models.activity_log import ActivityLog


EXPORT_GENERATORS = {
    "records": generate_records_csv,
    "users": generate_users_csv,
    "activity_logs": generate_activity_logs_csv,
}


def _count_users(db) -> int:
    return db.scalar(select(func.count()).select_from(User)) or 0


def _count_records(db) -> int:
    return db.scalar(select(func.count()).select_from(Record)) or 0


def _count_activity_logs(db) -> int:
    return db.scalar(select(func.count()).select_from(ActivityLog)) or 0


EXPORT_TOTALS = {
    "records": _count_records,
    "users": _count_users,
    "activity_logs": _count_activity_logs,
}


def get_export_total_rows(db, export_type: str) -> int:
    counter = EXPORT_TOTALS.get(export_type)
    if not counter:
        return 0
    return int(counter(db))
