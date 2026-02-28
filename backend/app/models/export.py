from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum
from datetime import datetime

from app.db.base import Base
from app.models.mixins import TimestampMixin

class ExportStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ExportJob(TimestampMixin, Base):
    __tablename__ = "export_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)

    status: Mapped[ExportStatus] = mapped_column(
        Enum(ExportStatus),
        default=ExportStatus.pending,
        nullable=False
    )
    file_path: Mapped[str | None]

    processing_started_at: Mapped[datetime | None]

    attempts: Mapped[int] = mapped_column(default=0)

    max_attempts: Mapped[int] = mapped_column(default=3)

    next_run_at: Mapped[datetime | None]
    
    last_error: Mapped[str | None]