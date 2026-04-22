from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import require_permission
from app.schemas.activity_log import MultiActivityLogs
from app.services.activity_service import list_activity_logs
from app.core.permissions import Permission

router = APIRouter(
    prefix="/activity-logs",
    tags=["Activity Logs"],
)

@router.get("", response_model=MultiActivityLogs, dependencies=[Depends(require_permission(Permission.ACTIVITY_VIEW))])
def get_activity_logs(
    *,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    user_id: UUID | None = None,
    action: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    return list_activity_logs(
        db=db,
        page=page,
        limit=limit,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        action=action,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
