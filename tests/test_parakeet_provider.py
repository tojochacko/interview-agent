"""Tests for Parakeet STT provider."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

# Mock nemo module before importing our code
sys.modules["nemo"] = MagicMock()
sys.modules["nemo.collections"] = MagicMock()
sys.modules["nemo.collections.asr"] = MagicMock()
sys.modules["nemo.collections.asr.models"] = MagicMock()

from conversation_agent.providers.stt import ParakeetProvider, STTError  # noqa: E402


class TestParakeetProvider:
    """Test Parakeet provider implementation."""

    def test_initialization_valid_model(self):
        """Test provider initialization with valid model."""
        # Mock NeMo to avoid actual model download
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider(
                model_name="nvidia/parakeet-tdt-0.6b-v3", language="en"
            )
            assert provider.model_name == "nvidia/parakeet-tdt-0.6b-v3"
            assert provider.language == "en"
            assert provider.enable_timestamps is True
            assert provider.use_local_attention is False

    def test_initialization_custom_model(self):
        """Test warning for untested model."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            # Should not raise, just warn
            provider = ParakeetProvider(model_name="custom/model")
            assert provider.model_name == "custom/model"

    def test_initialization_unsupported_language(self):
        """Test warning for unsupported language."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            # Should not raise, just warn
            provider = ParakeetProvider(language="zh")
            assert provider.language == "zh"

    def test_load_model_missing_nemo(self):
        """Test error when NeMo not installed."""
        with patch("builtins.__import__", side_effect=ImportError("No module named 'nemo'")):
            with pytest.raises(STTError, match="NeMo toolkit not installed"):
                ParakeetProvider()

    def test_load_model_failure(self):
        """Test error when model loading fails."""
        with patch(
            "nemo.collections.asr.models.ASRModel.from_pretrained",
            side_effect=RuntimeError("Model download failed"),
        ):
            with pytest.raises(STTError, match="Failed to load Parakeet model"):
                ParakeetProvider()

    def test_transcribe_file_success(self, tmp_path):
        """Test transcribing audio file."""
        # Create dummy audio file
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"dummy audio data")

        # Mock NeMo model
        mock_model = MagicMock()
        mock_output = Mock()
        mock_output.text = "Hello world."
        mock_output.timestamp = {
            "segment": [{"start": 0.0, "end": 1.5, "text": "Hello world."}]
        }
        mock_model.transcribe.return_value = [mock_output]

        with patch(
            "nemo.collections.asr.models.ASRModel.from_pretrained", return_value=mock_model
        ):
            provider = ParakeetProvider()
            result = provider.transcribe(str(audio_file))

        assert result["text"] == "Hello world."
        assert result["language"] == "en"
        assert len(result["segments"]) == 1
        assert result["segments"][0]["text"] == "Hello world."
        assert result["segments"][0]["start"] == 0.0
        assert result["segments"][0]["end"] == 1.5

    def test_transcribe_file_not_found(self):
        """Test error when audio file doesn't exist."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider()
            with pytest.raises(FileNotFoundError):
                provider.transcribe("/nonexistent/audio.wav")

    def test_transcribe_no_timestamps(self, tmp_path):
        """Test transcription without timestamps."""
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"dummy")

        mock_model = MagicMock()
        mock_output = Mock()
        mock_output.text = "Test transcription."
        # No timestamp attribute
        mock_model.transcribe.return_value = [mock_output]

        with patch(
            "nemo.collections.asr.models.ASRModel.from_pretrained", return_value=mock_model
        ):
            provider = ParakeetProvider(enable_timestamps=False)
            result = provider.transcribe(str(audio_file))

        assert result["text"] == "Test transcription."
        assert len(result["segments"]) == 1
        assert result["segments"][0]["text"] == "Test transcription."

    def test_transcribe_failure(self, tmp_path):
        """Test error handling when transcription fails."""
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"dummy")

        mock_model = MagicMock()
        mock_model.transcribe.side_effect = RuntimeError("Transcription error")

        with patch(
            "nemo.collections.asr.models.ASRModel.from_pretrained", return_value=mock_model
        ):
            provider = ParakeetProvider()
            with pytest.raises(STTError, match="Transcription failed"):
                provider.transcribe(str(audio_file))

    def test_transcribe_audio_data(self):
        """Test transcribing raw audio data."""
        # Mock NeMo and temp file creation
        mock_model = MagicMock()
        mock_output = Mock()
        mock_output.text = "Test transcription."
        mock_output.timestamp = {"segment": []}
        mock_model.transcribe.return_value = [mock_output]

        with patch(
            "nemo.collections.asr.models.ASRModel.from_pretrained", return_value=mock_model
        ):
            provider = ParakeetProvider()

            # Create dummy PCM audio data
            audio_data = np.random.randint(-32768, 32767, size=16000, dtype=np.int16).tobytes()

            result = provider.transcribe_audio_data(audio_data, sample_rate=16000)

        assert "text" in result
        assert result["text"] == "Test transcription."

    def test_transcribe_audio_data_failure(self):
        """Test error handling for audio data transcription failure."""
        mock_model = MagicMock()
        mock_model.transcribe.side_effect = RuntimeError("Processing error")

        with patch(
            "nemo.collections.asr.models.ASRModel.from_pretrained", return_value=mock_model
        ):
            provider = ParakeetProvider()

            audio_data = b"\x00" * 16000

            with pytest.raises(STTError, match="Transcription failed for audio data"):
                provider.transcribe_audio_data(audio_data)

    def test_get_available_models(self):
        """Test listing available models."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider()
            models = provider.get_available_models()

        assert "nvidia/parakeet-tdt-0.6b-v3" in models
        assert "nvidia/parakeet-tdt-0.6b-v2" in models
        assert "nvidia/parakeet-rnnt-1.1b" in models
        assert len(models) == 3

    def test_set_language_valid(self):
        """Test setting valid language."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider()
            provider.set_language("es")
            assert provider.get_language() == "es"

    def test_set_language_invalid(self):
        """Test error for invalid language."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider()
            with pytest.raises(STTError, match="not supported"):
                provider.set_language("invalid")

    def test_set_language_empty_for_auto_detect(self):
        """Test setting empty language for auto-detection."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider()
            provider.set_language("")
            assert provider.get_language() == ""

    def test_get_model_size(self):
        """Test getting model name."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider(model_name="nvidia/parakeet-rnnt-1.1b")
            assert provider.get_model_size() == "nvidia/parakeet-rnnt-1.1b"

    def test_local_attention_mode(self):
        """Test local attention configuration for long audio."""
        mock_model = MagicMock()
        with patch(
            "nemo.collections.asr.models.ASRModel.from_pretrained", return_value=mock_model
        ):
            provider = ParakeetProvider(use_local_attention=True)

        # Verify change_attention_model was called
        mock_model.change_attention_model.assert_called_once_with(
            self_attention_model="rel_pos_local_attn", att_context_size=[256, 256]
        )
        assert provider.use_local_attention is True

    def test_timestamps_enabled(self, tmp_path):
        """Test timestamp extraction when enabled."""
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"dummy")

        mock_model = MagicMock()
        mock_output = Mock()
        mock_output.text = "Test."
        mock_output.timestamp = {
            "word": [{"start": 0.0, "end": 0.5, "text": "Test."}],
            "segment": [{"start": 0.0, "end": 0.5, "text": "Test."}],
        }
        mock_model.transcribe.return_value = [mock_output]

        with patch(
            "nemo.collections.asr.models.ASRModel.from_pretrained", return_value=mock_model
        ):
            provider = ParakeetProvider(enable_timestamps=True)
            result = provider.transcribe(str(audio_file))

        # Verify transcribe called with timestamps=True
        call_args = mock_model.transcribe.call_args
        assert call_args[1]["timestamps"] is True

        # Verify segments extracted
        assert len(result["segments"]) > 0

    def test_supported_languages(self):
        """Test that all expected languages are supported."""
        expected_languages = [
            "en",
            "es",
            "fr",
            "de",
            "it",
            "pt",
            "pl",
            "nl",
            "cs",
            "ro",
            "hu",
            "el",
            "bg",
            "hr",
            "da",
            "fi",
            "sk",
            "sl",
            "sv",
            "et",
            "lt",
            "lv",
            "mt",
            "ga",
            "cy",
        ]

        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider()

            for lang in expected_languages:
                # Should not raise
                provider.set_language(lang)
                assert provider.get_language() == lang
