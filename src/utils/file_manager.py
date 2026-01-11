"""
Beautelligence Video Pipeline - File Manager

Handles file operations for videos, prompts, and logs.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from config.settings import settings


class FileManager:
    """Manages file operations for the pipeline."""

    def __init__(
        self,
        video_dir: Path | None = None,
        prompt_dir: Path | None = None,
        log_dir: Path | None = None,
    ):
        self.video_dir = video_dir or settings.video_output_dir
        self.prompt_dir = prompt_dir or settings.prompt_log_dir
        self.log_dir = log_dir or settings.log_dir

    def ensure_directories(self) -> None:
        """Create all required directories."""
        for directory in [self.video_dir, self.prompt_dir, self.log_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_video_path(self, keyword: str, extension: str = "mp4") -> Path:
        """
        Generate a unique video file path.

        Args:
            keyword: The keyword used for generation
            extension: File extension (default: mp4)

        Returns:
            Path to the video file
        """
        self.ensure_directories()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = self._sanitize_filename(keyword)
        filename = f"{timestamp}_{safe_keyword}.{extension}"
        return self.video_dir / filename

    def save_prompt_log(
        self,
        keyword: str,
        prompt: str,
        negative_prompt: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """
        Save prompt and metadata to a JSON file.

        Args:
            keyword: The keyword used
            prompt: The generated prompt
            negative_prompt: Optional negative prompt
            metadata: Additional metadata

        Returns:
            Path to the saved log file
        """
        self.ensure_directories()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = self._sanitize_filename(keyword)
        filename = f"{timestamp}_{safe_keyword}.json"

        data = {
            "timestamp": datetime.now().isoformat(),
            "keyword": keyword,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "metadata": metadata or {},
        }

        log_path = self.prompt_dir / filename
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return log_path

    def save_video(self, data: bytes, keyword: str) -> Path:
        """
        Save video data to file.

        Args:
            data: Video binary data
            keyword: The keyword used for generation

        Returns:
            Path to the saved video file
        """
        video_path = self.get_video_path(keyword)
        with open(video_path, "wb") as f:
            f.write(data)
        return video_path

    def get_file_size(self, path: Path) -> int:
        """Get file size in bytes."""
        return path.stat().st_size if path.exists() else 0

    def list_videos(self, limit: int = 50) -> list[Path]:
        """List recent video files."""
        if not self.video_dir.exists():
            return []
        videos = sorted(
            self.video_dir.glob("*.mp4"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return videos[:limit]

    def list_prompt_logs(self, limit: int = 50) -> list[Path]:
        """List recent prompt log files."""
        if not self.prompt_dir.exists():
            return []
        logs = sorted(
            self.prompt_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return logs[:limit]

    def read_prompt_log(self, path: Path) -> dict[str, Any]:
        """Read a prompt log file."""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _sanitize_filename(name: str, max_length: int = 50) -> str:
        """Sanitize a string for use as a filename."""
        # Replace problematic characters
        safe = name.lower()
        for char in ' -/\\:*?"<>|':
            safe = safe.replace(char, "_")
        # Remove consecutive underscores
        while "__" in safe:
            safe = safe.replace("__", "_")
        # Trim and limit length
        safe = safe.strip("_")[:max_length]
        return safe or "untitled"

    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Remove files older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of files removed
        """
        from datetime import timedelta

        threshold = datetime.now() - timedelta(days=days)
        removed = 0

        for directory in [self.video_dir, self.prompt_dir]:
            if not directory.exists():
                continue
            for file_path in directory.iterdir():
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < threshold:
                        file_path.unlink()
                        removed += 1

        return removed
