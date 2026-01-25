from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import require_role
from app.schemas.activity_log import ActivityLogResponse
from app.services.activity_service import list_activity_logs

router = APIRouter(
    prefix="/activity-logs",
    tags=["Activity Logs"],
)

@router.get("", response_model=List[ActivityLogResponse], dependencies=[Depends(require_role("admin"))])
def get_activity_logs(
    *,
    db: Session = Depends(get_db),
    cursor: datetime | None = Query(None),
    limit: int = Query(20, le=100),
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    user_id: UUID | None = None,
    action: str | None = None,
):
    return list_activity_logs(
        db=db,
        cursor=cursor,
        limit=limit,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        action=action,
    )
