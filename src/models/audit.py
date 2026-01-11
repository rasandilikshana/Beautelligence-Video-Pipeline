"""
Beautelligence Video Pipeline - Audit and Quota Models

Tracks operations for debugging and manages daily quotas.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, func, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.models.database import Base
from src.models.keyword import GUID

from src.models.database import Base


class AuditLog(Base):
    """Audit log for debugging and analytics."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    operation: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<AuditLog(operation='{self.operation}', action='{self.action}')>"

    @classmethod
    def log(
        cls,
        operation: str,
        action: str,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        details: dict | None = None,
        error_details: dict | None = None,
    ) -> "AuditLog":
        """Create a new audit log entry."""
        return cls(
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            details=details,
            error_details=error_details,
        )


class DailyQuota(Base):
    """Daily quota tracking for rate limiting."""

    __tablename__ = "daily_quotas"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    quota_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    videos_generated: Mapped[int] = mapped_column(Integer, default=0)
    videos_limit: Mapped[int] = mapped_column(Integer, default=3)
    api_calls_gemini: Mapped[int] = mapped_column(Integer, default=0)
    api_calls_veo: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<DailyQuota(date='{self.quota_date}', videos={self.videos_generated}/{self.videos_limit})>"

    @property
    def can_generate(self) -> bool:
        """Check if more videos can be generated today."""
        return self.videos_generated < self.videos_limit

    @property
    def remaining_videos(self) -> int:
        """Get remaining video quota for today."""
        return max(0, self.videos_limit - self.videos_generated)

    def increment_videos(self) -> None:
        """Increment video generation count."""
        self.videos_generated += 1

    def increment_gemini_calls(self) -> None:
        """Increment Gemini API call count."""
        self.api_calls_gemini += 1

    def increment_veo_calls(self) -> None:
        """Increment Veo API call count."""
        self.api_calls_veo += 1

    @classmethod
    def for_today(cls, video_limit: int = 3) -> "DailyQuota":
        """Create a quota record for today."""
        return cls(
            quota_date=date.today(),
            videos_limit=video_limit,
        )
