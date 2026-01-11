"""
Beautelligence Video Pipeline - Gemini Prompt Generator

Uses Google Gemini AI to generate creative, Veo 3-optimized prompts.
"""

import json
from dataclasses import dataclass
from typing import Any

from config.logging import get_logger
from config.settings import settings
from src.services.prompt.prompt_templates import (
    BEAUTELLIGENCE_TEMPLATE,
    get_color_palette,
    get_default_action,
    get_default_environment,
    get_random_options,
)
from src.utils.rate_limiter import gemini_limiter
from src.utils.retry import retry_async, APIError

logger = get_logger(__name__)


@dataclass
class GeneratedPrompt:
    """Result of prompt generation."""

    prompt: str
    negative_prompt: str
    keyword: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "keyword": self.keyword,
            "metadata": self.metadata,
        }


SYSTEM_INSTRUCTION = """You are a creative director for Beautelligence, a social media brand that creates cute 3D animated character videos.

Your task is to generate Veo 3-optimized video prompts based on trending keywords. The videos feature:
- Cute, anthropomorphic food/fruit/object characters
- Big expressive eyes (googly or anime-style)
- Pixar/Dreamworks quality 3D animation
- Happy, wholesome, family-friendly content
- 8-second duration, vertical 9:16 format

For each keyword, you must generate a creative, detailed prompt that will result in an engaging, adorable video.

Always respond with valid JSON in this exact format:
{
  "prompt": "The full video prompt text",
  "action": "What the character is doing",
  "emotion": "The character's emotion",
  "environment": "The setting/background",
  "audio_description": "Description of music and sound effects"
}"""


class GeminiPromptGenerator:
    """Generates video prompts using Google Gemini AI."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.google_api_key
        self.model_name = model or settings.gemini_model
        self._client = None

    @property
    def client(self) -> Any:
        """Lazy-load Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=SYSTEM_INSTRUCTION,
                )
            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. "
                    "Run: pip install google-generativeai"
                )
        return self._client

    async def generate_prompt(
        self,
        keyword: str,
        mock: bool = False,
    ) -> GeneratedPrompt:
        """
        Generate a Veo 3-optimized prompt for a keyword.

        Args:
            keyword: The trending keyword to generate a prompt for
            mock: If True, return a mock prompt without calling the API

        Returns:
            GeneratedPrompt with the complete prompt data
        """
        if mock or not settings.has_api_key:
            return self._generate_mock_prompt(keyword)

        try:
            return await self._generate_with_gemini(keyword)
        except Exception as e:
            logger.error("gemini_generation_failed", keyword=keyword, error=str(e))
            # Fall back to template-based generation
            return self._generate_mock_prompt(keyword)

    @retry_async(max_attempts=3, initial_delay=5)
    async def _generate_with_gemini(self, keyword: str) -> GeneratedPrompt:
        """Generate prompt using Gemini API."""
        await gemini_limiter.acquire()

        user_prompt = f"""Generate a creative video prompt for a cute 3D animated "{keyword}" character.

Make it adorable, engaging, and suitable for TikTok/Instagram Reels.
The character should have a distinct personality and be doing something fun or satisfying.

Remember to respond with valid JSON only."""

        logger.info("calling_gemini", keyword=keyword, model=self.model_name)

        try:
            response = await self.client.generate_content_async(user_prompt)
            return self._parse_gemini_response(keyword, response.text)
        except Exception as e:
            logger.error("gemini_api_error", error=str(e))
            raise APIError(f"Gemini API error: {e}")

    def _parse_gemini_response(self, keyword: str, response_text: str) -> GeneratedPrompt:
        """Parse Gemini response into GeneratedPrompt."""
        try:
            # Try to extract JSON from response
            json_text = response_text
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0]

            data = json.loads(json_text.strip())

            # Get template options
            options = get_random_options()
            color_palette = get_color_palette(keyword)

            # Build full prompt from template + AI response
            full_prompt = BEAUTELLIGENCE_TEMPLATE.render(
                object=keyword,
                eye_style=options["eye_style"],
                emotion=data.get("emotion", options["emotion"]),
                action=data.get("action", get_default_action()),
                environment=data.get("environment", get_default_environment()),
                color_palette=color_palette,
                camera_movement=options["camera_movement"],
                duration=settings.veo_duration_seconds,
                audio_description=data.get(
                    "audio_description",
                    f"{options['audio_mood']} music with {options['audio_effect']} sound effects",
                ),
            )

            return GeneratedPrompt(
                prompt=full_prompt,
                negative_prompt=BEAUTELLIGENCE_TEMPLATE.negative_prompt,
                keyword=keyword,
                metadata={
                    "model": self.model_name,
                    "ai_generated": True,
                    "raw_response": data,
                    "options": options,
                },
            )

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.warning(
                "gemini_parse_warning",
                error=str(e),
                response_preview=response_text[:200],
            )
            # Fall back to mock if parsing fails
            return self._generate_mock_prompt(keyword)

    def _generate_mock_prompt(self, keyword: str) -> GeneratedPrompt:
        """Generate a prompt using templates without AI."""
        options = get_random_options()
        color_palette = get_color_palette(keyword)

        prompt = BEAUTELLIGENCE_TEMPLATE.render(
            object=keyword,
            eye_style=options["eye_style"],
            emotion=options["emotion"],
            action=get_default_action(),
            environment=get_default_environment(),
            color_palette=color_palette,
            camera_movement=options["camera_movement"],
            duration=settings.veo_duration_seconds,
            audio_description=f"{options['audio_mood']} music with {options['audio_effect']} sound effects",
        )

        return GeneratedPrompt(
            prompt=prompt,
            negative_prompt=BEAUTELLIGENCE_TEMPLATE.negative_prompt,
            keyword=keyword,
            metadata={
                "model": "template",
                "ai_generated": False,
                "options": options,
            },
        )
