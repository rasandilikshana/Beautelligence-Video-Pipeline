"""
Beautelligence Video Pipeline - TikTok Creative Center Scraper

Discovers trending hashtags from TikTok Creative Center.
"""

import asyncio
import re
from dataclasses import dataclass
from typing import Any

from config.logging import get_logger
from config.settings import settings

logger = get_logger(__name__)


@dataclass
class TrendingKeyword:
    """Represents a trending keyword from TikTok."""

    keyword: str
    trending_score: int
    posts_count: str | None = None
    growth_rate: str | None = None
    category: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "keyword": self.keyword,
            "trending_score": self.trending_score,
            "posts_count": self.posts_count,
            "growth_rate": self.growth_rate,
            "category": self.category,
            "metadata": self.metadata or {},
        }


class TikTokCreativeCenterScraper:
    """
    Scrapes trending hashtags from TikTok Creative Center.

    Uses Playwright for headless browser automation.
    """

    def __init__(
        self,
        region: str | None = None,
        headless: bool = True,
    ):
        self.region = region or settings.tiktok_region
        self.headless = headless
        self.base_url = settings.tiktok_cc_base_url
        self.trending_url = f"{self.base_url}/inspiration/popular/hashtag/pc/en"

    async def scrape_trending(
        self,
        limit: int = 20,
        mock: bool = False,
    ) -> list[TrendingKeyword]:
        """
        Scrape trending hashtags from TikTok Creative Center.

        Args:
            limit: Maximum number of trends to return
            mock: If True, return mock data instead of scraping

        Returns:
            List of trending keywords
        """
        if mock:
            return self._get_mock_trends(limit)

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                )
                page = await context.new_page()

                logger.info("scraping_started", url=self.trending_url)

                await page.goto(self.trending_url, wait_until="networkidle")

                # Wait for content to load
                await asyncio.sleep(3)

                # Extract trending hashtags
                trends = await self._extract_trends(page, limit)

                await browser.close()

                logger.info("scraping_completed", trends_found=len(trends))
                return trends

        except ImportError:
            logger.warning("playwright_not_installed", message="Using mock data")
            return self._get_mock_trends(limit)
        except Exception as e:
            logger.error("scraping_failed", error=str(e))
            # Fall back to mock data
            return self._get_mock_trends(limit)

    async def _extract_trends(self, page: Any, limit: int) -> list[TrendingKeyword]:
        """Extract trending data from the page."""
        trends = []

        try:
            # Try to find hashtag elements (structure may vary)
            hashtag_elements = await page.query_selector_all(
                "[class*='hashtag'], [class*='trend'], table tr"
            )

            for i, element in enumerate(hashtag_elements[:limit]):
                try:
                    text = await element.text_content()
                    if text:
                        # Extract hashtag from text
                        keyword = self._extract_keyword(text)
                        if keyword:
                            trends.append(
                                TrendingKeyword(
                                    keyword=keyword,
                                    trending_score=max(100 - (i * 3), 50),
                                    metadata={"rank": i + 1, "region": self.region},
                                )
                            )
                except Exception:
                    continue

        except Exception as e:
            logger.warning("trend_extraction_warning", error=str(e))

        return trends

    def _extract_keyword(self, text: str) -> str | None:
        """Extract clean keyword from text."""
        # Remove hashtag symbol and clean up
        clean = text.strip()
        clean = re.sub(r"^#", "", clean)
        clean = re.sub(r"\s+", " ", clean)
        clean = clean.split("\n")[0].strip()

        # Skip if too short or too long
        if len(clean) < 2 or len(clean) > 50:
            return None

        return clean

    def _get_mock_trends(self, limit: int) -> list[TrendingKeyword]:
        """Return mock trending data for testing."""
        mock_trends = [
            TrendingKeyword(
                keyword="strawberry",
                trending_score=95,
                posts_count="2.5M",
                category="food",
                metadata={"mock": True},
            ),
            TrendingKeyword(
                keyword="avocado",
                trending_score=92,
                posts_count="1.8M",
                category="food",
                metadata={"mock": True},
            ),
            TrendingKeyword(
                keyword="mango",
                trending_score=88,
                posts_count="1.2M",
                category="food",
                metadata={"mock": True},
            ),
            TrendingKeyword(
                keyword="papaya",
                trending_score=85,
                posts_count="900K",
                category="food",
                metadata={"mock": True},
            ),
            TrendingKeyword(
                keyword="kiwi",
                trending_score=82,
                posts_count="750K",
                category="food",
                metadata={"mock": True},
            ),
            TrendingKeyword(
                keyword="blueberry",
                trending_score=80,
                posts_count="600K",
                category="food",
                metadata={"mock": True},
            ),
            TrendingKeyword(
                keyword="watermelon",
                trending_score=78,
                posts_count="500K",
                category="food",
                metadata={"mock": True},
            ),
            TrendingKeyword(
                keyword="pineapple",
                trending_score=75,
                posts_count="450K",
                category="food",
                metadata={"mock": True},
            ),
            TrendingKeyword(
                keyword="coconut",
                trending_score=72,
                posts_count="400K",
                category="food",
                metadata={"mock": True},
            ),
            TrendingKeyword(
                keyword="peach",
                trending_score=70,
                posts_count="350K",
                category="food",
                metadata={"mock": True},
            ),
        ]
        return mock_trends[:limit]


# Filter lists for brand-safe content
BLOCKED_KEYWORDS = {
    "violence", "fight", "war", "death", "kill", "blood",
    "adult", "nsfw", "explicit", "sexy", "hot",
    "political", "election", "trump", "biden", "protest",
    "controversial", "scandal", "drama",
}

PREFERRED_CATEGORIES = {"food", "animals", "cute", "satisfying", "wholesome", "art", "nature"}


def is_brand_safe(keyword: str) -> bool:
    """Check if a keyword is safe for the Beautelligence brand."""
    lower = keyword.lower()
    return not any(blocked in lower for blocked in BLOCKED_KEYWORDS)


def matches_brand(keyword: str, category: str | None = None) -> bool:
    """Check if a keyword matches the Beautelligence brand."""
    if not is_brand_safe(keyword):
        return False
    if category and category.lower() in PREFERRED_CATEGORIES:
        return True
    # Default to True for uncategorized keywords that pass safety check
    return True
