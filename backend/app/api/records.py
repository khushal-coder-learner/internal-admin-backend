from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from app.schemas.record import RecordCreate, RecordResponse, RecordUpdate, RecordStatusUpdate, RecordAssign
from app.services.record_service import create_record, list_records, update_record, change_record_status, assign_record, soft_delete_record
from app.models.user import User

from typing import List
from uuid import UUID


router = APIRouter(
    prefix="/records",
    tags=["Records"],
)

@router.post("", response_model=RecordResponse)
def create_record_endpoint(
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_record(
        db=db,
        data=payload,
        current_user=current_user,
    )

@router.get("", response_model=List[RecordResponse])
def list_records_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    status: str | None = None,
    assigned_to: UUID | None = None,
    search: str | None = None,
):
    return list_records(
        db=db,
        current_user = current_user,
        page=page,
        limit=limit,
        status=status,
        assigned_to=assigned_to,
        search=search,
    )

@router.patch("/{record_id}", response_model=RecordResponse)
def update_record_endpoint(
    record_id: UUID,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_record(
        db=db,
        record_id=record_id,
        data=payload,
        current_user=current_user,
    )

@router.post("/{record_id}/status", response_model=RecordResponse)
def change_status_endpoint(
    record_id: UUID,
    payload: RecordStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return change_record_status(
        db=db,
        record_id=record_id,
        new_status=payload.status,
        current_user=current_user,
    )

@router.post("/{record_id}/assign", response_model=RecordResponse, dependencies=[Depends(require_role("admin"))]
)
def assign_record_endpoint(
    record_id: UUID,
    payload: RecordAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return assign_record(
        db=db,
        record_id=record_id,
        assignee_id=payload.user_id,
        current_user=current_user,
    )

@router.delete("/{record_id}", status_code=204, dependencies=[Depends(require_role("admin"))])
def delete_record_endpoint(
    record_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    soft_delete_record(
        db=db,
        record_id=record_id,
        current_user=current_user,
    )
