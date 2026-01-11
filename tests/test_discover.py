"""
Tests for the Discover service (TikTok trending scraper).
"""

import pytest
from src.services.discover.tiktok_creative_center import (
    TikTokCreativeCenterScraper,
    TrendingKeyword,
    is_brand_safe,
    matches_brand,
)
from src.services.discover.trend_aggregator import TrendAggregator


class TestTikTokScraper:
    """Tests for TikTokCreativeCenterScraper."""

    @pytest.mark.asyncio
    async def test_mock_scraping(self):
        """Test that mock scraping returns valid data."""
        scraper = TikTokCreativeCenterScraper()
        trends = await scraper.scrape_trending(limit=5, mock=True)

        assert len(trends) == 5
        assert all(isinstance(t, TrendingKeyword) for t in trends)
        assert all(t.keyword for t in trends)
        assert all(t.trending_score > 0 for t in trends)

    @pytest.mark.asyncio
    async def test_mock_data_has_required_fields(self):
        """Test that mock data includes all required fields."""
        scraper = TikTokCreativeCenterScraper()
        trends = await scraper.scrape_trending(limit=3, mock=True)

        for trend in trends:
            data = trend.to_dict()
            assert "keyword" in data
            assert "trending_score" in data
            assert "metadata" in data


class TestBrandSafety:
    """Tests for brand safety filtering."""

    def test_safe_keywords(self):
        """Test that safe keywords pass the filter."""
        safe_keywords = ["strawberry", "cute cat", "happy dance", "rainbow", "food"]
        for keyword in safe_keywords:
            assert is_brand_safe(keyword), f"{keyword} should be brand safe"

    def test_unsafe_keywords(self):
        """Test that unsafe keywords are blocked."""
        unsafe_keywords = ["violence", "fight club", "adult content", "political protest"]
        for keyword in unsafe_keywords:
            assert not is_brand_safe(keyword), f"{keyword} should NOT be brand safe"


class TestTrendAggregator:
    """Tests for TrendAggregator."""

    @pytest.mark.asyncio
    async def test_discover_trends_mock(self):
        """Test trend discovery with mock data."""
        aggregator = TrendAggregator(min_score=50)
        trends = await aggregator.discover_trends(limit=5, mock=True)

        assert len(trends) > 0
        assert all(t.trending_score >= 50 for t in trends)

    @pytest.mark.asyncio
    async def test_deduplication(self):
        """Test that existing keywords are filtered out."""
        aggregator = TrendAggregator()
        existing = {"strawberry", "avocado"}  # Already used

        trends = await aggregator.discover_trends(
            limit=10,
            mock=True,
            existing_keywords=existing,
        )

        # None of the returned trends should match existing keywords
        for trend in trends:
            assert trend.normalized not in existing

    @pytest.mark.asyncio
    async def test_get_best_keyword(self):
        """Test getting the single best keyword."""
        aggregator = TrendAggregator()
        best = await aggregator.get_best_keyword(mock=True)

        assert best is not None
        assert best.keyword
        assert best.trending_score > 0
