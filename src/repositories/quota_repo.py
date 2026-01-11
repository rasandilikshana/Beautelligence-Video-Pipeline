"""
Beautelligence Video Pipeline - Quota Repository

Database operations for daily quota management.
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit import DailyQuota, AuditLog


class QuotaRepository:
    """Repository for quota and audit log operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_today(self, video_limit: int = 3) -> DailyQuota:
        """Get or create today's quota record."""
        today = date.today()

        result = await self.session.execute(
            select(DailyQuota).where(DailyQuota.quota_date == today)
        )
        quota = result.scalar_one_or_none()

        if not quota:
            quota = DailyQuota.for_today(video_limit=video_limit)
            self.session.add(quota)
            await self.session.flush()

        return quota

    async def can_generate_video(self, video_limit: int = 3) -> bool:
        """Check if daily video quota is not exhausted."""
        quota = await self.get_or_create_today(video_limit)
        return quota.can_generate

    async def get_remaining_videos(self, video_limit: int = 3) -> int:
        """Get remaining video quota for today."""
        quota = await self.get_or_create_today(video_limit)
        return quota.remaining_videos

    async def increment_video_count(self, video_limit: int = 3) -> DailyQuota:
        """Increment today's video count."""
        quota = await self.get_or_create_today(video_limit)
        quota.increment_videos()
        await self.session.flush()
        return quota

    async def increment_gemini_calls(self, video_limit: int = 3) -> DailyQuota:
        """Increment today's Gemini API call count."""
        quota = await self.get_or_create_today(video_limit)
        quota.increment_gemini_calls()
        await self.session.flush()
        return quota

    async def increment_veo_calls(self, video_limit: int = 3) -> DailyQuota:
        """Increment today's Veo API call count."""
        quota = await self.get_or_create_today(video_limit)
        quota.increment_veo_calls()
        await self.session.flush()
        return quota

    async def log_operation(
        self,
        operation: str,
        action: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        details: dict | None = None,
        error_details: dict | None = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        import uuid as uuid_module

        entity_uuid = None
        if entity_id:
            try:
                entity_uuid = uuid_module.UUID(entity_id)
            except ValueError:
                pass

        log = AuditLog.log(
            operation=operation,
            action=action,
            entity_type=entity_type,
            entity_id=entity_uuid,
            details=details,
            error_details=error_details,
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def get_today_stats(self, video_limit: int = 3) -> dict:
        """Get today's quota statistics."""
        quota = await self.get_or_create_today(video_limit)
        return {
            "date": str(quota.quota_date),
            "videos_generated": quota.videos_generated,
            "videos_limit": quota.videos_limit,
            "videos_remaining": quota.remaining_videos,
            "api_calls_gemini": quota.api_calls_gemini,
            "api_calls_veo": quota.api_calls_veo,
            "can_generate": quota.can_generate,
        }
