"""
Beautelligence Video Pipeline - Fruit Story Generator

Generates emotionally intelligent 3-episode story content
using Gemini AI for creative prompt generation optimized for Veo 3.

This service creates psychologically-crafted stories that:
- Hook attention in Episode 1
- Build emotional connection in Episode 2
- Deliver memorable health messages in Episode 3
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from config.logging import get_logger
from config.settings import settings
from src.services.story.story_templates import (
    FruitCharacter,
    EpisodeTemplate,
    FRUIT_CHARACTERS,
    EPISODE_TEMPLATES,
    get_character,
    get_episode_template,
)
from src.utils.rate_limiter import gemini_limiter
from src.utils.retry import retry_async, APIError

logger = get_logger(__name__)


@dataclass
class StoryEpisode:
    """A single episode in the fruit story."""
    
    episode_number: int
    title: str
    scene_description: str
    dialogue: str  # What the character "says" (for audio narration)
    emotion: str
    action: str
    health_message: str
    full_veo_prompt: str  # The complete prompt for Veo 3
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "episode_number": self.episode_number,
            "title": self.title,
            "scene_description": self.scene_description,
            "dialogue": self.dialogue,
            "emotion": self.emotion,
            "action": self.action,
            "health_message": self.health_message,
            "full_veo_prompt": self.full_veo_prompt,
        }


@dataclass
class FruitStory:
    """A complete 3-episode fruit character story."""
    
    story_id: str
    fruit_key: str
    fruit_name: str
    character_description: str
    visual_consistency_anchor: str  # Used across all episodes for consistency
    color_palette: str
    episodes: list[StoryEpisode] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "story_id": self.story_id,
            "fruit_key": self.fruit_key,
            "fruit_name": self.fruit_name,
            "character_description": self.character_description,
            "visual_consistency_anchor": self.visual_consistency_anchor,
            "color_palette": self.color_palette,
            "episodes": [ep.to_dict() for ep in self.episodes],
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


# =============================================================================
# GEMINI SYSTEM INSTRUCTION
# Crafted for emotionally intelligent content generation
# =============================================================================

STORY_SYSTEM_INSTRUCTION = """You are an expert content creator for Beautelligence, specializing in 
emotionally intelligent animated content that creates deep connections with viewers.

Your expertise includes:
- Emotional Intelligence: Understanding and evoking specific emotional responses
- Psychology: Using Jungian archetypes and behavioral psychology principles
- NLP Communication: Crafting messages that resonate at subconscious levels
- Storytelling: Creating narratives that hook, connect, and inspire

You create content for cute 3D animated fruit characters that:
- Look like Pixar-quality 3D renders with big expressive eyes
- Have genuine personality that shines through every movement
- Deliver health messages in authentic, non-preachy ways
- Create emotional bonds with viewers in just 8 seconds

CRITICAL RULES:
1. Characters must feel ALIVE and GENUINE, never corporate or fake
2. Health messages must feel like friendly advice, never sales pitches
3. Every episode must have emotional purpose, not just visual filler
4. Dialogue must be conversational and warm, like talking to a friend
5. Actions must express personality, not just generic movements

You always respond in valid JSON format."""


class FruitStoryGenerator:
    """
    Generates emotionally intelligent 3-episode fruit character stories.
    
    Uses Gemini AI to create psychologically-crafted content that:
    - Hooks attention immediately
    - Builds genuine emotional connection
    - Delivers memorable health messages
    """
    
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
                    system_instruction=STORY_SYSTEM_INSTRUCTION,
                )
            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. "
                    "Run: pip install google-generativeai"
                )
        return self._client
    
    async def generate_story(
        self,
        fruit_key: str,
        custom_message: Optional[str] = None,
        mock: bool = False,
    ) -> FruitStory:
        """
        Generate a complete 3-episode story for a fruit character.
        
        Args:
            fruit_key: The fruit type (e.g., "apple", "banana")
            custom_message: Optional custom health message to incorporate
            mock: If True, return mock story without API calls
            
        Returns:
            FruitStory with 3 complete episodes ready for Veo 3
        """
        character = get_character(fruit_key)
        if not character:
            raise ValueError(f"Unknown fruit character: {fruit_key}")
        
        logger.info(
            "generating_fruit_story",
            fruit=fruit_key,
            character_name=character.name,
            archetype=character.archetype,
        )
        
        if mock or not settings.has_api_key:
            return self._generate_mock_story(character)
        
        try:
            return await self._generate_with_gemini(character, custom_message)
        except Exception as e:
            logger.error("story_generation_failed", fruit=fruit_key, error=str(e))
            # Fall back to template-based generation
            return self._generate_mock_story(character)
    
    @retry_async(max_attempts=3, initial_delay=5)
    async def _generate_with_gemini(
        self,
        character: FruitCharacter,
        custom_message: Optional[str] = None,
    ) -> FruitStory:
        """Generate story using Gemini AI."""
        await gemini_limiter.acquire()
        
        story_id = str(uuid4())
        
        # Build the visual consistency anchor - this ensures the character
        # looks the same across all 3 episodes
        visual_anchor = self._build_visual_anchor(character)
        
        # Generate all 3 episodes
        episodes = []
        for episode_num in range(1, 4):
            episode = await self._generate_episode(
                character=character,
                episode_number=episode_num,
                visual_anchor=visual_anchor,
                custom_message=custom_message,
            )
            episodes.append(episode)
        
        return FruitStory(
            story_id=story_id,
            fruit_key=character.key,
            fruit_name=character.name,
            character_description=f"{character.archetype}: {character.personality}",
            visual_consistency_anchor=visual_anchor,
            color_palette=character.color_palette,
            episodes=episodes,
            metadata={
                "model": self.model_name,
                "ai_generated": True,
                "custom_message": custom_message,
            },
        )
    
    def _build_visual_anchor(self, character: FruitCharacter) -> str:
        """
        Build a visual consistency anchor that ensures the character
        maintains identical appearance across all 3 episodes.
        """
        return f"""A cute 3D animated {character.name} character with big expressive googly eyes.

EXACT CHARACTER DESIGN (maintain precisely across all scenes):
- Physical form: {character.visual_traits}
- Color palette: {character.color_palette}
- Texture: Glossy plastic-like surface with soft shadows
- Eyes: Big, round, expressive cartoon eyes with shiny catchlights
- Expression style: Warm, genuine, and emotionally expressive
- Size: Small and adorable, perfectly proportioned

VISUAL STYLE (Pixar-quality 3D animation):
- Soft studio lighting with subtle rim light
- Clean, bright, minimalist background
- High-quality 3D render with professional polish
- Smooth, fluid character animation"""
    
    async def _generate_episode(
        self,
        character: FruitCharacter,
        episode_number: int,
        visual_anchor: str,
        custom_message: Optional[str] = None,
    ) -> StoryEpisode:
        """Generate a single episode using Gemini."""
        template = get_episode_template(episode_number)
        if not template:
            raise ValueError(f"Invalid episode number: {episode_number}")
        
        # Build the prompt for Gemini
        user_prompt = self._build_episode_prompt(
            character=character,
            template=template,
            custom_message=custom_message,
        )
        
        logger.info(
            "generating_episode",
            episode=episode_number,
            character=character.name,
        )
        
        try:
            response = await self.client.generate_content_async(user_prompt)
            episode_data = self._parse_episode_response(response.text)
        except Exception as e:
            logger.warning(
                "gemini_episode_generation_failed",
                episode=episode_number,
                error=str(e),
            )
            # Fall back to template-based content
            episode_data = self._get_fallback_episode_content(character, template)
        
        # Build the complete Veo 3 prompt
        full_veo_prompt = self._build_veo_prompt(
            character=character,
            template=template,
            visual_anchor=visual_anchor,
            episode_data=episode_data,
        )
        
        return StoryEpisode(
            episode_number=episode_number,
            title=episode_data.get("title", f"Episode {episode_number}"),
            scene_description=episode_data.get("scene_description", ""),
            dialogue=episode_data.get("dialogue", ""),
            emotion=episode_data.get("emotion", "happy"),
            action=episode_data.get("action", ""),
            health_message=episode_data.get("health_message", character.core_message),
            full_veo_prompt=full_veo_prompt,
        )
    
    def _build_episode_prompt(
        self,
        character: FruitCharacter,
        template: EpisodeTemplate,
        custom_message: Optional[str] = None,
    ) -> str:
        """Build the Gemini prompt for episode generation."""
        
        health_message = custom_message or character.core_message
        
        return f"""Generate Episode {template.episode_number} for a {character.name} character video.

CHARACTER PROFILE:
- Name: {character.name}
- Archetype: {character.archetype}
- Personality: {character.personality}
- Voice/Tone: {character.voice_tone}
- Emotional Hook: {character.emotional_hook}
- Trust Builder: {character.trust_builder}
- Core Message: {health_message}

EPISODE PURPOSE: {template.purpose}
EMOTIONAL GOAL: {template.emotional_goal}

STORY STRUCTURE:
{template.structure}

SCENE GUIDANCE:
{template.scene_guidance}

CHARACTER SIGNATURE ELEMENTS:
- Intro Gesture: {character.intro_gesture}
- Signature Move: {character.signature_move}
- Farewell Gesture: {character.farewell_gesture}

Generate content that creates GENUINE emotional connection. The character must feel alive, 
not like a corporate mascot. The health message should feel like advice from a caring friend.

Respond with this exact JSON structure:
{{
    "title": "Episode title (catchy, emotional)",
    "scene_description": "Detailed 2-3 sentence scene description",
    "dialogue": "What the character says/expresses (for audio narration, 2-3 short sentences)",
    "emotion": "Primary emotion displayed (e.g., warm, excited, caring)",
    "action": "Specific actions the character performs (detailed for animation)",
    "health_message": "The health message woven into this episode (if Episode 3)"
}}"""
    
    def _parse_episode_response(self, response_text: str) -> dict[str, Any]:
        """Parse Gemini response into episode data."""
        try:
            json_text = response_text
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0]
            
            return json.loads(json_text.strip())
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning("episode_parse_error", error=str(e))
            return {}
    
    def _get_fallback_episode_content(
        self,
        character: FruitCharacter,
        template: EpisodeTemplate,
    ) -> dict[str, Any]:
        """Get fallback content when AI generation fails."""
        
        if template.episode_number == 1:
            return {
                "title": f"Meet {character.name}!",
                "scene_description": f"A cute {character.name} character appears with a warm, welcoming presence, ready to share something special with you.",
                "dialogue": f"Hey there, friend! I'm so happy to meet you. I've got something wonderful to share...",
                "emotion": "warm and welcoming",
                "action": character.intro_gesture,
                "health_message": "",
            }
        elif template.episode_number == 2:
            return {
                "title": f"{character.name}'s Secret",
                "scene_description": f"The {character.name} character leans in with genuine care, creating an intimate moment of connection.",
                "dialogue": f"You know what? I really care about you. Let me tell you something that changed my life...",
                "emotion": "caring and intimate",
                "action": character.signature_move,
                "health_message": "",
            }
        else:
            return {
                "title": f"{character.name}'s Gift",
                "scene_description": f"The {character.name} character shares their wisdom with confident warmth, delivering an inspiring message.",
                "dialogue": f"{character.core_message} Remember, I'm always here for you!",
                "emotion": "confident and inspiring",
                "action": character.farewell_gesture,
                "health_message": character.core_message,
            }
    
    def _build_veo_prompt(
        self,
        character: FruitCharacter,
        template: EpisodeTemplate,
        visual_anchor: str,
        episode_data: dict[str, Any],
    ) -> str:
        """Build the complete Veo 3 prompt for video generation."""
        
        return f"""{visual_anchor}

SCENE: {episode_data.get('scene_description', '')}

ACTION: The {character.name} character is {episode_data.get('action', character.signature_move)}.
The character displays a {episode_data.get('emotion', 'warm')} expression throughout.

DIALOGUE/NARRATION (for audio): "{episode_data.get('dialogue', '')}"

CAMERA: {template.camera_movement}
DURATION: {settings.veo_duration_seconds} seconds
ASPECT RATIO: {settings.veo_aspect_ratio}

AUDIO: {template.audio_mood}. The character's voice should be {character.voice_tone}.
Include subtle, satisfying sound effects that match the character's movements.

CRITICAL: Maintain the EXACT character design from the visual anchor. The character must 
look identical to other episodes in this series - same proportions, colors, and features."""
    
    def _generate_mock_story(self, character: FruitCharacter) -> FruitStory:
        """Generate a mock story using templates only."""
        story_id = str(uuid4())
        visual_anchor = self._build_visual_anchor(character)
        
        episodes = []
        for episode_num in range(1, 4):
            template = get_episode_template(episode_num)
            episode_data = self._get_fallback_episode_content(character, template)
            
            full_veo_prompt = self._build_veo_prompt(
                character=character,
                template=template,
                visual_anchor=visual_anchor,
                episode_data=episode_data,
            )
            
            episodes.append(StoryEpisode(
                episode_number=episode_num,
                title=episode_data["title"],
                scene_description=episode_data["scene_description"],
                dialogue=episode_data["dialogue"],
                emotion=episode_data["emotion"],
                action=episode_data["action"],
                health_message=episode_data.get("health_message", ""),
                full_veo_prompt=full_veo_prompt,
            ))
        
        return FruitStory(
            story_id=story_id,
            fruit_key=character.key,
            fruit_name=character.name,
            character_description=f"{character.archetype}: {character.personality}",
            visual_consistency_anchor=visual_anchor,
            color_palette=character.color_palette,
            episodes=episodes,
            metadata={
                "model": "template",
                "ai_generated": False,
            },
        )
    
    def get_available_characters(self) -> list[dict[str, Any]]:
        """Get list of available fruit characters with preview info."""
        return [
            {
                "key": char.key,
                "name": char.name,
                "archetype": char.archetype,
                "personality": char.personality,
                "core_message": char.core_message,
                "color_palette": char.color_palette,
                "health_benefits": char.health_benefits,
            }
            for char in FRUIT_CHARACTERS.values()
        ]
