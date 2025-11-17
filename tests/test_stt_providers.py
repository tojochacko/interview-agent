"""Tests for Speech-to-Text (STT) providers."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

# Mock whisper module before importing our code
sys.modules["whisper"] = MagicMock()

from conversation_agent.config import STTConfig
from conversation_agent.providers.stt import STTError, STTProvider, WhisperProvider


class TestSTTProviderInterface:
    """Test STT provider abstract interface."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that STTProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            STTProvider()

    def test_subclass_must_implement_abstract_methods(self):
        """Test that subclasses must implement all abstract methods."""

        class IncompleteProvider(STTProvider):
            pass

        with pytest.raises(TypeError):
            IncompleteProvider()


class TestWhisperProvider:
    """Test Whisper STT provider."""

    @patch("whisper.load_model")
    def test_initialization_success(self, mock_load_model):
        """Test successful Whisper provider initialization."""
        mock_model = Mock()
        mock_load_model.return_value = mock_model

        provider = WhisperProvider(model_size="base", language="en", device="cpu")

        assert provider.model_size == "base"
        assert provider.language == "en"
        assert provider.device == "cpu"
        mock_load_model.assert_called_once_with("base", device="cpu")

    def test_initialization_invalid_model(self):
        """Test initialization with invalid model size."""
        with pytest.raises(STTError) as exc_info:
            WhisperProvider(model_size="invalid")

        assert "Invalid model size" in str(exc_info.value)

    @patch("whisper.load_model")
    def test_initialization_import_error(self, mock_load_model):
        """Test initialization when Whisper is not installed."""
        mock_load_model.side_effect = ImportError("No module named 'whisper'")

        with pytest.raises(STTError) as exc_info:
            WhisperProvider()

        assert "Whisper not installed" in str(exc_info.value)

    @patch("whisper.load_model")
    def test_transcribe_file_success(self, mock_load_model):
        """Test transcribing audio file successfully."""
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "Hello world",
            "language": "en",
            "segments": [
                {"start": 0.0, "end": 1.5, "text": "Hello"},
                {"start": 1.5, "end": 2.5, "text": "world"},
            ],
        }
        mock_load_model.return_value = mock_model

        provider = WhisperProvider()

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(b"fake audio data")
            tmp_path = tmp.name

        try:
            result = provider.transcribe(tmp_path)

            assert result["text"] == "Hello world"
            assert result["language"] == "en"
            assert len(result["segments"]) == 2
            assert result["segments"][0]["text"] == "Hello"

            mock_model.transcribe.assert_called_once()
        finally:
            Path(tmp_path).unlink()

    @patch("whisper.load_model")
    def test_transcribe_file_not_found(self, mock_load_model):
        """Test transcribing non-existent file."""
        mock_model = Mock()
        mock_load_model.return_value = mock_model

        provider = WhisperProvider()

        with pytest.raises(FileNotFoundError):
            provider.transcribe("nonexistent.wav")

    @patch("whisper.load_model")
    def test_transcribe_file_error(self, mock_load_model):
        """Test transcription failure."""
        mock_model = Mock()
        mock_model.transcribe.side_effect = Exception("Transcription failed")
        mock_load_model.return_value = mock_model

        provider = WhisperProvider()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(b"fake audio data")
            tmp_path = tmp.name

        try:
            with pytest.raises(STTError) as exc_info:
                provider.transcribe(tmp_path)

            assert "Transcription failed" in str(exc_info.value)
        finally:
            Path(tmp_path).unlink()

    @patch("whisper.DecodingOptions")
    @patch("whisper.decode")
    @patch("whisper.log_mel_spectrogram")
    @patch("whisper.pad_or_trim")
    @patch("whisper.load_model")
    def test_transcribe_audio_data_success(
        self,
        mock_load_model,
        mock_pad_or_trim,
        mock_log_mel,
        mock_decode,
        mock_decoding_options,
    ):
        """Test transcribing raw audio data successfully."""
        mock_model = Mock()
        mock_model.dims.n_mels = 80
        mock_model.device = "cpu"

        # Mock detect_language
        mock_model.detect_language.return_value = (
            None,
            {"en": 0.99, "es": 0.01},
        )

        # Mock decode
        mock_result = Mock()
        mock_result.text = "Hello from audio data"
        mock_decode.return_value = mock_result

        # Mock other Whisper functions
        mock_pad_or_trim.return_value = np.zeros(480000, dtype=np.float32)
        mock_mel = Mock()
        mock_mel.to.return_value = mock_mel
        mock_log_mel.return_value = mock_mel
        mock_decoding_options.return_value = Mock()

        mock_load_model.return_value = mock_model

        provider = WhisperProvider(language="")  # Empty for auto-detect

        # Create fake audio data (16-bit PCM)
        audio_array = np.random.randint(-32768, 32767, size=16000, dtype=np.int16)
        audio_data = audio_array.tobytes()

        result = provider.transcribe_audio_data(audio_data, sample_rate=16000)

        assert result["text"] == "Hello from audio data"
        assert result["language"] == "en"
        assert len(result["segments"]) == 1

    @patch("whisper.load_model")
    def test_get_available_models(self, mock_load_model):
        """Test getting available models."""
        mock_load_model.return_value = Mock()
        provider = WhisperProvider()

        models = provider.get_available_models()

        assert "tiny" in models
        assert "base" in models
        assert "small" in models
        assert "medium" in models
        assert "large" in models
        assert "turbo" in models

    @patch("whisper.load_model")
    def test_set_language(self, mock_load_model):
        """Test setting language."""
        mock_load_model.return_value = Mock()
        provider = WhisperProvider(language="en")

        assert provider.language == "en"

        provider.set_language("es")
        assert provider.language == "es"

        provider.set_language("")  # Auto-detect
        assert provider.language == ""

    @patch("whisper.load_model")
    def test_set_language_invalid(self, mock_load_model):
        """Test setting invalid language."""
        mock_load_model.return_value = Mock()
        provider = WhisperProvider()

        with pytest.raises(STTError):
            provider.set_language(123)  # Not a string

    @patch("whisper.load_model")
    def test_get_model_size(self, mock_load_model):
        """Test getting model size."""
        mock_load_model.return_value = Mock()
        provider = WhisperProvider(model_size="small")

        assert provider.get_model_size() == "small"

    @patch("whisper.load_model")
    def test_get_language(self, mock_load_model):
        """Test getting language."""
        mock_load_model.return_value = Mock()
        provider = WhisperProvider(language="fr")

        assert provider.get_language() == "fr"

    @patch("whisper.load_model")
    def test_resample_audio(self, mock_load_model):
        """Test audio resampling."""
        mock_load_model.return_value = Mock()
        provider = WhisperProvider()

        # Create test audio at 44100 Hz
        audio_44k = np.random.randn(44100).astype(np.float32)

        # Resample to 16000 Hz
        audio_16k = provider._resample(audio_44k, 44100, 16000)

        # Check that output length is approximately correct
        expected_length = int(len(audio_44k) * 16000 / 44100)
        assert abs(len(audio_16k) - expected_length) < 10


class TestSTTConfig:
    """Test STT configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = STTConfig()

        assert config.provider == "whisper"
        assert config.model_size == "base"
        assert config.language == "en"
        assert config.device == "cpu"
        assert config.sample_rate == 16000
        assert config.silence_threshold == 0.01
        assert config.silence_duration == 2.0

    def test_custom_config(self):
        """Test custom configuration values."""
        config = STTConfig(
            model_size="small",
            language="es",
            device="cuda",
            sample_rate=22050,
            silence_threshold=0.02,
            silence_duration=3.0,
        )

        assert config.model_size == "small"
        assert config.language == "es"
        assert config.device == "cuda"
        assert config.sample_rate == 22050
        assert config.silence_threshold == 0.02
        assert config.silence_duration == 3.0

    def test_validation_sample_rate(self):
        """Test sample rate validation."""
        with pytest.raises(Exception):  # Pydantic validation error
            STTConfig(sample_rate=100)  # Too low

        with pytest.raises(Exception):
            STTConfig(sample_rate=100000)  # Too high

    def test_validation_silence_threshold(self):
        """Test silence threshold validation."""
        with pytest.raises(Exception):
            STTConfig(silence_threshold=-0.1)  # Negative

        with pytest.raises(Exception):
            STTConfig(silence_threshold=1.5)  # Too high

    def test_validation_silence_duration(self):
        """Test silence duration validation."""
        with pytest.raises(Exception):
            STTConfig(silence_duration=0.1)  # Too short

        with pytest.raises(Exception):
            STTConfig(silence_duration=20.0)  # Too long

    @patch("whisper.load_model")
    def test_get_provider_whisper(self, mock_load_model):
        """Test getting Whisper provider from config."""
        mock_model = Mock()
        mock_load_model.return_value = mock_model

        config = STTConfig(model_size="small", language="fr", device="cpu")
        provider = config.get_provider()

        assert provider.model_size == "small"
        assert provider.language == "fr"
        assert provider.device == "cpu"

    @patch("whisper.load_model")
    def test_get_provider_initialization_error(self, mock_load_model):
        """Test provider initialization error."""
        mock_load_model.side_effect = STTError("Model load failed")

        config = STTConfig()

        with pytest.raises(ValueError) as exc_info:
            config.get_provider()

        assert "Failed to initialize Whisper provider" in str(exc_info.value)

    def test_get_provider_unknown(self):
        """Test getting unknown provider."""
        config = STTConfig(provider="unknown")

        with pytest.raises(ValueError) as exc_info:
            config.get_provider()

        assert "Unknown STT provider" in str(exc_info.value)

    def test_env_var_override(self, monkeypatch):
        """Test environment variable override."""
        monkeypatch.setenv("STT_MODEL_SIZE", "large")
        monkeypatch.setenv("STT_LANGUAGE", "de")
        monkeypatch.setenv("STT_DEVICE", "cuda")

        config = STTConfig()

        assert config.model_size == "large"
        assert config.language == "de"
        assert config.device == "cuda"
