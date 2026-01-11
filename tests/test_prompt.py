"""
Tests for the Prompt service (Gemini prompt generation).
"""

import pytest
from src.services.prompt.prompt_templates import (
    BEAUTELLIGENCE_TEMPLATE,
    get_color_palette,
    get_default_action,
    get_default_environment,
    get_random_options,
)
from src.services.prompt.gemini_prompt_generator import GeminiPromptGenerator


class TestPromptTemplates:
    """Tests for prompt template system."""

    def test_template_renders(self):
        """Test that the template renders without errors."""
        options = get_random_options()
        prompt = BEAUTELLIGENCE_TEMPLATE.render(
            object="strawberry",
            eye_style=options["eye_style"],
            emotion=options["emotion"],
            action=get_default_action(),
            environment=get_default_environment(),
            color_palette=get_color_palette("strawberry"),
            camera_movement=options["camera_movement"],
            duration=8,
            audio_description="cheerful music with pop sounds",
        )

        assert "strawberry" in prompt
        assert "3D animated" in prompt
        assert "eyes" in prompt.lower()

    def test_color_palette_mapping(self):
        """Test color palette lookup for common objects."""
        assert "red" in get_color_palette("strawberry")
        assert "green" in get_color_palette("avocado")
        assert "orange" in get_color_palette("mango")
        assert "blue" in get_color_palette("blueberry")

    def test_unknown_object_fallback(self):
        """Test that unknown objects get a default palette."""
        palette = get_color_palette("unknown_item")
        assert palette  # Should return a non-empty string

    def test_negative_prompt_exists(self):
        """Test that negative prompt is defined."""
        assert BEAUTELLIGENCE_TEMPLATE.negative_prompt
        assert len(BEAUTELLIGENCE_TEMPLATE.negative_prompt) > 50


class TestGeminiPromptGenerator:
    """Tests for GeminiPromptGenerator."""

    @pytest.mark.asyncio
    async def test_mock_generation(self):
        """Test prompt generation in mock mode."""
        generator = GeminiPromptGenerator()
        result = await generator.generate_prompt("strawberry", mock=True)

        assert result.keyword == "strawberry"
        assert result.prompt
        assert result.negative_prompt
        assert "strawberry" in result.prompt.lower()

    @pytest.mark.asyncio
    async def test_mock_metadata(self):
        """Test that mock generation includes proper metadata."""
        generator = GeminiPromptGenerator()
        result = await generator.generate_prompt("mango", mock=True)

        assert result.metadata is not None
        assert result.metadata.get("model") == "template"
        assert result.metadata.get("ai_generated") is False

    @pytest.mark.asyncio
    async def test_different_keywords_produce_different_prompts(self):
        """Test that different keywords produce different prompts."""
        generator = GeminiPromptGenerator()

        result1 = await generator.generate_prompt("strawberry", mock=True)
        result2 = await generator.generate_prompt("avocado", mock=True)

        assert "strawberry" in result1.prompt.lower()
        assert "avocado" in result2.prompt.lower()
        assert result1.prompt != result2.prompt
