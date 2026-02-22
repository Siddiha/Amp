"""
Tests for the AMP audio utilities.
Run: pytest tests/test_audio_utils.py -v
"""

import pytest
from amp.utils.audio_utils import (
    AudioFeatures,
    get_mood_features,
    analyze_mood_from_features,
    format_duration,
    format_progress_bar,
    calculate_similarity,
    get_key_name,
)


class TestGetMoodFeatures:
    """get_mood_features should return known params for valid moods."""

    def test_happy_has_high_valence(self):
        params = get_mood_features("happy")
        assert params["target_valence"] >= 0.7

    def test_sad_has_low_valence(self):
        params = get_mood_features("sad")
        assert params["target_valence"] <= 0.3

    def test_workout_has_high_energy(self):
        params = get_mood_features("workout")
        assert params["target_energy"] >= 0.8

    def test_chill_has_low_energy(self):
        params = get_mood_features("chill")
        assert params["target_energy"] <= 0.5

    def test_unknown_mood_returns_empty_dict(self):
        assert get_mood_features("nonexistent_mood") == {}

    def test_case_insensitive(self):
        assert get_mood_features("HAPPY") == get_mood_features("happy")


class TestFormatDuration:
    """format_duration should produce mm:ss or hh:mm:ss strings."""

    def test_zero_ms(self):
        assert format_duration(0) == "0:00"

    def test_one_minute(self):
        assert format_duration(60_000) == "1:00"

    def test_three_minutes_thirty(self):
        assert format_duration(210_000) == "3:30"

    def test_over_one_hour(self):
        result = format_duration(3_661_000)  # 1h 1m 1s
        assert result == "1:01:01"

    def test_seconds_zero_padded(self):
        result = format_duration(65_000)  # 1m 5s
        assert result == "1:05"


class TestFormatProgressBar:
    """format_progress_bar should return a string of the right length."""

    def test_zero_progress(self):
        bar = format_progress_bar(0.0, width=10)
        assert "○" in bar
        assert bar.startswith("[")
        assert bar.endswith("]")

    def test_full_progress(self):
        bar = format_progress_bar(1.0, width=10)
        assert "○" in bar

    def test_width_respected(self):
        # total chars = width (━ + ○ + ─) inside [ ]
        bar = format_progress_bar(0.5, width=20)
        # inner content length should be 20
        inner = bar[1:-1]
        assert len(inner) == 20


class TestAnalyzeMoodFromFeatures:
    """analyze_mood_from_features should classify AudioFeatures correctly."""

    def test_energetic_happy(self):
        features = AudioFeatures(energy=0.9, valence=0.8, danceability=0.6)
        mood = analyze_mood_from_features(features)
        assert "energetic" in mood or "happy" in mood

    def test_sleep(self):
        features = AudioFeatures(energy=0.1, instrumentalness=0.7)
        mood = analyze_mood_from_features(features)
        assert "sleep" in mood or "ambient" in mood

    def test_sad(self):
        features = AudioFeatures(energy=0.2, valence=0.2)
        mood = analyze_mood_from_features(features)
        assert "sad" in mood or "melancholic" in mood


class TestGetKeyName:
    """get_key_name should return musical key strings."""

    def test_c_major(self):
        assert get_key_name(0, 1) == "C major"

    def test_a_minor(self):
        assert get_key_name(9, 0) == "A minor"

    def test_invalid_key(self):
        assert get_key_name(-1, 1) == "Unknown"

    def test_all_12_keys_are_strings(self):
        for k in range(12):
            result = get_key_name(k, 1)
            assert isinstance(result, str)
            assert "major" in result


class TestCalculateSimilarity:
    """calculate_similarity should return 0–1 similarity scores."""

    def test_identical_features_score_one(self):
        f = AudioFeatures(energy=0.5, valence=0.5, danceability=0.5)
        score = calculate_similarity(f, f)
        assert score == pytest.approx(1.0, abs=0.01)

    def test_opposite_features_score_lower(self):
        f1 = AudioFeatures(energy=0.0, valence=0.0, danceability=0.0, instrumentalness=0.0, acousticness=0.0, speechiness=0.0)
        f2 = AudioFeatures(energy=1.0, valence=1.0, danceability=1.0, instrumentalness=1.0, acousticness=1.0, speechiness=1.0)
        score = calculate_similarity(f1, f2)
        assert score < 0.3
