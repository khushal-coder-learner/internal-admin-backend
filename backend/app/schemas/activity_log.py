from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ActivityLogResponse(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    performed_by: UUID
    details: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
