"""Tests for TTS provider implementations.

This module tests the TTS provider interface and concrete implementations.
"""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

from conversation_agent.config import TTSConfig
from conversation_agent.providers.tts import (
    PiperTTSProvider,
    Pyttsx3Provider,
    TTSError,
    TTSProvider,
)


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


class TestPiperTTSProvider:
    """Tests for Piper TTS provider."""

    @pytest.fixture
    def mock_model_files(self, tmp_path):
        """Create mock model files."""
        model_path = tmp_path / "test_model.onnx"
        config_path = tmp_path / "test_model.onnx.json"

        model_path.write_bytes(b"fake model data")
        config_path.write_text('{"sample_rate": 22050}')

        return str(model_path), str(config_path)

    @pytest.fixture
    def mock_piper_voice(self):
        """Create a mock PiperVoice."""
        # Create a simple class that acts like AudioChunk
        class MockAudioChunk:
            def __init__(self, data):
                self.audio_int16_bytes = data

        voice = Mock()
        # Return mock AudioChunk objects with audio_int16_bytes property
        voice.synthesize.return_value = [MockAudioChunk(b"\x00\x01" * 100)]
        return voice

    @pytest.fixture
    def provider(self, mock_model_files):
        """Create a PiperTTSProvider with mocked files."""
        model_path, config_path = mock_model_files
        return PiperTTSProvider(model_path=model_path, config_path=config_path)

    def test_initialization_success(self, mock_model_files):
        """Provider initializes successfully with valid files."""
        model_path, config_path = mock_model_files
        provider = PiperTTSProvider(model_path=model_path, config_path=config_path)

        assert provider.model_path.exists()
        assert provider.config_path.exists()
        assert provider.sample_rate == 22050
        assert provider.voice is None  # Lazy loading
        assert provider._volume == 1.0

    def test_initialization_missing_model(self, tmp_path):
        """Provider raises TTSError if model file missing."""
        nonexistent = str(tmp_path / "nonexistent.onnx")

        with pytest.raises(TTSError, match="Model not found"):
            PiperTTSProvider(model_path=nonexistent)

    def test_initialization_missing_config(self, tmp_path):
        """Provider raises TTSError if config file missing."""
        model_path = tmp_path / "model.onnx"
        model_path.write_bytes(b"fake")

        with pytest.raises(TTSError, match="Config not found"):
            PiperTTSProvider(model_path=str(model_path))

    def test_auto_detect_config_path(self, tmp_path):
        """Provider auto-detects config path from model path."""
        model_path = tmp_path / "model.onnx"
        config_path = tmp_path / "model.onnx.json"
        model_path.write_bytes(b"fake")
        config_path.write_text("{}")

        provider = PiperTTSProvider(model_path=str(model_path))
        assert provider.config_path == config_path

    @patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
    def test_initialize_loads_model(self, mock_piper_class, provider, mock_piper_voice):
        """initialize() loads the Piper voice model."""
        mock_piper_class.load.return_value = mock_piper_voice

        assert provider.voice is None
        provider.initialize()
        assert provider.voice is not None
        mock_piper_class.load.assert_called_once()

    @patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
    def test_initialize_idempotent(self, mock_piper_class, provider, mock_piper_voice):
        """initialize() does not reload if model already loaded."""
        mock_piper_class.load.return_value = mock_piper_voice

        provider.initialize()
        provider.initialize()  # Call twice

        mock_piper_class.load.assert_called_once()  # Only loaded once

    @patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
    @patch.object(PiperTTSProvider, "_play_audio")
    def test_speak_synthesizes_and_plays(
        self, mock_play, mock_piper_class, provider, mock_piper_voice
    ):
        """speak() synthesizes and plays audio."""
        mock_piper_class.load.return_value = mock_piper_voice

        provider.speak("Hello world")

        mock_piper_voice.synthesize.assert_called_once_with("Hello world")
        mock_play.assert_called_once()

    def test_speak_empty_text(self, provider):
        """speak() with empty text does nothing."""
        provider.speak("")
        # Should not raise, just log warning
        assert provider.voice is None  # Model not loaded

        provider.speak("   ")
        assert provider.voice is None

    @patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
    def test_speak_lazy_initializes(
        self, mock_piper_class, provider, mock_piper_voice
    ):
        """speak() initializes model on first call."""
        mock_piper_class.load.return_value = mock_piper_voice

        assert provider.voice is None
        provider.speak("Test")
        assert provider.voice is not None

    @patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
    def test_speak_failure(self, mock_piper_class, provider):
        """speak() raises TTSError on synthesis failure."""
        mock_voice = Mock()
        mock_voice.synthesize.side_effect = Exception("Synthesis failed")
        mock_piper_class.load.return_value = mock_voice

        with pytest.raises(TTSError, match="Failed to speak"):
            provider.speak("Test")

    def test_set_rate_logs_warning(self, provider, caplog):
        """set_rate() logs warning (not supported)."""
        provider.set_rate(150)
        assert "not supported" in caplog.text.lower()

    @patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
    def test_set_voice_reloads_model(
        self, mock_piper_class, provider, mock_piper_voice, tmp_path
    ):
        """set_voice() reloads model with new path."""
        mock_piper_class.load.return_value = mock_piper_voice

        # Create new model files
        new_model = tmp_path / "new_model.onnx"
        new_config = tmp_path / "new_model.onnx.json"
        new_model.write_bytes(b"new model")
        new_config.write_text("{}")

        provider.voice = mock_piper_voice  # Simulate existing model
        provider.set_voice(str(new_model))

        # Model path should be updated and model reloaded
        assert provider.model_path == new_model
        assert provider.voice is not None  # Reloaded by initialize()
        mock_piper_class.load.assert_called()  # Reloaded

    def test_set_voice_invalid_path(self, provider):
        """set_voice() raises TTSError for invalid path."""
        with pytest.raises(TTSError, match="Model not found"):
            provider.set_voice("nonexistent.onnx")

    def test_set_volume_valid(self, provider):
        """set_volume() sets volume within valid range."""
        provider.set_volume(0.5)
        assert provider._volume == 0.5

        provider.set_volume(0.0)
        assert provider._volume == 0.0

        provider.set_volume(1.0)
        assert provider._volume == 1.0

    def test_set_volume_out_of_range(self, provider):
        """set_volume() raises TTSError for invalid volumes."""
        with pytest.raises(TTSError, match="out of range"):
            provider.set_volume(1.5)

        with pytest.raises(TTSError, match="out of range"):
            provider.set_volume(-0.1)

    @patch("conversation_agent.providers.tts.piper_provider.pyaudio.PyAudio")
    def test_play_audio_with_volume(self, mock_pyaudio_class, provider):
        """_play_audio() applies volume scaling."""
        import numpy as np

        mock_audio = Mock()
        mock_stream = Mock()
        mock_audio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_audio

        # Create test audio data (16-bit mono)
        audio_data = (np.ones(100, dtype=np.int16) * 1000).tobytes()

        provider.set_volume(0.5)
        provider._play_audio(audio_data)

        # Verify stream was opened and audio written
        mock_audio.open.assert_called_once()
        mock_stream.write.assert_called_once()

        # Verify written audio was scaled (not exact original)
        written_audio = mock_stream.write.call_args[0][0]
        assert written_audio != audio_data  # Should be scaled

    @patch("conversation_agent.providers.tts.piper_provider.pyaudio.PyAudio")
    def test_play_audio_failure(self, mock_pyaudio_class, provider):
        """_play_audio() raises TTSError on playback failure."""
        mock_pyaudio_class.side_effect = Exception("Playback failed")

        with pytest.raises(TTSError, match="Audio playback failed"):
            provider._play_audio(b"\x00\x01" * 100)

    @patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
    def test_save_to_file_creates_wav(
        self, mock_piper_class, provider, mock_piper_voice, tmp_path
    ):
        """save_to_file() creates WAV file."""
        mock_piper_class.load.return_value = mock_piper_voice

        output_path = tmp_path / "output.wav"
        provider.save_to_file("Test", str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_save_to_file_invalid_format(self, provider):
        """save_to_file() raises TTSError for non-WAV files."""
        with pytest.raises(TTSError, match="only supports .wav"):
            provider.save_to_file("Test", "output.mp3")

    @patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
    def test_save_to_file_failure(self, mock_piper_class, provider):
        """save_to_file() raises TTSError on save failure."""
        mock_voice = Mock()
        mock_voice.synthesize.side_effect = Exception("Save failed")
        mock_piper_class.load.return_value = mock_voice

        with pytest.raises(TTSError, match="Failed to save"):
            provider.save_to_file("Test", "output.wav")

    def test_get_available_voices_lists_models(self, tmp_path, monkeypatch):
        """get_available_voices() lists .onnx files in models directory."""
        # Create fake models directory
        models_dir = tmp_path / "models" / "tts" / "piper"
        models_dir.mkdir(parents=True)
        (models_dir / "en_US-voice1.onnx").write_bytes(b"fake")
        (models_dir / "en_GB-voice2.onnx").write_bytes(b"fake")

        # Change working directory to tmp_path
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Create provider (doesn't matter which model)
            config_path = models_dir / "test.onnx.json"
            config_path.write_text("{}")
            model_path = models_dir / "test.onnx"
            model_path.write_bytes(b"fake")

            provider = PiperTTSProvider(model_path=str(model_path))
            voices = provider.get_available_voices()

            assert len(voices) == 3  # Including test.onnx
            assert any(v["name"] == "en_US-voice1" for v in voices)
            assert any(v["name"] == "en_GB-voice2" for v in voices)
        finally:
            os.chdir(original_cwd)

    def test_get_available_voices_no_models_dir(self, provider):
        """get_available_voices() returns empty list if directory missing."""
        voices = provider.get_available_voices()
        assert isinstance(voices, list)
        # May be empty or contain default model depending on setup

    def test_stop_sets_flag(self, provider):
        """stop() sets speaking flag to False."""
        provider._is_speaking = True
        provider.stop()
        assert provider._is_speaking is False

    def test_shutdown_clears_model(self, provider, mock_piper_voice):
        """shutdown() clears the voice model."""
        provider.voice = mock_piper_voice
        provider.shutdown()
        assert provider.voice is None


class TestTTSConfig:
    """Tests for TTS configuration."""

    def test_default_config(self):
        """TTSConfig has correct defaults."""
        config = TTSConfig()

        assert config.provider == "piper"
        assert config.voice is None
        assert config.rate == 150
        assert config.volume == 0.9
        assert config.piper_model_path == "models/tts/piper/en_US-lessac-medium.onnx"
        assert config.piper_sample_rate == 22050

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

    def test_get_provider_piper(self, tmp_path):
        """get_provider() returns configured Piper provider."""
        # Create mock model files
        model_path = tmp_path / "test_model.onnx"
        config_path = tmp_path / "test_model.onnx.json"
        model_path.write_bytes(b"fake")
        config_path.write_text("{}")

        with patch("conversation_agent.providers.tts.piper_provider.PiperVoice"):
            config = TTSConfig(
                provider="piper",
                piper_model_path=str(model_path),
                volume=0.8,
            )
            provider = config.get_provider()

            assert isinstance(provider, PiperTTSProvider)
            assert provider._volume == 0.8

    def test_get_provider_pyttsx3(self):
        """get_provider() returns configured pyttsx3 provider."""
        with patch("pyttsx3.init") as mock_init:
            mock_engine = MagicMock()
            mock_init.return_value = mock_engine

            # Set voice to None to avoid voice validation in test
            config = TTSConfig(
                provider="pyttsx3",
                rate=150,
                volume=0.8,
                voice=None,
            )
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

            config = TTSConfig(provider="pyttsx3", voice="voice1")
            _provider = config.get_provider()

            mock_engine.setProperty.assert_any_call("voice", "voice1")

    def test_get_provider_unknown_provider(self):
        """get_provider() raises ValueError for unknown provider."""
        config = TTSConfig(provider="unknown")

        with pytest.raises(ValueError, match="Unknown TTS provider"):
            config.get_provider()

    def test_get_provider_init_failure_pyttsx3(self):
        """get_provider() raises ValueError if pyttsx3 init fails."""
        with patch("pyttsx3.init", side_effect=Exception("Init failed")):
            config = TTSConfig(provider="pyttsx3")

            with pytest.raises(ValueError, match="Failed to initialize"):
                config.get_provider()

    def test_get_provider_init_failure_piper(self, tmp_path):
        """get_provider() raises ValueError if Piper init fails."""
        model_path = tmp_path / "test.onnx"
        config_path = tmp_path / "test.onnx.json"
        model_path.write_bytes(b"fake")
        config_path.write_text("{}")

        with patch(
            "conversation_agent.providers.tts.piper_provider.PiperVoice.load",
            side_effect=Exception("Load failed"),
        ):
            config = TTSConfig(
                provider="piper",
                piper_model_path=str(model_path),
            )

            with pytest.raises(ValueError, match="Failed to initialize"):
                config.get_provider()
