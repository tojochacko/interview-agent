"""pyttsx3-based Text-to-Speech provider implementation.

This module provides an offline TTS solution using pyttsx3, which works
across Windows (SAPI5), macOS (NSSpeechSynthesizer), and Linux (eSpeak).
"""

from __future__ import annotations

import logging

import pyttsx3

from conversation_agent.providers.tts.base import TTSError, TTSProvider

logger = logging.getLogger(__name__)


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

    def __init__(self, enable_macos_workaround: bool = True) -> None:
        """Initialize the pyttsx3 TTS provider.

        Args:
            enable_macos_workaround: Enable startLoop/iterate/endLoop pattern
                on macOS instead of runAndWait(). This works around a known issue
                where NSSpeechSynthesizer fails on subsequent calls. Default: True.

        Raises:
            TTSError: If pyttsx3 engine initialization fails.
        """
        logger.info("🔧 Initializing Pyttsx3Provider...")

        # Store workaround preference
        self._enable_macos_workaround = enable_macos_workaround

        try:
            self.engine = pyttsx3.init()
            logger.info("✅ pyttsx3 engine initialized successfully")

            # Log current engine properties
            try:
                rate = self.engine.getProperty("rate")
                volume = self.engine.getProperty("volume")
                voice = self.engine.getProperty("voice")
                logger.info(f"   Default rate: {rate} WPM")
                logger.info(f"   Default volume: {volume}")
                logger.info(f"   Default voice: {voice}")
            except Exception as e:
                logger.warning(f"⚠️ Could not retrieve engine properties: {e}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize pyttsx3 engine: {e}")
            raise TTSError(f"Failed to initialize pyttsx3 engine: {e}") from e

    def speak(self, text: str) -> None:
        """Speak the given text aloud.

        Note: On macOS, uses startLoop/iterate/endLoop pattern instead of
        runAndWait() to work around a known issue where NSSpeechSynthesizer
        fails on subsequent calls.

        Args:
            text: The text to speak.

        Raises:
            TTSError: If speech synthesis fails.
        """
        logger.info(f"🎙️ Pyttsx3Provider.speak() called with text: '{text}'")
        logger.info(f"   Text length: {len(text)} characters")

        if not text or not text.strip():
            logger.warning("⚠️ Empty text provided, skipping speech")
            return  # Don't speak empty text

        try:
            import platform
            import time

            logger.info("📝 Calling engine.say()...")
            self.engine.say(text)

            # macOS workaround: Use startLoop/iterate/endLoop instead of runAndWait
            if self._enable_macos_workaround and platform.system() == 'Darwin':
                logger.info("🍎 macOS detected - using startLoop/iterate/endLoop pattern")

                # Start the event loop without blocking
                self.engine.startLoop(False)

                # Estimate speech duration based on text length and rate
                # Average word length: 5 characters + 1 space = 6 chars
                # Rate is in words per minute
                rate = self.engine.getProperty("rate") or 150
                estimated_words = len(text) / 6.0
                estimated_seconds = (estimated_words / rate) * 60.0

                # Dynamic buffer: 20% overhead + minimum 1s for engine startup
                # Longer texts need proportionally more time for natural pauses
                buffer = max(1.0, estimated_seconds * 0.2)
                timeout = estimated_seconds + buffer

                logger.debug(
                    f"Estimated speech duration: {estimated_seconds:.2f}s "
                    f"(buffer: {buffer:.2f}s, timeout: {timeout:.2f}s)"
                )

                # Iterate for the estimated duration
                start_time = time.time()
                iteration_count = 0

                while time.time() - start_time < timeout:
                    self.engine.iterate()
                    iteration_count += 1

                    # Minimal delay every 10 iterations to prevent CPU spinning
                    if iteration_count % 10 == 0:
                        time.sleep(0.001)  # 1ms

                elapsed = time.time() - start_time
                logger.info(
                    f"✅ Speech completed after {iteration_count} iterations "
                    f"({elapsed:.2f}s)"
                )

                # End the loop
                self.engine.endLoop()
                logger.info("✅ Event loop ended")

            else:
                # Standard runAndWait for non-macOS or when workaround is disabled
                logger.info("⏳ Calling engine.runAndWait() - blocking until speech completes...")
                self.engine.runAndWait()
                logger.info("✅ engine.runAndWait() completed - speech finished")

        except Exception as e:
            logger.error(f"❌ Failed to speak text: {e}", exc_info=True)
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
        logger.info(f"🎚️ Setting TTS rate to {rate} WPM")

        if rate < 50 or rate > 400:
            logger.error(f"❌ Rate {rate} out of range (50-400 WPM)")
            raise TTSError(f"Rate {rate} out of range. Use 50-400 WPM.")

        try:
            self.engine.setProperty("rate", rate)
            logger.info(f"✅ Rate set to {rate} WPM")
        except Exception as e:
            logger.error(f"❌ Failed to set rate: {e}")
            raise TTSError(f"Failed to set rate: {e}") from e

    def set_volume(self, volume: float) -> None:
        """Set the speech volume.

        Args:
            volume: Volume level between 0.0 (silent) and 1.0 (maximum).

        Raises:
            TTSError: If volume is out of range.
        """
        logger.info(f"🔊 Setting TTS volume to {volume}")

        if volume < 0.0 or volume > 1.0:
            logger.error(f"❌ Volume {volume} out of range (0.0-1.0)")
            raise TTSError(f"Volume {volume} out of range. Use 0.0-1.0.")

        try:
            self.engine.setProperty("volume", volume)
            logger.info(f"✅ Volume set to {volume}")
        except Exception as e:
            logger.error(f"❌ Failed to set volume: {e}")
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
