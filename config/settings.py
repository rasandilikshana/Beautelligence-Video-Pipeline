"""
Beautelligence Video Pipeline - Configuration Settings

Uses Pydantic Settings for type-safe configuration with .env file support.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = True
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Database (SQLite for development, PostgreSQL for production)
    database_url: str = Field(
        default="sqlite+aiosqlite:///data/pipeline.db",
        description="Database connection URL (SQLite or PostgreSQL)",
    )
    database_pool_size: int = Field(default=5, ge=1, le=20)

    # Google AI / Gemini
    google_api_key: str = Field(
        default="",
        description="Google API key for Gemini and Veo 3",
    )
    gemini_model: str = "gemini-2.0-flash"

    # Veo 3 Video Generation
    veo_model: str = "veo-3.0-fast-generate-001"
    veo_resolution: str = "720p"
    veo_aspect_ratio: str = "9:16"
    veo_duration_seconds: int = Field(default=8, ge=5, le=60)

    # TikTok Scraping
    tiktok_cc_base_url: str = "https://ads.tiktok.com/business/creativecenter"
    tiktok_region: str = "US"
    tiktok_scrape_interval_hours: int = 6

    # Rate Limits
    daily_video_limit: int = Field(default=3, ge=1, le=100)
    gemini_rpm_limit: int = Field(default=60, ge=1)
    veo_daily_limit: int = Field(default=10, ge=1)

    # Keyword Settings
    keyword_expiry_days: int = Field(default=30, ge=1)
    min_trending_score: int = Field(default=70, ge=0, le=100)

    # File Storage
    video_output_dir: Path = Path("./data/videos")
    prompt_log_dir: Path = Path("./data/prompts")
    log_dir: Path = Path("./data/logs")

    # Optional Redis
    redis_url: str | None = None

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        for directory in [self.video_output_dir, self.prompt_log_dir, self.log_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"

    @property
    def has_api_key(self) -> bool:
        """Check if Google API key is configured."""
        return bool(self.google_api_key and self.google_api_key != "your_gemini_api_key_here")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience alias
settings = get_settings()
