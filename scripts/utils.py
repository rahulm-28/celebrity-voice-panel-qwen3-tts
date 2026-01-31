"""
Utility functions for Celebrity Voice Panel
"""

import os
from pathlib import Path
from typing import Optional


def ensure_dir(path: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object for the directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_voice_sample_path(voice_id: str, voices_dir: str = "voices/samples") -> Optional[Path]:
    """
    Get the path to a voice sample file.

    Args:
        voice_id: ID of the voice (e.g., "modi", "srk")
        voices_dir: Directory containing voice samples

    Returns:
        Path to the voice sample file, or None if not found
    """
    sample_path = Path(voices_dir) / f"{voice_id}.wav"
    if sample_path.exists():
        return sample_path
    return None


def validate_audio_file(path: str) -> bool:
    """
    Validate that a file is a valid audio file.

    Args:
        path: Path to the audio file

    Returns:
        True if valid, False otherwise
    """
    valid_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    file_path = Path(path)
    return file_path.exists() and file_path.suffix.lower() in valid_extensions


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "1:23" or "0:05")
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be used as a filename.

    Args:
        name: Original name

    Returns:
        Sanitized filename
    """
    # Replace spaces and special characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.replace(' ', '_')
