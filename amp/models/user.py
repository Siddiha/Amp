"""User model representing a Spotify user."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class User:
    """Represents a Spotify user with preferences."""

    id: str
    display_name: str
    email: str = ""
    country: str = ""
    product: str = "free"  # free, premium, etc.
    profile_url: Optional[str] = None
    image_url: Optional[str] = None

    # User preferences (stored locally)
    preferred_llm: str = "claude"
    favorite_genres: List[str] = field(default_factory=list)
    favorite_artists: List[str] = field(default_factory=list)
    mood_preferences: Dict[str, Any] = field(default_factory=dict)

    # Settings
    auto_play_recommendations: bool = True
    show_explicit: bool = True
    default_playlist_size: int = 20
    volume_default: int = 50

    # Stats
    total_plays: int = 0
    total_playlists_created: int = 0
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None

    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription."""
        return self.product == "premium"

    @classmethod
    def from_spotify_dict(cls, data: dict) -> "User":
        """Create User from Spotify API response."""
        images = data.get("images", [])
        return cls(
            id=data.get("id", ""),
            display_name=data.get("display_name", "User"),
            email=data.get("email", ""),
            country=data.get("country", ""),
            product=data.get("product", "free"),
            profile_url=data.get("external_urls", {}).get("spotify"),
            image_url=images[0]["url"] if images else None,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "display_name": self.display_name,
            "email": self.email,
            "country": self.country,
            "product": self.product,
            "profile_url": self.profile_url,
            "image_url": self.image_url,
            "preferred_llm": self.preferred_llm,
            "favorite_genres": self.favorite_genres,
            "favorite_artists": self.favorite_artists,
            "mood_preferences": self.mood_preferences,
            "auto_play_recommendations": self.auto_play_recommendations,
            "show_explicit": self.show_explicit,
            "default_playlist_size": self.default_playlist_size,
            "volume_default": self.volume_default,
            "total_plays": self.total_plays,
            "total_playlists_created": self.total_playlists_created,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create User from stored dictionary."""
        return cls(
            id=data.get("id", ""),
            display_name=data.get("display_name", "User"),
            email=data.get("email", ""),
            country=data.get("country", ""),
            product=data.get("product", "free"),
            profile_url=data.get("profile_url"),
            image_url=data.get("image_url"),
            preferred_llm=data.get("preferred_llm", "claude"),
            favorite_genres=data.get("favorite_genres", []),
            favorite_artists=data.get("favorite_artists", []),
            mood_preferences=data.get("mood_preferences", {}),
            auto_play_recommendations=data.get("auto_play_recommendations", True),
            show_explicit=data.get("show_explicit", True),
            default_playlist_size=data.get("default_playlist_size", 20),
            volume_default=data.get("volume_default", 50),
            total_plays=data.get("total_plays", 0),
            total_playlists_created=data.get("total_playlists_created", 0),
        )

    def __str__(self) -> str:
        return f"{self.display_name} ({self.id})"
