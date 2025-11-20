"""Demo script for Parakeet STT provider.

Shows:
- Model loading and initialization
- File transcription with timestamps
- Audio data transcription
- Multi-language support
- Performance comparison with Whisper
- Long-form audio handling

Usage:
    python examples/demo_parakeet.py [audio_file.wav]
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

from conversation_agent.config import STTConfig
from conversation_agent.providers.stt import ParakeetProvider, STTError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def demo_basic_usage():
    """Demonstrate basic Parakeet usage."""
    print("\n" + "=" * 60)
    print("Demo 1: Basic Parakeet Usage")
    print("=" * 60)

    try:
        # Initialize provider
        provider = ParakeetProvider(
            model_name="nvidia/parakeet-tdt-0.6b-v3", language="en", enable_timestamps=True
        )

        print(f"✓ Loaded model: {provider.get_model_size()}")
        print(f"✓ Language: {provider.get_language()}")

        # Show available models
        models = provider.get_available_models()
        print(f"\nAvailable models ({len(models)}):")
        for model in models:
            print(f"  - {model}")

    except STTError as e:
        print(f"✗ Error: {e}")


def demo_transcription(audio_file: str):
    """Demonstrate file transcription."""
    print("\n" + "=" * 60)
    print("Demo 2: Audio File Transcription")
    print("=" * 60)

    if not Path(audio_file).exists():
        print(f"✗ Audio file not found: {audio_file}")
        return

    try:
        provider = ParakeetProvider(enable_timestamps=True)

        # Transcribe with timing
        start = time.time()
        result = provider.transcribe(audio_file)
        duration = time.time() - start

        print(f"\n✓ Transcription ({duration:.2f}s):")
        print(f"  Text: {result['text']}")
        print(f"  Language: {result['language']}")
        print(f"  Segments: {len(result['segments'])}")

        # Show segments with timestamps
        print("\n  Segment timestamps:")
        for i, seg in enumerate(result["segments"][:3], 1):
            text_preview = seg["text"][:50] + "..." if len(seg["text"]) > 50 else seg["text"]
            print(f"    {i}. [{seg['start']:.2f}s - {seg['end']:.2f}s] {text_preview}")

        if len(result["segments"]) > 3:
            print(f"    ... and {len(result['segments']) - 3} more segments")

    except STTError as e:
        print(f"✗ Error: {e}")


def demo_multilingual():
    """Demonstrate multilingual support."""
    print("\n" + "=" * 60)
    print("Demo 3: Multilingual Support")
    print("=" * 60)

    try:
        provider = ParakeetProvider(
            model_name="nvidia/parakeet-tdt-0.6b-v3"  # Multilingual model
        )

        # Show supported languages
        print("\nSupported languages (25 European languages):")
        languages = provider.SUPPORTED_LANGUAGES
        for i in range(0, len(languages), 5):
            print("  " + ", ".join(languages[i : i + 5]))

        # Test language switching
        test_languages = ["en", "es", "fr", "de"]
        print(f"\nTesting language switching:")
        for lang in test_languages:
            provider.set_language(lang)
            print(f"  ✓ {lang}: {provider.get_language()}")

    except STTError as e:
        print(f"✗ Error: {e}")


def demo_config_usage():
    """Demonstrate configuration-based usage."""
    print("\n" + "=" * 60)
    print("Demo 4: Configuration-Based Usage")
    print("=" * 60)

    try:
        # Create config with Parakeet
        config = STTConfig(
            provider="parakeet",
            parakeet_model="nvidia/parakeet-tdt-0.6b-v3",
            language="en",
            parakeet_enable_timestamps=True,
        )

        print(f"Config:")
        print(f"  Provider: {config.provider}")
        print(f"  Model: {config.parakeet_model}")
        print(f"  Language: {config.language}")
        print(f"  Timestamps: {config.parakeet_enable_timestamps}")

        # Get provider from config
        provider = config.get_provider()
        print(f"\n✓ Provider initialized: {type(provider).__name__}")

    except Exception as e:
        print(f"✗ Error: {e}")


def demo_long_form_audio():
    """Demonstrate long-form audio with local attention."""
    print("\n" + "=" * 60)
    print("Demo 5: Long-Form Audio (Local Attention)")
    print("=" * 60)

    try:
        # Configure for long audio
        provider = ParakeetProvider(
            use_local_attention=True  # Enables processing >24 min audio
        )

        print("✓ Configured local attention mode")
        print("  - Full attention: Up to 24 minutes")
        print("  - Local attention: Up to 3 hours")
        print("  - Context size: [256, 256]")

    except STTError as e:
        print(f"✗ Error: {e}")


def demo_features_comparison():
    """Show feature comparison between Whisper and Parakeet."""
    print("\n" + "=" * 60)
    print("Demo 6: Parakeet vs Whisper Features")
    print("=" * 60)

    comparison = """
    Feature Comparison:
    ┌─────────────────────────┬──────────────┬────────────────┐
    │ Feature                 │ Whisper      │ Parakeet       │
    ├─────────────────────────┼──────────────┼────────────────┤
    │ Speed (GPU)             │ 5-10x        │ 50x realtime   │
    │ Word Error Rate (WER)   │ ~8-10%       │ ~6.05%         │
    │ Model Size              │ 74MB (base)  │ 600MB (v3)     │
    │ Languages               │ 99           │ 25 (European)  │
    │ Auto Punctuation        │ No           │ Yes ✓          │
    │ Auto Capitalization     │ No           │ Yes ✓          │
    │ Timestamps              │ Yes          │ Yes ✓          │
    │ GPU Optimization        │ Good         │ Excellent      │
    └─────────────────────────┴──────────────┴────────────────┘

    Use Parakeet when:
      ✓ You have Nvidia GPU available
      ✓ Speed is critical (production, real-time)
      ✓ You need automatic punctuation/capitalization
      ✓ Working with European languages
      ✓ High accuracy is required

    Use Whisper when:
      ✓ CPU-only environment
      ✓ Need non-European languages
      ✓ Smaller model size preferred
      ✓ Development/testing (faster setup)
    """

    print(comparison)


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("Nvidia Parakeet STT Provider Demo")
    print("=" * 60)

    # Run demos
    demo_basic_usage()
    demo_multilingual()
    demo_config_usage()
    demo_long_form_audio()
    demo_features_comparison()

    # Transcription demo (if audio file provided)
    if len(sys.argv) > 1:
        demo_transcription(sys.argv[1])
    else:
        print("\n" + "=" * 60)
        print("To test transcription, run:")
        print("  python examples/demo_parakeet.py <audio_file.wav>")
        print("=" * 60)


if __name__ == "__main__":
    main()
