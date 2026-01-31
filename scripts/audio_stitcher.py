"""
Audio Stitcher Module
Combines multiple audio clips with transitions
"""

import numpy as np
import soundfile as sf
from pathlib import Path
from typing import List, Tuple, Optional


class AudioStitcher:
    """
    Combines multiple audio clips into a single panel recording.
    """

    def __init__(self, default_sample_rate: int = 24000):
        """
        Initialize the audio stitcher.

        Args:
            default_sample_rate: Default sample rate for output
        """
        self.sample_rate = default_sample_rate

    def add_silence(self, duration_ms: int) -> np.ndarray:
        """
        Generate silence of specified duration.

        Args:
            duration_ms: Duration in milliseconds

        Returns:
            Numpy array of zeros
        """
        num_samples = int(self.sample_rate * duration_ms / 1000)
        return np.zeros(num_samples, dtype=np.float32)

    def normalize_audio(self, audio: np.ndarray, target_db: float = -20.0) -> np.ndarray:
        """
        Normalize audio to target dB level.

        Args:
            audio: Input audio array
            target_db: Target loudness in dB

        Returns:
            Normalized audio array
        """
        rms = np.sqrt(np.mean(audio**2))
        if rms > 0:
            target_rms = 10 ** (target_db / 20)
            audio = audio * (target_rms / rms)
        return np.clip(audio, -1.0, 1.0)

    def crossfade(
        self,
        audio1: np.ndarray,
        audio2: np.ndarray,
        fade_duration_ms: int = 50
    ) -> np.ndarray:
        """
        Apply crossfade between two audio clips.

        Args:
            audio1: First audio clip
            audio2: Second audio clip
            fade_duration_ms: Duration of crossfade in milliseconds

        Returns:
            Combined audio with crossfade
        """
        fade_samples = int(self.sample_rate * fade_duration_ms / 1000)

        if len(audio1) < fade_samples or len(audio2) < fade_samples:
            return np.concatenate([audio1, audio2])

        # Create fade curves
        fade_out = np.linspace(1.0, 0.0, fade_samples)
        fade_in = np.linspace(0.0, 1.0, fade_samples)

        # Apply fades
        audio1_end = audio1[-fade_samples:] * fade_out
        audio2_start = audio2[:fade_samples] * fade_in

        # Combine
        crossfaded = audio1_end + audio2_start

        return np.concatenate([
            audio1[:-fade_samples],
            crossfaded,
            audio2[fade_samples:]
        ])

    def stitch_panel(
        self,
        audio_clips: List[Tuple[np.ndarray, int]],
        pause_between_ms: int = 800,
        normalize: bool = True,
        output_path: Optional[str] = None
    ) -> Tuple[np.ndarray, int]:
        """
        Stitch multiple audio clips into a panel recording.

        Args:
            audio_clips: List of (audio_array, sample_rate) tuples
            pause_between_ms: Pause between speakers in milliseconds
            normalize: Whether to normalize each clip
            output_path: Optional path to save the final audio

        Returns:
            Tuple of (combined_audio, sample_rate)
        """
        if not audio_clips:
            raise ValueError("No audio clips provided")

        # Resample all clips to the same sample rate if needed
        resampled_clips = []
        for audio, sr in audio_clips:
            if sr != self.sample_rate:
                # Simple resampling (for production, use librosa.resample)
                ratio = self.sample_rate / sr
                new_length = int(len(audio) * ratio)
                indices = np.linspace(0, len(audio) - 1, new_length).astype(int)
                audio = audio[indices]

            if normalize:
                audio = self.normalize_audio(audio)

            resampled_clips.append(audio)

        # Combine with pauses
        silence = self.add_silence(pause_between_ms)
        combined = resampled_clips[0]

        for clip in resampled_clips[1:]:
            combined = np.concatenate([combined, silence, clip])

        if output_path:
            sf.write(output_path, combined, self.sample_rate)

        return combined, self.sample_rate

    def add_intro_outro(
        self,
        main_audio: np.ndarray,
        intro_path: Optional[str] = None,
        outro_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Add intro and outro audio to the main panel.

        Args:
            main_audio: Main panel audio
            intro_path: Path to intro audio file
            outro_path: Path to outro audio file

        Returns:
            Combined audio with intro/outro
        """
        result = main_audio

        if intro_path:
            intro, _ = sf.read(intro_path)
            result = self.crossfade(intro, result)

        if outro_path:
            outro, _ = sf.read(outro_path)
            result = self.crossfade(result, outro)

        return result
