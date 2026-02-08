"""YouTube Music player service for AMP."""

from typing import Optional, List, Dict
import webbrowser

from ytmusicapi import YTMusic

from amp.utils.logger import get_logger
from amp.utils.audio_utils import get_mood_features

logger = get_logger("youtube")


class YouTubePlayer:
    """Handles all YouTube Music interactions."""

    def __init__(self):
        # YTMusic doesn't require auth for basic searches and playback control
        # For authenticated features (library, playlists), you'd need to set up oauth.txt
        self.yt = YTMusic()
        self.current_video_id: Optional[str] = None
        self.current_track_info: Optional[Dict] = None
        logger.info("YouTube Music player initialized")

    def get_current_track(self) -> Optional[Dict]:
        """Get currently playing track info."""
        if self.current_track_info:
            return {
                "name": self.current_track_info.get("title", "Unknown"),
                "artists": ", ".join([a["name"] for a in self.current_track_info.get("artists", [])]),
                "album": self.current_track_info.get("album", {}).get("name", ""),
                "uri": f"https://music.youtube.com/watch?v={self.current_video_id}",
                "is_playing": True,
                "progress_ms": 0,
                "duration_ms": int(self.current_track_info.get("duration_seconds", 0)) * 1000,
            }
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
        """Pause playback (browser-based, manual)."""
        return "Pause playback in your YouTube Music browser tab"

    def next_track(self) -> str:
        """Skip to next track (browser-based, manual)."""
        return "Skip to next in your YouTube Music browser tab"

    def previous_track(self) -> str:
        """Go to previous track (browser-based, manual)."""
        return "Go to previous in your YouTube Music browser tab"

    def set_volume(self, volume: int) -> str:
        """Set volume (browser-based, manual)."""
        return f"Set volume to {volume}% in your YouTube Music browser tab"

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for tracks."""
        try:
            results = self.yt.search(query, filter="songs", limit=limit)
            tracks = []
            for item in results:
                tracks.append({
                    "name": item.get("title", "Unknown"),
                    "artists": ", ".join([a["name"] for a in item.get("artists", [])]),
                    "uri": item.get("videoId", ""),
                })
            return tracks
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def search_and_play(self, query: str) -> str:
        """Search for a track and play it."""
        tracks = self.search(query, limit=1)
        if tracks:
            result = self.play(tracks[0]["uri"])
            self.current_track_info = {"title": tracks[0]["name"], "artists": [{"name": tracks[0]["artists"]}], "duration_seconds": 180}
            return f"Playing: {tracks[0]['name']} by {tracks[0]['artists']}"
        return f"No results for '{query}'"

    def add_to_queue(self, query: str) -> str:
        """Search and add to queue (manual in browser)."""
        tracks = self.search(query, limit=1)
        if tracks:
            return f"Found: {tracks[0]['name']} - add manually in YouTube Music"
        return f"No results for '{query}'"

    def get_recommendations(self, mood: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """Get recommendations based on mood."""
        try:
            # Use mood-based search queries
            query = f"{mood} music" if mood else "popular music"
            results = self.yt.search(query, filter="songs", limit=limit)

            tracks = []
            for item in results:
                tracks.append({
                    "name": item.get("title", "Unknown"),
                    "artists": ", ".join([a["name"] for a in item.get("artists", [])]),
                    "uri": item.get("videoId", ""),
                })
            return tracks
        except Exception as e:
            logger.error(f"Recommendations failed: {e}")
            return []

    def create_playlist(self, name: str, mood: Optional[str] = None, count: int = 20) -> str:
        """Create a playlist with recommendations (requires auth)."""
        return "Playlist creation requires YouTube Music authentication. Creating playlists manually is recommended."

    def save_current(self) -> str:
        """Save current track to library (requires auth)."""
        return "Saving tracks requires YouTube Music authentication. Use the browser to like songs."

    def shuffle(self, state: bool) -> str:
        """Toggle shuffle (browser-based, manual)."""
        return f"Toggle shuffle {'on' if state else 'off'} in your YouTube Music browser tab"
