"""
Pytest configuration and fixtures for Beautelligence Video Pipeline tests.
"""

import asyncio
import pytest
from pathlib import Path
from typing import AsyncGenerator

# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Create temporary data directories for tests."""
    (tmp_path / "videos").mkdir()
    (tmp_path / "prompts").mkdir()
    (tmp_path / "logs").mkdir()
    return tmp_path


@pytest.fixture
def mock_settings(monkeypatch, temp_data_dir: Path):
    """Mock settings for testing."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_key")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("VIDEO_OUTPUT_DIR", str(temp_data_dir / "videos"))
    monkeypatch.setenv("PROMPT_LOG_DIR", str(temp_data_dir / "prompts"))
    monkeypatch.setenv("LOG_DIR", str(temp_data_dir / "logs"))


@pytest.fixture
def sample_keyword() -> str:
    """Sample keyword for testing."""
    return "strawberry"


@pytest.fixture
def sample_prompt() -> str:
    """Sample prompt for testing."""
    return """A cute 3D animated strawberry character with big expressive googly eyes and a happy expression.

The character is dancing excitedly in a clean white studio backdrop.

Visual Style:
- Soft studio lighting with subtle rim light
- Glossy plastic-like texture with soft shadows
- Vibrant red, pink, and green color palette
- High-quality 3D render, Pixar-style animation quality

Camera: slow zoom in with gentle rotation
Duration: 8 seconds
Audio: upbeat cheerful music with satisfying sound effects"""
