"""
Beautelligence Video Pipeline - Trend Aggregator

Aggregates and filters trends from multiple sources.
"""

from dataclasses import dataclass
from datetime import datetime

from config.logging import get_logger
from config.settings import settings
from src.models.keyword import Keyword
from src.services.discover.tiktok_creative_center import (
    TikTokCreativeCenterScraper,
    TrendingKeyword,
    is_brand_safe,
)

logger = get_logger(__name__)


@dataclass
class AggregatedTrend:
    """A trend aggregated from multiple sources."""

    keyword: str
    normalized: str
    trending_score: int
    sources: list[str]
    category: str | None
    discovered_at: datetime
    metadata: dict

    def to_keyword_model(self, expiry_days: int = 30) -> Keyword:
        """Convert to Keyword database model."""
        return Keyword.create(
            keyword=self.keyword,
            source=",".join(self.sources),
            trending_score=self.trending_score,
            expiry_days=expiry_days,
            metadata={
                "category": self.category,
                "sources": self.sources,
                **self.metadata,
            },
        )


class TrendAggregator:
    """
    Aggregates trends from multiple sources and applies filtering.

    Currently supports:
    - TikTok Creative Center
    - (Future) Google Trends
    """

    def __init__(
        self,
        min_score: int | None = None,
        expiry_days: int | None = None,
    ):
        self.min_score = min_score or settings.min_trending_score
        self.expiry_days = expiry_days or settings.keyword_expiry_days
        self.tiktok_scraper = TikTokCreativeCenterScraper()

    async def discover_trends(
        self,
        limit: int = 20,
        mock: bool = False,
        existing_keywords: set[str] | None = None,
    ) -> list[AggregatedTrend]:
        """
        Discover trending topics from all sources.

        Args:
            limit: Maximum number of trends to return
            mock: Use mock data instead of real scraping
            existing_keywords: Set of already-used keyword normalized forms

        Returns:
            List of aggregated, filtered trends
        """
        existing = existing_keywords or set()
        all_trends: list[TrendingKeyword] = []

        # Scrape TikTok Creative Center
        logger.info("discovering_trends", source="tiktok_cc", mock=mock)
        tiktok_trends = await self.tiktok_scraper.scrape_trending(
            limit=limit * 2,  # Get more to account for filtering
            mock=mock,
        )
        all_trends.extend(tiktok_trends)

        # TODO: Add Google Trends as fallback source

        # Aggregate and filter
        aggregated = self._aggregate_trends(all_trends)
        filtered = self._filter_trends(aggregated, existing)

        # Sort by score and limit
        sorted_trends = sorted(
            filtered,
            key=lambda t: t.trending_score,
            reverse=True,
        )[:limit]

        logger.info(
            "trends_discovered",
            total_raw=len(all_trends),
            after_filter=len(filtered),
            returned=len(sorted_trends),
        )

        return sorted_trends

    def _aggregate_trends(
        self, trends: list[TrendingKeyword]
    ) -> list[AggregatedTrend]:
        """Aggregate trends by normalized keyword."""
        keyword_map: dict[str, AggregatedTrend] = {}

        for trend in trends:
            normalized = Keyword.normalize(trend.keyword)

            if normalized in keyword_map:
                # Update existing entry
                existing = keyword_map[normalized]
                existing.trending_score = max(
                    existing.trending_score, trend.trending_score
                )
                if "tiktok_cc" not in existing.sources:
                    existing.sources.append("tiktok_cc")
            else:
                # Create new entry
                keyword_map[normalized] = AggregatedTrend(
                    keyword=trend.keyword,
                    normalized=normalized,
                    trending_score=trend.trending_score,
                    sources=["tiktok_cc"],
                    category=trend.category,
                    discovered_at=datetime.now(),
                    metadata=trend.metadata or {},
                )

        return list(keyword_map.values())

    def _filter_trends(
        self,
        trends: list[AggregatedTrend],
        existing_keywords: set[str],
    ) -> list[AggregatedTrend]:
        """Apply filters to trends."""
        filtered = []

        for trend in trends:
            # Check minimum score
            if trend.trending_score < self.min_score:
                logger.debug(
                    "trend_filtered",
                    keyword=trend.keyword,
                    reason="low_score",
                    score=trend.trending_score,
                )
                continue

            # Check for duplicates
            if trend.normalized in existing_keywords:
                logger.debug(
                    "trend_filtered",
                    keyword=trend.keyword,
                    reason="duplicate",
                )
                continue

            # Check brand safety
            if not is_brand_safe(trend.keyword):
                logger.debug(
                    "trend_filtered",
                    keyword=trend.keyword,
                    reason="not_brand_safe",
                )
                continue

            filtered.append(trend)

        return filtered

    async def get_best_keyword(
        self,
        existing_keywords: set[str] | None = None,
        mock: bool = False,
    ) -> AggregatedTrend | None:
        """
        Get the single best trending keyword for video generation.

        Args:
            existing_keywords: Keywords to exclude (already used)
            mock: Use mock data

        Returns:
            Best trending keyword or None
        """
        trends = await self.discover_trends(
            limit=1,
            mock=mock,
            existing_keywords=existing_keywords,
        )
        return trends[0] if trends else None
