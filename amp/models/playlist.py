"""Playlist model representing a Spotify playlist."""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

from .track import Track


@dataclass
class Playlist:
    """Represents a Spotify playlist."""

    uri: str
    name: str
    description: str = ""
    owner_id: str = ""
    owner_name: str = ""
    is_public: bool = True
    is_collaborative: bool = False

    # Tracks
    tracks: List[Track] = field(default_factory=list)
    total_tracks: int = 0

    # Images
    image_url: Optional[str] = None

    # Metadata
    followers: int = 0
    snapshot_id: str = ""
    external_url: Optional[str] = None

    # Local metadata
    mood: Optional[str] = None
    created_by_amp: bool = False
    created_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None

    @property
    def id(self) -> str:
        """Extract playlist ID from URI."""
        return self.uri.split(":")[-1] if self.uri else ""

    @property
    def duration_ms(self) -> int:
        """Get total duration of all tracks."""
        return sum(t.duration_ms for t in self.tracks)

    @property
    def duration_str(self) -> str:
        """Get total duration as human-readable string."""
        total_seconds = self.duration_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    @classmethod
    def from_spotify_dict(cls, data: dict, include_tracks: bool = False) -> "Playlist":
        """Create Playlist from Spotify API response."""
        images = data.get("images", [])
        owner = data.get("owner", {})

        playlist = cls(
            uri=data.get("uri", ""),
            name=data.get("name", "Unnamed Playlist"),
            description=data.get("description", ""),
            owner_id=owner.get("id", ""),
            owner_name=owner.get("display_name", ""),
            is_public=data.get("public", True),
            is_collaborative=data.get("collaborative", False),
            total_tracks=data.get("tracks", {}).get("total", 0),
            image_url=images[0]["url"] if images else None,
            followers=data.get("followers", {}).get("total", 0),
            snapshot_id=data.get("snapshot_id", ""),
            external_url=data.get("external_urls", {}).get("spotify"),
        )

        if include_tracks and "tracks" in data:
            track_items = data["tracks"].get("items", [])
            for item in track_items:
                if item and item.get("track"):
                    playlist.tracks.append(Track.from_spotify_dict(item["track"]))

        return playlist

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "owner_name": self.owner_name,
            "is_public": self.is_public,
            "is_collaborative": self.is_collaborative,
            "total_tracks": self.total_tracks,
            "image_url": self.image_url,
            "mood": self.mood,
            "created_by_amp": self.created_by_amp,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def add_track(self, track: Track) -> None:
        """Add a track to the playlist."""
        self.tracks.append(track)
        self.total_tracks = len(self.tracks)

    def remove_track(self, uri: str) -> bool:
        """Remove a track from the playlist by URI."""
        for i, track in enumerate(self.tracks):
            if track.uri == uri:
                self.tracks.pop(i)
                self.total_tracks = len(self.tracks)
                return True
        return False

    def __str__(self) -> str:
        return f"{self.name} ({self.total_tracks} tracks)"

    def __repr__(self) -> str:
        return f"Playlist(name='{self.name}', uri='{self.uri}', tracks={self.total_tracks})"
