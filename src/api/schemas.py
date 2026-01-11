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
