from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, UUID4

class GenerationRequest(BaseModel):
    """Request model for triggering a video generation."""
    prompt: str
    aspect_ratio: str = "9:16"
    duration_seconds: int = 8
    force: bool = False
    mock: bool = False

class KeywordResponse(BaseModel):
    """Response model for a keyword/task."""
    id: UUID4
    keyword: str
    status: str
    source: str
    trending_score: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class GenerationResponse(BaseModel):
    """Response model for a completed generation."""
    id: UUID4
    status: str
    prompt: str
    video_file_path: Optional[str]
    file_size_bytes: Optional[int]
    created_at: datetime
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class QuotaStatus(BaseModel):
    """Response model for daily quota status."""
    videos_generated: int
    videos_limit: int
    videos_remaining: int
    can_generate: bool

class PipelineStatus(BaseModel):
    """Global pipeline status response."""
    quota: QuotaStatus
    queue_size: int
    recent_generations: List[GenerationResponse]


# =============================================================================
# FRUIT STORY GENERATION SCHEMAS
# =============================================================================

class FruitCharacterInfo(BaseModel):
    """Information about a fruit character."""
    key: str
    name: str
    archetype: str
    personality: str
    core_message: str
    color_palette: str
    health_benefits: List[str]


class StoryEpisodeResponse(BaseModel):
    """Response model for a single story episode."""
    episode_number: int
    title: str
    scene_description: str
    dialogue: str
    emotion: str
    action: str
    health_message: str
    status: str = "pending"  # pending, generating, complete, failed
    video_url: Optional[str] = None
    video_path: Optional[str] = None


class FruitStoryRequest(BaseModel):
    """Request model for generating a fruit character story."""
    fruit_type: str  # e.g., "apple", "banana"
    custom_message: Optional[str] = None  # Override default health message
    mock: bool = False  # Use mock services


class FruitStoryResponse(BaseModel):
    """Response model for a generated fruit story."""
    story_id: str
    fruit_type: str
    fruit_name: str
    character_description: str
    color_palette: str
    episodes: List[StoryEpisodeResponse]
    overall_status: str  # pending, generating_prompts, generating_videos, complete, failed
    videos_completed: int = 0
    videos_total: int = 3
    created_at: Optional[datetime] = None


class StoryGenerationStatus(BaseModel):
    """Status of an ongoing story generation."""
    story_id: str
    overall_status: str
    current_episode: int
    episodes: List[StoryEpisodeResponse]
    message: str
