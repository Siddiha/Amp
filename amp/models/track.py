"""Track model representing a Spotify track."""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Track:
    """Represents a Spotify track with all relevant metadata."""

    uri: str
    name: str
    artists: List[str]
    album: str = ""
    album_uri: str = ""
    duration_ms: int = 0
    popularity: int = 0
    explicit: bool = False
    preview_url: Optional[str] = None

    # Audio features (from Spotify API)
    danceability: float = 0.0
    energy: float = 0.0
    valence: float = 0.0  # Musical positiveness
    tempo: float = 0.0
    instrumentalness: float = 0.0
    acousticness: float = 0.0

    # Playback state (when currently playing)
    is_playing: bool = False
    progress_ms: int = 0

    # Metadata
    added_at: Optional[datetime] = None
    played_at: Optional[datetime] = None
    play_count: int = 0

    @property
    def id(self) -> str:
        """Extract track ID from URI."""
        return self.uri.split(":")[-1] if self.uri else ""

    @property
    def artists_str(self) -> str:
        """Get artists as comma-separated string."""
        return ", ".join(self.artists)

    @property
    def duration_str(self) -> str:
        """Get duration as mm:ss string."""
        seconds = self.duration_ms // 1000
        return f"{seconds // 60}:{seconds % 60:02d}"

    @property
    def progress_str(self) -> str:
        """Get progress as mm:ss string."""
        seconds = self.progress_ms // 1000
        return f"{seconds // 60}:{seconds % 60:02d}"

    @property
    def progress_percent(self) -> float:
        """Get playback progress as percentage (0-1)."""
        if self.duration_ms == 0:
            return 0.0
        return self.progress_ms / self.duration_ms

    @classmethod
    def from_spotify_dict(cls, data: dict, playback_data: Optional[dict] = None) -> "Track":
        """Create Track from Spotify API response."""
        track = cls(
            uri=data.get("uri", ""),
            name=data.get("name", "Unknown"),
            artists=[a["name"] for a in data.get("artists", [])],
            album=data.get("album", {}).get("name", ""),
            album_uri=data.get("album", {}).get("uri", ""),
            duration_ms=data.get("duration_ms", 0),
            popularity=data.get("popularity", 0),
            explicit=data.get("explicit", False),
            preview_url=data.get("preview_url"),
        )

        if playback_data:
            track.is_playing = playback_data.get("is_playing", False)
            track.progress_ms = playback_data.get("progress_ms", 0)

        return track

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "uri": self.uri,
            "name": self.name,
            "artists": self.artists,
            "album": self.album,
            "album_uri": self.album_uri,
            "duration_ms": self.duration_ms,
            "popularity": self.popularity,
            "explicit": self.explicit,
            "danceability": self.danceability,
            "energy": self.energy,
            "valence": self.valence,
            "tempo": self.tempo,
            "instrumentalness": self.instrumentalness,
            "acousticness": self.acousticness,
            "play_count": self.play_count,
        }

    def __str__(self) -> str:
        return f"{self.name} by {self.artists_str}"

    def __repr__(self) -> str:
        return f"Track(name='{self.name}', artists={self.artists}, uri='{self.uri}')"
