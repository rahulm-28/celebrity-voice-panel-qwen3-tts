"""
Celebrity Voice Panel - Gradio Web Application
Main entry point for the web interface
"""

import gradio as gr
import json
from pathlib import Path
from typing import List, Optional
import tempfile
import os

from scripts.voice_cloner import VoiceCloner
from scripts.script_generator import ScriptGenerator
from scripts.audio_stitcher import AudioStitcher
from config import Config

# Initialize components
config = Config()
script_gen = ScriptGenerator(config.CHARACTERS_PATH)
stitcher = AudioStitcher()
cloner = None  # Lazy load due to GPU memory


def initialize_cloner():
    """Initialize the voice cloner (lazy loading)."""
    global cloner
    if cloner is None:
        cloner = VoiceCloner(config.MODEL_NAME, config.DEVICE)
        # Load all available voice samples
        for char_id, char_data in script_gen.characters.items():
            sample_path = Path(config.VOICES_DIR) / "samples" / char_data["sample_file"]
            if sample_path.exists():
                # Use actual transcript from config for better voice cloning quality
                transcript = char_data.get("sample_transcript", "Sample voice for cloning.")
                cloner.load_voice_sample(
                    char_id,
                    str(sample_path),
                    transcript
                )


def generate_panel(
    topic: str,
    selected_characters: List[str],
    progress=gr.Progress()
) -> str:
    """
    Generate the full panel audio.

    Args:
        topic: Topic for discussion
        selected_characters: List of character IDs to include

    Returns:
        Path to generated audio file
    """
    progress(0, desc="Initializing...")
    initialize_cloner()

    # Generate script
    progress(0.1, desc="Generating script...")
    script = script_gen.generate_panel_script(topic, selected_characters)

    # Generate audio for each character
    audio_clips = []
    for i, item in enumerate(script):
        progress((0.1 + 0.7 * i / len(script)), desc=f"Generating {item['character_name']}...")

        try:
            audio, sr = cloner.generate_speech(
                item["character_id"],
                item["line"],
                item["language"]
            )
            audio_clips.append((audio, sr))
        except Exception as e:
            print(f"Error generating {item['character_id']}: {e}")
            continue

    if not audio_clips:
        raise gr.Error("No audio clips were generated. Check voice samples.")

    # Stitch together
    progress(0.9, desc="Combining audio...")
    output_path = Path(config.OUTPUT_DIR) / "generated" / f"panel_{topic.replace(' ', '_')}.wav"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    stitcher.stitch_panel(audio_clips, output_path=str(output_path))

    progress(1.0, desc="Done!")
    return str(output_path)


def generate_single_voice(
    character: str,
    text: str,
    language: str
) -> str:
    """
    Generate speech for a single character with custom text.

    Args:
        character: Character ID
        text: Custom text to speak
        language: Language code

    Returns:
        Path to generated audio file
    """
    initialize_cloner()

    output_path = Path(config.OUTPUT_DIR) / "generated" / f"{character}_custom.wav"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cloner.generate_speech(character, text, language, str(output_path))

    return str(output_path)


def get_script_preview(topic: str, characters: List[str]) -> str:
    """Preview the generated script without audio."""
    script = script_gen.generate_panel_script(topic, characters)

    preview = "## Generated Script\n\n"
    for item in script:
        preview += f"**{item['character_name']}** ({item['language']}):\n"
        preview += f"> {item['line']}\n\n"

    return preview


# Custom CSS
custom_css = """
.header { text-align: center; margin-bottom: 20px; }
.disclaimer {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeeba;
    padding: 12px 16px;
    border-radius: 5px;
    margin: 10px 0;
}
.disclaimer strong {
    color: #664d03;
}
"""

# Build Gradio Interface
with gr.Blocks(title="Celebrity Voice Panel - Qwen3-TTS Demo") as app:

    gr.Markdown(
        """
        # Celebrity Voice Panel
        ### AI-Generated Tech Discussion with Famous Voices

        <div class="disclaimer">
        <strong>Disclaimer:</strong> This is a technology demonstration using AI voice cloning.
        All voices are AI-generated for educational/entertainment purposes only.
        Not affiliated with any celebrities shown.
        </div>
        """,
        elem_classes=["header"]
    )

    with gr.Tabs():
        # Tab 1: Panel Mode
        with gr.TabItem("Panel Mode"):
            gr.Markdown("Generate a fun discussion panel with multiple celebrity voices!")

            with gr.Row():
                with gr.Column(scale=1):
                    topic_input = gr.Textbox(
                        label="Topic",
                        placeholder="AI, JavaScript, Startups, Coding...",
                        value="Artificial Intelligence"
                    )

                    character_select = gr.CheckboxGroup(
                        choices=[
                            ("Modi", "modi"),
                            ("Amitabh", "amitabh"),
                            ("SRK", "srk"),
                            ("Trump", "trump")
                        ],
                        value=["modi", "amitabh", "srk", "trump"],
                        label="Select Characters"
                    )

                    preview_btn = gr.Button("Preview Script", variant="secondary")
                    generate_btn = gr.Button("Generate Panel", variant="primary")

                with gr.Column(scale=1):
                    script_preview = gr.Markdown(label="Script Preview")
                    audio_output = gr.Audio(label="Generated Panel", type="filepath")

            preview_btn.click(
                get_script_preview,
                inputs=[topic_input, character_select],
                outputs=[script_preview]
            )

            generate_btn.click(
                generate_panel,
                inputs=[topic_input, character_select],
                outputs=[audio_output]
            )

        # Tab 2: Single Voice Mode
        with gr.TabItem("Single Voice"):
            gr.Markdown("Generate custom text with a single celebrity voice.")

            with gr.Row():
                with gr.Column():
                    single_character = gr.Dropdown(
                        choices=[
                            ("Modi", "modi"),
                            ("Amitabh", "amitabh"),
                            ("SRK", "srk"),
                            ("Trump", "trump")
                        ],
                        value="modi",
                        label="Select Character"
                    )

                    single_language = gr.Dropdown(
                        choices=["Auto", "English", "Japanese", "Korean"],
                        value="Auto",
                        label="Language"
                    )

                    single_text = gr.Textbox(
                        label="Text to Speak",
                        placeholder="Enter your custom text here...",
                        lines=3
                    )

                    single_generate_btn = gr.Button("Generate", variant="primary")

                with gr.Column():
                    single_audio_output = gr.Audio(label="Generated Audio", type="filepath")

            single_generate_btn.click(
                generate_single_voice,
                inputs=[single_character, single_text, single_language],
                outputs=[single_audio_output]
            )

        # Tab 3: About
        with gr.TabItem("About"):
            gr.Markdown(
                """
                ## About This Project

                This demo showcases **Qwen3-TTS-12Hz-1.7B**, an open-source text-to-speech model
                that can clone voices with just 3 seconds of audio.

                ### Technology Stack
                - **Model**: Qwen3-TTS-12Hz-1.7B-Base
                - **Framework**: Gradio
                - **Voice Cloning**: 3-second reference audio
                - **Languages**: 10+ supported

                ### Features
                - Multi-voice panel generation
                - Custom text synthesis
                - Character-appropriate dialogue generation

                ### Credits
                - Model by [Qwen Team (Alibaba Cloud)](https://huggingface.co/Qwen)
                - Demo by [Rahul Mittal](https://github.com/yourusername)

                ### Disclaimer
                This is purely a technology demonstration. All voices are AI-generated
                and should not be used to impersonate real individuals or spread misinformation.

                ---

                **Links**:
                - [GitHub Repository](https://github.com/yourusername/celebrity-voice-panel)
                - [Qwen3-TTS on HuggingFace](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base)
                """
            )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft(),
        css=custom_css
    )
