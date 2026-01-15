"""
Beautelligence Video Pipeline - Story Services

Provides fruit character story generation capabilities.
"""

from src.services.story.fruit_story_generator import (
    FruitStoryGenerator,
    FruitStory,
    StoryEpisode,
)
from src.services.story.story_templates import (
    FruitCharacter,
    EpisodeTemplate,
    FRUIT_CHARACTERS,
    EPISODE_TEMPLATES,
    get_character,
    get_all_characters,
    get_random_character,
    get_episode_template,
)

__all__ = [
    # Generator
    "FruitStoryGenerator",
    "FruitStory",
    "StoryEpisode",
    # Templates
    "FruitCharacter",
    "EpisodeTemplate",
    "FRUIT_CHARACTERS",
    "EPISODE_TEMPLATES",
    "get_character",
    "get_all_characters",
    "get_random_character",
    "get_episode_template",
]
