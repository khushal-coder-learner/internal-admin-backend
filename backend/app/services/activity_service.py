from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

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
    cursor: datetime | None = None,
    limit: int,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    user_id: UUID | None = None,
    action: str | None = None,
):
    stmt = select(ActivityLog)

    if entity_type:
        stmt = stmt.where(ActivityLog.entity_type == entity_type)

    if entity_id:
        stmt = stmt.where(ActivityLog.entity_id == entity_id)

    if user_id:
        stmt = stmt.where(ActivityLog.performed_by == user_id)

    if action:
        stmt = stmt.where(ActivityLog.action == action)

    #Keyset Condition
    if cursor:
        stmt = stmt.where(ActivityLog.created_at < cursor)

    stmt = (
        stmt.order_by(ActivityLog.created_at.desc())
        .limit(limit)
        )

    return db.scalars(stmt).all()
