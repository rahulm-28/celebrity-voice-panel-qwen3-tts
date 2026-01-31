"""
Voice Cloner Module
Uses Qwen3-TTS for voice cloning and generation
"""

import torch
import soundfile as sf
from pathlib import Path
from typing import Optional, Tuple
import numpy as np


class VoiceCloner:
    """
    Handles voice cloning using Qwen3-TTS-12Hz-1.7B-Base model.
    """

    def __init__(self, model_name: str = "Qwen/Qwen3-TTS-12Hz-1.7B-Base", device: str = None):
        """
        Initialize the voice cloner.

        Args:
            model_name: HuggingFace model identifier
            device: Device to run model on (cuda:0, mps, cpu, etc.). Auto-detects if None.
        """
        from qwen_tts import Qwen3TTSModel

        # Auto-detect best available device
        if device is None:
            if torch.cuda.is_available():
                device = "cuda:0"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"

        self.device = device

        # Determine dtype and attention implementation based on device
        if device.startswith("cuda") and torch.cuda.is_available():
            # CUDA with flash attention if available
            try:
                import flash_attn
                attn_impl = "flash_attention_2"
            except ImportError:
                attn_impl = "sdpa"  # Scaled dot product attention (PyTorch native)
            dtype = torch.bfloat16
        elif device == "mps":
            # Apple Silicon - use float16 and sdpa
            attn_impl = "sdpa"
            dtype = torch.float32
        else:
            # CPU fallback
            attn_impl = "eager"
            dtype = torch.float32

        print(f"Loading model on device: {device} with dtype: {dtype}")
        self.model = Qwen3TTSModel.from_pretrained(
            model_name,
            device_map=device,
            dtype=dtype,
            attn_implementation=attn_impl,
        )
        print("Model loaded successfully!")
        self.voice_prompts = {}  # Cache for reusable voice prompts

    def load_voice_sample(self, voice_id: str, audio_path: str, transcript: str) -> None:
        """
        Load and cache a voice sample for cloning.

        Args:
            voice_id: Unique identifier for this voice (e.g., "modi", "srk")
            audio_path: Path to the audio sample file
            transcript: Text transcript of what is spoken in the audio
        """
        print(f"Loading voice sample: {voice_id} from {audio_path}")
        prompt = self.model.create_voice_clone_prompt(
            ref_audio=audio_path,
            ref_text=transcript,
            x_vector_only_mode=False,
        )
        self.voice_prompts[voice_id] = prompt
        print(f"Voice sample '{voice_id}' loaded successfully")

    def generate_speech(
        self,
        voice_id: str,
        text: str,
        language: str = "Auto",
        output_path: Optional[str] = None
    ) -> Tuple[np.ndarray, int]:
        """
        Generate speech using a cloned voice.

        Args:
            voice_id: ID of the previously loaded voice
            text: Text to synthesize
            language: Language code (Auto, English, English, etc.)
            output_path: Optional path to save the audio file

        Returns:
            Tuple of (audio_array, sample_rate)
        """
        if voice_id not in self.voice_prompts:
            raise ValueError(f"Voice '{voice_id}' not loaded. Call load_voice_sample first.")

        print(f"Generating speech for '{voice_id}': {text[:50]}...")
        wavs, sr = self.model.generate_voice_clone(
            text=text,
            language=language,
            voice_clone_prompt=self.voice_prompts[voice_id],
        )
        print(f"Generated audio: {len(wavs[0])/sr:.1f} seconds")

        if output_path:
            sf.write(output_path, wavs[0], sr)

        return wavs[0], sr

    def generate_batch(
        self,
        voice_id: str,
        texts: list,
        languages: list,
        output_dir: Optional[str] = None
    ) -> list:
        """
        Generate multiple speech clips with the same voice.

        Args:
            voice_id: ID of the voice to use
            texts: List of texts to synthesize
            languages: List of language codes for each text
            output_dir: Optional directory to save audio files

        Returns:
            List of (audio_array, sample_rate) tuples
        """
        if voice_id not in self.voice_prompts:
            raise ValueError(f"Voice '{voice_id}' not loaded.")

        wavs, sr = self.model.generate_voice_clone(
            text=texts,
            language=languages,
            voice_clone_prompt=self.voice_prompts[voice_id],
        )

        results = []
        for i, wav in enumerate(wavs):
            if output_dir:
                output_path = Path(output_dir) / f"{voice_id}_{i}.wav"
                sf.write(str(output_path), wav, sr)
            results.append((wav, sr))

        return results
