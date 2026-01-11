"""
Beautelligence Video Pipeline - Prompt Templates

Templates and guidelines for generating Veo 3-optimized prompts.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class PromptTemplate:
    """Template for generating video prompts."""

    base_template: str
    style_guidelines: str
    negative_prompt: str
    audio_template: str

    def render(self, **kwargs: Any) -> str:
        """Render the template with provided values."""
        return self.base_template.format(**kwargs)


# Default Beautelligence brand template
BEAUTELLIGENCE_TEMPLATE = PromptTemplate(
    base_template="""A cute 3D animated {object} character with big expressive {eye_style} eyes and a {emotion} expression.

The character is {action} in a {environment}.

Visual Style:
- Soft studio lighting with subtle rim light
- Glossy plastic-like texture with soft shadows
- Vibrant {color_palette} color palette
- High-quality 3D render, Pixar-style animation quality

Camera: {camera_movement}
Duration: {duration} seconds
Audio: {audio_description}""",
    style_guidelines="""
VISUAL REQUIREMENTS:
- Cute, anthropomorphic character design
- Big, expressive eyes with catchlights
- Smooth, glossy textures like plastic or clay
- Soft, diffused lighting with rim highlights
- Pastel to vibrant color palette
- Clean, simple background that doesn't distract
- Professional 3D render quality (Pixar/Dreamworks style)

ANIMATION REQUIREMENTS:
- Smooth, fluid movements
- Expressive character emotions
- Satisfying, loopable motion (if applicable)
- 8 seconds duration, vertical 9:16 format
""",
    negative_prompt="""realistic human faces, scary elements, dark themes, violence, 
text overlays, watermarks, low quality, blurry, distorted faces,
inappropriate content, branded logos, copyrighted characters,
horror, creepy, unsettling, ugly, deformed, extra limbs,
low resolution, pixelated, amateur, unfinished""",
    audio_template="{mood} background music with {effect_type} sound effects",
)

# Predefined options for template variables
EYE_STYLES = ["googly", "anime-style", "cartoon", "sparkly", "big round"]
EMOTIONS = ["happy", "surprised", "excited", "joyful", "curious", "amazed", "cheerful"]
CAMERA_MOVEMENTS = [
    "slow zoom in with gentle rotation",
    "smooth dolly forward",
    "subtle orbit around the character",
    "gentle push in",
    "slow pan up",
]
AUDIO_MOODS = ["upbeat cheerful", "playful bouncy", "whimsical magical", "happy energetic"]
AUDIO_EFFECTS = ["satisfying", "cute pop", "bouncy", "magical sparkle", "squishy"]


def get_random_options() -> dict[str, str]:
    """Get random options for template variables."""
    import random

    return {
        "eye_style": random.choice(EYE_STYLES),
        "emotion": random.choice(EMOTIONS),
        "camera_movement": random.choice(CAMERA_MOVEMENTS),
        "audio_mood": random.choice(AUDIO_MOODS),
        "audio_effect": random.choice(AUDIO_EFFECTS),
    }


# Object-specific color palettes
OBJECT_COLOR_PALETTES = {
    "strawberry": "red, pink, and green",
    "avocado": "green, cream, and brown",
    "mango": "orange, yellow, and green",
    "papaya": "orange, yellow, and green",
    "kiwi": "green, brown, and cream",
    "blueberry": "blue, purple, and green",
    "watermelon": "red, green, and pink",
    "pineapple": "yellow, green, and brown",
    "coconut": "white, cream, and brown",
    "peach": "peach, pink, and green",
    "lemon": "yellow, green, and white",
    "orange": "orange, green, and yellow",
    "banana": "yellow and cream",
    "cherry": "red, pink, and green",
    "grape": "purple, green, and pink",
}

# Default actions for food items
DEFAULT_ACTIONS = [
    "dancing excitedly",
    "jumping with joy",
    "waving adorably at the camera",
    "spinning around happily",
    "bouncing playfully",
    "doing a cute little dance",
    "wiggling with excitement",
]

# Default environments
DEFAULT_ENVIRONMENTS = [
    "a clean white studio backdrop",
    "a colorful pastel kitchen",
    "a magical sparkly void",
    "a cute minimalist setting",
    "a dreamy soft-lit space",
]


def get_color_palette(object_name: str) -> str:
    """Get color palette for an object."""
    lower = object_name.lower()
    return OBJECT_COLOR_PALETTES.get(lower, "vibrant and cheerful")


def get_default_action() -> str:
    """Get a random default action."""
    import random

    return random.choice(DEFAULT_ACTIONS)


def get_default_environment() -> str:
    """Get a random default environment."""
    import random

    return random.choice(DEFAULT_ENVIRONMENTS)
