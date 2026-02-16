"""Google Gemini LLM provider for AMP."""

import json
import uuid
from typing import List, Dict, Any

from google import genai
from google.genai import types

from amp.config import get_config
from amp.utils.logger import get_logger

logger = get_logger("llm.gemini")

# Same tools as Claude, converted to Gemini FunctionDeclaration format
TOOLS = [
    types.FunctionDeclaration(
        name="play_music",
        description="Play a specific song, artist, or resume playback",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "query": types.Schema(type="STRING", description="Song/artist to search and play. Empty to resume.")
            },
        ),
    ),
    types.FunctionDeclaration(
        name="pause_music",
        description="Pause the current playback",
        parameters=types.Schema(type="OBJECT", properties={}),
    ),
    types.FunctionDeclaration(
        name="skip_track",
        description="Skip to the next song",
        parameters=types.Schema(type="OBJECT", properties={}),
    ),
    types.FunctionDeclaration(
        name="previous_track",
        description="Go back to previous song",
        parameters=types.Schema(type="OBJECT", properties={}),
    ),
    types.FunctionDeclaration(
        name="search_music",
        description="Search for songs without playing",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "query": types.Schema(type="STRING", description="What to search for")
            },
            required=["query"],
        ),
    ),
    types.FunctionDeclaration(
        name="get_now_playing",
        description="Get info about currently playing track",
        parameters=types.Schema(type="OBJECT", properties={}),
    ),
    types.FunctionDeclaration(
        name="set_volume",
        description="Set playback volume",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "volume": types.Schema(type="INTEGER", description="Volume 0-100")
            },
            required=["volume"],
        ),
    ),
    types.FunctionDeclaration(
        name="add_to_queue",
        description="Add a song to the queue",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "query": types.Schema(type="STRING", description="Song to add")
            },
            required=["query"],
        ),
    ),
    types.FunctionDeclaration(
        name="get_recommendations",
        description="Get music recommendations based on mood",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "mood": types.Schema(
                    type="STRING",
                    description="Mood category",
                    enum=["happy", "sad", "chill", "energetic", "focus", "party", "workout", "sleep"],
                )
            },
        ),
    ),
    types.FunctionDeclaration(
        name="create_playlist",
        description="Create a new playlist with AI-curated songs",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "name": types.Schema(type="STRING", description="Playlist name"),
                "mood": types.Schema(type="STRING", description="Mood/vibe for the playlist"),
                "count": types.Schema(type="INTEGER", description="Number of tracks (default 20)"),
            },
            required=["name"],
        ),
    ),
    types.FunctionDeclaration(
        name="save_current_track",
        description="Save/like the currently playing song",
        parameters=types.Schema(type="OBJECT", properties={}),
    ),
    types.FunctionDeclaration(
        name="toggle_shuffle",
        description="Turn shuffle on or off",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "enabled": types.Schema(type="BOOLEAN", description="True for on, False for off")
            },
            required=["enabled"],
        ),
    ),
]


class GeminiProvider:
    """Google Gemini LLM provider."""

    def __init__(self):
        config = get_config()
        self.client = genai.Client(api_key=config.llm.google_api_key)
        self.model = config.llm.gemini_model
        self.max_tokens = config.llm.gemini_max_tokens
        logger.info(f"Gemini provider initialized (model: {self.model})")

    def chat(
        self,
        messages: List[Dict],
        system_prompt: str,
        use_tools: bool = True,
    ) -> Dict[str, Any]:
        """Send a message to Gemini and get a response.

        Returns a dict with:
            - "text": str or None
            - "tool_use": dict or None ({"name": str, "input": dict, "id": str})
        """
        # Convert messages to Gemini format
        gemini_contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            content = msg["content"]
            if isinstance(content, str):
                gemini_contents.append(types.Content(role=role, parts=[types.Part.from_text(text=content)]))

        config_kwargs = {
            "system_instruction": system_prompt,
            "max_output_tokens": self.max_tokens,
            "temperature": 0.7,
        }

        if use_tools:
            config_kwargs["tools"] = [types.Tool(function_declarations=TOOLS)]
            config_kwargs["automatic_function_calling"] = types.AutomaticFunctionCallingConfig(disable=True)

        response = self.client.models.generate_content(
            model=self.model,
            contents=gemini_contents,
            config=types.GenerateContentConfig(**config_kwargs),
        )

        result = {"text": None, "tool_use": None}

        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    fc = part.function_call
                    result["tool_use"] = {
                        "id": f"call_{uuid.uuid4().hex[:12]}",
                        "name": fc.name,
                        "input": dict(fc.args) if fc.args else {},
                    }
                elif part.text:
                    result["text"] = part.text

        return result

    def chat_simple(self, messages: List[Dict], system_prompt: str) -> str:
        """Simple chat without tools — just get a text response."""
        gemini_contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            content = msg["content"]
            if isinstance(content, str):
                gemini_contents.append(types.Content(role=role, parts=[types.Part.from_text(text=content)]))
            elif isinstance(content, list):
                # Tool result messages — extract text content for simple chat
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        text = block.get("content", "")
                        gemini_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=text)]))

        response = self.client.models.generate_content(
            model=self.model,
            contents=gemini_contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=150,
                temperature=0.7,
            ),
        )

        if response.text:
            return response.text
        return ""
