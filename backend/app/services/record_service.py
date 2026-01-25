from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.record import Record
from app.models.user import User

from app.services.activity_service import log_activity



def create_record(
    db: Session,
    *,
    data,
    current_user: User,
) -> Record:
    record = Record(
        title=data.title,
        description=data.description,
        created_by=current_user.id,
    )

    db.add(record)
    db.flush()  # 👈 important

    log_activity(
        db=db,
        entity_type="record",
        entity_id=record.id,
        action="create",
        performed_by=current_user.id,
        details={
            "title": record.title,
        },
    )

    return record

def list_records(
    db: Session,
    *,
    current_user: User,
    page: int,
    limit: int,
    status: str | None = None,
    assigned_to: UUID | None = None,
    search: str | None = None,
):
    stmt = select(Record).where(Record.is_deleted == False)

    # 🔐 STAFF VISIBILITY RESTRICTION
    if current_user.role == "staff":
        stmt = stmt.where(Record.assigned_to == current_user.id)

    # ADMIN-ONLY FILTERS
    else:
        if assigned_to:
            stmt = stmt.where(Record.assigned_to == assigned_to)

    # Filter by status
    if status:
        stmt = stmt.where(Record.status == status)

    # Simple search
    if search:
        stmt = stmt.where(Record.title.ilike(f"%{search}%"))

    stmt = stmt.order_by(Record.created_at.desc())

    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)

    return db.scalars(stmt).all()


def update_record(
    db: Session,
    *,
    record_id: UUID,
    data,
    current_user: User,
) -> Record:
    record = db.get(Record, record_id)

    if not record or record.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )
    
     # 🔐 Ensure Permission for editing
    _ensure_record_edit_permission(
        record=record,
        current_user=current_user,
    )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        return record  # nothing to update

    before = {
        field: getattr(record, field)
        for field in update_data.keys()
    }

    for field, value in update_data.items():
        setattr(record, field, value)

    log_activity(
        db=db,
        entity_type="record",
        entity_id=record.id,
        action="update",
        performed_by=current_user.id,
        details={
            "before": before,
            "after": update_data,
        },
    )

    return record

def change_record_status(
    db: Session,
    *,
    record_id: UUID,
    new_status: str,
    current_user: User,
) -> Record:
    record = db.get(Record, record_id)

    if not record or record.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )
    
     # 🔐 Ensure Permission for editing
    _ensure_record_edit_permission(
        record=record,
        current_user=current_user,
    )

    old_status = record.status
    record.status = new_status

    log_activity(
        db=db,
        entity_type="record",
        entity_id=record.id,
        action="status_change",
        performed_by=current_user.id,
        details={
            "from": old_status,
            "to": new_status,
        },
    )

    return record

def assign_record(
    db: Session,
    *,
    record_id: UUID,
    assignee_id: UUID,
    current_user: User,
) -> Record:
    record = db.get(Record, record_id)

    if not record or record.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )

    record.assigned_to = assignee_id

    log_activity(
        db=db,
        entity_type="record",
        entity_id=record.id,
        action="assign",
        performed_by=current_user.id,
        details={
            "assigned_to": str(assignee_id),
        },
    )

    return record

def soft_delete_record(
    db: Session,
    *,
    record_id: UUID,
    current_user: User,
) -> None:
    record = db.get(Record, record_id)

    if not record or record.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )

    record.is_deleted = True

    log_activity(
        db=db,
        entity_type="record",
        entity_id=record.id,
        action="delete",
        performed_by=current_user.id,
        details={
            "soft_delete": True
        },
    )


def _ensure_record_edit_permission(
    *,
    record: Record,
    current_user: User,
):
    if current_user.role == "admin":
        return

    if record.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this record",
        )
