"""
Beautelligence Video Pipeline - Generation Repository

Database operations for Generations table.
"""

import uuid
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.generation import Generation


class GenerationRepository:
    """Repository for Generation database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, generation: Generation) -> Generation:
        """Create a new generation record."""
        self.session.add(generation)
        await self.session.flush()
        return generation

    async def get_by_id(self, generation_id: uuid.UUID) -> Generation | None:
        """Get generation by ID."""
        result = await self.session.execute(
            select(Generation).where(Generation.id == generation_id)
        )
        return result.scalar_one_or_none()

    async def get_pending(self, limit: int = 10) -> list[Generation]:
        """Get pending generations."""
        result = await self.session.execute(
            select(Generation)
            .where(Generation.status == "pending")
            .order_by(Generation.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_recent(
        self, days: int = 7, limit: int = 50
    ) -> list[Generation]:
        """Get recent generations."""
        since = datetime.now() - timedelta(days=days)
        result = await self.session.execute(
            select(Generation)
            .where(Generation.created_at >= since)
            .order_by(Generation.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_status(self, status: str) -> int:
        """Count generations by status."""
        result = await self.session.execute(
            select(func.count(Generation.id)).where(Generation.status == status)
        )
        return result.scalar_one()

    async def count_today(self) -> int:
        """Count generations created today."""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.session.execute(
            select(func.count(Generation.id)).where(
                Generation.created_at >= today_start
            )
        )
        return result.scalar_one()

    async def count_completed_today(self) -> int:
        """Count completed generations today."""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.session.execute(
            select(func.count(Generation.id)).where(
                Generation.status == "complete",
                Generation.completed_at >= today_start,
            )
        )
        return result.scalar_one()

    async def update_status(
        self,
        generation_id: uuid.UUID,
        status: str,
        error_message: str | None = None,
        video_path: str | None = None,
        file_size: int | None = None,
    ) -> Generation | None:
        """Update generation status."""
        generation = await self.get_by_id(generation_id)
        if generation:
            generation.status = status
            if status == "generating":
                generation.started_at = datetime.now()
            elif status == "complete":
                generation.completed_at = datetime.now()
                if video_path:
                    generation.video_file_path = video_path
                if file_size:
                    generation.file_size_bytes = file_size
            elif status == "failed" and error_message:
                generation.error_message = error_message
                generation.retry_count += 1
            await self.session.flush()
        return generation

    async def get_stats(self) -> dict:
        """Get generation statistics."""
        total = await self.session.execute(
            select(func.count(Generation.id))
        )
        complete = await self.count_by_status("complete")
        failed = await self.count_by_status("failed")
        pending = await self.count_by_status("pending")
        today = await self.count_completed_today()

        return {
            "total": total.scalar_one(),
            "complete": complete,
            "failed": failed,
            "pending": pending,
            "completed_today": today,
        }
