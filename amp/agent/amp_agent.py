"""AMP AI Agent — understands commands and controls Spotify via Claude."""

from typing import List, Dict

from amp.spotify.player import SpotifyPlayer
from amp.llm.llm_provider import ClaudeProvider
from amp.utils.logger import get_logger

logger = get_logger("agent")


class AMPAgent:
    """AI brain that understands natural language and controls Spotify."""

    SYSTEM_PROMPT = """You are AMP, a friendly AI music assistant that controls Spotify. You understand natural language and help users with their music.

Your personality: Casual, music-loving, helpful. Use emojis sparingly.

When users give commands:
- "play X" -> use play_music with the query
- "pause/stop" -> use pause_music
- "skip/next" -> use skip_track
- "back/previous" -> use previous_track
- "what's playing" -> use get_now_playing
- "search X" -> use search_music
- "volume X" -> use set_volume
- "queue X" -> use add_to_queue
- "recommend/suggest" -> use get_recommendations
- "create playlist" -> use create_playlist
- "like/save this" -> use save_current_track
- "shuffle on/off" -> use toggle_shuffle

If unsure, ask for clarification. Be concise in responses."""

    def __init__(self, spotify: SpotifyPlayer):
        self.spotify = spotify
        self.llm = ClaudeProvider()
        self.history: List[Dict] = []
        logger.info("AMP Agent initialized")

    def _execute_function(self, name: str, args: Dict) -> str:
        """Execute a Spotify function by name."""
        if name == "play_music":
            query = args.get("query", "")
            if query:
                return self.spotify.search_and_play(query)
            return self.spotify.play()
        elif name == "pause_music":
            return self.spotify.pause()
        elif name == "skip_track":
            return self.spotify.next_track()
        elif name == "previous_track":
            return self.spotify.previous_track()
        elif name == "search_music":
            tracks = self.spotify.search(args["query"])
            if tracks:
                return "\n".join(
                    f"  {i+1}. {t['name']} - {t['artists']}"
                    for i, t in enumerate(tracks)
                )
            return "No results found"
        elif name == "get_now_playing":
            track = self.spotify.get_current_track()
            if track:
                status = "Playing" if track["is_playing"] else "Paused"
                return f"{status}: {track['name']} by {track['artists']}"
            return "Nothing playing"
        elif name == "set_volume":
            return self.spotify.set_volume(args["volume"])
        elif name == "add_to_queue":
            return self.spotify.add_to_queue(args["query"])
        elif name == "get_recommendations":
            tracks = self.spotify.get_recommendations(args.get("mood"))
            if tracks:
                return "Recommendations:\n" + "\n".join(
                    f"  - {t['name']} - {t['artists']}" for t in tracks
                )
            return "Couldn't get recommendations"
        elif name == "create_playlist":
            return self.spotify.create_playlist(
                args["name"], args.get("mood"), args.get("count", 20)
            )
        elif name == "save_current_track":
            return self.spotify.save_current()
        elif name == "toggle_shuffle":
            return self.spotify.shuffle(args["enabled"])
        return "Unknown command"

    def process(self, user_input: str) -> str:
        """Process user input and return a response."""
        self.history.append({"role": "user", "content": user_input})

        # Keep last 10 messages for context
        messages = self.history[-10:]

        try:
            # Ask Claude (with tools)
            result = self.llm.chat(
                messages=messages,
                system_prompt=self.SYSTEM_PROMPT,
                use_tools=True,
            )

            # If Claude wants to call a tool
            if result["tool_use"]:
                tool = result["tool_use"]
                fn_name = tool["name"]
                fn_args = tool["input"]

                logger.info(f"Executing tool: {fn_name}({fn_args})")
                fn_result = self._execute_function(fn_name, fn_args)

                # Send the tool result back to Claude for a natural response
                tool_messages = messages + [
                    {
                        "role": "assistant",
                        "content": [
                            {"type": "tool_use", "id": tool["id"], "name": fn_name, "input": fn_args}
                        ],
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "tool_result", "tool_use_id": tool["id"], "content": fn_result}
                        ],
                    },
                ]

                response_text = self.llm.chat_simple(
                    messages=tool_messages,
                    system_prompt=self.SYSTEM_PROMPT,
                )
            else:
                response_text = result["text"] or "I'm not sure what to do with that."

            self.history.append({"role": "assistant", "content": response_text})
            return response_text

        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            return f"Error: {str(e)}"
