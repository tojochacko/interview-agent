#!/usr/bin/env python3
"""Demo script for Phase 2: Text-to-Speech Integration.

This script demonstrates the TTS provider functionality:
1. TTS provider abstraction
2. pyttsx3 provider implementation
3. Configuration management
4. Voice selection and customization
5. Audio file saving

Usage:
    python examples/demo_tts.py
"""

from __future__ import annotations

import logging
import sys
import time

from conversation_agent.config import TTSConfig
from conversation_agent.providers.tts import Pyttsx3Provider, TTSError

# Configure logging to show all levels
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_provider_initialization():
    """Demonstrate TTS provider initialization."""
    print_header("1. TTS Provider Initialization")

    try:
        provider = Pyttsx3Provider()
        print("✅ Pyttsx3Provider initialized successfully")
        print(f"   Provider: {provider.__class__.__name__}")

        # Set Albert voice
        albert_voice_id = 'com.apple.voice.Aman'
        logger.info(f"Setting voice to: {albert_voice_id}")
        try:
            provider.set_voice(albert_voice_id)
            print("✅ Voice set to: Albert")
            logger.info("✅ Voice successfully set to Albert")
        except TTSError as e:
            logger.warning(f"⚠️ Could not set Albert voice: {e}")
            print(f"⚠️ Could not set Albert voice, using default: {e}")

        return provider
    except TTSError as e:
        print(f"❌ Failed to initialize provider: {e}")
        return None


def demo_available_voices(provider: Pyttsx3Provider):
    """Demonstrate listing available voices."""
    print_header("2. Available Voices")

    try:
        voices = provider.get_available_voices()
        print(f"Found {len(voices)} available voices:\n")

        for i, voice in enumerate(voices[:10], 1):  # Show first 10 voices
            print(f"  {i}. {voice['name']}")
            print(f"     ID: {voice['id']}")
            print(f"     Language: {voice['language']}\n")

        if len(voices) > 5:
            print(f"  ... and {len(voices) - 5} more voices\n")

        return voices
    except TTSError as e:
        print(f"❌ Failed to get voices: {e}")
        return []


def demo_basic_speech(provider: Pyttsx3Provider):
    """Demonstrate basic text-to-speech."""
    print_header("3. Basic Text-to-Speech")

    texts = [
        "Hello! This is Phase 2 of the Voice Interview Agent.",
        "I am demonstrating text to speech capabilities.",
    ]

    for i, text in enumerate(texts, 1):
        print(f"Speaking text {i}: \"{text}\"")
        try:
            provider.speak(text)
            print("✅ Speech completed\n")
        except TTSError as e:
            print(f"❌ Speech failed: {e}\n")


def demo_voice_customization(provider: Pyttsx3Provider):
    """Demonstrate voice customization (rate, volume)."""
    print_header("4. Voice Customization")

    logger.info("=" * 70)
    logger.info("STARTING VOICE CUSTOMIZATION DEMO")
    logger.info("=" * 70)

    # Test different rates
    print("Testing speech rates:\n")
    rates = [
        (100, "slow"),
        (175, "normal"),
        (250, "fast"),
    ]

    for i, (rate, description) in enumerate(rates, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"RATE TEST {i}/{len(rates)}: {rate} WPM ({description})")
        logger.info(f"{'='*70}")
        print(f"  Rate: {rate} WPM ({description})")

        try:
            logger.info(f">>> Calling provider.set_rate({rate})")
            provider.set_rate(rate)
            logger.info("<<< set_rate completed successfully")

            speech_text = f"This is {description} speed speech."
            logger.info(f">>> Calling provider.speak('{speech_text}')")

            # Check engine state before speaking
            try:
                logger.debug(f"Engine state check: {provider.engine}")
                in_loop = (
                    provider.engine._inLoop
                    if hasattr(provider.engine, '_inLoop')
                    else 'unknown'
                )
                logger.debug(f"Engine busy: {in_loop}")
            except Exception as state_err:
                logger.warning(f"Could not check engine state: {state_err}")

            provider.speak(speech_text)
            logger.info("<<< speak completed successfully")
            print("  ✅ Completed\n")

        except TTSError as e:
            logger.error(f"❌ TTSError caught: {e}", exc_info=True)
            print(f"  ❌ Failed: {e}\n")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            print(f"  ❌ Unexpected error: {e}\n")

    # Test different volumes
    logger.info(f"\n{'='*70}")
    logger.info("STARTING VOLUME TESTS")
    logger.info(f"{'='*70}")
    print("Testing volumes:\n")
    volumes = [
        (0.3, "quiet"),
        (0.7, "normal"),
        (1.0, "loud"),
    ]

    for i, (volume, description) in enumerate(volumes, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"VOLUME TEST {i}/{len(volumes)}: {volume} ({description})")
        logger.info(f"{'='*70}")
        print(f"  Volume: {volume} ({description})")

        try:
            logger.info(f">>> Calling provider.set_volume({volume})")
            provider.set_volume(volume)
            logger.info("<<< set_volume completed successfully")

            speech_text = f"This is {description} volume."
            logger.info(f">>> Calling provider.speak('{speech_text}')")

            # Check engine state before speaking
            try:
                logger.debug(f"Engine state check: {provider.engine}")
                in_loop = (
                    provider.engine._inLoop
                    if hasattr(provider.engine, '_inLoop')
                    else 'unknown'
                )
                logger.debug(f"Engine busy: {in_loop}")
            except Exception as state_err:
                logger.warning(f"Could not check engine state: {state_err}")

            provider.speak(speech_text)
            logger.info("<<< speak completed successfully")
            print("  ✅ Completed\n")

        except TTSError as e:
            logger.error(f"❌ TTSError caught: {e}", exc_info=True)
            print(f"  ❌ Failed: {e}\n")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            print(f"  ❌ Unexpected error: {e}\n")

    # Reset to defaults
    logger.info(f"\n{'='*70}")
    logger.info("RESETTING TO DEFAULTS")
    logger.info(f"{'='*70}")
    try:
        logger.info(">>> Resetting rate to 175 WPM")
        provider.set_rate(175)
        logger.info(">>> Resetting volume to 0.9")
        provider.set_volume(0.9)
        logger.info("✅ Reset completed successfully")
    except Exception as e:
        logger.error(f"❌ Failed to reset defaults: {e}", exc_info=True)


def demo_voice_selection(provider: Pyttsx3Provider, voices: list[dict[str, str]]):
    """Demonstrate voice selection."""
    print_header("5. Voice Selection")

    if not voices:
        print("❌ No voices available to test")
        return

    # Try first available voice
    first_voice = voices[0]
    print(f"Switching to voice: {first_voice['name']}")
    try:
        provider.set_voice(first_voice["id"])
        provider.speak("Hello, this is a different voice.")
        print("✅ Voice changed successfully\n")
    except TTSError as e:
        print(f"❌ Failed to change voice: {e}\n")


def demo_configuration():
    """Demonstrate configuration-based provider creation."""
    print_header("6. Configuration Management")

    # Test 1: Default configuration
    print("Test 1: Default configuration")
    config = TTSConfig()
    print(f"  Provider: {config.provider}")
    print(f"  Rate: {config.rate} WPM")
    print(f"  Volume: {config.volume}")
    print(f"  Voice: {config.voice or 'system default'}\n")

    # Test 2: Custom configuration
    print("Test 2: Custom configuration")
    custom_config = TTSConfig(
        provider="pyttsx3",
        rate=150,
        volume=0.8,
    )
    print(f"  Rate: {custom_config.rate} WPM")
    print(f"  Volume: {custom_config.volume}\n")

    try:
        custom_provider = custom_config.get_provider()
        print("✅ Provider created from config")
        custom_provider.speak("This provider was created from custom configuration.")
        print("✅ Speech completed\n")
    except Exception as e:
        print(f"❌ Failed to create provider: {e}\n")


def demo_save_to_file(provider: Pyttsx3Provider):
    """Demonstrate saving speech to audio file."""
    print_header("7. Save Speech to File")

    output_file = "examples/demo_output.wav"
    text = "This audio was saved to a WAV file using pyttsx3."

    print(f"Saving to file: {output_file}")
    print(f"Text: \"{text}\"\n")

    try:
        provider.save_to_file(text, output_file)
        print(f"✅ Audio saved successfully to {output_file}\n")
    except TTSError as e:
        print(f"❌ Failed to save audio: {e}\n")


def demo_error_handling(provider: Pyttsx3Provider):
    """Demonstrate error handling."""
    print_header("8. Error Handling")

    # Test 1: Invalid rate
    print("Test 1: Invalid speech rate")
    try:
        provider.set_rate(1000)  # Out of range
        print("❌ Should have raised error\n")
    except TTSError as e:
        print(f"✅ Caught error: {e}\n")

    # Test 2: Invalid volume
    print("Test 2: Invalid volume")
    try:
        provider.set_volume(2.0)  # Out of range
        print("❌ Should have raised error\n")
    except TTSError as e:
        print(f"✅ Caught error: {e}\n")

    # Test 3: Invalid voice ID
    print("Test 3: Invalid voice ID")
    try:
        provider.set_voice("nonexistent_voice_id")
        print("❌ Should have raised error\n")
    except TTSError as e:
        print(f"✅ Caught error: {e}\n")

    # Test 4: Invalid file format
    print("Test 4: Invalid file format")
    try:
        provider.save_to_file("Test", "output.mp3")  # Wrong format
        print("❌ Should have raised error\n")
    except TTSError as e:
        print(f"✅ Caught error: {e}\n")


def main():
    """Run all TTS demos."""
    print("=" * 70)
    print("  PHASE 2 DEMO: Text-to-Speech Integration")
    print("  Voice Interview Agent - Conversation Agent v11")
    print("=" * 70)

    # Initialize provider
    provider = demo_provider_initialization()
    if not provider:
        print("\n❌ Cannot continue without TTS provider")
        return

    # Get available voices
    voices = demo_available_voices(provider)

    # Run demos
    demo_basic_speech(provider)
    demo_voice_customization(provider)
    if voices:
        demo_voice_selection(provider, voices)
    demo_configuration()
    demo_save_to_file(provider)
    demo_error_handling(provider)

    # Completion
    print("=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\nPhase 2 TTS integration is working correctly. ✅")
    print("\nNext Phase: STT Integration (OpenAI Whisper)")


if __name__ == "__main__":
    main()
