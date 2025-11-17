"""Tests for audio manager."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest

# Mock pyaudio module before importing our code
sys.modules["pyaudio"] = Mock()

from conversation_agent.core.audio import AudioError, AudioManager


class TestAudioManager:
    """Test audio manager functionality."""

    def test_initialization_success(self):
        """Test successful audio manager initialization."""
        audio_mgr = AudioManager(sample_rate=16000, chunk_size=1024)

        assert audio_mgr.sample_rate == 16000
        assert audio_mgr.chunk_size == 1024
        assert audio_mgr.channels == 1
        assert audio_mgr.format_bits == 16

    def test_initialization_invalid_bit_depth(self):
        """Test initialization with invalid bit depth."""
        with pytest.raises(AudioError) as exc_info:
            AudioManager(format_bits=24)

        assert "Unsupported bit depth" in str(exc_info.value)

    def test_record_negative_duration(self):
        """Test recording with negative duration."""
        audio_mgr = AudioManager()

        with pytest.raises(AudioError) as exc_info:
            audio_mgr.record(duration=-1.0)

        assert "Duration must be positive" in str(exc_info.value)

    def test_record_until_silence_invalid_threshold(self):
        """Test recording with invalid silence threshold."""
        audio_mgr = AudioManager()

        with pytest.raises(AudioError) as exc_info:
            audio_mgr.record_until_silence(silence_threshold=1.5)

        assert "Silence threshold must be 0.0-1.0" in str(exc_info.value)

    def test_record_until_silence_invalid_duration(self):
        """Test recording with invalid silence duration."""
        audio_mgr = AudioManager()

        with pytest.raises(AudioError) as exc_info:
            audio_mgr.record_until_silence(silence_duration=-1.0)

        assert "Silence duration must be positive" in str(exc_info.value)

    def test_record_until_silence_invalid_max_duration(self):
        """Test recording with invalid max duration."""
        audio_mgr = AudioManager()

        with pytest.raises(AudioError) as exc_info:
            audio_mgr.record_until_silence(max_duration=-1.0)

        assert "Max duration must be positive" in str(exc_info.value)

    def test_calculate_amplitude(self):
        """Test amplitude calculation."""
        audio_mgr = AudioManager()

        # Test with 16-bit audio
        audio_array = np.array([0, 16384, -16384, 0], dtype=np.int16)
        audio_data = audio_array.tobytes()

        amplitude = audio_mgr._calculate_amplitude(audio_data)

        assert 0.0 <= amplitude <= 1.0
        assert amplitude > 0.0  # Non-silent audio

    def test_save_to_wav_invalid_extension(self):
        """Test saving with invalid file extension."""
        audio_mgr = AudioManager()

        with pytest.raises(AudioError) as exc_info:
            audio_mgr.save_to_wav(b"data", "output.mp3")

        assert "must end with .wav" in str(exc_info.value)

    def test_save_to_wav_file_exists(self):
        """Test saving when file already exists."""
        audio_mgr = AudioManager()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(b"existing data")
            tmp_path = tmp.name

        try:
            with pytest.raises(FileExistsError):
                audio_mgr.save_to_wav(b"new data", tmp_path, overwrite=False)
        finally:
            Path(tmp_path).unlink()

    def test_save_to_wav_success(self):
        """Test saving audio to WAV file."""
        audio_mgr = AudioManager(sample_rate=16000)

        # Create fake audio data
        audio_array = np.random.randint(-32768, 32767, size=16000, dtype=np.int16)
        audio_data = audio_array.tobytes()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.wav"
            audio_mgr.save_to_wav(audio_data, str(output_path))

            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_save_to_wav_overwrite(self):
        """Test saving with overwrite enabled."""
        audio_mgr = AudioManager(sample_rate=16000)

        audio_array = np.random.randint(-32768, 32767, size=1000, dtype=np.int16)
        audio_data = audio_array.tobytes()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(b"old data")
            tmp_path = tmp.name

        try:
            # Should succeed with overwrite=True
            audio_mgr.save_to_wav(audio_data, tmp_path, overwrite=True)
            assert Path(tmp_path).exists()
        finally:
            Path(tmp_path).unlink()

    def test_get_sample_rate(self):
        """Test getting sample rate."""
        audio_mgr = AudioManager(sample_rate=22050)

        assert audio_mgr.get_sample_rate() == 22050

    def test_get_channels(self):
        """Test getting number of channels."""
        audio_mgr = AudioManager(channels=2)

        assert audio_mgr.get_channels() == 2
