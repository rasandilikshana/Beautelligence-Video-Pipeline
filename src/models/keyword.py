"""
Beautelligence Video Pipeline - Keyword Model

Stores trending keywords discovered from TikTok Creative Center and other sources.
"""

import uuid
from datetime import datetime, timedelta
from typing import Literal

from sqlalchemy import DateTime, Index, Integer, String, Text, func, JSON
from sqlalchemy.types import CHAR, TypeDecorator
import uuid as uuid_module


class GUID(TypeDecorator):
    """Platform-independent GUID type. Uses CHAR(32) for SQLite, UUID for PostgreSQL."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            return value.hex if isinstance(value, uuid_module.UUID) else value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            return uuid_module.UUID(value) if isinstance(value, str) else value
from sqlalchemy.orm import Mapped, mapped_column

from src.models.database import Base


KeywordStatus = Literal["pending", "processing", "used", "skipped", "expired"]


class Keyword(Base):
    """Trending keywords discovered from various sources."""

    __tablename__ = "keywords"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    keyword_normalized: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # 'tiktok_cc', 'google_trends'
    trending_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    skip_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_keywords_status", "status"),
        Index("idx_keywords_discovered", discovered_at.desc()),
    )

    def __repr__(self) -> str:
        return f"<Keyword(keyword='{self.keyword}', status='{self.status}')>"

    @staticmethod
    def normalize(keyword: str) -> str:
        """Normalize a keyword for deduplication."""
        return keyword.lower().strip().replace("-", " ").replace("_", " ")

    @classmethod
    def create(
        cls,
        keyword: str,
        source: str,
        trending_score: int | None = None,
        expiry_days: int = 30,
        metadata: dict | None = None,
    ) -> "Keyword":
        """Create a new keyword with automatic normalization."""
        now = datetime.now()
        return cls(
            keyword=keyword,
            keyword_normalized=cls.normalize(keyword),
            source=source,
            trending_score=trending_score,
            discovered_at=now,
            expires_at=now + timedelta(days=expiry_days),
            metadata_=metadata,
        )
