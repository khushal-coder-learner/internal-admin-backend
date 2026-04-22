from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.activity_log import ActivityLog


def log_activity(
    db: Session,
    *,
    entity_type: str,
    entity_id: UUID,
    action: str,
    performed_by: UUID,
    details: dict | None = None,
):
    activity = ActivityLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        performed_by=performed_by,
        details=dict(details) if details else None,
    )

    db.add(activity)

def list_activity_logs(
    db: Session,
    *,
    page: int,
    limit: int,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    user_id: UUID | None = None,
    action: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    stmt = select(ActivityLog)

    # filters
    if entity_type:
        stmt = stmt.where(ActivityLog.entity_type == entity_type)

    if entity_id:
        stmt = stmt.where(ActivityLog.entity_id == entity_id)

    if user_id:
        stmt = stmt.where(ActivityLog.performed_by == user_id)

    if action:
        stmt = stmt.where(ActivityLog.action == action)

    if search:
        stmt = stmt.where(ActivityLog.entity_type.ilike(f"%{search}%"))

    # count
    total = db.scalar(
        select(func.count()).select_from(ActivityLog).where(*stmt._where_criteria)
    ) or 0

    # sorting
    ALLOWED_SORTS = {"created_at", "action", "entity_type"}
    sort_col = getattr(ActivityLog, sort_by) if sort_by in ALLOWED_SORTS else ActivityLog.created_at
    order_expr = sort_col.desc() if sort_order == "desc" else sort_col.asc()

    # pagination
    offset = (page - 1) * limit

    stmt = (
        stmt
        .order_by(order_expr)
        .offset(offset)
        .limit(limit)
    )

    items = db.scalars(stmt).all()

    return {
        "items": items,
        "total": total,
    }