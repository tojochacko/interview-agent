"""Piper TTS provider implementation.

This module provides a high-quality neural TTS solution using Piper ONNX models.
Piper is fast, CPU-only, and produces natural-sounding speech (~9/10 quality).
"""

from __future__ import annotations

import logging
import wave
from pathlib import Path
from typing import Optional  # noqa: UP045

import numpy as np
import pyaudio
from piper import PiperVoice

from conversation_agent.providers.tts.base import TTSError, TTSProvider

logger = logging.getLogger(__name__)


class PiperTTSProvider(TTSProvider):
    """Piper neural TTS provider.

    High-quality neural text-to-speech using ONNX models.
    Models are CPU-based and run efficiently without GPU.

    Note: Unlike pyttsx3, voice selection requires model reload (expensive).
    Rate control is not supported - models have fixed prosody.

    Example:
        provider = PiperTTSProvider(
            model_path="models/tts/piper/en_US-lessac-medium.onnx"
        )
        provider.initialize()
        provider.set_volume(0.9)
        provider.speak("Hello, world!")

    Attributes:
        model_path: Path to the ONNX model file.
        config_path: Path to the model config JSON file.
        sample_rate: Audio sample rate in Hz.
        voice: Loaded Piper voice model (lazy-loaded).
    """

    def __init__(
        self,
        model_path: str,
        config_path: Optional[str] = None,  # noqa: UP045
        sample_rate: int = 22050,
    ) -> None:
        """Initialize Piper TTS provider.

        Args:
            model_path: Path to ONNX model file (.onnx)
            config_path: Path to config file (.onnx.json).
                        If None, uses model_path + '.json'
            sample_rate: Audio sample rate (default: 22050 Hz)

        Raises:
            TTSError: If model files not found
        """
        logger.info("🔧 Initializing PiperTTSProvider...")

        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise TTSError(f"Model not found: {model_path}")

        # Auto-detect config path
        if config_path is None:
            self.config_path = Path(str(model_path) + ".json")
        else:
            self.config_path = Path(config_path)

        if not self.config_path.exists():
            raise TTSError(f"Config not found: {self.config_path}")

        self.sample_rate = sample_rate
        self.voice: Optional[PiperVoice] = None  # noqa: UP045
        self._volume = 1.0
        self._is_speaking = False

        logger.info("✅ PiperTTSProvider initialized")
        logger.info(f"   Model: {self.model_path}")
        logger.info(f"   Config: {self.config_path}")
        logger.info(f"   Sample rate: {self.sample_rate} Hz")

    def initialize(self) -> None:
        """Load the Piper voice model (lazy initialization).

        Raises:
            TTSError: If model loading fails
        """
        if self.voice is not None:
            logger.info("⚠️ Voice model already loaded, skipping initialization")
            return

        logger.info("📥 Loading Piper voice model...")
        try:
            self.voice = PiperVoice.load(
                str(self.model_path),
                config_path=str(self.config_path),
            )
            logger.info("✅ Piper voice model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Piper model: {e}")
            raise TTSError(f"Failed to load Piper model: {e}") from e

    def speak(self, text: str) -> None:
        """Synthesize and play text.

        Args:
            text: Text to speak

        Raises:
            TTSError: If synthesis or playback fails
        """
        logger.info(f"🎙️ PiperTTSProvider.speak() called with text: '{text}'")
        logger.info(f"   Text length: {len(text)} characters")

        if not text or not text.strip():
            logger.warning("⚠️ Empty text provided, skipping speech")
            return

        # Lazy load model on first speak
        if self.voice is None:
            logger.info("⏳ Model not loaded, initializing...")
            self.initialize()

        try:
            logger.info("🎵 Synthesizing audio...")
            # Synthesize returns a generator of AudioChunk objects
            audio_bytes = b""
            for audio_chunk in self.voice.synthesize(text):
                # AudioChunk has 'audio_int16_bytes' property containing the raw PCM bytes
                audio_bytes += audio_chunk.audio_int16_bytes

            logger.info(f"✅ Synthesized {len(audio_bytes)} bytes of audio")

            # Play the audio
            logger.info("🔊 Playing audio...")
            self._play_audio(audio_bytes)
            logger.info("✅ Audio playback complete")

        except Exception as e:
            logger.error(f"❌ Failed to speak text: {e}", exc_info=True)
            raise TTSError(f"Failed to speak text: {e}") from e

    def set_voice(self, voice_id: str) -> None:
        """Set voice by loading a different model.

        Warning: This is an expensive operation as it requires reloading
        the ONNX model from disk (~100ms).

        Args:
            voice_id: Path to .onnx model file

        Raises:
            TTSError: If model file not found or load fails
        """
        logger.info(f"🔄 Changing voice to: {voice_id}")

        # Validate new model path
        new_model_path = Path(voice_id)
        if not new_model_path.exists():
            raise TTSError(f"Model not found: {voice_id}")

        new_config_path = Path(str(voice_id) + ".json")
        if not new_config_path.exists():
            raise TTSError(f"Config not found: {new_config_path}")

        # Update paths and reload
        self.model_path = new_model_path
        self.config_path = new_config_path
        self.voice = None  # Clear existing model

        logger.info("🔄 Reloading model with new voice...")
        self.initialize()
        logger.info(f"✅ Voice changed to: {voice_id}")

    def set_rate(self, rate: int) -> None:
        """Rate control not supported for Piper.

        Piper models have fixed prosody. This method logs a warning
        and does nothing.

        Args:
            rate: Ignored
        """
        logger.warning(
            "⚠️ Rate control not supported for Piper TTS. "
            "Models have fixed prosody. Ignoring set_rate(%d)", rate
        )

    def set_volume(self, volume: float) -> None:
        """Set playback volume.

        Args:
            volume: Volume level 0.0-1.0

        Raises:
            TTSError: If volume out of range
        """
        logger.info(f"🔊 Setting volume to {volume}")

        if not 0.0 <= volume <= 1.0:
            logger.error(f"❌ Volume {volume} out of range (0.0-1.0)")
            raise TTSError(f"Volume {volume} out of range (0.0-1.0)")

        self._volume = volume
        logger.info(f"✅ Volume set to {volume}")

    def get_available_voices(self) -> list[dict[str, str]]:
        """Get list of available Piper models.

        Scans models/tts/piper/ for .onnx files.

        Returns:
            List of voice dictionaries with 'id', 'name', 'language' keys
        """
        logger.info("🔍 Scanning for available Piper models...")

        voices = []
        models_dir = Path("models/tts/piper")

        if not models_dir.exists():
            logger.warning(f"⚠️ Models directory not found: {models_dir}")
            return voices

        for model_file in models_dir.glob("*.onnx"):
            # Extract voice name from filename (e.g., en_US-lessac-medium)
            voice_name = model_file.stem

            # Parse language from filename (e.g., en_US)
            parts = voice_name.split("-")
            language = parts[0] if parts else "unknown"

            voices.append({
                "id": str(model_file),
                "name": voice_name,
                "language": language,
            })

        logger.info(f"✅ Found {len(voices)} Piper models")
        return voices

    def stop(self) -> None:
        """Stop current speech immediately.

        Note: Current implementation does not support interruption
        during playback. This is a limitation of the simple pyaudio
        playback approach.
        """
        logger.warning("⚠️ Stop not fully supported for Piper (playback blocking)")
        self._is_speaking = False

    def save_to_file(self, text: str, filename: str) -> None:
        """Save speech to WAV file.

        Args:
            text: Text to synthesize
            filename: Output path (.wav)

        Raises:
            TTSError: If save fails
        """
        logger.info(f"💾 Saving speech to file: {filename}")

        if not filename.endswith(".wav"):
            raise TTSError("Piper only supports .wav format. Use filename ending in .wav")

        # Lazy load model if needed
        if self.voice is None:
            self.initialize()

        try:
            # Synthesize audio
            logger.info("🎵 Synthesizing audio...")
            audio_bytes = b""
            for audio_chunk in self.voice.synthesize(text):
                # AudioChunk has 'audio_int16_bytes' property containing the raw PCM bytes
                audio_bytes += audio_chunk.audio_int16_bytes

            logger.info(f"✅ Synthesized {len(audio_bytes)} bytes")

            # Write to WAV file
            logger.info(f"💾 Writing to {filename}...")
            with wave.open(filename, "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_bytes)

            logger.info(f"✅ Saved to {filename}")

        except Exception as e:
            logger.error(f"❌ Failed to save to file: {e}", exc_info=True)
            raise TTSError(f"Failed to save to file: {e}") from e

    def _play_audio(self, audio_data: bytes) -> None:
        """Play PCM audio with volume control.

        Args:
            audio_data: Raw PCM audio bytes (16-bit mono)
        """
        logger.info(f"🔊 Playing {len(audio_data)} bytes of audio")

        try:
            # Apply volume scaling
            if self._volume != 1.0:
                logger.info(f"🎚️ Applying volume scaling: {self._volume}")
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                audio_array = (audio_array * self._volume).astype(np.int16)
                audio_data = audio_array.tobytes()

            # Initialize PyAudio
            p = pyaudio.PyAudio()

            # Open stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,  # Mono
                rate=self.sample_rate,
                output=True,
            )

            # Play audio
            self._is_speaking = True
            stream.write(audio_data)

            # Cleanup
            stream.stop_stream()
            stream.close()
            p.terminate()
            self._is_speaking = False

            logger.info("✅ Audio playback complete")

        except Exception as e:
            self._is_speaking = False
            logger.error(f"❌ Audio playback failed: {e}", exc_info=True)
            raise TTSError(f"Audio playback failed: {e}") from e

    def shutdown(self) -> None:
        """Clean up resources."""
        logger.info("🧹 Shutting down PiperTTSProvider...")
        self.voice = None
        logger.info("✅ Shutdown complete")

    def __del__(self) -> None:
        """Clean up on deletion."""
        try:
            self.shutdown()
        except Exception:
            pass  # Ignore errors during cleanup
