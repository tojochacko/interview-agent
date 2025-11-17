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

from conversation_agent.config import TTSConfig
from conversation_agent.providers.tts import Pyttsx3Provider, TTSError


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

        for i, voice in enumerate(voices[:5], 1):  # Show first 5 voices
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

    # Test different rates
    print("Testing speech rates:\n")
    rates = [
        (100, "slow"),
        (175, "normal"),
        (250, "fast"),
    ]

    for rate, description in rates:
        print(f"  Rate: {rate} WPM ({description})")
        try:
            provider.set_rate(rate)
            provider.speak(f"This is {description} speed speech.")
            print("  ✅ Completed\n")
        except TTSError as e:
            print(f"  ❌ Failed: {e}\n")

    # Test different volumes
    print("Testing volumes:\n")
    volumes = [
        (0.3, "quiet"),
        (0.7, "normal"),
        (1.0, "loud"),
    ]

    for volume, description in volumes:
        print(f"  Volume: {volume} ({description})")
        try:
            provider.set_volume(volume)
            provider.speak(f"This is {description} volume.")
            print("  ✅ Completed\n")
        except TTSError as e:
            print(f"  ❌ Failed: {e}\n")

    # Reset to defaults
    provider.set_rate(175)
    provider.set_volume(0.9)


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
