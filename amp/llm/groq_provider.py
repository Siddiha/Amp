"""Groq LLM provider for AMP — free and fast (Llama 3)."""

import json
from typing import List, Dict, Any

from groq import Groq

from amp.config import get_config
from amp.utils.logger import get_logger

logger = get_logger("llm.groq")

# Same tools as Claude, in OpenAI-compatible format (Groq uses this)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Play a specific song, artist, or resume playback",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Song/artist to search and play. Empty to resume."}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pause_music",
            "description": "Pause the current playback",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "skip_track",
            "description": "Skip to the next song",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "previous_track",
            "description": "Go back to previous song",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_music",
            "description": "Search for songs without playing",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_now_playing",
            "description": "Get info about currently playing track",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Set playback volume",
            "parameters": {
                "type": "object",
                "properties": {
                    "volume": {"type": "integer", "description": "Volume 0-100"}
                },
                "required": ["volume"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_queue",
            "description": "Add a song to the queue",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Song to add"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recommendations",
            "description": "Get music recommendations based on mood",
            "parameters": {
                "type": "object",
                "properties": {
                    "mood": {
                        "type": "string",
                        "enum": ["happy", "sad", "chill", "energetic", "focus", "party", "workout", "sleep"],
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_playlist",
            "description": "Create a new playlist with AI-curated songs",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Playlist name"},
                    "mood": {"type": "string", "description": "Mood/vibe for the playlist"},
                    "count": {"type": "integer", "description": "Number of tracks (default 20)"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_current_track",
            "description": "Save/like the currently playing song",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_shuffle",
            "description": "Turn shuffle on or off",
            "parameters": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean", "description": "True for on, False for off"}
                },
                "required": ["enabled"],
            },
        },
    },
]


class GroqProvider:
    """Groq LLM provider (free, fast Llama 3)."""

    def __init__(self):
        config = get_config()
        self.client = Groq(api_key=config.llm.groq_api_key)
        self.model = getattr(config.llm, "groq_model", "llama-3.3-70b-versatile")
        self.max_tokens = 300
        logger.info(f"Groq provider initialized (model: {self.model})")

    def chat(
        self,
        messages: List[Dict],
        system_prompt: str,
        use_tools: bool = True,
    ) -> Dict[str, Any]:
        """Send a message to Groq and get a response.

        Returns a dict with:
            - "text": str or None
            - "tool_use": dict or None ({"name": str, "input": dict, "id": str})
        """
        groq_messages = [{"role": "system", "content": system_prompt}]

        for msg in messages:
            if isinstance(msg["content"], str):
                groq_messages.append({"role": msg["role"], "content": msg["content"]})

        kwargs = {
            "model": self.model,
            "messages": groq_messages,
            "max_tokens": self.max_tokens,
            "temperature": 0.7,
        }

        if use_tools:
            kwargs["tools"] = TOOLS
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        result = {"text": None, "tool_use": None}

        if choice.message.tool_calls:
            tc = choice.message.tool_calls[0]
            result["tool_use"] = {
                "id": tc.id,
                "name": tc.function.name,
                "input": json.loads(tc.function.arguments) if tc.function.arguments else {},
            }

        if choice.message.content:
            result["text"] = choice.message.content

        return result

    def chat_simple(self, messages: List[Dict], system_prompt: str) -> str:
        """Simple chat without tools — just get a text response."""
        groq_messages = [{"role": "system", "content": system_prompt}]

        for msg in messages:
            if isinstance(msg["content"], str):
                groq_messages.append({"role": msg["role"], "content": msg["content"]})
            elif isinstance(msg["content"], list):
                for block in msg["content"]:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        groq_messages.append({"role": "user", "content": block.get("content", "")})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=groq_messages,
            max_tokens=150,
            temperature=0.7,
        )

        return response.choices[0].message.content or ""
