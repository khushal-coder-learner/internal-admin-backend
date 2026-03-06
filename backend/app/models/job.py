from sqlalchemy import Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column
import enum
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

    id: Mapped[int] = mapped_column(primary_key=True)

    type: Mapped[JobType] = mapped_column(Enum(JobType), nullable=False)

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.pending,
        nullable=False
    )

    payload: Mapped[dict] = mapped_column(JSON, nullable=True)

    processing_started_at: Mapped[datetime | None]

    attempts: Mapped[int] = mapped_column(default=0)

    max_attempts: Mapped[int] = mapped_column(default=3)

    next_run_at: Mapped[datetime | None]
    
    last_error: Mapped[str | None]