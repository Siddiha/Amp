"""Spotify player service for AMP."""

from typing import Optional, List, Dict

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from amp.config import get_config
from amp.utils.logger import get_logger
from amp.utils.audio_utils import get_mood_features

logger = get_logger("spotify")


class SpotifyPlayer:
    """Handles all Spotify interactions."""

    def __init__(self):
        config = get_config()
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=config.spotify.client_id,
            client_secret=config.spotify.client_secret,
            redirect_uri=config.spotify.redirect_uri,
            scope=" ".join(config.spotify.scopes),
            cache_path=config.spotify.cache_path,
        ))
        logger.info("Spotify client initialized")

    def get_current_track(self) -> Optional[Dict]:
        """Get currently playing track."""
        try:
            current = self.sp.current_playback()
            if current and current.get("item"):
                track = current["item"]
                return {
                    "name": track["name"],
                    "artists": ", ".join(a["name"] for a in track["artists"]),
                    "album": track["album"]["name"],
                    "uri": track["uri"],
                    "is_playing": current["is_playing"],
                    "progress_ms": current["progress_ms"],
                    "duration_ms": track["duration_ms"],
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get current track: {e}")
            return None

    def play(self, uri: Optional[str] = None) -> str:
        """Play music. If URI provided, play that track/album/playlist."""
        try:
            if uri:
                if "track" in uri:
                    self.sp.start_playback(uris=[uri])
                else:
                    self.sp.start_playback(context_uri=uri)
            else:
                self.sp.start_playback()
            return "Playing"
        except spotipy.exceptions.SpotifyException as e:
            if "No active device" in str(e):
                return "No active device. Open Spotify app first!"
            return f"Error: {str(e)}"

    def pause(self) -> str:
        """Pause playback."""
        try:
            self.sp.pause_playback()
            return "Paused"
        except Exception as e:
            return f"Error: {str(e)}"

    def next_track(self) -> str:
        """Skip to next track."""
        try:
            self.sp.next_track()
            return "Skipped to next"
        except Exception as e:
            return f"Error: {str(e)}"

    def previous_track(self) -> str:
        """Go to previous track."""
        try:
            self.sp.previous_track()
            return "Previous track"
        except Exception as e:
            return f"Error: {str(e)}"

    def set_volume(self, volume: int) -> str:
        """Set volume (0-100)."""
        try:
            self.sp.volume(max(0, min(100, volume)))
            return f"Volume: {volume}%"
        except Exception as e:
            return f"Error: {str(e)}"

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for tracks."""
        try:
            results = self.sp.search(q=query, type="track", limit=limit)
            tracks = []
            for item in results["tracks"]["items"]:
                tracks.append({
                    "name": item["name"],
                    "artists": ", ".join(a["name"] for a in item["artists"]),
                    "uri": item["uri"],
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
            return f"{result} - {tracks[0]['name']} by {tracks[0]['artists']}"
        return f"No results for '{query}'"

    def add_to_queue(self, query: str) -> str:
        """Search and add to queue."""
        tracks = self.search(query, limit=1)
        if tracks:
            try:
                self.sp.add_to_queue(tracks[0]["uri"])
                return f"Added to queue: {tracks[0]['name']}"
            except Exception as e:
                return f"Error: {str(e)}"
        return f"No results for '{query}'"

    def get_recommendations(self, mood: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """Get recommendations based on mood or top tracks."""
        try:
            top = self.sp.current_user_top_tracks(limit=5, time_range="short_term")
            seed_tracks = [t["id"] for t in top["items"][:2]] if top["items"] else []

            params = {"limit": limit}
            if seed_tracks:
                params["seed_tracks"] = seed_tracks

            if mood:
                mood_params = get_mood_features(mood)
                # Only pass target_ params to Spotify API
                for key, value in mood_params.items():
                    if key.startswith("target_"):
                        params[key] = value

            results = self.sp.recommendations(**params)
            return [
                {"name": t["name"], "artists": ", ".join(a["name"] for a in t["artists"]), "uri": t["uri"]}
                for t in results["tracks"]
            ]
        except Exception as e:
            logger.error(f"Recommendations failed: {e}")
            return []

    def create_playlist(self, name: str, mood: Optional[str] = None, count: int = 20) -> str:
        """Create a playlist with recommendations."""
        try:
            tracks = self.get_recommendations(mood, limit=count)
            if not tracks:
                return "Couldn't generate tracks"

            user = self.sp.current_user()
            playlist = self.sp.user_playlist_create(
                user["id"], name,
                description=f"Created by AMP AI - {mood or 'personalized'} vibes"
            )

            self.sp.playlist_add_items(playlist["id"], [t["uri"] for t in tracks])
            return f"Created '{name}' with {len(tracks)} tracks!"
        except Exception as e:
            return f"Error: {str(e)}"

    def save_current(self) -> str:
        """Save current track to library."""
        try:
            current = self.sp.current_playback()
            if current and current.get("item"):
                self.sp.current_user_saved_tracks_add([current["item"]["id"]])
                return f"Saved '{current['item']['name']}' to library!"
            return "Nothing playing"
        except Exception as e:
            return f"Error: {str(e)}"

    def shuffle(self, state: bool) -> str:
        """Toggle shuffle."""
        try:
            self.sp.shuffle(state)
            return f"Shuffle {'on' if state else 'off'}"
        except Exception as e:
            return f"Error: {str(e)}"
