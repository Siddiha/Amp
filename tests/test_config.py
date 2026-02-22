"""
Tests for AMP configuration management.
Run: pytest tests/test_config.py -v
"""

import os
import pytest
from unittest.mock import patch

# Ensure we're loading a clean config each time
from amp.config import AMPConfig, init_config


class TestAMPConfigDefaults:
    """Verify sensible defaults when no .env or TOML is provided."""

    def setup_method(self):
        # Patch load_dotenv so it does nothing (no real .env file required)
        self.dotenv_patcher = patch("amp.config.amp_config.load_dotenv")
        self.dotenv_patcher.start()

    def teardown_method(self):
        self.dotenv_patcher.stop()

    @patch.dict(os.environ, {}, clear=True)
    def test_default_music_provider_is_youtube(self):
        config = AMPConfig.load()
        assert config.music_provider == "youtube"

    @patch.dict(os.environ, {}, clear=True)
    def test_default_llm_provider_is_claude(self):
        # Default in the dataclass is 'claude'; env var overrides it
        config = AMPConfig.load()
        assert config.llm.default_provider == "claude"

    @patch.dict(os.environ, {"AMP_LLM_PROVIDER": "gemini", "GOOGLE_API_KEY": "test-key"}, clear=True)
    def test_env_overrides_llm_provider(self):
        config = AMPConfig.load()
        assert config.llm.default_provider == "gemini"
        assert config.llm.google_api_key == "test-key"

    @patch.dict(os.environ, {"MUSIC_PROVIDER": "spotify"}, clear=True)
    def test_env_overrides_music_provider(self):
        config = AMPConfig.load()
        assert config.music_provider == "spotify"


class TestAMPConfigValidation:
    """Verify that validate() returns the correct errors."""

    def setup_method(self):
        self.dotenv_patcher = patch("amp.config.amp_config.load_dotenv")
        self.dotenv_patcher.start()

    def teardown_method(self):
        self.dotenv_patcher.stop()

    @patch.dict(os.environ, {"MUSIC_PROVIDER": "spotify"}, clear=True)
    def test_missing_spotify_keys_gives_errors(self):
        config = AMPConfig.load()
        errors = config.validate()
        assert any("SPOTIFY_CLIENT_ID" in e for e in errors)
        assert any("SPOTIFY_CLIENT_SECRET" in e for e in errors)

    @patch.dict(os.environ, {"AMP_LLM_PROVIDER": "gemini"}, clear=True)
    def test_missing_gemini_key_gives_error(self):
        config = AMPConfig.load()
        errors = config.validate()
        assert any("GOOGLE_API_KEY" in e for e in errors)

    @patch.dict(os.environ, {"AMP_LLM_PROVIDER": "groq"}, clear=True)
    def test_missing_groq_key_gives_error(self):
        config = AMPConfig.load()
        errors = config.validate()
        assert any("GROQ_API_KEY" in e for e in errors)

    @patch.dict(
        os.environ,
        {
            "AMP_LLM_PROVIDER": "gemini",
            "GOOGLE_API_KEY": "my-key",
            "MUSIC_PROVIDER": "youtube",
        },
        clear=True,
    )
    def test_valid_youtube_gemini_config_has_no_errors(self):
        config = AMPConfig.load()
        errors = config.validate()
        assert errors == []

    @patch.dict(
        os.environ,
        {
            "AMP_LLM_PROVIDER": "claude",
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "MUSIC_PROVIDER": "youtube",
        },
        clear=True,
    )
    def test_valid_youtube_claude_config_has_no_errors(self):
        config = AMPConfig.load()
        errors = config.validate()
        assert errors == []
