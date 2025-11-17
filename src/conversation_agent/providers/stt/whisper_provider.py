"""Whisper provider for Speech-to-Text using OpenAI Whisper."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from conversation_agent.providers.stt.base import STTError, STTProvider


class WhisperProvider(STTProvider):
    """OpenAI Whisper Speech-to-Text provider.

    This provider uses OpenAI's Whisper model for local, offline speech
    recognition. Models are downloaded automatically on first use and cached.

    Example:
        provider = WhisperProvider(model_size="base", language="en")
        result = provider.transcribe("audio.mp3")
        print(result["text"])
    """

    # Available Whisper models
    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large", "turbo"]

    def __init__(
        self, model_size: str = "base", language: str = "en", device: str = "cpu"
    ):
        """Initialize Whisper provider.

        Args:
            model_size: Model size (tiny, base, small, medium, large, turbo).
            language: Language code for transcription (e.g., "en", "es", "fr").
            device: Device to use ("cpu" or "cuda").

        Raises:
            STTError: If model loading fails or invalid parameters.
        """
        if model_size not in self.AVAILABLE_MODELS:
            raise STTError(
                f"Invalid model size: {model_size}. "
                f"Available: {', '.join(self.AVAILABLE_MODELS)}"
            )

        self.model_size = model_size
        self.language = language
        self.device = device
        self._model = None

        # Lazy load model (load on first use)
        self._load_model()

    def _load_model(self) -> None:
        """Load Whisper model.

        Raises:
            STTError: If model loading fails.
        """
        try:
            import whisper

            self._model = whisper.load_model(self.model_size, device=self.device)
        except ImportError as e:
            raise STTError(
                "Whisper not installed. Install with: pip install openai-whisper"
            ) from e
        except Exception as e:
            raise STTError(f"Failed to load Whisper model '{self.model_size}': {e}") from e

    def transcribe(self, audio_path: str) -> dict[str, Any]:
        """Transcribe audio file to text.

        Args:
            audio_path: Path to audio file.

        Returns:
            Dictionary with transcription results:
            {
                "text": "full transcription",
                "language": "en",
                "segments": [
                    {"start": 0.0, "end": 3.5, "text": "segment text"},
                    ...
                ]
            }

        Raises:
            STTError: If transcription fails.
            FileNotFoundError: If audio file doesn't exist.
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            # Transcribe with Whisper
            result = self._model.transcribe(
                audio_path,
                language=self.language if self.language else None,
                fp16=(self.device == "cuda"),  # Use FP16 on GPU
            )

            return {
                "text": result["text"],
                "language": result.get("language", self.language),
                "segments": [
                    {
                        "start": seg["start"],
                        "end": seg["end"],
                        "text": seg["text"],
                    }
                    for seg in result.get("segments", [])
                ],
            }
        except Exception as e:
            raise STTError(f"Transcription failed for '{audio_path}': {e}") from e

    def transcribe_audio_data(
        self, audio_data: bytes, sample_rate: int = 16000
    ) -> dict[str, Any]:
        """Transcribe raw audio data to text.

        Args:
            audio_data: Raw audio bytes (PCM format, 16-bit).
            sample_rate: Sample rate in Hz.

        Returns:
            Dictionary with transcription results (same format as transcribe()).

        Raises:
            STTError: If transcription fails.
        """
        try:
            import whisper

            # Convert bytes to numpy array
            # Assuming 16-bit PCM audio
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)

            # Normalize to [-1.0, 1.0]
            audio_array = audio_array / 32768.0

            # Resample if needed (Whisper expects 16kHz)
            if sample_rate != 16000:
                audio_array = self._resample(audio_array, sample_rate, 16000)

            # Pad or trim to 30 seconds (Whisper processes in 30s chunks)
            audio_array = whisper.pad_or_trim(audio_array)

            # Create mel spectrogram
            mel = whisper.log_mel_spectrogram(
                audio_array, n_mels=self._model.dims.n_mels
            ).to(self._model.device)

            # Detect language if not specified
            if not self.language:
                _, probs = self._model.detect_language(mel)
                detected_lang = max(probs, key=probs.get)
            else:
                detected_lang = self.language

            # Decode audio
            options = whisper.DecodingOptions(language=detected_lang, fp16=(self.device == "cuda"))
            result = whisper.decode(self._model, mel, options)

            return {
                "text": result.text,
                "language": detected_lang,
                "segments": [
                    {
                        "start": 0.0,
                        "end": 30.0,
                        "text": result.text,
                    }
                ],
            }
        except ImportError as e:
            raise STTError(
                "Required libraries not installed. Install with: "
                "pip install openai-whisper numpy"
            ) from e
        except Exception as e:
            raise STTError(f"Transcription failed for audio data: {e}") from e

    def _resample(
        self, audio: np.ndarray, orig_sr: int, target_sr: int
    ) -> np.ndarray:
        """Resample audio to target sample rate.

        Args:
            audio: Audio array.
            orig_sr: Original sample rate.
            target_sr: Target sample rate.

        Returns:
            Resampled audio array.
        """
        # Simple linear interpolation resampling
        # For production, consider using librosa or scipy for better quality
        duration = len(audio) / orig_sr
        target_length = int(duration * target_sr)

        indices = np.linspace(0, len(audio) - 1, target_length)
        resampled = np.interp(indices, np.arange(len(audio)), audio)

        return resampled.astype(np.float32)

    def get_available_models(self) -> list[str]:
        """Get list of available Whisper models.

        Returns:
            List of model names.
        """
        return self.AVAILABLE_MODELS.copy()

    def set_language(self, language: str) -> None:
        """Set the language for transcription.

        Args:
            language: Language code (e.g., "en", "es", "fr").
                     Use empty string for auto-detection.

        Raises:
            STTError: If language format is invalid.
        """
        if language and not isinstance(language, str):
            raise STTError(f"Language must be a string, got {type(language)}")

        self.language = language

    def get_model_size(self) -> str:
        """Get current model size.

        Returns:
            Model size identifier (e.g., "base", "small").
        """
        return self.model_size

    def get_language(self) -> str:
        """Get current language setting.

        Returns:
            Language code (e.g., "en"). Empty string means auto-detection.
        """
        return self.language
