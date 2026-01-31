"""
Script Generator Module
Generates character-appropriate dialogues for the panel
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional


class ScriptGenerator:
    """
    Generates contextually appropriate scripts for each character.
    """

    def __init__(self, characters_path: str = "prompts/character_prompts.json"):
        """
        Initialize with character definitions.

        Args:
            characters_path: Path to the characters JSON file
        """
        with open(characters_path, 'r', encoding='utf-8') as f:
            self.characters = json.load(f)

        # Load topic aliases
        templates_path = Path(characters_path).parent / "topic_templates.json"
        if templates_path.exists():
            with open(templates_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
                self.topic_aliases = templates.get("topic_aliases", {})
        else:
            self.topic_aliases = {}

    def _normalize_topic(self, topic: str) -> str:
        """Convert topic to canonical form using aliases."""
        topic_lower = topic.lower().strip()
        # Check if it's an alias
        if topic_lower in self.topic_aliases:
            return self.topic_aliases[topic_lower]
        # Check if it's already a canonical topic
        return topic_lower

    def generate_panel_script(
        self,
        topic: str,
        character_order: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Generate a full panel script for a given topic.

        Args:
            topic: The topic to discuss (AI, coding, startups, etc.)
            character_order: Optional custom order of characters

        Returns:
            List of dicts with character info and their lines
        """
        if character_order is None:
            character_order = ["modi", "amitabh", "srk", "trump"]

        script = []
        normalized_topic = self._normalize_topic(topic)

        for char_id in character_order:
            if char_id not in self.characters:
                continue

            char = self.characters[char_id]

            # Get topic-specific line or generate generic one
            if normalized_topic in char.get("topics", {}):
                line = char["topics"][normalized_topic]
            else:
                # Generate a meaningful generic line based on character style
                intro = random.choice(char.get("intro_phrases", [""]))
                line = f"{intro} {topic} is an important subject that deserves our attention and thoughtful discussion."

            script.append({
                "character_id": char_id,
                "character_name": char["name"],
                "language": char["language"],
                "line": line,
                "sample_file": char.get("sample_file", f"{char_id}.wav")
            })

        return script

    def generate_custom_line(
        self,
        character_id: str,
        topic: str,
        custom_text: Optional[str] = None
    ) -> Dict:
        """
        Generate a single character's line.

        Args:
            character_id: ID of the character
            topic: Topic to discuss
            custom_text: Optional custom text to use

        Returns:
            Dict with character info and their line
        """
        if character_id not in self.characters:
            raise ValueError(f"Unknown character: {character_id}")

        char = self.characters[character_id]

        normalized_topic = self._normalize_topic(topic)

        if custom_text:
            line = custom_text
        elif normalized_topic in char.get("topics", {}):
            line = char["topics"][normalized_topic]
        else:
            intro = random.choice(char.get("intro_phrases", [""]))
            line = f"{intro} Let me share my thoughts on {topic}."

        return {
            "character_id": character_id,
            "character_name": char["name"],
            "language": char["language"],
            "line": line,
            "sample_file": char.get("sample_file", f"{character_id}.wav")
        }

    def get_available_characters(self) -> List[str]:
        """Return list of available character IDs."""
        return list(self.characters.keys())

    def get_available_topics(self) -> List[str]:
        """Return list of pre-defined topics."""
        topics = set()
        for char in self.characters.values():
            topics.update(char.get("topics", {}).keys())
        return list(topics)
