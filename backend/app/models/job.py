from sqlalchemy import Enum, DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

import enum
import uuid
from datetime import datetime

from app.db.base import Base
from app.models.mixins import TimestampMixin
from app.jobs.types import JobType

class JobStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        String, 
        primary_key=True,
        default=uuid.uuid4
    )

    type: Mapped[JobType] = mapped_column(
        Enum(JobType), 
        nullable=False
    )

    user_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    request_id: Mapped[str | None] = mapped_column(
        String, 
        nullable=True, 
        index=True
    )

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.pending,
        nullable=False,
        index=True
    )

    payload: Mapped[dict] = mapped_column(JSONB, nullable=True)

    attempts: Mapped[int] = mapped_column(default=0)

    max_attempts: Mapped[int] = mapped_column(default=3)

    processing_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    last_error: Mapped[str | None] = mapped_column(String, nullable=True)

    user = relationship("User", back_populates="jobs")