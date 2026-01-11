"""
Beautelligence Video Pipeline - Generation Model

Stores video generation records with prompts and output references.
"""

import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base
from src.models.keyword import GUID

from src.models.database import Base


GenerationStatus = Literal["pending", "generating", "complete", "failed"]


class Generation(Base):
    """Video generation records."""

    __tablename__ = "generations"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    keyword_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("keywords.id"), nullable=True
    )

    # Prompt data
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    negative_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Veo 3 configuration
    veo_model: Mapped[str] = mapped_column(String(50), default="veo-3.0-fast-generate-001")
    aspect_ratio: Mapped[str] = mapped_column(String(10), default="9:16")
    resolution: Mapped[str] = mapped_column(String(10), default="720p")
    duration_seconds: Mapped[int] = mapped_column(Integer, default=8)

    # Output
    video_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Status tracking
    status: Mapped[str] = mapped_column(String(20), default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    keyword = relationship("Keyword", backref="generations")

    def __repr__(self) -> str:
        return f"<Generation(id='{self.id}', status='{self.status}')>"

    def mark_started(self) -> None:
        """Mark generation as started."""
        self.status = "generating"
        self.started_at = datetime.now()

    def mark_complete(self, video_path: str, file_size: int | None = None) -> None:
        """Mark generation as complete with video output."""
        self.status = "complete"
        self.video_file_path = video_path
        self.file_size_bytes = file_size
        self.completed_at = datetime.now()

    def mark_failed(self, error: str) -> None:
        """Mark generation as failed with error message."""
        self.status = "failed"
        self.error_message = error
        self.retry_count += 1
