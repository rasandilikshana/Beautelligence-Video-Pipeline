from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from uuid import UUID

from src.api.schemas import (
    GenerationRequest, 
    GenerationResponse, 
    KeywordResponse, 
    PipelineStatus,
    QuotaStatus,
    # Story schemas
    FruitCharacterInfo,
    FruitStoryRequest,
    FruitStoryResponse,
    StoryEpisodeResponse,
    StoryGenerationStatus,
)
from src.orchestrator.pipeline import VideoPipeline
from src.models.database import get_session
from src.models.keyword import Keyword
from src.models.generation import Generation
from src.repositories.quota_repo import QuotaRepository
from src.services.story import FruitStoryGenerator, get_all_characters

router = APIRouter()

# In-memory storage for active story generations (for MVP)
# In production, this would be stored in the database
_active_stories: Dict[str, Dict[str, Any]] = {}


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
        queue_size=status_data.get("generations", {}).get("pending", 0),
        recent_generations=[]
    )


@router.post("/generate", response_model=Dict[str, Any])
async def generate_video(
    request: GenerationRequest, 
    background_tasks: BackgroundTasks
):
    """Trigger a video generation task (runs in background)."""
    
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
                k = Keyword.create(keyword=kw, source="api_manual")
                session.add(k)
                count += 1
            except:
                pass
        await session.commit()
    return {"added": count}


@router.get("/videos", response_model=List[GenerationResponse])
async def get_videos(limit: int = 20):
    """Get list of generated videos."""
    async with get_session() as session:
        query = select(Generation).order_by(desc(Generation.created_at)).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()


# =============================================================================
# FRUIT STORY GENERATION ENDPOINTS
# =============================================================================

@router.get("/story/characters", response_model=List[FruitCharacterInfo])
async def list_fruit_characters():
    """
    Get list of available fruit characters with their personalities and messages.
    
    Returns all pre-defined fruit characters that can be used for story generation.
    Each character has a unique archetype, personality, and health message.
    """
    characters = get_all_characters()
    return [
        FruitCharacterInfo(
            key=char.key,
            name=char.name,
            archetype=char.archetype,
            personality=char.personality,
            core_message=char.core_message,
            color_palette=char.color_palette,
            health_benefits=char.health_benefits,
        )
        for char in characters
    ]


@router.post("/story/generate", response_model=FruitStoryResponse)
async def generate_fruit_story(
    request: FruitStoryRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a 3-episode fruit character story.
    
    This creates an emotionally intelligent story series featuring the selected
    fruit character. The story is structured for maximum emotional impact:
    
    - Episode 1: Introduction & Curiosity Hook
    - Episode 2: Emotional Connection & Trust Building  
    - Episode 3: Value Delivery & Memorable Farewell
    
    The generation runs in the background. Use /story/{story_id}/status to 
    check progress and get video URLs when complete.
    """
    # Validate fruit type
    generator = FruitStoryGenerator()
    available = [c["key"] for c in generator.get_available_characters()]
    
    if request.fruit_type.lower() not in available:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown fruit type: {request.fruit_type}. Available: {available}"
        )
    
    # Generate the story prompts (this is fast)
    try:
        story = await generator.generate_story(
            fruit_key=request.fruit_type.lower(),
            custom_message=request.custom_message,
            mock=request.mock,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate story: {str(e)}"
        )
    
    # Store story in memory for status tracking
    _active_stories[story.story_id] = {
        "story": story,
        "status": "prompts_ready",
        "current_episode": 0,
        "episodes_status": ["pending", "pending", "pending"],
        "video_paths": [None, None, None],
    }
    
    # Start video generation in background
    background_tasks.add_task(
        _generate_story_videos,
        story.story_id,
        story,
        request.mock,
    )
    
    # Return immediate response with prompts
    return FruitStoryResponse(
        story_id=story.story_id,
        fruit_type=story.fruit_key,
        fruit_name=story.fruit_name,
        character_description=story.character_description,
        color_palette=story.color_palette,
        episodes=[
            StoryEpisodeResponse(
                episode_number=ep.episode_number,
                title=ep.title,
                scene_description=ep.scene_description,
                dialogue=ep.dialogue,
                emotion=ep.emotion,
                action=ep.action,
                health_message=ep.health_message,
                status="pending",
            )
            for ep in story.episodes
        ],
        overall_status="generating_videos",
        videos_completed=0,
        videos_total=3,
        created_at=story.created_at,
    )


async def _generate_story_videos(story_id: str, story: Any, mock: bool):
    """Background task to generate all 3 episode videos."""
    from src.services.video import VeoClient
    from config.logging import get_logger
    
    logger = get_logger(__name__)
    
    if story_id not in _active_stories:
        logger.error("story_not_found_for_video_generation", story_id=story_id)
        return
    
    veo_client = VeoClient()
    story_data = _active_stories[story_id]
    
    for i, episode in enumerate(story.episodes):
        episode_num = i + 1
        story_data["current_episode"] = episode_num
        story_data["episodes_status"][i] = "generating"
        
        logger.info(
            "generating_episode_video",
            story_id=story_id,
            episode=episode_num,
        )
        
        try:
            # Generate video for this episode
            result = await veo_client.generate_video(
                prompt=episode.full_veo_prompt,
                keyword=f"{story.fruit_name}_ep{episode_num}",
                mock=mock,
            )
            
            if result.success:
                story_data["episodes_status"][i] = "complete"
                story_data["video_paths"][i] = str(result.video_path) if result.video_path else None
                logger.info(
                    "episode_video_complete",
                    story_id=story_id,
                    episode=episode_num,
                    video_path=story_data["video_paths"][i],
                )
            else:
                story_data["episodes_status"][i] = "failed"
                logger.error(
                    "episode_video_failed",
                    story_id=story_id,
                    episode=episode_num,
                    error=result.error_message,
                )
                
        except Exception as e:
            story_data["episodes_status"][i] = "failed"
            logger.error(
                "episode_video_exception",
                story_id=story_id,
                episode=episode_num,
                error=str(e),
            )
    
    # Update overall status
    if all(s == "complete" for s in story_data["episodes_status"]):
        story_data["status"] = "complete"
    elif any(s == "failed" for s in story_data["episodes_status"]):
        story_data["status"] = "partial_failure"
    else:
        story_data["status"] = "complete"
    
    logger.info(
        "story_generation_complete",
        story_id=story_id,
        status=story_data["status"],
        episodes_status=story_data["episodes_status"],
    )


@router.get("/story/{story_id}/status", response_model=StoryGenerationStatus)
async def get_story_status(story_id: str):
    """
    Get the current status of a story generation.
    
    Use this to poll for completion after starting a story generation.
    Returns the status of each episode and video URLs when available.
    """
    if story_id not in _active_stories:
        raise HTTPException(
            status_code=404,
            detail=f"Story not found: {story_id}"
        )
    
    story_data = _active_stories[story_id]
    story = story_data["story"]
    
    episodes = []
    for i, episode in enumerate(story.episodes):
        video_path = story_data["video_paths"][i]
        video_url = f"/data/videos/{video_path.split('/')[-1]}" if video_path else None
        
        episodes.append(StoryEpisodeResponse(
            episode_number=episode.episode_number,
            title=episode.title,
            scene_description=episode.scene_description,
            dialogue=episode.dialogue,
            emotion=episode.emotion,
            action=episode.action,
            health_message=episode.health_message,
            status=story_data["episodes_status"][i],
            video_url=video_url,
            video_path=video_path,
        ))
    
    completed = sum(1 for s in story_data["episodes_status"] if s == "complete")
    
    status_messages = {
        "prompts_ready": "Story prompts generated. Starting video generation...",
        "generating_videos": f"Generating video {story_data['current_episode']} of 3...",
        "complete": "All 3 episode videos generated successfully!",
        "partial_failure": "Some episodes failed to generate. Check individual status.",
    }
    
    return StoryGenerationStatus(
        story_id=story_id,
        overall_status=story_data["status"],
        current_episode=story_data["current_episode"],
        episodes=episodes,
        message=status_messages.get(story_data["status"], "Processing..."),
    )


@router.get("/story/active", response_model=List[Dict[str, Any]])
async def list_active_stories():
    """Get list of all active/recent story generations."""
    return [
        {
            "story_id": story_id,
            "fruit_type": data["story"].fruit_key,
            "fruit_name": data["story"].fruit_name,
            "status": data["status"],
            "videos_completed": sum(1 for s in data["episodes_status"] if s == "complete"),
        }
        for story_id, data in _active_stories.items()
    ]
