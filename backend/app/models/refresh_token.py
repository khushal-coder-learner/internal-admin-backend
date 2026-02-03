from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Index, ForeignKey, Text, DateTime, func
import uuid 
from datetime import datetime

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete='CASCADE'), 
        primary_key=True )
    
    token_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        Index("ix_refresh_tokens_expires_at", "expires_at"),
    )