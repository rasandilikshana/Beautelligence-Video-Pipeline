"""
Beautelligence Video Pipeline - Main Orchestrator

Coordinates all pipeline stages: discover → prompt → generate → save.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from config.logging import get_logger, setup_logging
from config.settings import settings
from src.models.database import get_session, init_db
from src.models.keyword import Keyword
from src.models.generation import Generation
from src.repositories.keyword_repo import KeywordRepository
from src.repositories.generation_repo import GenerationRepository
from src.repositories.quota_repo import QuotaRepository
from src.services.discover.trend_aggregator import TrendAggregator
from src.services.prompt.gemini_prompt_generator import GeminiPromptGenerator
from src.services.video.veo_client import VeoClient
from src.utils.file_manager import FileManager

logger = get_logger(__name__)


@dataclass
class PipelineResult:
    """Result of a pipeline run."""

    success: bool
    videos_generated: int
    videos_failed: int
    errors: list[str] = field(default_factory=list)
    details: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "videos_generated": self.videos_generated,
            "videos_failed": self.videos_failed,
            "errors": self.errors,
            "details": self.details,
        }


class VideoPipeline:
    """
    Main pipeline orchestrator.

    Coordinates the full workflow:
    1. Check daily quota
    2. Discover trending keywords
    3. Filter and deduplicate
    4. Generate prompts via Gemini
    5. Create videos via Veo 3
    6. Save results to database
    """

    def __init__(self, mock: bool = False):
        self.mock = mock
        self.file_manager = FileManager()
        self.trend_aggregator = TrendAggregator()
        self.prompt_generator = GeminiPromptGenerator()
        self.veo_client = VeoClient(file_manager=self.file_manager)

    async def initialize(self) -> None:
        """Initialize the pipeline (create directories, init DB)."""
        self.file_manager.ensure_directories()
        await init_db()
        logger.info("pipeline_initialized")

    async def run(self, video_count: int | None = None) -> PipelineResult:
        """
        Run the complete pipeline.

        Args:
            video_count: Number of videos to generate (default: daily limit)

        Returns:
            PipelineResult with summary of the run
        """
        start_time = datetime.now()
        result = PipelineResult(
            success=True,
            videos_generated=0,
            videos_failed=0,
        )

        try:
            async with get_session() as session:
                quota_repo = QuotaRepository(session)
                keyword_repo = KeywordRepository(session)
                generation_repo = GenerationRepository(session)

                # 1. Check quota
                remaining = await quota_repo.get_remaining_videos(
                    settings.daily_video_limit
                )
                if remaining == 0:
                    logger.warning("daily_quota_exhausted")
                    result.errors.append("Daily video quota exhausted")
                    result.success = False
                    return result

                # Determine how many videos to generate
                target_count = min(
                    video_count or settings.daily_video_limit,
                    remaining,
                )

                logger.info(
                    "pipeline_started",
                    target_videos=target_count,
                    remaining_quota=remaining,
                    mock=self.mock,
                )

                # 2. Get existing keywords for deduplication
                recent_keywords = await keyword_repo.get_recent_keywords(
                    days=settings.keyword_expiry_days
                )
                existing_normalized = {k.keyword_normalized for k in recent_keywords}

                # 3. Discover trending keywords
                trends = await self.trend_aggregator.discover_trends(
                    limit=target_count * 3,  # Get extra for filtering
                    mock=self.mock,
                    existing_keywords=existing_normalized,
                )

                if not trends:
                    logger.warning("no_trends_found")
                    result.errors.append("No new trending keywords found")
                    result.success = False
                    return result

                logger.info("trends_discovered", count=len(trends))

                # 4. Process each trend
                for i, trend in enumerate(trends[:target_count]):
                    try:
                        video_result = await self._process_keyword(
                            session=session,
                            keyword_repo=keyword_repo,
                            generation_repo=generation_repo,
                            quota_repo=quota_repo,
                            keyword=trend.keyword,
                            trending_score=trend.trending_score,
                            metadata=trend.metadata,
                        )

                        if video_result["success"]:
                            result.videos_generated += 1
                            await quota_repo.increment_video_count(
                                settings.daily_video_limit
                            )
                        else:
                            result.videos_failed += 1
                            result.errors.append(
                                f"Failed: {trend.keyword} - {video_result.get('error', 'Unknown')}"
                            )

                        result.details.append(video_result)

                    except Exception as e:
                        logger.error(
                            "keyword_processing_failed",
                            keyword=trend.keyword,
                            error=str(e),
                        )
                        result.videos_failed += 1
                        result.errors.append(f"Error processing {trend.keyword}: {e}")

        except Exception as e:
            logger.error("pipeline_failed", error=str(e))
            result.success = False
            result.errors.append(f"Pipeline error: {e}")

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            "pipeline_completed",
            videos_generated=result.videos_generated,
            videos_failed=result.videos_failed,
            duration_seconds=duration,
        )

        return result

    async def _process_keyword(
        self,
        session: Any,
        keyword_repo: KeywordRepository,
        generation_repo: GenerationRepository,
        quota_repo: QuotaRepository,
        keyword: str,
        trending_score: int,
        metadata: dict,
    ) -> dict[str, Any]:
        """Process a single keyword through the pipeline."""
        logger.info("processing_keyword", keyword=keyword)

        # Create keyword record
        keyword_model = Keyword.create(
            keyword=keyword,
            source="tiktok_cc",
            trending_score=trending_score,
            expiry_days=settings.keyword_expiry_days,
            metadata=metadata,
        )
        await keyword_repo.create(keyword_model)

        try:
            # Generate prompt
            logger.info("generating_prompt", keyword=keyword)
            prompt_result = await self.prompt_generator.generate_prompt(
                keyword=keyword,
                mock=self.mock,
            )

            # Save prompt log
            prompt_log_path = self.file_manager.save_prompt_log(
                keyword=keyword,
                prompt=prompt_result.prompt,
                negative_prompt=prompt_result.negative_prompt,
                metadata=prompt_result.metadata,
            )

            # Create generation record
            generation = Generation(
                keyword_id=keyword_model.id,
                prompt=prompt_result.prompt,
                negative_prompt=prompt_result.negative_prompt,
                prompt_metadata=prompt_result.metadata,
                veo_model=settings.veo_model,
                aspect_ratio=settings.veo_aspect_ratio,
                resolution=settings.veo_resolution,
                duration_seconds=settings.veo_duration_seconds,
            )
            await generation_repo.create(generation)

            # Generate video
            logger.info("generating_video", keyword=keyword)
            generation.mark_started()

            video_result = await self.veo_client.generate_video(
                prompt=prompt_result.prompt,
                keyword=keyword,
                negative_prompt=prompt_result.negative_prompt,
                mock=self.mock,
            )

            if video_result.success:
                generation.mark_complete(
                    video_path=str(video_result.video_path),
                    file_size=video_result.file_size,
                )
                await keyword_repo.mark_as_used(keyword_model.id)

                # Log audit
                await quota_repo.log_operation(
                    operation="video_generation",
                    action="complete",
                    entity_type="generation",
                    entity_id=str(generation.id),
                    details={
                        "keyword": keyword,
                        "video_path": str(video_result.video_path),
                        "file_size": video_result.file_size,
                    },
                )

                return {
                    "success": True,
                    "keyword": keyword,
                    "video_path": str(video_result.video_path),
                    "file_size": video_result.file_size,
                    "generation_time": video_result.generation_time_seconds,
                }
            else:
                generation.mark_failed(video_result.error_message or "Unknown error")
                await keyword_repo.mark_as_skipped(
                    keyword_model.id,
                    reason=video_result.error_message or "Generation failed",
                )

                return {
                    "success": False,
                    "keyword": keyword,
                    "error": video_result.error_message,
                }

        except Exception as e:
            logger.error("keyword_processing_error", keyword=keyword, error=str(e))
            await keyword_repo.mark_as_skipped(keyword_model.id, reason=str(e))
            return {
                "success": False,
                "keyword": keyword,
                "error": str(e),
            }

    async def run_single(
        self,
        keyword: str,
        force: bool = False,
    ) -> dict[str, Any]:
        """
        Generate a video for a single specific keyword.

        Args:
            keyword: The keyword to generate for
            force: If True, skip deduplication check

        Returns:
            Dictionary with result details
        """
        async with get_session() as session:
            keyword_repo = KeywordRepository(session)
            generation_repo = GenerationRepository(session)
            quota_repo = QuotaRepository(session)

            # Check for duplicates (unless forced)
            if not force:
                is_dup = await keyword_repo.is_duplicate(
                    keyword, days=settings.keyword_expiry_days
                )
                if is_dup:
                    return {
                        "success": False,
                        "keyword": keyword,
                        "error": "Keyword already used recently (use --force to override)",
                    }

            return await self._process_keyword(
                session=session,
                keyword_repo=keyword_repo,
                generation_repo=generation_repo,
                quota_repo=quota_repo,
                keyword=keyword,
                trending_score=100,
                metadata={"source": "manual", "forced": force},
            )

    async def get_status(self) -> dict[str, Any]:
        """Get current pipeline status."""
        async with get_session() as session:
            quota_repo = QuotaRepository(session)
            generation_repo = GenerationRepository(session)
            keyword_repo = KeywordRepository(session)

            quota_stats = await quota_repo.get_today_stats(settings.daily_video_limit)
            gen_stats = await generation_repo.get_stats()
            pending_keywords = await keyword_repo.count_by_status("pending")

            return {
                "quota": quota_stats,
                "generations": gen_stats,
                "pending_keywords": pending_keywords,
                "config": {
                    "daily_limit": settings.daily_video_limit,
                    "veo_model": settings.veo_model,
                    "gemini_model": settings.gemini_model,
                    "has_api_key": settings.has_api_key,
                },
            }
