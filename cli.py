"""
Command-line interface for Celebrity Voice Panel
"""

import argparse
import json
from pathlib import Path

from scripts.voice_cloner import VoiceCloner
from scripts.script_generator import ScriptGenerator
from scripts.audio_stitcher import AudioStitcher
from config import Config


def main():
    parser = argparse.ArgumentParser(description="Celebrity Voice Panel CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Panel command
    panel_parser = subparsers.add_parser("panel", help="Generate a panel discussion")
    panel_parser.add_argument("topic", help="Topic for discussion")
    panel_parser.add_argument(
        "--characters",
        nargs="+",
        default=["modi", "amitabh", "srk", "trump"],
        help="Characters to include"
    )
    panel_parser.add_argument("--output", "-o", help="Output file path")

    # Single voice command
    single_parser = subparsers.add_parser("single", help="Generate single voice")
    single_parser.add_argument("character", help="Character ID")
    single_parser.add_argument("text", help="Text to speak")
    single_parser.add_argument("--language", "-l", default="Auto", help="Language")
    single_parser.add_argument("--output", "-o", help="Output file path")

    # List command
    list_parser = subparsers.add_parser("list", help="List available characters/topics")
    list_parser.add_argument("--characters", action="store_true", help="List characters")
    list_parser.add_argument("--topics", action="store_true", help="List topics")

    args = parser.parse_args()

    config = Config()

    if args.command == "panel":
        print(f"Generating panel on topic: {args.topic}")
        print(f"Characters: {', '.join(args.characters)}")

        cloner = VoiceCloner(config.MODEL_NAME, config.DEVICE)
        script_gen = ScriptGenerator(str(config.CHARACTERS_PATH))
        stitcher = AudioStitcher()

        # Load voices
        for char_id in args.characters:
            sample_path = config.VOICES_DIR / "samples" / f"{char_id}.wav"
            if sample_path.exists():
                char_data = script_gen.characters.get(char_id, {})
                transcript = char_data.get("sample_transcript", "Sample voice.")
                cloner.load_voice_sample(char_id, str(sample_path), transcript)
                print(f"Loaded voice: {char_id}")
            else:
                print(f"Missing voice sample: {char_id}")

        # Generate script
        script = script_gen.generate_panel_script(args.topic, args.characters)

        # Generate audio
        audio_clips = []
        for item in script:
            print(f"Generating: {item['character_name']}...")
            try:
                audio, sr = cloner.generate_speech(
                    item["character_id"],
                    item["line"],
                    item["language"]
                )
                audio_clips.append((audio, sr))
            except Exception as e:
                print(f"  Error: {e}")

        # Stitch
        output_path = args.output or f"panel_{args.topic.replace(' ', '_')}.wav"
        stitcher.stitch_panel(audio_clips, output_path=output_path)
        print(f"\nPanel saved to: {output_path}")

    elif args.command == "single":
        print(f"Generating {args.character} saying: {args.text[:50]}...")

        cloner = VoiceCloner(config.MODEL_NAME, config.DEVICE)
        sample_path = config.VOICES_DIR / "samples" / f"{args.character}.wav"

        if not sample_path.exists():
            print(f"Error: Voice sample not found at {sample_path}")
            return

        script_gen = ScriptGenerator(str(config.CHARACTERS_PATH))
        char_data = script_gen.characters.get(args.character, {})
        transcript = char_data.get("sample_transcript", "Sample voice.")
        cloner.load_voice_sample(args.character, str(sample_path), transcript)

        output_path = args.output or f"{args.character}_output.wav"
        cloner.generate_speech(args.character, args.text, args.language, output_path)
        print(f"Audio saved to: {output_path}")

    elif args.command == "list":
        script_gen = ScriptGenerator(str(config.CHARACTERS_PATH))

        if args.characters or not args.topics:
            print("\nAvailable Characters:")
            for char_id in script_gen.get_available_characters():
                print(f"  - {char_id}")

        if args.topics:
            print("\nAvailable Topics:")
            for topic in script_gen.get_available_topics():
                print(f"  - {topic}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
