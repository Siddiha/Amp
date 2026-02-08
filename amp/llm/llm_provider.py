"""Claude LLM provider for AMP."""

import json
from typing import List, Dict, Optional, Any

import anthropic

from amp.config import get_config
from amp.utils.logger import get_logger

logger = get_logger("llm.claude")


# Tool definitions for Claude's tool_use API
TOOLS = [
    {
        "name": "play_music",
        "description": "Play a specific song, artist, or resume playback",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Song/artist to search and play. Empty to resume."}
            }
        }
    },
    {
        "name": "pause_music",
        "description": "Pause the current playback",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "skip_track",
        "description": "Skip to the next song",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "previous_track",
        "description": "Go back to previous song",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "search_music",
        "description": "Search for songs without playing",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_now_playing",
        "description": "Get info about currently playing track",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "set_volume",
        "description": "Set playback volume",
        "input_schema": {
            "type": "object",
            "properties": {
                "volume": {"type": "integer", "description": "Volume 0-100"}
            },
            "required": ["volume"]
        }
    },
    {
        "name": "add_to_queue",
        "description": "Add a song to the queue",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Song to add"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_recommendations",
        "description": "Get music recommendations based on mood",
        "input_schema": {
            "type": "object",
            "properties": {
                "mood": {
                    "type": "string",
                    "enum": ["happy", "sad", "chill", "energetic", "focus", "party", "workout", "sleep"]
                }
            }
        }
    },
    {
        "name": "create_playlist",
        "description": "Create a new playlist with AI-curated songs",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Playlist name"},
                "mood": {"type": "string", "description": "Mood/vibe for the playlist"},
                "count": {"type": "integer", "description": "Number of tracks (default 20)"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "save_current_track",
        "description": "Save/like the currently playing song",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "toggle_shuffle",
        "description": "Turn shuffle on or off",
        "input_schema": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "description": "True for on, False for off"}
            },
            "required": ["enabled"]
        }
    }
]


class ClaudeProvider:
    """Anthropic Claude LLM provider."""

    def __init__(self):
        config = get_config()
        self.client = anthropic.Anthropic(api_key=config.llm.anthropic_api_key)
        self.model = config.llm.anthropic_model
        self.max_tokens = config.llm.anthropic_max_tokens
        self.temperature = getattr(config.llm, "anthropic_temperature", 0.7)
        logger.info(f"Claude provider initialized (model: {self.model})")

    def chat(
        self,
        messages: List[Dict],
        system_prompt: str,
        use_tools: bool = True,
    ) -> Dict[str, Any]:
        """Send a message to Claude and get a response.

        Returns a dict with:
            - "text": str or None (text response)
            - "tool_use": dict or None ({"name": str, "input": dict, "id": str})
        """
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": system_prompt,
            "messages": messages,
        }

        if use_tools:
            kwargs["tools"] = TOOLS

        response = self.client.messages.create(**kwargs)

        result = {"text": None, "tool_use": None}

        for block in response.content:
            if block.type == "text":
                result["text"] = block.text
            elif block.type == "tool_use":
                result["tool_use"] = {
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                }

        return result

    def chat_simple(self, messages: List[Dict], system_prompt: str) -> str:
        """Simple chat without tools — just get a text response."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=150,
            temperature=self.temperature,
            system=system_prompt,
            messages=messages,
        )

        for block in response.content:
            if block.type == "text":
                return block.text

        return ""
