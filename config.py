"""
Configuration settings for Celebrity Voice Panel
"""

import os
from pathlib import Path


class Config:
    """Application configuration."""

    # Paths
    BASE_DIR = Path(__file__).parent
    VOICES_DIR = BASE_DIR / "voices"
    OUTPUT_DIR = BASE_DIR / "outputs"
    PROMPTS_DIR = BASE_DIR / "prompts"
    CHARACTERS_PATH = PROMPTS_DIR / "character_prompts.json"

    # Model settings
    MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
    # Device auto-detection: None means VoiceCloner will auto-detect (cuda > mps > cpu)
    DEVICE = os.getenv("DEVICE", None)

    # Audio settings
    SAMPLE_RATE = 24000
    PAUSE_BETWEEN_SPEAKERS_MS = 800

    # App settings
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
