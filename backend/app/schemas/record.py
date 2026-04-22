from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RecordCreate(BaseModel):
    title: str
    description: str | None = None


class RecordUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    

class RecordResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: str
    assigned_to: UUID | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MultiRecordResponse(BaseModel):
    items: list[RecordResponse]
    total: int

class RecordStatusUpdate(BaseModel):
    status: str

class RecordAssign(BaseModel):
    # Allow null to support "unassign" from the UI (and allow omission if desired).
    user_id: UUID | None = None
