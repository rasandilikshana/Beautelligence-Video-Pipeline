from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from uuid import UUID

from src.api.schemas import (
    GenerationRequest, 
    GenerationResponse, 
    KeywordResponse, 
    PipelineStatus,
    QuotaStatus
)
from src.orchestrator.pipeline import VideoPipeline
from src.models.database import get_session
from src.models.keyword import Keyword
from src.models.generation import Generation
from src.repositories.quota_repo import QuotaRepository

router = APIRouter()

# Dependency to get pipeline instance
async def get_pipeline():
    pipeline = VideoPipeline()
    await pipeline.initialize()
    return pipeline

@router.get("/status", response_model=PipelineStatus)
async def get_status():
    """Get current pipeline status and quota."""
    pipeline = VideoPipeline()
    status_data = await pipeline.get_status()
    
    quota_data = status_data.get("quota", {})
    return PipelineStatus(
        quota=QuotaStatus(
            videos_generated=quota_data.get("videos_generated", 0),
            videos_limit=quota_data.get("videos_limit", 0),
            videos_remaining=quota_data.get("videos_remaining", 0),
            can_generate=quota_data.get("can_generate", False)
        ),
        queue_size=status_data.get("generations", {}).get("pending", 0), # This is generation pending, not keyword queue
        recent_generations=[] # TODO: Populate this
    )

@router.post("/generate", response_model=Dict[str, Any])
async def generate_video(
    request: GenerationRequest, 
    background_tasks: BackgroundTasks
):
    """Trigger a video generation task (runs in background)."""
    # For now, we'll just queue it as a keyword if it's not a direct generation
    # But user wants immediate generation usually. 
    # Let's use run_single in background.
    
    async def _run_single(prompt: str, force: bool, mock: bool):
        pipeline = VideoPipeline(mock=mock)
        await pipeline.initialize()
        await pipeline.run_single(keyword=prompt, force=force)

    background_tasks.add_task(_run_single, request.prompt, request.force, request.mock)
    
    return {"status": "queued", "message": f"Generation started for '{request.prompt}'"}

@router.get("/queue", response_model=List[KeywordResponse])
async def get_queue(limit: int = 50, status: Optional[str] = None):
    """Get the current keyword queue."""
    async with get_session() as session:
        query = select(Keyword).order_by(desc(Keyword.created_at)).limit(limit)
        if status:
            query = query.where(Keyword.status == status)
        
        result = await session.execute(query)
        return result.scalars().all()

@router.post("/queue")
async def add_to_queue(keywords: List[str]):
    """Add new keywords to the processing queue."""
    async with get_session() as session:
        count = 0
        for kw in keywords:
            try:
                # Simple dedupe check logic should be here or in repo
                # For now just create
                k = Keyword.create(keyword=kw, source="api_manual")
                session.add(k)
                count += 1
            except:
                pass # Ignore duplicates/errors for bulk add
        await session.commit()
    return {"added": count}

@router.get("/videos", response_model=List[GenerationResponse])
async def get_videos(limit: int = 20):
    """Get list of generated videos."""
    async with get_session() as session:
        query = select(Generation).order_by(desc(Generation.created_at)).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()
