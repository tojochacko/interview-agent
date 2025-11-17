"""Abstract base class for Text-to-Speech providers.

This module defines the interface that all TTS providers must implement,
enabling easy swapping between different TTS engines (pyttsx3, gTTS, OpenAI, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """Abstract base class for Text-to-Speech providers.

    All TTS providers must implement this interface to ensure consistent
    behavior across different TTS engines.

    Example:
        class MyTTSProvider(TTSProvider):
            def speak(self, text: str) -> None:
                # Implementation here
                pass

            def set_voice(self, voice_id: str) -> None:
                # Implementation here
                pass
    """

    @abstractmethod
    def speak(self, text: str) -> None:
        """Speak the given text aloud.

        This method should block until speech is complete.

        Args:
            text: The text to speak.

        Raises:
            TTSError: If speech synthesis fails.
        """
        pass

    @abstractmethod
    def set_voice(self, voice_id: str) -> None:
        """Set the voice to use for speech synthesis.

        Args:
            voice_id: The voice identifier. Available voices depend on the provider.

        Raises:
            TTSError: If voice ID is invalid or not available.
        """
        pass

    @abstractmethod
    def set_rate(self, rate: int) -> None:
        """Set the speech rate (words per minute).

        Args:
            rate: Speech rate in words per minute. Typical range: 100-300.

        Raises:
            TTSError: If rate is out of valid range.
        """
        pass

    @abstractmethod
    def set_volume(self, volume: float) -> None:
        """Set the speech volume.

        Args:
            volume: Volume level between 0.0 (silent) and 1.0 (maximum).

        Raises:
            TTSError: If volume is out of range.
        """
        pass

    @abstractmethod
    def get_available_voices(self) -> list[dict[str, str]]:
        """Get list of available voices.

        Returns:
            List of voice dictionaries with 'id', 'name', 'language' keys.

        Example:
            [
                {"id": "com.apple.voice.Alex", "name": "Alex", "language": "en_US"},
                {"id": "com.apple.voice.Samantha", "name": "Samantha", "language": "en_US"}
            ]
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop current speech immediately.

        This method should interrupt any ongoing speech synthesis.
        """
        pass

    def save_to_file(self, text: str, filename: str) -> None:
        """Save speech to an audio file.

        Optional method. Not all providers may support this.

        Args:
            text: The text to synthesize.
            filename: Path to save the audio file.

        Raises:
            NotImplementedError: If provider doesn't support file saving.
            TTSError: If file save fails.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support saving to file"
        )


class TTSError(Exception):
    """Exception raised when TTS operations fail."""

    pass
