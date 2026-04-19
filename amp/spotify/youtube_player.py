"""YouTube Music player service for AMP."""

from typing import Optional, List
import webbrowser

from ytmusicapi import YTMusic

from amp.models import Track
from amp.utils.logger import get_logger
from amp.utils.cache_manager import cache

logger = get_logger("youtube")


class YouTubePlayer:
    """Handles all YouTube Music interactions."""

    def __init__(self):
        self.yt = YTMusic()
        self.current_video_id: Optional[str] = None
        self.current_track_info: Optional[dict] = None
        logger.info("YouTube Music player initialized")

    def get_current_track(self) -> Optional[Track]:
        """Get currently playing track info."""
        if self.current_track_info:
            return Track(
                uri=f"https://music.youtube.com/watch?v={self.current_video_id}",
                name=self.current_track_info.get("title", "Unknown"),
                artists=[a["name"] for a in self.current_track_info.get("artists", [])],
                is_playing=True,
                progress_ms=0,
                duration_ms=int(self.current_track_info.get("duration_seconds", 0)) * 1000,
            )
        return None

    def play(self, uri: Optional[str] = None) -> str:
        """Play music. If URI/video_id provided, play that track."""
        try:
            if uri:
                video_id = uri.split("v=")[-1] if "v=" in uri else uri
                url = f"https://music.youtube.com/watch?v={video_id}"
                webbrowser.open(url)
                self.current_video_id = video_id
                return f"Opening in browser: {url}"
            return "No track specified"
        except Exception as e:
            return f"Error: {str(e)}"

    def pause(self) -> str:
        return "Pause playback in your YouTube Music browser tab"

    def next_track(self) -> str:
        return "Skip to next in your YouTube Music browser tab"

    def previous_track(self) -> str:
        return "Go to previous in your YouTube Music browser tab"

    def set_volume(self, volume: int) -> str:
        return f"Set volume to {volume}% in your YouTube Music browser tab"

    @cache(ttl=60, key_prefix="yt_search")
    def search(self, query: str, limit: int = 5) -> List[Track]:
        """Search for tracks."""
        try:
            results = self.yt.search(query, filter="songs", limit=limit)
            return [
                Track(
                    uri=item.get("videoId", ""),
                    name=item.get("title", "Unknown"),
                    artists=[a["name"] for a in item.get("artists", [])],
                )
                for item in results
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def search_and_play(self, query: str) -> str:
        """Search for a track and play it."""
        tracks = self.search(query, limit=1)
        if tracks:
            self.play(tracks[0].uri)
            self.current_track_info = {
                "title": tracks[0].name,
                "artists": [{"name": a} for a in tracks[0].artists],
                "duration_seconds": 180,
            }
            return f"Playing: {tracks[0].name} by {tracks[0].artists_str}"
        return f"No results for '{query}'"

    def add_to_queue(self, query: str) -> str:
        """Search and add to queue (manual in browser)."""
        tracks = self.search(query, limit=1)
        if tracks:
            return f"Found: {tracks[0].name} - add manually in YouTube Music"
        return f"No results for '{query}'"

    def get_recommendations(self, mood: Optional[str] = None, limit: int = 5) -> List[Track]:
        """Get recommendations based on mood."""
        query = f"{mood} music" if mood else "popular music"
        return self.search(query, limit=limit)

    def create_playlist(self, name: str, mood: Optional[str] = None, count: int = 20) -> str:
        return "Playlist creation requires YouTube Music authentication. Creating playlists manually is recommended."

    def save_current(self) -> str:
        return "Saving tracks requires YouTube Music authentication. Use the browser to like songs."

    def shuffle(self, state: bool) -> str:
        return f"Toggle shuffle {'on' if state else 'off'} in your YouTube Music browser tab"
