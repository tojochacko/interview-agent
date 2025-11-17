"""pyttsx3-based Text-to-Speech provider implementation.

This module provides an offline TTS solution using pyttsx3, which works
across Windows (SAPI5), macOS (NSSpeechSynthesizer), and Linux (eSpeak).
"""

from __future__ import annotations

import pyttsx3

from conversation_agent.providers.tts.base import TTSError, TTSProvider


class Pyttsx3Provider(TTSProvider):
    """TTS provider using pyttsx3 for offline speech synthesis.

    This provider uses the system's built-in TTS engine:
    - Windows: SAPI5
    - macOS: NSSpeechSynthesizer
    - Linux: eSpeak

    Example:
        provider = Pyttsx3Provider()
        provider.set_rate(150)
        provider.set_volume(0.9)
        provider.speak("Hello, world!")

    Attributes:
        engine: The pyttsx3 engine instance.
    """

    def __init__(self) -> None:
        """Initialize the pyttsx3 TTS provider.

        Raises:
            TTSError: If pyttsx3 engine initialization fails.
        """
        try:
            self.engine = pyttsx3.init()
        except Exception as e:
            raise TTSError(f"Failed to initialize pyttsx3 engine: {e}") from e

    def speak(self, text: str) -> None:
        """Speak the given text aloud.

        Args:
            text: The text to speak.

        Raises:
            TTSError: If speech synthesis fails.
        """
        if not text or not text.strip():
            return  # Don't speak empty text

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            raise TTSError(f"Failed to speak text: {e}") from e

    def set_voice(self, voice_id: str) -> None:
        """Set the voice to use for speech synthesis.

        Args:
            voice_id: The voice identifier from available voices.

        Raises:
            TTSError: If voice ID is invalid or not available.
        """
        try:
            voices = self.engine.getProperty("voices")
            voice_ids = [voice.id for voice in voices]

            if voice_id not in voice_ids:
                raise TTSError(
                    f"Voice '{voice_id}' not found. Available voices: {voice_ids}"
                )

            self.engine.setProperty("voice", voice_id)
        except TTSError:
            raise
        except Exception as e:
            raise TTSError(f"Failed to set voice: {e}") from e

    def set_rate(self, rate: int) -> None:
        """Set the speech rate (words per minute).

        Args:
            rate: Speech rate in words per minute. Typical range: 100-300.
                 Default is usually ~200 WPM.

        Raises:
            TTSError: If rate setting fails.
        """
        if rate < 50 or rate > 400:
            raise TTSError(f"Rate {rate} out of range. Use 50-400 WPM.")

        try:
            self.engine.setProperty("rate", rate)
        except Exception as e:
            raise TTSError(f"Failed to set rate: {e}") from e

    def set_volume(self, volume: float) -> None:
        """Set the speech volume.

        Args:
            volume: Volume level between 0.0 (silent) and 1.0 (maximum).

        Raises:
            TTSError: If volume is out of range.
        """
        if volume < 0.0 or volume > 1.0:
            raise TTSError(f"Volume {volume} out of range. Use 0.0-1.0.")

        try:
            self.engine.setProperty("volume", volume)
        except Exception as e:
            raise TTSError(f"Failed to set volume: {e}") from e

    def get_available_voices(self) -> list[dict[str, str]]:
        """Get list of available voices.

        Returns:
            List of voice dictionaries with 'id', 'name', 'language' keys.

        Example:
            [
                {
                    "id": "com.apple.voice.Alex",
                    "name": "Alex",
                    "language": "en_US"
                }
            ]
        """
        try:
            voices = self.engine.getProperty("voices")
            return [
                {
                    "id": voice.id,
                    "name": voice.name,
                    "language": getattr(voice, "languages", ["unknown"])[0]
                    if hasattr(voice, "languages")
                    else "unknown",
                }
                for voice in voices
            ]
        except Exception as e:
            raise TTSError(f"Failed to get available voices: {e}") from e

    def stop(self) -> None:
        """Stop current speech immediately."""
        try:
            self.engine.stop()
        except Exception as e:
            raise TTSError(f"Failed to stop speech: {e}") from e

    def save_to_file(self, text: str, filename: str) -> None:
        """Save speech to an audio file.

        Args:
            text: The text to synthesize.
            filename: Path to save the audio file (must end with .wav).

        Raises:
            TTSError: If file save fails or filename doesn't end with .wav.
        """
        if not filename.endswith(".wav"):
            raise TTSError("pyttsx3 only supports .wav format. Use filename ending in .wav")

        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
        except Exception as e:
            raise TTSError(f"Failed to save to file: {e}") from e

    def __del__(self) -> None:
        """Clean up the pyttsx3 engine on deletion."""
        try:
            if hasattr(self, "engine"):
                self.engine.stop()
        except Exception:
            pass  # Ignore errors during cleanup
