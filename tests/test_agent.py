"""
Tests for the AMP agent command dispatcher.
Uses mock players so no real Spotify or YouTube Music connection is needed.
Run: pytest tests/test_agent.py -v
"""

import os
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers — lightweight mock players that mimic the real ones' method sigs
# ---------------------------------------------------------------------------

def make_mock_spotify():
    """Create a mock SpotifyPlayer with common methods stubbed."""
    player = MagicMock()
    player.search_and_play.return_value = "Playing - Bohemian Rhapsody by Queen"
    player.play.return_value = "Playing"
    player.pause.return_value = "Paused"
    player.next_track.return_value = "Skipped to next"
    player.previous_track.return_value = "Previous track"
    player.set_volume.return_value = "Volume: 75%"
    player.search.return_value = [
        {"name": "Test Song", "artists": "Test Artist", "uri": "spotify:track:abc"}
    ]
    player.add_to_queue.return_value = "Added to queue: Test Song"
    player.get_recommendations.return_value = [
        {"name": "Rec Song", "artists": "Rec Artist", "uri": "spotify:track:xyz"}
    ]
    player.create_playlist.return_value = "Created 'Chill' with 5 tracks!"
    player.save_current.return_value = "Saved 'Test Song' to library!"
    player.shuffle.return_value = "Shuffle on"
    player.get_current_track.return_value = {
        "name": "Test Song",
        "artists": "Test Artist",
        "is_playing": True,
        "progress_ms": 30_000,
        "duration_ms": 200_000,
    }
    return player


def _make_agent(player):
    """
    Build an AMPAgent without touching any real API.

    Strategy:
     - Patch get_config so no real config/API keys are needed
     - Patch the LLM provider module so the lazy import in __init__ gets a mock
     - After construction, replace agent.llm with a local mock
    """
    mock_cfg = MagicMock()
    mock_cfg.llm.default_provider = "claude"
    mock_cfg.llm.anthropic_api_key = "sk-ant-test"
    mock_cfg.llm.anthropic_model = "claude-haiku-20240307"
    mock_cfg.llm.anthropic_max_tokens = 100

    mock_llm = MagicMock()
    mock_llm.chat.return_value = {"text": "Done!", "tool_use": None}
    mock_llm.chat_simple.return_value = "Done!"

    # Patch get_config in the agent module
    # Patch ClaudeProvider in the llm_provider module it lives in
    with patch("amp.agent.amp_agent.get_config", return_value=mock_cfg), \
         patch("amp.llm.llm_provider.ClaudeProvider", return_value=mock_llm):
        from amp.agent.amp_agent import AMPAgent
        agent = AMPAgent(player)

    # Override with a fresh mock so tests control it cleanly
    agent.llm = mock_llm
    return agent


# ---------------------------------------------------------------------------
# Tests for _execute_function dispatch
# ---------------------------------------------------------------------------

class TestExecuteFunction:
    """AMPAgent._execute_function should call the correct player method."""

    @pytest.fixture
    def player(self):
        return make_mock_spotify()

    @pytest.fixture
    def agent(self, player):
        return _make_agent(player)

    def test_play_music_with_query(self, agent, player):
        result = agent._execute_function("play_music", {"query": "Bohemian Rhapsody"})
        player.search_and_play.assert_called_once_with("Bohemian Rhapsody")
        assert "Playing" in result

    def test_play_music_without_query_resumes(self, agent, player):
        result = agent._execute_function("play_music", {})
        player.play.assert_called_once()

    def test_pause_music(self, agent, player):
        result = agent._execute_function("pause_music", {})
        player.pause.assert_called_once()
        assert "Paused" in result

    def test_skip_track(self, agent, player):
        result = agent._execute_function("skip_track", {})
        player.next_track.assert_called_once()

    def test_previous_track(self, agent, player):
        result = agent._execute_function("previous_track", {})
        player.previous_track.assert_called_once()

    def test_set_volume(self, agent, player):
        result = agent._execute_function("set_volume", {"volume": 75})
        player.set_volume.assert_called_once_with(75)
        assert "75" in result

    def test_search_music_returns_formatted_list(self, agent, player):
        result = agent._execute_function("search_music", {"query": "jazz"})
        player.search.assert_called_once_with("jazz")
        assert "Test Song" in result

    def test_get_now_playing_when_playing(self, agent, player):
        result = agent._execute_function("get_now_playing", {})
        assert "Playing" in result
        assert "Test Song" in result

    def test_get_now_playing_when_nothing(self, agent, player):
        player.get_current_track.return_value = None
        result = agent._execute_function("get_now_playing", {})
        assert "Nothing" in result

    def test_add_to_queue(self, agent, player):
        result = agent._execute_function("add_to_queue", {"query": "Stairway to Heaven"})
        player.add_to_queue.assert_called_once_with("Stairway to Heaven")

    def test_get_recommendations(self, agent, player):
        result = agent._execute_function("get_recommendations", {"mood": "chill"})
        player.get_recommendations.assert_called_once_with("chill")
        assert "Rec Song" in result

    def test_create_playlist(self, agent, player):
        result = agent._execute_function("create_playlist", {"name": "Chill", "mood": "chill", "count": 5})
        player.create_playlist.assert_called_once_with("Chill", "chill", 5)
        assert "Created" in result

    def test_save_current_track(self, agent, player):
        result = agent._execute_function("save_current_track", {})
        player.save_current.assert_called_once()

    def test_toggle_shuffle_on(self, agent, player):
        result = agent._execute_function("toggle_shuffle", {"enabled": True})
        player.shuffle.assert_called_once_with(True)

    def test_unknown_command(self, agent, player):
        result = agent._execute_function("does_not_exist", {})
        assert "Unknown" in result


# ---------------------------------------------------------------------------
# Tests for dynamic system prompt based on player type
# ---------------------------------------------------------------------------

class TestDynamicSystemPrompt:
    """AMPAgent should use a different system prompt for YouTube vs Spotify."""

    def _build(self, player_cls):
        mock_cfg = MagicMock()
        mock_cfg.llm.default_provider = "claude"
        mock_cfg.llm.anthropic_api_key = "sk-ant-test"
        mock_cfg.llm.anthropic_model = "claude-haiku-20240307"
        mock_cfg.llm.anthropic_max_tokens = 100

        with patch("amp.agent.amp_agent.get_config", return_value=mock_cfg), \
             patch("amp.llm.llm_provider.ClaudeProvider"):
            from amp.agent.amp_agent import AMPAgent
            player = MagicMock(spec=player_cls)
            return AMPAgent(player)

    def test_spotify_prompt_mentions_spotify(self):
        from amp.spotify.player import SpotifyPlayer
        agent = self._build(SpotifyPlayer)
        assert "Spotify" in agent.SYSTEM_PROMPT

    def test_youtube_prompt_mentions_browser(self):
        from amp.spotify.youtube_player import YouTubePlayer
        agent = self._build(YouTubePlayer)
        assert "browser" in agent.SYSTEM_PROMPT.lower()
