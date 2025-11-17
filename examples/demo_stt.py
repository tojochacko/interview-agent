"""Demo script for Speech-to-Text (STT) providers.

This script demonstrates:
1. STT provider initialization
2. Available models listing
3. Transcribing audio file
4. Recording from microphone
5. Transcribing recorded audio
6. Configuration management
7. Audio device listing
8. Error handling

Usage:
    python examples/demo_stt.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Add src to path for running directly
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def demo_basic_transcription():
    """Demo 1: Basic transcription from file."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Transcription")
    print("=" * 70)

    from conversation_agent.providers.stt import STTError, WhisperProvider

    try:
        print("\n1. Initializing Whisper provider (base model)...")
        provider = WhisperProvider(model_size="base", language="en", device="cpu")
        print(f"   ✓ Model loaded: {provider.get_model_size()}")
        print(f"   ✓ Language: {provider.get_language()}")

        # Note: This would require an actual audio file
        print("\n2. To transcribe an audio file:")
        print('   result = provider.transcribe("audio.mp3")')
        print('   print(result["text"])')

        print("\n   ✓ Whisper provider ready for transcription")

    except STTError as e:
        print(f"   ✗ Error: {e}")
        print("\n   Note: Whisper will download models on first use (~74MB for base)")
    except ImportError as e:
        print(f"   ✗ Import Error: {e}")
        print("\n   Install dependencies: pip install openai-whisper pyaudio numpy")


def demo_available_models():
    """Demo 2: List available models."""
    print("\n" + "=" * 70)
    print("DEMO 2: Available Models")
    print("=" * 70)

    from conversation_agent.providers.stt import WhisperProvider

    try:
        print("\n1. Getting available Whisper models...")
        provider = WhisperProvider(model_size="base")
        models = provider.get_available_models()

        print(f"\n   Available models ({len(models)}):")
        model_info = {
            "tiny": "39MB - Fast, good accuracy",
            "base": "74MB - Balanced (recommended)",
            "small": "244MB - Better accuracy",
            "medium": "769MB - High accuracy",
            "large": "1.5GB - Highest accuracy",
            "turbo": "809MB - Fast, high accuracy",
        }

        for model in models:
            info = model_info.get(model, "")
            print(f"   • {model:8s} - {info}")

    except Exception as e:
        print(f"   ✗ Error: {e}")


def demo_language_support():
    """Demo 3: Language support."""
    print("\n" + "=" * 70)
    print("DEMO 3: Language Support")
    print("=" * 70)

    from conversation_agent.providers.stt import WhisperProvider

    try:
        print("\n1. Initializing Whisper with English...")
        provider = WhisperProvider(model_size="base", language="en")
        print(f"   ✓ Current language: {provider.get_language()}")

        print("\n2. Changing to Spanish...")
        provider.set_language("es")
        print(f"   ✓ New language: {provider.get_language()}")

        print("\n3. Setting to auto-detect (empty string)...")
        provider.set_language("")
        print(f"   ✓ Language setting: '{provider.get_language()}' (auto-detect)")

        print("\n   Whisper supports 99 languages including:")
        print("   • English (en), Spanish (es), French (fr)")
        print("   • German (de), Italian (it), Portuguese (pt)")
        print("   • Japanese (ja), Korean (ko), Chinese (zh)")
        print("   • And many more...")

    except Exception as e:
        print(f"   ✗ Error: {e}")


def demo_audio_devices():
    """Demo 4: List audio devices."""
    print("\n" + "=" * 70)
    print("DEMO 4: Audio Devices")
    print("=" * 70)

    from conversation_agent.core.audio import AudioError, AudioManager

    try:
        print("\n1. Initializing audio manager...")
        audio_mgr = AudioManager(sample_rate=16000)
        print("   ✓ Audio manager initialized")

        print("\n2. Listing available input devices...")
        devices = audio_mgr.list_devices()

        if devices:
            print(f"\n   Found {len(devices)} input device(s):")
            for device in devices:
                print(f"\n   Device {device['index']}:")
                print(f"   • Name: {device['name']}")
                print(f"   • Channels: {device['channels']}")
                print(f"   • Sample Rate: {device['sample_rate']} Hz")
        else:
            print("   ✗ No input devices found")

    except AudioError as e:
        print(f"   ✗ Audio Error: {e}")
    except ImportError as e:
        print(f"   ✗ Import Error: {e}")
        print("\n   Install PyAudio:")
        print("   • macOS: brew install portaudio && pip install pyaudio")
        print("   • Linux: sudo apt-get install portaudio19-dev && pip install pyaudio")
        print("   • Windows: pip install pyaudio")


def demo_recording():
    """Demo 5: Record audio (simulated)."""
    print("\n" + "=" * 70)
    print("DEMO 5: Audio Recording")
    print("=" * 70)

    from conversation_agent.core.audio import AudioError, AudioManager

    try:
        print("\n1. Initializing audio manager...")
        audio_mgr = AudioManager(sample_rate=16000, chunk_size=1024)
        print("   ✓ Audio manager initialized")

        print("\n2. Recording methods available:")
        print("   • record(duration=5.0) - Fixed duration recording")
        print("   • record_until_silence() - Auto-stop on silence")

        print("\n3. Example usage:")
        print("   # Record for 5 seconds")
        print("   audio_data = audio_mgr.record(duration=5.0)")
        print("")
        print("   # Record until 2 seconds of silence")
        print("   audio_data = audio_mgr.record_until_silence(")
        print("       silence_threshold=0.01,")
        print("       silence_duration=2.0")
        print("   )")
        print("")
        print("   # Save to file")
        print('   audio_mgr.save_to_wav(audio_data, "recording.wav")')

        print("\n   Note: Actual recording requires a microphone")

    except AudioError as e:
        print(f"   ✗ Audio Error: {e}")
    except ImportError:
        print("   ✗ PyAudio not installed")


def demo_configuration():
    """Demo 6: Configuration management."""
    print("\n" + "=" * 70)
    print("DEMO 6: Configuration Management")
    print("=" * 70)

    from conversation_agent.config import STTConfig

    try:
        print("\n1. Creating default configuration...")
        config = STTConfig()
        print(f"   • Provider: {config.provider}")
        print(f"   • Model Size: {config.model_size}")
        print(f"   • Language: {config.language}")
        print(f"   • Device: {config.device}")
        print(f"   • Sample Rate: {config.sample_rate} Hz")
        print(f"   • Silence Threshold: {config.silence_threshold}")
        print(f"   • Silence Duration: {config.silence_duration}s")

        print("\n2. Creating custom configuration...")
        custom_config = STTConfig(
            model_size="small", language="es", device="cpu", sample_rate=22050
        )
        print(f"   • Model Size: {custom_config.model_size}")
        print(f"   • Language: {custom_config.language}")
        print(f"   • Sample Rate: {custom_config.sample_rate} Hz")

        print("\n3. Environment variables supported:")
        print("   export STT_MODEL_SIZE=small")
        print("   export STT_LANGUAGE=es")
        print("   export STT_DEVICE=cuda")
        print("   export STT_SAMPLE_RATE=16000")

        print("\n4. Getting configured provider:")
        print("   provider = config.get_provider()")
        print("   # Returns configured WhisperProvider instance")

    except Exception as e:
        print(f"   ✗ Error: {e}")


def demo_error_handling():
    """Demo 7: Error handling."""
    print("\n" + "=" * 70)
    print("DEMO 7: Error Handling")
    print("=" * 70)

    from conversation_agent.providers.stt import STTError, WhisperProvider

    print("\n1. Invalid model size...")
    try:
        provider = WhisperProvider(model_size="invalid")
    except STTError as e:
        print(f"   ✓ Caught error: {e}")

    print("\n2. Non-existent file...")
    try:
        provider = WhisperProvider(model_size="base")
        provider.transcribe("nonexistent.wav")
    except FileNotFoundError as e:
        print(f"   ✓ Caught error: Audio file not found")
    except Exception as e:
        print(f"   ✓ Expected error (no model loaded yet)")

    print("\n3. Invalid language type...")
    try:
        provider = WhisperProvider(model_size="base")
        provider.set_language(123)  # Not a string
    except STTError as e:
        print(f"   ✓ Caught error: {e}")
    except Exception as e:
        print(f"   ✓ Expected error")

    print("\n   All errors handled gracefully!")


def demo_full_workflow():
    """Demo 8: Full workflow (simulated)."""
    print("\n" + "=" * 70)
    print("DEMO 8: Full Workflow (Simulated)")
    print("=" * 70)

    print("\n1. Initialize components...")
    print("   from conversation_agent.config import STTConfig")
    print("   from conversation_agent.core.audio import AudioManager")
    print("")
    print("   config = STTConfig(model_size='base', language='en')")
    print("   provider = config.get_provider()")
    print("   audio_mgr = AudioManager(sample_rate=16000)")

    print("\n2. List devices and select...")
    print("   devices = audio_mgr.list_devices()")
    print("   device_index = devices[0]['index']")

    print("\n3. Record audio...")
    print("   print('Recording... speak now!')")
    print("   audio_data = audio_mgr.record_until_silence(")
    print("       silence_threshold=0.01,")
    print("       silence_duration=2.0,")
    print("       device_index=device_index")
    print("   )")

    print("\n4. Save recording...")
    print("   audio_mgr.save_to_wav(audio_data, 'recording.wav')")

    print("\n5. Transcribe...")
    print("   result = provider.transcribe('recording.wav')")
    print("   print(f'Transcription: {result[\"text\"]}')")
    print("   print(f'Language: {result[\"language\"]}')")

    print("\n6. Process segments...")
    print("   for segment in result['segments']:")
    print("       print(f'{segment[\"start\"]:.1f}s: {segment[\"text\"]}')")

    print("\n   ✓ Full workflow complete!")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print(" Speech-to-Text (STT) Provider Demo")
    print(" Phase 3: OpenAI Whisper Integration")
    print("=" * 70)

    demos = [
        demo_basic_transcription,
        demo_available_models,
        demo_language_support,
        demo_audio_devices,
        demo_recording,
        demo_configuration,
        demo_error_handling,
        demo_full_workflow,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n✗ Demo failed with unexpected error: {e}")

    print("\n" + "=" * 70)
    print(" Demo Complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Install dependencies: pip install -e '.[dev]'")
    print("2. Install system dependencies (macOS): brew install portaudio")
    print("3. Run tests: python -m pytest tests/test_stt_providers.py -v")
    print("4. Try transcribing: create an audio file and use provider.transcribe()")
    print("\nNote: First run will download Whisper models (~74MB for base)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
