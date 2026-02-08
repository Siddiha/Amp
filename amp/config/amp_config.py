"""AMP Configuration Management."""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

try:
    import tomli
except ImportError:
    tomli = None

from dotenv import load_dotenv


@dataclass
class SpotifyConfig:
    """Spotify API configuration."""
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8888/callback"
    cache_path: str = ".spotify_cache"
    scopes: list = field(default_factory=lambda: [
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
        "playlist-read-private",
        "playlist-modify-private",
        "playlist-modify-public",
        "user-library-read",
        "user-library-modify",
        "user-top-read",
        "user-read-recently-played",
    ])


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    default_provider: str = "claude"

    # Anthropic Claude (primary)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5-20250929"
    anthropic_max_tokens: int = 300
    anthropic_temperature: float = 0.7

    # OpenAI (optional)
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    openai_max_tokens: int = 300
    openai_temperature: float = 0.7

    # Google Gemini (optional)
    google_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    gemini_max_tokens: int = 300


@dataclass
class MemoryConfig:
    """Memory/storage configuration."""
    database_path: str = "amp_data.db"
    max_conversation_history: int = 20
    max_listening_history: int = 1000
    cache_ttl_seconds: int = 300


@dataclass
class CLIConfig:
    """CLI interface configuration."""
    theme: str = "dark"
    show_now_playing: bool = True
    show_progress_bar: bool = True
    auto_refresh_interval: int = 5


@dataclass
class AMPConfig:
    """Main AMP configuration."""

    spotify: SpotifyConfig = field(default_factory=SpotifyConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    cli: CLIConfig = field(default_factory=CLIConfig)

    # App settings
    debug: bool = False
    log_level: str = "INFO"
    log_file: Optional[str] = None
    music_provider: str = "youtube"  # "spotify" or "youtube"

    @classmethod
    def load(cls, config_path: Optional[str] = None, env_file: Optional[str] = None) -> "AMPConfig":
        """Load configuration from TOML file and environment variables."""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        config = cls()

        if config_path and Path(config_path).exists() and tomli:
            config._load_toml(config_path)

        config._load_env()
        return config

    def _load_toml(self, path: str) -> None:
        """Load settings from TOML file."""
        with open(path, "rb") as f:
            data = tomli.load(f)

        if "spotify" in data:
            sp = data["spotify"]
            self.spotify.redirect_uri = sp.get("redirect_uri", self.spotify.redirect_uri)
            self.spotify.cache_path = sp.get("cache_path", self.spotify.cache_path)
            if "scopes" in sp:
                self.spotify.scopes = sp["scopes"]

        if "llm" in data:
            llm = data["llm"]
            self.llm.default_provider = llm.get("default_provider", self.llm.default_provider)
            self.llm.anthropic_model = llm.get("anthropic_model", self.llm.anthropic_model)
            self.llm.anthropic_max_tokens = llm.get("anthropic_max_tokens", self.llm.anthropic_max_tokens)
            self.llm.openai_model = llm.get("openai_model", self.llm.openai_model)
            self.llm.openai_max_tokens = llm.get("openai_max_tokens", self.llm.openai_max_tokens)
            self.llm.openai_temperature = llm.get("openai_temperature", self.llm.openai_temperature)
            self.llm.gemini_model = llm.get("gemini_model", self.llm.gemini_model)
            self.llm.gemini_max_tokens = llm.get("gemini_max_tokens", self.llm.gemini_max_tokens)

        if "memory" in data:
            mem = data["memory"]
            self.memory.database_path = mem.get("database_path", self.memory.database_path)
            self.memory.max_conversation_history = mem.get("max_conversation_history", self.memory.max_conversation_history)
            self.memory.max_listening_history = mem.get("max_listening_history", self.memory.max_listening_history)
            self.memory.cache_ttl_seconds = mem.get("cache_ttl_seconds", self.memory.cache_ttl_seconds)

        if "cli" in data:
            cli = data["cli"]
            self.cli.theme = cli.get("theme", self.cli.theme)
            self.cli.show_now_playing = cli.get("show_now_playing", self.cli.show_now_playing)
            self.cli.show_progress_bar = cli.get("show_progress_bar", self.cli.show_progress_bar)
            self.cli.auto_refresh_interval = cli.get("auto_refresh_interval", self.cli.auto_refresh_interval)

        if "app" in data:
            app = data["app"]
            self.debug = app.get("debug", self.debug)
            self.log_level = app.get("log_level", self.log_level)
            self.log_file = app.get("log_file", self.log_file)

    def _load_env(self) -> None:
        """Load settings from environment variables."""
        # Music provider
        self.music_provider = os.getenv("MUSIC_PROVIDER", "youtube").lower()

        # Spotify
        self.spotify.client_id = os.getenv("SPOTIFY_CLIENT_ID", "")
        self.spotify.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "")
        if os.getenv("SPOTIFY_REDIRECT_URI"):
            self.spotify.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

        # LLM API keys
        self.llm.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.llm.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.llm.google_api_key = os.getenv("GOOGLE_API_KEY", "")

        if os.getenv("AMP_LLM_PROVIDER"):
            self.llm.default_provider = os.getenv("AMP_LLM_PROVIDER")

        if os.getenv("AMP_DEBUG"):
            self.debug = os.getenv("AMP_DEBUG", "").lower() in ("true", "1", "yes")

        if os.getenv("AMP_LOG_LEVEL"):
            self.log_level = os.getenv("AMP_LOG_LEVEL")

    def validate(self) -> list:
        """Validate configuration and return list of errors."""
        errors = []

        # Only validate Spotify keys if using Spotify
        if self.music_provider == "spotify":
            if not self.spotify.client_id:
                errors.append("SPOTIFY_CLIENT_ID is required when using Spotify")
            if not self.spotify.client_secret:
                errors.append("SPOTIFY_CLIENT_SECRET is required when using Spotify")

        # Validate LLM provider
        provider = self.llm.default_provider
        if provider == "claude" and not self.llm.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY is required when using Claude")
        elif provider == "openai" and not self.llm.openai_api_key:
            errors.append("OPENAI_API_KEY is required when using OpenAI")
        elif provider == "gemini" and not self.llm.google_api_key:
            errors.append("GOOGLE_API_KEY is required when using Gemini")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (masks sensitive values)."""
        return {
            "spotify": {
                "client_id": "***" if self.spotify.client_id else "",
                "redirect_uri": self.spotify.redirect_uri,
            },
            "llm": {
                "default_provider": self.llm.default_provider,
                "anthropic_configured": bool(self.llm.anthropic_api_key),
                "openai_configured": bool(self.llm.openai_api_key),
                "google_configured": bool(self.llm.google_api_key),
            },
            "debug": self.debug,
            "log_level": self.log_level,
        }


# Global config instance
_config: Optional[AMPConfig] = None


def get_config() -> AMPConfig:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = AMPConfig.load()
    return _config


def init_config(config_path: Optional[str] = None, env_file: Optional[str] = None) -> AMPConfig:
    """Initialize global config."""
    global _config
    _config = AMPConfig.load(config_path, env_file)
    return _config
