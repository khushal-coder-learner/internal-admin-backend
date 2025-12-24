from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from app.schemas.activity_log import ActivityLogResponse
from app.services.activity_service import list_activity_logs
from app.models.user import User

router = APIRouter(
    prefix="/activity-logs",
    tags=["Activity Logs"],
)

@router.get("", response_model=List[ActivityLogResponse])
def get_activity_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    user_id: UUID | None = None,
    action: str | None = None,
):
    return list_activity_logs(
        db=db,
        page=page,
        limit=limit,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        action=action,
    )
