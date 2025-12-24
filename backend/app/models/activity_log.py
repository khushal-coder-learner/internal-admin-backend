import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ActivityLog(TimestampMixin ,Base):
    __tablename__ = "activity_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    entity_type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )

    action: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    performed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    details: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )
