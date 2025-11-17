"""Abstract base class for Speech-to-Text (STT) providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class STTError(Exception):
    """Exception raised when STT operations fail."""

    pass


class STTProvider(ABC):
    """Abstract base class for Speech-to-Text providers.

    All STT providers must implement this interface to ensure consistent
    behavior across different STT engines.

    Example:
        class MySTTProvider(STTProvider):
            def transcribe(self, audio_path: str) -> dict[str, Any]:
                # Implementation here
                pass

            def transcribe_audio_data(
                self, audio_data: bytes, sample_rate: int
            ) -> dict[str, Any]:
                # Implementation here
                pass
    """

    @abstractmethod
    def transcribe(self, audio_path: str) -> dict[str, Any]:
        """Transcribe audio file to text.

        Args:
            audio_path: Path to audio file (mp3, wav, m4a, etc.).

        Returns:
            Dictionary containing transcription results:
            {
                "text": "transcribed text",
                "language": "en",
                "segments": [
                    {
                        "start": 0.0,
                        "end": 3.5,
                        "text": "segment text"
                    }
                ]
            }

        Raises:
            STTError: If transcription fails.
            FileNotFoundError: If audio file doesn't exist.
        """
        pass

    @abstractmethod
    def transcribe_audio_data(
        self, audio_data: bytes, sample_rate: int = 16000
    ) -> dict[str, Any]:
        """Transcribe raw audio data to text.

        Args:
            audio_data: Raw audio bytes (PCM format).
            sample_rate: Sample rate in Hz (default: 16000).

        Returns:
            Dictionary containing transcription results (same format as transcribe()).

        Raises:
            STTError: If transcription fails.
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of available models for this provider.

        Returns:
            List of model identifiers.

        Example:
            ["tiny", "base", "small", "medium", "large"]
        """
        pass

    @abstractmethod
    def set_language(self, language: str) -> None:
        """Set the language for transcription.

        Args:
            language: Language code (e.g., "en", "es", "fr").

        Raises:
            STTError: If language is not supported.
        """
        pass

    def get_model_size(self) -> str:
        """Get current model size/name.

        Optional method. Not all providers may support this.

        Returns:
            Model size identifier (e.g., "base", "small").

        Raises:
            NotImplementedError: If provider doesn't support this operation.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support getting model size"
        )

    def get_language(self) -> str:
        """Get current language setting.

        Optional method. Not all providers may support this.

        Returns:
            Language code (e.g., "en").

        Raises:
            NotImplementedError: If provider doesn't support this operation.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support getting language"
        )
