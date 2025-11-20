"""Nvidia Parakeet provider for Speech-to-Text using NeMo toolkit."""

from __future__ import annotations

import logging
import tempfile
import wave
from pathlib import Path
from typing import Any

from conversation_agent.providers.stt.base import STTError, STTProvider

logger = logging.getLogger(__name__)


class ParakeetProvider(STTProvider):
    """Nvidia Parakeet-TDT Speech-to-Text provider.

    Uses Nvidia's Parakeet-TDT model via NeMo toolkit for high-performance
    speech recognition with automatic punctuation and capitalization.

    Features:
    - 50x faster than Whisper on GPU hardware
    - 25 European languages with auto-detection
    - Automatic punctuation and capitalization
    - Word-level and segment-level timestamps
    - Industry-leading 6.05% WER

    Example:
        provider = ParakeetProvider(
            model_name="nvidia/parakeet-tdt-0.6b-v3",
            language="en"
        )
        result = provider.transcribe("audio.wav")
        print(result["text"])
    """

    # Available Parakeet models
    AVAILABLE_MODELS = [
        "nvidia/parakeet-tdt-0.6b-v2",  # English-only, 600M params
        "nvidia/parakeet-tdt-0.6b-v3",  # 25 European languages, 600M params
        "nvidia/parakeet-rnnt-1.1b",  # English, 1.1B params, higher accuracy
    ]

    # Supported languages (v3 model)
    SUPPORTED_LANGUAGES = [
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

    def __init__(
        self,
        model_name: str = "nvidia/parakeet-tdt-0.6b-v3",
        language: str = "en",
        enable_timestamps: bool = True,
        use_local_attention: bool = False,
    ):
        """Initialize Parakeet provider.

        Args:
            model_name: Parakeet model identifier from HuggingFace.
            language: Language code (e.g., "en", "es"). Empty for auto-detect.
            enable_timestamps: Extract word/segment timestamps (default: True).
            use_local_attention: Use local attention for long audio (default: False).

        Raises:
            STTError: If model loading fails or invalid parameters.
        """
        if model_name not in self.AVAILABLE_MODELS:
            logger.warning(
                f"Model {model_name} not in tested list. "
                f"Tested: {', '.join(self.AVAILABLE_MODELS)}"
            )

        if language and language not in self.SUPPORTED_LANGUAGES:
            logger.warning(
                f"Language {language} may not be supported. "
                f"Supported: {', '.join(self.SUPPORTED_LANGUAGES)}"
            )

        self.model_name = model_name
        self.language = language
        self.enable_timestamps = enable_timestamps
        self.use_local_attention = use_local_attention
        self._model = None

        # Lazy load model (load on first use)
        self._load_model()

    def _load_model(self) -> None:
        """Load Parakeet model using NeMo toolkit.

        Raises:
            STTError: If model loading fails.
        """
        try:
            import nemo.collections.asr as nemo_asr  # noqa: F401

            logger.info(f"Loading Parakeet model: {self.model_name}")
            self._model = nemo_asr.models.ASRModel.from_pretrained(model_name=self.model_name)

            # Configure local attention for long audio if requested
            if self.use_local_attention:
                self._model.change_attention_model(
                    self_attention_model="rel_pos_local_attn", att_context_size=[256, 256]
                )
                logger.info("Configured local attention for long-form audio")

            logger.info(f"Successfully loaded {self.model_name}")

        except ImportError as e:
            raise STTError(
                "NeMo toolkit not installed. Install with: " "pip install nemo_toolkit[asr]"
            ) from e
        except Exception as e:
            raise STTError(f"Failed to load Parakeet model '{self.model_name}': {e}") from e

    def transcribe(self, audio_path: str) -> dict[str, Any]:
        """Transcribe audio file to text.

        Args:
            audio_path: Path to audio file (.wav, .flac preferred).

        Returns:
            Dictionary with transcription results:
            {
                "text": "Full transcription with punctuation.",
                "language": "en",
                "segments": [
                    {
                        "start": 0.0,
                        "end": 3.5,
                        "text": "Segment text."
                    }
                ]
            }

        Raises:
            STTError: If transcription fails.
            FileNotFoundError: If audio file doesn't exist.
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            # Transcribe with optional timestamps
            output = self._model.transcribe([audio_path], timestamps=self.enable_timestamps)

            # Extract transcription text
            text = output[0].text if hasattr(output[0], "text") else output[0]

            # Build segments from timestamps if available
            segments = []
            if self.enable_timestamps and hasattr(output[0], "timestamp"):
                segment_timestamps = output[0].timestamp.get("segment", [])
                for seg in segment_timestamps:
                    segments.append(
                        {
                            "start": seg.get("start", 0.0),
                            "end": seg.get("end", 0.0),
                            "text": seg.get("text", ""),
                        }
                    )
            else:
                # Fallback: single segment
                segments = [{"start": 0.0, "end": 0.0, "text": text}]

            return {
                "text": text,
                "language": self.language if self.language else "auto",
                "segments": segments,
            }

        except Exception as e:
            raise STTError(f"Transcription failed for '{audio_path}': {e}") from e

    def transcribe_audio_data(
        self, audio_data: bytes, sample_rate: int = 16000
    ) -> dict[str, Any]:
        """Transcribe raw audio data to text.

        Args:
            audio_data: Raw audio bytes (PCM format, 16-bit).
            sample_rate: Sample rate in Hz (Parakeet expects 16kHz).

        Returns:
            Dictionary with transcription results (same format as transcribe()).

        Raises:
            STTError: If transcription fails.
        """
        try:
            # Parakeet NeMo models expect file input, so write to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name

                # Write audio data to WAV file
                with wave.open(tmp_path, "wb") as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data)

            try:
                # Transcribe the temporary file
                result = self.transcribe(tmp_path)
                return result
            finally:
                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)

        except Exception as e:
            raise STTError(f"Transcription failed for audio data: {e}") from e

    def get_available_models(self) -> list[str]:
        """Get list of available Parakeet models.

        Returns:
            List of model identifiers.
        """
        return self.AVAILABLE_MODELS.copy()

    def set_language(self, language: str) -> None:
        """Set the language for transcription.

        Args:
            language: Language code (e.g., "en", "es").
                     Use empty string for auto-detection (v3 model only).

        Raises:
            STTError: If language is not supported.
        """
        if language and language not in self.SUPPORTED_LANGUAGES:
            raise STTError(
                f"Language '{language}' not supported. "
                f"Supported: {', '.join(self.SUPPORTED_LANGUAGES)}"
            )

        self.language = language
        logger.info(f"Language set to: {language if language else 'auto-detect'}")

    def get_model_size(self) -> str:
        """Get current model name.

        Returns:
            Model identifier (e.g., "nvidia/parakeet-tdt-0.6b-v3").
        """
        return self.model_name

    def get_language(self) -> str:
        """Get current language setting.

        Returns:
            Language code (e.g., "en"). Empty string means auto-detection.
        """
        return self.language
