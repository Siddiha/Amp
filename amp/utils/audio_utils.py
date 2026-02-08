"""Audio utilities for AMP."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class AudioFeatures:
    """Spotify audio features for a track."""
    danceability: float = 0.0
    energy: float = 0.0
    valence: float = 0.0
    tempo: float = 0.0
    instrumentalness: float = 0.0
    acousticness: float = 0.0
    speechiness: float = 0.0
    liveness: float = 0.0
    loudness: float = 0.0
    key: int = 0
    mode: int = 0
    time_signature: int = 4

    @classmethod
    def from_spotify_dict(cls, data: dict) -> "AudioFeatures":
        return cls(
            danceability=data.get("danceability", 0.0),
            energy=data.get("energy", 0.0),
            valence=data.get("valence", 0.0),
            tempo=data.get("tempo", 0.0),
            instrumentalness=data.get("instrumentalness", 0.0),
            acousticness=data.get("acousticness", 0.0),
            speechiness=data.get("speechiness", 0.0),
            liveness=data.get("liveness", 0.0),
            loudness=data.get("loudness", 0.0),
            key=data.get("key", 0),
            mode=data.get("mode", 0),
            time_signature=data.get("time_signature", 4),
        )

    def to_dict(self) -> dict:
        return {
            "danceability": self.danceability,
            "energy": self.energy,
            "valence": self.valence,
            "tempo": self.tempo,
            "instrumentalness": self.instrumentalness,
            "acousticness": self.acousticness,
            "speechiness": self.speechiness,
            "liveness": self.liveness,
            "loudness": self.loudness,
            "key": self.key,
            "mode": self.mode,
            "time_signature": self.time_signature,
        }


MOOD_FEATURES: Dict[str, Dict[str, float]] = {
    "happy": {"target_valence": 0.8, "target_energy": 0.7, "min_valence": 0.6},
    "sad": {"target_valence": 0.2, "target_energy": 0.3, "max_valence": 0.4},
    "chill": {"target_energy": 0.3, "target_valence": 0.5, "max_energy": 0.5},
    "energetic": {"target_energy": 0.9, "min_energy": 0.7},
    "focus": {"target_energy": 0.5, "target_instrumentalness": 0.7, "min_instrumentalness": 0.3},
    "party": {"target_danceability": 0.9, "target_energy": 0.8, "min_danceability": 0.7},
    "workout": {"target_energy": 0.9, "target_tempo": 140, "min_energy": 0.7, "min_tempo": 120},
    "sleep": {"target_energy": 0.2, "target_instrumentalness": 0.5, "max_energy": 0.4},
    "romantic": {"target_valence": 0.6, "target_energy": 0.4, "target_acousticness": 0.6},
    "angry": {"target_energy": 0.9, "target_valence": 0.3, "min_energy": 0.8},
    "melancholic": {"target_valence": 0.3, "target_acousticness": 0.6, "max_valence": 0.5},
}


def get_mood_features(mood: str) -> Dict[str, float]:
    """Get Spotify recommendation parameters for a mood."""
    return MOOD_FEATURES.get(mood.lower(), {})


def analyze_mood_from_features(features: AudioFeatures) -> str:
    """Analyze mood from audio features."""
    if features.energy > 0.8 and features.valence > 0.6:
        return "energetic/happy"
    elif features.energy > 0.7 and features.danceability > 0.7:
        return "party"
    elif features.energy < 0.3 and features.instrumentalness > 0.5:
        return "sleep/ambient"
    elif features.energy < 0.4 and features.valence < 0.4:
        return "sad/melancholic"
    elif features.valence > 0.7:
        return "happy"
    elif features.energy < 0.5 and features.acousticness > 0.5:
        return "chill/acoustic"
    elif features.instrumentalness > 0.7:
        return "focus/instrumental"
    else:
        return "neutral"


def format_duration(ms: int) -> str:
    """Format milliseconds as mm:ss or hh:mm:ss."""
    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def format_progress_bar(progress: float, width: int = 30) -> str:
    """Create a progress bar string."""
    filled = int(progress * width)
    filled = max(0, min(width - 1, filled))
    bar = "━" * filled + "○" + "─" * (width - filled - 1)
    return f"[{bar}]"


def calculate_similarity(features1: AudioFeatures, features2: AudioFeatures) -> float:
    """Calculate similarity score between two tracks (0-1)."""
    weights = {
        "energy": 0.2, "valence": 0.2, "danceability": 0.15,
        "instrumentalness": 0.15, "acousticness": 0.1, "tempo": 0.1, "speechiness": 0.1,
    }

    score = 0.0
    for attr, weight in weights.items():
        val1 = getattr(features1, attr)
        val2 = getattr(features2, attr)
        if attr == "tempo":
            val1 = (val1 - 60) / 140
            val2 = (val2 - 60) / 140
        diff = abs(val1 - val2)
        score += weight * (1 - diff)

    return score


def get_key_name(key: int, mode: int) -> str:
    """Get musical key name from Spotify key/mode values."""
    keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    mode_name = "major" if mode == 1 else "minor"
    if 0 <= key < 12:
        return f"{keys[key]} {mode_name}"
    return "Unknown"
