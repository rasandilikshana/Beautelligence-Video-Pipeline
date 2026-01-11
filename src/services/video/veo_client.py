"""
Beautelligence Video Pipeline - Veo 3 Client

Generates videos using Google's Veo 3 API via the google.genai SDK.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from config.logging import get_logger
from config.settings import settings
from src.utils.file_manager import FileManager
from src.utils.rate_limiter import veo_limiter
from src.utils.retry import retry_async, APIError

logger = get_logger(__name__)


@dataclass
class VideoGenerationResult:
    """Result of video generation."""

    success: bool
    video_path: Path | None
    video_url: str | None
    file_size: int
    duration_seconds: int
    generation_time_seconds: float
    error_message: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "video_path": str(self.video_path) if self.video_path else None,
            "video_url": self.video_url,
            "file_size": self.file_size,
            "duration_seconds": self.duration_seconds,
            "generation_time_seconds": self.generation_time_seconds,
            "error_message": self.error_message,
            "metadata": self.metadata or {},
        }


class VeoClient:
    """
    Client for Google's Veo 3 video generation API.

    Uses the google.genai SDK for video generation with audio.
    """

    # Valid Veo 3 model names (from API)
    VALID_MODELS = [
        "veo-3.0-generate-001",
        "veo-3.0-fast-generate-001",
        "veo-3.1-generate-preview",
        "veo-3.1-fast-generate-preview",
    ]

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        file_manager: FileManager | None = None,
    ):
        self.api_key = api_key or settings.google_api_key
        
        # Map old model names to new model names
        requested_model = model or settings.veo_model
        self.model_name = self._normalize_model_name(requested_model)
        
        self.file_manager = file_manager or FileManager()
        self._client = None

    def _normalize_model_name(self, model: str) -> str:
        """Normalize model name to valid Veo 3 model."""
        # Map config model names to actual API model names
        model_mapping = {
            "veo-3.0-fast-generate-001": "veo-3.0-fast-generate-001",  # Already correct
            "veo-3.0-generate-001": "veo-3.0-generate-001",  # Already correct
            "veo-3.0-fast-generate-preview": "veo-3.0-fast-generate-001",  # Map preview to actual
            "veo-3.0-generate-preview": "veo-3.0-generate-001",  # Map preview to actual
            "veo-3": "veo-3.0-generate-001",
            "veo-3-fast": "veo-3.0-fast-generate-001",
        }
        
        if model in model_mapping:
            return model_mapping[model]
        elif model in self.VALID_MODELS:
            return model
        else:
            logger.warning(
                "unknown_model_using_default",
                requested=model,
                using="veo-3.0-fast-generate-001"
            )
            return "veo-3.0-fast-generate-001"

    @property
    def client(self) -> Any:
        """Lazy-load genai client."""
        if self._client is None:
            try:
                from google import genai
                
                self._client = genai.Client(api_key=self.api_key)
                logger.info("genai_client_initialized", model=self.model_name)
            except ImportError:
                raise ImportError(
                    "google-genai package not installed. "
                    "Run: pip install google-genai"
                )
        return self._client

    async def generate_video(
        self,
        prompt: str,
        keyword: str,
        negative_prompt: str | None = None,
        mock: bool = False,
    ) -> VideoGenerationResult:
        """
        Generate a video using Veo 3.

        Args:
            prompt: The video generation prompt
            keyword: The keyword (used for filename)
            negative_prompt: Optional negative prompt
            mock: If True, return mock result without calling API

        Returns:
            VideoGenerationResult with path, size, and metadata
        """
        start_time = datetime.now()

        if mock or not settings.has_api_key:
            return await self._generate_mock_video(prompt, keyword, start_time)

        try:
            return await self._generate_with_veo(
                prompt, keyword, negative_prompt, start_time
            )
        except Exception as e:
            logger.error("veo_generation_failed", keyword=keyword, error=str(e))
            return VideoGenerationResult(
                success=False,
                video_path=None,
                video_url=None,
                file_size=0,
                duration_seconds=0,
                generation_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e),
            )

    @retry_async(max_attempts=3, initial_delay=30)
    async def _generate_with_veo(
        self,
        prompt: str,
        keyword: str,
        negative_prompt: str | None,
        start_time: datetime,
    ) -> VideoGenerationResult:
        """Generate video using Veo 3 API with google.genai SDK."""
        await veo_limiter.acquire()

        logger.info(
            "veo_generation_started",
            keyword=keyword,
            model=self.model_name,
        )

        try:
            from google.genai import types
            
            client = self.client

            # Build the full prompt
            full_prompt = prompt

            # Configure generation parameters using GenerateVideosConfig
            # Note: Veo 3 generates audio automatically, no generateAudio param needed
            generation_config = types.GenerateVideosConfig(
                aspectRatio=settings.veo_aspect_ratio,  # "9:16" for vertical
                durationSeconds=settings.veo_duration_seconds,  # 4, 6, or 8 seconds
                negativePrompt=negative_prompt,
                numberOfVideos=1,
            )

            # Start video generation
            logger.info("veo_requesting_generation", prompt_length=len(full_prompt))
            
            # Use the models.generate_videos method (plural)
            operation = client.models.generate_videos(
                model=self.model_name,
                prompt=full_prompt,
                config=generation_config,
            )

            # Poll for completion
            logger.info("veo_polling_for_completion", operation_name=getattr(operation, 'name', 'unknown'))
            
            timeout_seconds = 300  # 5 minutes max
            poll_interval = 10  # Check every 10 seconds
            elapsed = 0

            while not operation.done:
                if elapsed >= timeout_seconds:
                    raise APIError("Video generation timed out after 5 minutes")
                
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
                
                # Refresh operation status
                operation = client.operations.get(operation)
                logger.info("veo_polling", elapsed=elapsed, done=operation.done)

            # Check for errors
            if operation.error:
                raise APIError(f"Veo 3 generation error: {operation.error.message}")

            # Get the result
            result = operation.result
            
            if not result or not result.generated_videos:
                raise APIError("No video generated in response")

            # Get the first generated video
            generated_video = result.generated_videos[0]
            
            # Get video path for saving
            video_path = self.file_manager.get_video_path(keyword)
            video_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download and save using official API pattern from docs:
            # client.files.download(file=generated_video.video)
            # generated_video.video.save("filename.mp4")
            logger.info("veo_downloading_video_via_sdk")
            
            try:
                # Download the video file (prepares it for saving)
                client.files.download(file=generated_video.video)
                
                # Save to local file using the SDK's save method
                generated_video.video.save(str(video_path))
                logger.info("video_saved_via_sdk", path=str(video_path))
                
            except Exception as save_error:
                logger.error("sdk_save_failed", error=str(save_error))
                raise APIError(f"Failed to save video: {save_error}")
            
            # Get file size and URI for metadata
            file_size = self.file_manager.get_file_size(video_path)
            video_uri = None
            if hasattr(generated_video, 'video') and generated_video.video:
                if hasattr(generated_video.video, 'uri'):
                    video_uri = generated_video.video.uri

            generation_time = (datetime.now() - start_time).total_seconds()

            logger.info(
                "veo_generation_completed",
                keyword=keyword,
                file_size=file_size,
                generation_time=generation_time,
            )

            return VideoGenerationResult(
                success=True,
                video_path=video_path,
                video_url=video_uri,
                file_size=file_size,
                duration_seconds=settings.veo_duration_seconds,
                generation_time_seconds=generation_time,
                metadata={
                    "model": self.model_name,
                    "aspect_ratio": settings.veo_aspect_ratio,
                    "resolution": settings.veo_resolution,
                    "has_audio": True,
                },
            )

        except ImportError as e:
            logger.error("google_genai_import_error", error=str(e))
            raise APIError(
                "google-genai package required. Install with: pip install google-genai"
            )
        except Exception as e:
            logger.error("veo_api_error", error=str(e), error_type=type(e).__name__)
            raise APIError(f"Veo 3 API error: {e}")

    async def _download_video(self, url: str) -> bytes:
        """Download video from URL with authentication."""
        import aiohttp
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

        # Add API key to URL for authenticated download
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params['key'] = [self.api_key]
        new_query = urlencode(query_params, doseq=True)
        authenticated_url = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, new_query, parsed.fragment
        ))

        logger.info("downloading_video_authenticated", url_length=len(url))

        async with aiohttp.ClientSession() as session:
            async with session.get(authenticated_url) as response:
                if response.status != 200:
                    logger.error(
                        "video_download_failed",
                        status=response.status,
                        reason=response.reason
                    )
                    raise APIError(f"Failed to download video: {response.status}")
                
                video_data = await response.read()
                logger.info("video_downloaded", size_bytes=len(video_data))
                return video_data

    async def _generate_mock_video(
        self,
        prompt: str,
        keyword: str,
        start_time: datetime,
    ) -> VideoGenerationResult:
        """Generate a mock video result for testing."""
        # Simulate generation time
        await asyncio.sleep(2)

        # Create a placeholder file
        video_path = self.file_manager.get_video_path(keyword)

        # Create empty placeholder file
        video_path.parent.mkdir(parents=True, exist_ok=True)
        video_path.write_bytes(b"MOCK_VIDEO_PLACEHOLDER")

        generation_time = (datetime.now() - start_time).total_seconds()

        logger.info(
            "mock_video_generated",
            keyword=keyword,
            path=str(video_path),
        )

        return VideoGenerationResult(
            success=True,
            video_path=video_path,
            video_url=None,
            file_size=len(b"MOCK_VIDEO_PLACEHOLDER"),
            duration_seconds=settings.veo_duration_seconds,
            generation_time_seconds=generation_time,
            metadata={
                "model": "mock",
                "mock": True,
                "prompt_preview": prompt[:200],
            },
        )

    async def list_available_models(self) -> list[str]:
        """List available Veo models from the API."""
        try:
            client = self.client
            models = client.models.list()
            
            veo_models = [
                model.name for model in models 
                if 'veo' in model.name.lower()
            ]
            
            logger.info("available_veo_models", models=veo_models)
            return veo_models
        except Exception as e:
            logger.error("list_models_failed", error=str(e))
            return self.VALID_MODELS
