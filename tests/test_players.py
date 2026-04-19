"""
Tests for SpotifyPlayer and YouTubePlayer.
Run: pytest tests/test_players.py -v
"""

import pytest
from unittest.mock import MagicMock, patch

from amp.models import Track


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _spotify_track(name="Test Song", artists=None, uri="spotify:track:abc"):
    return {
        "name": name,
        "artists": [{"name": a} for a in (artists or ["Test Artist"])],
        "album": {"name": "Test Album", "uri": "spotify:album:xyz"},
        "uri": uri,
        "duration_ms": 200_000,
        "popularity": 70,
        "explicit": False,
        "preview_url": None,
    }


def _playback(track_dict, is_playing=True, progress_ms=30_000):
    return {
        "item": track_dict,
        "is_playing": is_playing,
        "progress_ms": progress_ms,
    }


def _make_spotify_player():
    """Build a SpotifyPlayer with a mocked Spotify client."""
    with patch("amp.spotify.player.SpotifyOAuth"), \
         patch("amp.spotify.player.spotipy.Spotify"), \
         patch("amp.spotify.player.get_config") as mock_cfg:
        mock_cfg.return_value.spotify.client_id = "x"
        mock_cfg.return_value.spotify.client_secret = "x"
        mock_cfg.return_value.spotify.redirect_uri = "http://localhost"
        mock_cfg.return_value.spotify.scopes = []
        mock_cfg.return_value.spotify.cache_path = ".cache"
        from amp.spotify.player import SpotifyPlayer
        player = SpotifyPlayer.__new__(SpotifyPlayer)
        player.sp = MagicMock()
        return player


def _make_youtube_player():
    """Build a YouTubePlayer with a mocked YTMusic client."""
    with patch("amp.spotify.youtube_player.YTMusic"):
        from amp.spotify.youtube_player import YouTubePlayer
        player = YouTubePlayer.__new__(YouTubePlayer)
        player.yt = MagicMock()
        player.current_video_id = None
        player.current_track_info = None
        return player


def _yt_item(title="YT Song", artists=None, video_id="abc123"):
    return {
        "title": title,
        "artists": [{"name": a} for a in (artists or ["YT Artist"])],
        "videoId": video_id,
    }


# ---------------------------------------------------------------------------
# SpotifyPlayer
# ---------------------------------------------------------------------------

class TestSpotifyPlayerSearch:

    @pytest.fixture
    def player(self):
        return _make_spotify_player()

    def test_search_returns_track_objects(self, player):
        player.sp.search.return_value = {
            "tracks": {"items": [_spotify_track("Jazz Song", ["Miles Davis"])]}
        }
        results = player.search("jazz")
        assert len(results) == 1
        assert isinstance(results[0], Track)
        assert results[0].name == "Jazz Song"
        assert results[0].artists_str == "Miles Davis"

    def test_search_empty_on_api_failure(self, player):
        player.sp.search.side_effect = Exception("API error")
        assert player.search("anything") == []

    def test_search_and_play_returns_track_name(self, player):
        player.sp.search.return_value = {
            "tracks": {"items": [_spotify_track("Bohemian Rhapsody", ["Queen"], "spotify:track:xyz")]}
        }
        player.sp.start_playback.return_value = None
        result = player.search_and_play("bohemian rhapsody")
        assert "Bohemian Rhapsody" in result
        assert "Queen" in result

    def test_search_and_play_no_results(self, player):
        player.sp.search.return_value = {"tracks": {"items": []}}
        result = player.search_and_play("xyznonexistent")
        assert "No results" in result


class TestSpotifyPlayerCurrentTrack:

    @pytest.fixture
    def player(self):
        return _make_spotify_player()

    def test_returns_track_when_playing(self, player):
        player.sp.current_playback.return_value = _playback(
            _spotify_track("Playing Now", ["Artist A"])
        )
        track = player.get_current_track()
        assert isinstance(track, Track)
        assert track.name == "Playing Now"
        assert track.is_playing is True
        assert track.progress_ms == 30_000

    def test_returns_track_when_paused(self, player):
        player.sp.current_playback.return_value = _playback(
            _spotify_track(), is_playing=False, progress_ms=0
        )
        track = player.get_current_track()
        assert track.is_playing is False

    def test_returns_none_when_idle(self, player):
        player.sp.current_playback.return_value = None
        assert player.get_current_track() is None

    def test_returns_none_on_error(self, player):
        player.sp.current_playback.side_effect = Exception("network error")
        assert player.get_current_track() is None


class TestSpotifyPlayerRecommendations:

    @pytest.fixture
    def player(self):
        return _make_spotify_player()

    def test_returns_track_objects(self, player):
        player.sp.current_user_top_tracks.return_value = {
            "items": [{"id": "seed1"}, {"id": "seed2"}]
        }
        player.sp.recommendations.return_value = {
            "tracks": [_spotify_track("Rec Song", ["Rec Artist"])]
        }
        results = player.get_recommendations()
        assert len(results) == 1
        assert isinstance(results[0], Track)
        assert results[0].name == "Rec Song"

    def test_falls_back_to_genre_seed_with_no_history(self, player):
        player.sp.current_user_top_tracks.return_value = {"items": []}
        player.sp.recommendations.return_value = {"tracks": [_spotify_track()]}
        player.get_recommendations()
        call_kwargs = player.sp.recommendations.call_args[1]
        assert call_kwargs.get("seed_genres") == ["pop"]
        assert "seed_tracks" not in call_kwargs

    def test_returns_empty_on_failure(self, player):
        player.sp.current_user_top_tracks.side_effect = Exception("error")
        assert player.get_recommendations() == []


# ---------------------------------------------------------------------------
# YouTubePlayer
# ---------------------------------------------------------------------------

class TestYouTubePlayerSearch:

    @pytest.fixture
    def player(self):
        return _make_youtube_player()

    def test_returns_track_objects(self, player):
        player.yt.search.return_value = [_yt_item("Lo-Fi Beat", ["Chillhop"], "vid001")]
        results = player.search("lo-fi")
        assert len(results) == 1
        assert isinstance(results[0], Track)
        assert results[0].name == "Lo-Fi Beat"
        assert results[0].uri == "vid001"
        assert results[0].artists_str == "Chillhop"

    def test_returns_empty_on_failure(self, player):
        player.yt.search.side_effect = Exception("network error")
        assert player.search("anything") == []

    def test_multiple_artists_joined(self, player):
        player.yt.search.return_value = [_yt_item("Collab", ["Artist A", "Artist B"])]
        results = player.search("collab")
        assert results[0].artists_str == "Artist A, Artist B"


class TestYouTubePlayerCurrentTrack:

    @pytest.fixture
    def player(self):
        return _make_youtube_player()

    def test_none_when_nothing_played(self, player):
        assert player.get_current_track() is None

    def test_returns_track_after_search_and_play(self, player):
        player.yt.search.return_value = [_yt_item("Lo-Fi Beat", ["Chillhop"], "vid999")]
        with patch("amp.spotify.youtube_player.webbrowser.open"):
            player.search_and_play("lo-fi")
        track = player.get_current_track()
        assert isinstance(track, Track)
        assert track.name == "Lo-Fi Beat"
        assert track.artists_str == "Chillhop"
        assert track.is_playing is True

    def test_no_results_returns_message(self, player):
        player.yt.search.return_value = []
        result = player.search_and_play("xyznotreal")
        assert "No results" in result


class TestYouTubePlayerRecommendations:

    @pytest.fixture
    def player(self):
        return _make_youtube_player()

    def test_delegates_to_search_with_mood_query(self, player):
        player.yt.search.return_value = [_yt_item()]
        results = player.get_recommendations(mood="chill", limit=3)
        player.yt.search.assert_called_once()
        query_used = player.yt.search.call_args[0][0]
        assert "chill" in query_used
        assert isinstance(results[0], Track)

    def test_default_query_without_mood(self, player):
        player.yt.search.return_value = [_yt_item()]
        player.get_recommendations()
        query_used = player.yt.search.call_args[0][0]
        assert "popular" in query_used
