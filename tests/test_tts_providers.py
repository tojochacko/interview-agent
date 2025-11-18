"""Tests for TTS provider implementations.

This module tests the TTS provider interface and concrete implementations.
"""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

from conversation_agent.config import TTSConfig
from conversation_agent.providers.tts import Pyttsx3Provider, TTSError, TTSProvider


class TestTTSProviderInterface:
    """Test that TTSProvider defines the correct interface."""

    def test_tts_provider_is_abstract(self):
        """TTSProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            TTSProvider()  # type: ignore

    def test_tts_provider_requires_speak_method(self):
        """Subclasses must implement speak()."""

        class IncompleteTTS(TTSProvider):
            def set_voice(self, voice_id: str) -> None:
                pass

            def set_rate(self, rate: int) -> None:
                pass

            def set_volume(self, volume: float) -> None:
                pass

            def get_available_voices(self) -> list[dict[str, str]]:
                return []

            def stop(self) -> None:
                pass

        with pytest.raises(TypeError):
            IncompleteTTS()  # type: ignore


class TestPyttsx3Provider:
    """Tests for pyttsx3 TTS provider."""

    @pytest.fixture
    def mock_engine(self):
        """Create a mock pyttsx3 engine."""
        engine = MagicMock()
        voice1 = Mock()
        voice1.id = "voice1"
        voice1.name = "Voice 1"
        voice1.languages = ["en_US"]

        voice2 = Mock()
        voice2.id = "voice2"
        voice2.name = "Voice 2"
        voice2.languages = ["en_GB"]

        engine.getProperty.return_value = [voice1, voice2]
        return engine

    @pytest.fixture
    def provider(self, mock_engine):
        """Create a Pyttsx3Provider with mocked engine."""
        with patch("pyttsx3.init", return_value=mock_engine):
            return Pyttsx3Provider(enable_macos_workaround=False)

    def test_initialization_success(self, mock_engine):
        """Provider initializes successfully."""
        with patch("pyttsx3.init", return_value=mock_engine):
            provider = Pyttsx3Provider()
            assert provider.engine is not None

    def test_initialization_failure(self):
        """Provider raises TTSError if pyttsx3 init fails."""
        with patch("pyttsx3.init", side_effect=Exception("Init failed")):
            with pytest.raises(TTSError, match="Failed to initialize"):
                Pyttsx3Provider()

    def test_speak_success(self, provider):
        """speak() calls engine.say() and runAndWait()."""
        provider.speak("Hello, world!")

        provider.engine.say.assert_called_once_with("Hello, world!")
        provider.engine.runAndWait.assert_called_once()

    def test_speak_empty_text(self, provider):
        """speak() with empty text does nothing."""
        provider.speak("")
        provider.engine.say.assert_not_called()

        provider.speak("   ")
        provider.engine.say.assert_not_called()

    def test_speak_failure(self, provider):
        """speak() raises TTSError on engine failure."""
        provider.engine.say.side_effect = Exception("Speech failed")

        with pytest.raises(TTSError, match="Failed to speak"):
            provider.speak("Hello")

    def test_set_voice_success(self, provider):
        """set_voice() sets voice when ID is valid."""
        provider.set_voice("voice1")
        provider.engine.setProperty.assert_called_with("voice", "voice1")

    def test_set_voice_invalid(self, provider):
        """set_voice() raises TTSError for invalid voice ID."""
        with pytest.raises(TTSError, match="Voice .* not found"):
            provider.set_voice("invalid_voice")

    def test_set_rate_success(self, provider):
        """set_rate() sets rate within valid range."""
        provider.set_rate(150)
        provider.engine.setProperty.assert_called_with("rate", 150)

    def test_set_rate_out_of_range(self, provider):
        """set_rate() raises TTSError for invalid rates."""
        with pytest.raises(TTSError, match="out of range"):
            provider.set_rate(30)  # Too low

        with pytest.raises(TTSError, match="out of range"):
            provider.set_rate(500)  # Too high

    def test_set_volume_success(self, provider):
        """set_volume() sets volume within valid range."""
        provider.set_volume(0.8)
        provider.engine.setProperty.assert_called_with("volume", 0.8)

    def test_set_volume_out_of_range(self, provider):
        """set_volume() raises TTSError for invalid volumes."""
        with pytest.raises(TTSError, match="out of range"):
            provider.set_volume(-0.1)  # Too low

        with pytest.raises(TTSError, match="out of range"):
            provider.set_volume(1.5)  # Too high

    def test_get_available_voices(self, provider):
        """get_available_voices() returns list of voice dicts."""
        voices = provider.get_available_voices()

        assert len(voices) == 2
        assert voices[0]["id"] == "voice1"
        assert voices[0]["name"] == "Voice 1"
        assert voices[0]["language"] == "en_US"
        assert voices[1]["id"] == "voice2"
        assert voices[1]["name"] == "Voice 2"
        assert voices[1]["language"] == "en_GB"

    def test_get_available_voices_no_language_attr(self, provider):
        """get_available_voices() handles voices without languages attribute."""
        provider.engine.getProperty.return_value = [
            Mock(id="voice3", name="Voice 3", spec=["id", "name"])
        ]

        voices = provider.get_available_voices()
        assert voices[0]["language"] == "unknown"

    def test_stop(self, provider):
        """stop() calls engine.stop()."""
        provider.stop()
        provider.engine.stop.assert_called_once()

    def test_save_to_file_success(self, provider):
        """save_to_file() saves to WAV file."""
        provider.save_to_file("Hello", "output.wav")

        provider.engine.save_to_file.assert_called_once_with("Hello", "output.wav")
        provider.engine.runAndWait.assert_called_once()

    def test_save_to_file_invalid_format(self, provider):
        """save_to_file() raises TTSError for non-WAV files."""
        with pytest.raises(TTSError, match="only supports .wav"):
            provider.save_to_file("Hello", "output.mp3")

    def test_save_to_file_failure(self, provider):
        """save_to_file() raises TTSError on engine failure."""
        provider.engine.save_to_file.side_effect = Exception("Save failed")

        with pytest.raises(TTSError, match="Failed to save"):
            provider.save_to_file("Hello", "output.wav")


class TestTTSConfig:
    """Tests for TTS configuration."""

    def test_default_config(self):
        """TTSConfig has correct defaults."""
        config = TTSConfig()

        assert config.provider == "pyttsx3"
        assert config.voice is None
        assert config.rate == 175
        assert config.volume == 0.9

    def test_config_override(self):
        """TTSConfig can be overridden via constructor."""
        config = TTSConfig(
            provider="pyttsx3",
            voice="voice1",
            rate=200,
            volume=0.7,
        )

        assert config.provider == "pyttsx3"
        assert config.voice == "voice1"
        assert config.rate == 200
        assert config.volume == 0.7

    def test_config_validation_rate(self):
        """TTSConfig validates rate range."""
        with pytest.raises(ValueError):
            TTSConfig(rate=10)  # Too low

        with pytest.raises(ValueError):
            TTSConfig(rate=500)  # Too high

    def test_config_validation_volume(self):
        """TTSConfig validates volume range."""
        with pytest.raises(ValueError):
            TTSConfig(volume=-0.1)  # Too low

        with pytest.raises(ValueError):
            TTSConfig(volume=1.5)  # Too high

    def test_get_provider_pyttsx3(self):
        """get_provider() returns configured pyttsx3 provider."""
        with patch("pyttsx3.init") as mock_init:
            mock_engine = MagicMock()
            mock_init.return_value = mock_engine

            # Set voice to None to avoid voice validation in test
            config = TTSConfig(rate=150, volume=0.8, voice=None)
            provider = config.get_provider()

            assert isinstance(provider, Pyttsx3Provider)
            mock_engine.setProperty.assert_any_call("rate", 150)
            mock_engine.setProperty.assert_any_call("volume", 0.8)

    def test_get_provider_with_voice(self):
        """get_provider() sets voice if specified."""
        with patch("pyttsx3.init") as mock_init:
            mock_engine = MagicMock()
            voice1 = Mock()
            voice1.id = "voice1"
            voice1.name = "Voice 1"
            voice1.languages = ["en_US"]
            mock_engine.getProperty.return_value = [voice1]
            mock_init.return_value = mock_engine

            config = TTSConfig(voice="voice1")
            _provider = config.get_provider()

            mock_engine.setProperty.assert_any_call("voice", "voice1")

    def test_get_provider_unknown_provider(self):
        """get_provider() raises ValueError for unknown provider."""
        config = TTSConfig(provider="unknown")

        with pytest.raises(ValueError, match="Unknown TTS provider"):
            config.get_provider()

    def test_get_provider_init_failure(self):
        """get_provider() raises ValueError if provider init fails."""
        with patch("pyttsx3.init", side_effect=Exception("Init failed")):
            config = TTSConfig()

            with pytest.raises(ValueError, match="Failed to initialize"):
                config.get_provider()
