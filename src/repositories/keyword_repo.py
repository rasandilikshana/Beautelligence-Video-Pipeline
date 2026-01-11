"""
Beautelligence Video Pipeline - Keyword Repository

Database operations for Keywords table.
"""

import uuid
from datetime import datetime, timedelta

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.keyword import Keyword


class KeywordRepository:
    """Repository for Keyword database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, keyword: Keyword) -> Keyword:
        """Create a new keyword record."""
        self.session.add(keyword)
        await self.session.flush()
        return keyword

    async def bulk_create(self, keywords: list[Keyword]) -> list[Keyword]:
        """Create multiple keyword records."""
        self.session.add_all(keywords)
        await self.session.flush()
        return keywords

    async def get_by_id(self, keyword_id: uuid.UUID) -> Keyword | None:
        """Get keyword by ID."""
        result = await self.session.execute(
            select(Keyword).where(Keyword.id == keyword_id)
        )
        return result.scalar_one_or_none()

    async def find_by_normalized(
        self, normalized: str, since: datetime | None = None
    ) -> Keyword | None:
        """Find keyword by normalized form, optionally within a time window."""
        query = select(Keyword).where(Keyword.keyword_normalized == normalized)

        if since:
            query = query.where(Keyword.discovered_at >= since)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def is_duplicate(self, keyword: str, days: int = 30) -> bool:
        """Check if keyword (normalized) has been used recently."""
        normalized = Keyword.normalize(keyword)
        since = datetime.now() - timedelta(days=days)
        existing = await self.find_by_normalized(normalized, since=since)
        return existing is not None

    async def get_pending_keywords(self, limit: int = 10) -> list[Keyword]:
        """Get pending keywords ordered by trending score."""
        result = await self.session.execute(
            select(Keyword)
            .where(Keyword.status == "pending")
            .order_by(Keyword.trending_score.desc().nullslast())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_unused_keyword(self, expiry_days: int = 30) -> Keyword | None:
        """Get the highest-scoring unused keyword that isn't a duplicate."""
        since = datetime.now() - timedelta(days=expiry_days)

        result = await self.session.execute(
            select(Keyword)
            .where(
                and_(
                    Keyword.status == "pending",
                    Keyword.discovered_at >= since,
                )
            )
            .order_by(Keyword.trending_score.desc().nullslast())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        keyword_id: uuid.UUID,
        status: str,
        skip_reason: str | None = None,
    ) -> Keyword | None:
        """Update keyword status."""
        keyword = await self.get_by_id(keyword_id)
        if keyword:
            keyword.status = status
            if skip_reason:
                keyword.skip_reason = skip_reason
            await self.session.flush()
        return keyword

    async def mark_as_used(self, keyword_id: uuid.UUID) -> Keyword | None:
        """Mark keyword as used for video generation."""
        return await self.update_status(keyword_id, "used")

    async def mark_as_skipped(
        self, keyword_id: uuid.UUID, reason: str
    ) -> Keyword | None:
        """Mark keyword as skipped with reason."""
        return await self.update_status(keyword_id, "skipped", skip_reason=reason)

    async def count_by_status(self, status: str) -> int:
        """Count keywords by status."""
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count(Keyword.id)).where(Keyword.status == status)
        )
        return result.scalar_one()

    async def get_recent_keywords(
        self, days: int = 7, limit: int = 50
    ) -> list[Keyword]:
        """Get recently discovered keywords."""
        since = datetime.now() - timedelta(days=days)
        result = await self.session.execute(
            select(Keyword)
            .where(Keyword.discovered_at >= since)
            .order_by(Keyword.discovered_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
