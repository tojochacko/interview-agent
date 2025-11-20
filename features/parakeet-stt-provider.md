# Feature Plan: Nvidia Parakeet STT Provider

**Status**: 📋 Planning
**Date**: 2025-11-20
**Estimated Complexity**: Medium
**Dependencies**: Phase 3 (STT Implementation) ✅

## Overview

Implement Nvidia Parakeet-TDT as an alternative STT provider to OpenAI Whisper. Parakeet offers faster transcription with comparable or better accuracy, making it an excellent option for production deployments, especially with Nvidia GPU hardware.

**⚠️ Platform Limitation**: Parakeet requires NeMo toolkit which depends on Triton. **Linux and Windows only** - not available on macOS.

### Key Benefits

- **50x faster** than Whisper on GPU-accelerated hardware
- **6.05% WER** (Word Error Rate) - industry-leading accuracy
- **Multilingual support**: 25 European languages with auto-detection
- **Automatic punctuation and capitalization**
- **Word-level and segment-level timestamps**
- **Open source**: CC BY 4.0 license
- **Production-ready**: Built on Nvidia NeMo framework

## Objectives

- ✅ Create `ParakeetProvider` class implementing `STTProvider` interface
- ✅ Add Parakeet model configuration to `STTConfig`
- ✅ Implement model loading with NeMo toolkit
- ✅ Support both file and audio data transcription
- ✅ Enable timestamp extraction (word and segment level)
- ✅ Configure provider selection in interview orchestrator
- ✅ Write comprehensive tests (target: >80% coverage)
- ✅ Create demo script showcasing Parakeet capabilities
- ✅ Document installation, usage, and performance comparisons

## Architecture

### File Structure

```
src/conversation_agent/
├── providers/
│   └── stt/
│       ├── __init__.py              # Export ParakeetProvider
│       ├── base.py                  # STTProvider interface (existing)
│       ├── whisper_provider.py      # Whisper implementation (existing)
│       └── parakeet_provider.py     # NEW: Parakeet implementation
│
├── config/
│   └── stt_config.py                # MODIFY: Add Parakeet config options
│
└── core/
    └── interview.py                 # MODIFY: Support Parakeet provider

tests/
├── test_stt_providers.py            # MODIFY: Add Parakeet tests
└── test_parakeet_provider.py        # NEW: Dedicated Parakeet tests

examples/
└── demo_parakeet.py                 # NEW: Parakeet demo script

docs/
└── parakeet-stt-guide.md            # NEW: Parakeet usage guide
```

### Design Patterns

Following existing STT architecture:

1. **Provider Pattern**: `ParakeetProvider` implements `STTProvider` abstract base class
2. **Configuration-Driven**: Use Pydantic Settings for configuration
3. **Dependency Inversion**: High-level code depends on `STTProvider` abstraction
4. **Lazy Loading**: Load model on first use (not at initialization)
5. **Error Handling**: Wrap exceptions in `STTError` with helpful messages

## Implementation Details

### Phase 1: ParakeetProvider Class

**File**: `src/conversation_agent/providers/stt/parakeet_provider.py`

**Class Structure**:

```python
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

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
        "nvidia/parakeet-tdt-0.6b-v2",   # English-only, 600M params
        "nvidia/parakeet-tdt-0.6b-v3",   # 25 European languages, 600M params
        "nvidia/parakeet-rnnt-1.1b",     # English, 1.1B params, higher accuracy
    ]

    # Supported languages (v3 model)
    SUPPORTED_LANGUAGES = [
        "en", "es", "fr", "de", "it", "pt", "pl", "nl", "cs", "ro",
        "hu", "el", "bg", "hr", "da", "fi", "sk", "sl", "sv", "et",
        "lt", "lv", "mt", "ga", "cy"
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
            import nemo.collections.asr as nemo_asr

            logger.info(f"Loading Parakeet model: {self.model_name}")
            self._model = nemo_asr.models.ASRModel.from_pretrained(
                model_name=self.model_name
            )

            # Configure local attention for long audio if requested
            if self.use_local_attention:
                self._model.change_attention_model(
                    self_attention_model="rel_pos_local_attn",
                    att_context_size=[256, 256]
                )
                logger.info("Configured local attention for long-form audio")

            logger.info(f"Successfully loaded {self.model_name}")

        except ImportError as e:
            raise STTError(
                "NeMo toolkit not installed. Install with: "
                "pip install nemo_toolkit['asr']"
            ) from e
        except Exception as e:
            raise STTError(
                f"Failed to load Parakeet model '{self.model_name}': {e}"
            ) from e

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
            output = self._model.transcribe(
                [audio_path],
                timestamps=self.enable_timestamps
            )

            # Extract transcription text
            text = output[0].text if hasattr(output[0], 'text') else output[0]

            # Build segments from timestamps if available
            segments = []
            if self.enable_timestamps and hasattr(output[0], 'timestamp'):
                segment_timestamps = output[0].timestamp.get('segment', [])
                for seg in segment_timestamps:
                    segments.append({
                        "start": seg.get("start", 0.0),
                        "end": seg.get("end", 0.0),
                        "text": seg.get("text", "")
                    })
            else:
                # Fallback: single segment
                segments = [{
                    "start": 0.0,
                    "end": 0.0,
                    "text": text
                }]

            return {
                "text": text,
                "language": self.language if self.language else "auto",
                "segments": segments
            }

        except Exception as e:
            raise STTError(
                f"Transcription failed for '{audio_path}': {e}"
            ) from e

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
            import tempfile
            import wave

            # Parakeet NeMo models expect file input, so write to temp file
            with tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False
            ) as tmp_file:
                tmp_path = tmp_file.name

                # Write audio data to WAV file
                with wave.open(tmp_path, 'wb') as wav_file:
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
            raise STTError(
                f"Transcription failed for audio data: {e}"
            ) from e

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
```

**Lines of Code**: ~250 lines

**Key Implementation Notes**:

1. **Model Loading**: Uses NeMo's `ASRModel.from_pretrained()` for HuggingFace integration
2. **Timestamps**: Supports both word-level and segment-level timestamps
3. **Long Audio**: Optional local attention mode for audio >24 minutes
4. **Audio Format**: Prefers .wav/.flac at 16kHz mono (same as Whisper)
5. **Temp Files**: Converts raw bytes to temp WAV file (NeMo expects file paths)

### Phase 2: Configuration Updates

**File**: `src/conversation_agent/config/stt_config.py`

**Modifications**:

```python
# Add to STTConfig class:

provider: str = Field(
    default="whisper",
    description="STT provider to use (whisper, parakeet)",  # UPDATED
)

# Add new Parakeet-specific fields:
parakeet_model: str = Field(
    default="nvidia/parakeet-tdt-0.6b-v3",
    description="Parakeet model name from HuggingFace",
)

parakeet_enable_timestamps: bool = Field(
    default=True,
    description="Enable word/segment timestamps for Parakeet",
)

parakeet_local_attention: bool = Field(
    default=False,
    description="Use local attention for long audio (Parakeet)",
)

# Update get_provider() method:
def get_provider(self):
    """Get configured STT provider instance."""
    from conversation_agent.providers.stt import (
        ParakeetProvider,  # NEW
        STTError,
        WhisperProvider,
    )

    provider_name = self.provider.lower()

    if provider_name == "whisper":
        try:
            return WhisperProvider(
                model_size=self.model_size,
                language=self.language,
                device=self.device,
            )
        except STTError as e:
            raise ValueError(f"Failed to initialize Whisper: {e}") from e

    elif provider_name == "parakeet":  # NEW
        try:
            return ParakeetProvider(
                model_name=self.parakeet_model,
                language=self.language,
                enable_timestamps=self.parakeet_enable_timestamps,
                use_local_attention=self.parakeet_local_attention,
            )
        except STTError as e:
            raise ValueError(f"Failed to initialize Parakeet: {e}") from e

    else:
        raise ValueError(
            f"Unknown STT provider: {self.provider}. "
            "Supported: whisper, parakeet"
        )
```

**Environment Variables** (new):

```bash
# Parakeet-specific config
export STT_PROVIDER=parakeet
export STT_PARAKEET_MODEL=nvidia/parakeet-tdt-0.6b-v3
export STT_PARAKEET_ENABLE_TIMESTAMPS=true
export STT_PARAKEET_LOCAL_ATTENTION=false
```

**Lines Modified**: ~40 lines

### Phase 3: Provider Exports

**File**: `src/conversation_agent/providers/stt/__init__.py`

**Modifications**:

```python
"""Speech-to-Text providers."""

from conversation_agent.providers.stt.base import STTError, STTProvider
from conversation_agent.providers.stt.parakeet_provider import ParakeetProvider  # NEW
from conversation_agent.providers.stt.whisper_provider import WhisperProvider

__all__ = [
    "STTError",
    "STTProvider",
    "ParakeetProvider",  # NEW
    "WhisperProvider",
]
```

**Lines Modified**: ~3 lines

### Phase 4: Testing

**File**: `tests/test_parakeet_provider.py` (NEW)

**Test Coverage**:

```python
"""Tests for Parakeet STT provider."""

import pytest
from unittest.mock import MagicMock, Mock, patch
import numpy as np

from conversation_agent.providers.stt import ParakeetProvider, STTError


class TestParakeetProvider:
    """Test Parakeet provider implementation."""

    def test_initialization_valid_model(self):
        """Test provider initialization with valid model."""
        # Mock NeMo to avoid actual model download
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider(
                model_name="nvidia/parakeet-tdt-0.6b-v3",
                language="en"
            )
            assert provider.model_name == "nvidia/parakeet-tdt-0.6b-v3"
            assert provider.language == "en"

    def test_initialization_invalid_model_warning(self):
        """Test warning for untested model."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            with pytest.warns(UserWarning):
                provider = ParakeetProvider(model_name="custom/model")

    def test_load_model_missing_nemo(self):
        """Test error when NeMo not installed."""
        with patch("builtins.__import__", side_effect=ImportError):
            with pytest.raises(STTError, match="NeMo toolkit not installed"):
                ParakeetProvider()

    def test_transcribe_file_success(self, tmp_path):
        """Test transcribing audio file."""
        # Create dummy audio file
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"dummy audio data")

        # Mock NeMo model
        mock_model = MagicMock()
        mock_output = Mock()
        mock_output.text = "Hello world."
        mock_output.timestamp = {
            "segment": [
                {"start": 0.0, "end": 1.5, "text": "Hello world."}
            ]
        }
        mock_model.transcribe.return_value = [mock_output]

        with patch("nemo.collections.asr.models.ASRModel.from_pretrained",
                   return_value=mock_model):
            provider = ParakeetProvider()
            result = provider.transcribe(str(audio_file))

        assert result["text"] == "Hello world."
        assert result["language"] == "en"
        assert len(result["segments"]) == 1
        assert result["segments"][0]["text"] == "Hello world."

    def test_transcribe_file_not_found(self):
        """Test error when audio file doesn't exist."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider()
            with pytest.raises(FileNotFoundError):
                provider.transcribe("/nonexistent/audio.wav")

    def test_transcribe_audio_data(self):
        """Test transcribing raw audio data."""
        # Mock NeMo and temp file creation
        mock_model = MagicMock()
        mock_output = Mock()
        mock_output.text = "Test transcription."
        mock_model.transcribe.return_value = [mock_output]

        with patch("nemo.collections.asr.models.ASRModel.from_pretrained",
                   return_value=mock_model):
            provider = ParakeetProvider()

            # Create dummy PCM audio data
            audio_data = np.random.randint(
                -32768, 32767, size=16000, dtype=np.int16
            ).tobytes()

            result = provider.transcribe_audio_data(audio_data, sample_rate=16000)

        assert "text" in result
        assert result["text"] == "Test transcription."

    def test_get_available_models(self):
        """Test listing available models."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider()
            models = provider.get_available_models()

        assert "nvidia/parakeet-tdt-0.6b-v3" in models
        assert "nvidia/parakeet-rnnt-1.1b" in models

    def test_set_language_valid(self):
        """Test setting valid language."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider()
            provider.set_language("es")
            assert provider.get_language() == "es"

    def test_set_language_invalid(self):
        """Test error for invalid language."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider()
            with pytest.raises(STTError, match="not supported"):
                provider.set_language("invalid")

    def test_get_model_size(self):
        """Test getting model name."""
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
            provider = ParakeetProvider(
                model_name="nvidia/parakeet-rnnt-1.1b"
            )
            assert provider.get_model_size() == "nvidia/parakeet-rnnt-1.1b"

    def test_local_attention_mode(self):
        """Test local attention configuration for long audio."""
        mock_model = MagicMock()
        with patch("nemo.collections.asr.models.ASRModel.from_pretrained",
                   return_value=mock_model):
            provider = ParakeetProvider(use_local_attention=True)

        # Verify change_attention_model was called
        mock_model.change_attention_model.assert_called_once_with(
            self_attention_model="rel_pos_local_attn",
            att_context_size=[256, 256]
        )

    def test_timestamps_enabled(self, tmp_path):
        """Test timestamp extraction when enabled."""
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"dummy")

        mock_model = MagicMock()
        mock_output = Mock()
        mock_output.text = "Test."
        mock_output.timestamp = {
            "word": [
                {"start": 0.0, "end": 0.5, "text": "Test."}
            ],
            "segment": [
                {"start": 0.0, "end": 0.5, "text": "Test."}
            ]
        }
        mock_model.transcribe.return_value = [mock_output]

        with patch("nemo.collections.asr.models.ASRModel.from_pretrained",
                   return_value=mock_model):
            provider = ParakeetProvider(enable_timestamps=True)
            result = provider.transcribe(str(audio_file))

        # Verify transcribe called with timestamps=True
        call_args = mock_model.transcribe.call_args
        assert call_args[1]["timestamps"] is True

        # Verify segments extracted
        assert len(result["segments"]) > 0
```

**Test Count**: 13 new tests
**Lines of Code**: ~180 lines

**Also Modify**: `tests/test_stt_providers.py`

```python
# Add to TestSTTConfig class:

def test_get_provider_parakeet(self):
    """Test getting Parakeet provider."""
    with patch("nemo.collections.asr.models.ASRModel.from_pretrained"):
        config = STTConfig(provider="parakeet")
        provider = config.get_provider()
        assert isinstance(provider, ParakeetProvider)

def test_parakeet_config_env_vars(self, monkeypatch):
    """Test Parakeet config from environment variables."""
    monkeypatch.setenv("STT_PROVIDER", "parakeet")
    monkeypatch.setenv("STT_PARAKEET_MODEL", "nvidia/parakeet-rnnt-1.1b")

    config = STTConfig()
    assert config.provider == "parakeet"
    assert config.parakeet_model == "nvidia/parakeet-rnnt-1.1b"
```

**Additional Tests**: 2
**Total New Tests**: 15

### Phase 5: Demo Script

**File**: `examples/demo_parakeet.py` (NEW)

**Purpose**: Demonstrate Parakeet capabilities and usage patterns.

**Content Outline**:

```python
"""Demo script for Parakeet STT provider.

Shows:
- Model loading and initialization
- File transcription with timestamps
- Audio data transcription
- Multi-language support
- Performance comparison with Whisper
- Long-form audio handling
"""

import logging
import time
from pathlib import Path

from conversation_agent.providers.stt import ParakeetProvider, STTError
from conversation_agent.config import STTConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_basic_usage():
    """Demonstrate basic Parakeet usage."""
    print("\n" + "="*60)
    print("Demo 1: Basic Parakeet Usage")
    print("="*60)

    try:
        # Initialize provider
        provider = ParakeetProvider(
            model_name="nvidia/parakeet-tdt-0.6b-v3",
            language="en",
            enable_timestamps=True
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
    print("\n" + "="*60)
    print("Demo 2: Audio File Transcription")
    print("="*60)

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
        for i, seg in enumerate(result['segments'][:3], 1):
            print(f"    {i}. [{seg['start']:.2f}s - {seg['end']:.2f}s] "
                  f"{seg['text'][:50]}...")

    except STTError as e:
        print(f"✗ Error: {e}")


def demo_multilingual():
    """Demonstrate multilingual support."""
    print("\n" + "="*60)
    print("Demo 3: Multilingual Support")
    print("="*60)

    try:
        provider = ParakeetProvider(
            model_name="nvidia/parakeet-tdt-0.6b-v3"  # Multilingual model
        )

        # Show supported languages
        print("\nSupported languages (25):")
        languages = provider.SUPPORTED_LANGUAGES
        for i in range(0, len(languages), 5):
            print("  " + ", ".join(languages[i:i+5]))

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
    print("\n" + "="*60)
    print("Demo 4: Configuration-Based Usage")
    print("="*60)

    try:
        # Create config with Parakeet
        config = STTConfig(
            provider="parakeet",
            parakeet_model="nvidia/parakeet-tdt-0.6b-v3",
            language="en",
            parakeet_enable_timestamps=True
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
    print("\n" + "="*60)
    print("Demo 5: Long-Form Audio (Local Attention)")
    print("="*60)

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


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Nvidia Parakeet STT Provider Demo")
    print("="*60)

    # Run demos
    demo_basic_usage()
    demo_multilingual()
    demo_config_usage()
    demo_long_form_audio()

    # Transcription demo (if audio file provided)
    import sys
    if len(sys.argv) > 1:
        demo_transcription(sys.argv[1])
    else:
        print("\n" + "="*60)
        print("To test transcription, run:")
        print("  python examples/demo_parakeet.py <audio_file.wav>")
        print("="*60)
```

**Lines of Code**: ~200 lines

### Phase 6: Documentation

**File**: `docs/parakeet-stt-guide.md` (NEW)

**Content Outline**:

1. **Overview**: What is Parakeet, why use it
2. **Installation**: NeMo toolkit, dependencies, system requirements
3. **Quick Start**: Basic usage examples
4. **Configuration**: Environment variables, STTConfig options
5. **Models**: Comparison of v2, v3, RNNT models
6. **Features**: Timestamps, multilingual, long-form audio
7. **Performance**: Benchmarks vs Whisper (speed, accuracy, memory)
8. **Troubleshooting**: Common issues and solutions
9. **API Reference**: Complete method documentation

**Lines**: ~400 lines

## Dependencies

### New Python Packages

Add to `pyproject.toml`:

```toml
dependencies = [
    # ... existing ...
    "nemo_toolkit[asr]>=1.23.0",  # Nvidia Parakeet (optional)
]
```

**Note**: NeMo is a large package (~500MB). Consider making it optional:

```toml
[project.optional-dependencies]
parakeet = [
    "nemo_toolkit[asr]>=1.23.0",
]
```

**Installation**:

```bash
# Standard (Whisper only)
pip install -e ".[dev]"

# With Parakeet support
pip install -e ".[dev,parakeet]"
```

### System Requirements

- **Python**: 3.9+ (same as existing)
- **Platform**: **Linux or Windows only** (Triton not available on macOS)
- **PyTorch**: Latest version (NeMo dependency)
- **GPU** (recommended): Nvidia with CUDA support
  - Tested: A10, A100, H100, T4, V100, L4, L40
  - 2GB+ VRAM for model loading
- **CPU** (fallback): Works but slower
- **RAM**: 2GB minimum, more for longer audio

## Testing Strategy

### Unit Tests

1. **Provider Tests** (`test_parakeet_provider.py`):
   - Initialization with valid/invalid models
   - Model loading (mocked NeMo)
   - File transcription
   - Audio data transcription
   - Language support
   - Timestamps extraction
   - Error handling

2. **Config Tests** (`test_stt_providers.py`):
   - Parakeet provider selection
   - Environment variable parsing
   - Invalid provider handling

3. **Integration Tests**:
   - End-to-end transcription with real audio
   - Provider switching (Whisper ↔ Parakeet)
   - Interview orchestrator with Parakeet

### Test Fixtures

```python
@pytest.fixture
def mock_nemo_model():
    """Mock NeMo ASR model."""
    with patch("nemo.collections.asr.models.ASRModel.from_pretrained") as mock:
        mock_model = MagicMock()
        mock_model.transcribe.return_value = [...]
        mock.return_value = mock_model
        yield mock_model

@pytest.fixture
def sample_audio_wav(tmp_path):
    """Create sample WAV file for testing."""
    import wave
    audio_file = tmp_path / "test.wav"
    with wave.open(str(audio_file), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b'\x00\x00' * 16000)  # 1 second of silence
    return audio_file
```

### Coverage Target

- **Overall**: Maintain >80% coverage
- **ParakeetProvider**: Target >85% coverage
- **STTConfig**: Target >90% coverage

### Testing Without GPU

All tests use mocked NeMo to avoid requiring:
- Actual model downloads
- GPU hardware
- Long test execution times

## Performance Benchmarks

### Expected Performance (based on Nvidia's benchmarks)

| Metric | Whisper (base) | Parakeet (v3) | Improvement |
|--------|----------------|---------------|-------------|
| **Speed (GPU)** | 5-10x realtime | 50x realtime | **5-10x faster** |
| **WER** | ~8-10% | ~6.05% | **25-40% better** |
| **Model Size** | 74MB | 600MB | 8x larger |
| **Languages** | 99 | 25 (European) | Fewer |
| **Punctuation** | No | Yes | ✅ |
| **Capitalization** | No | Yes | ✅ |
| **Timestamps** | Yes | Yes | ✅ |

### Use Case Recommendations

**Use Parakeet when**:
- ✅ You have Nvidia GPU available
- ✅ Speed is critical (production, real-time)
- ✅ You need automatic punctuation/capitalization
- ✅ Working with European languages
- ✅ WER matters (high accuracy needed)

**Use Whisper when**:
- ✅ CPU-only environment
- ✅ Need non-European languages
- ✅ Smaller model size preferred
- ✅ Development/testing (faster setup)

## Migration Guide

### Switching from Whisper to Parakeet

**Option 1: Environment Variables**

```bash
# Before (Whisper)
export STT_PROVIDER=whisper
export STT_MODEL_SIZE=base

# After (Parakeet)
export STT_PROVIDER=parakeet
export STT_PARAKEET_MODEL=nvidia/parakeet-tdt-0.6b-v3
```

**Option 2: Code Changes**

```python
# Before
from conversation_agent.config import STTConfig
config = STTConfig(provider="whisper", model_size="base")

# After
config = STTConfig(
    provider="parakeet",
    parakeet_model="nvidia/parakeet-tdt-0.6b-v3"
)
```

**Option 3: CLI (when implemented)**

```bash
# Before
python -m conversation_agent.cli start --stt-provider whisper

# After
python -m conversation_agent.cli start --stt-provider parakeet
```

### Backward Compatibility

- ✅ All existing code continues to work
- ✅ Whisper remains default provider
- ✅ No breaking changes to `STTProvider` interface
- ✅ Interview orchestrator unchanged

## Implementation Phases

### Phase 1: Core Implementation (Day 1-2)
- ✅ Create `ParakeetProvider` class
- ✅ Implement all abstract methods
- ✅ Add basic error handling
- ✅ Write unit tests

### Phase 2: Configuration (Day 2)
- ✅ Update `STTConfig` class
- ✅ Add environment variable support
- ✅ Update provider factory
- ✅ Test config integration

### Phase 3: Testing (Day 3)
- ✅ Write comprehensive tests
- ✅ Create test fixtures
- ✅ Achieve >80% coverage
- ✅ Test provider switching

### Phase 4: Documentation (Day 3-4)
- ✅ Write usage guide
- ✅ Create demo script
- ✅ Document performance benchmarks
- ✅ Add troubleshooting section

### Phase 5: Integration (Day 4)
- ✅ Test with interview orchestrator
- ✅ End-to-end testing
- ✅ Performance validation
- ✅ Code review

## Risks and Mitigations

### Risk 1: Large Dependency Size

**Risk**: NeMo toolkit is ~500MB, increases install size significantly.

**Mitigation**:
- Make Parakeet optional dependency (`pip install -e ".[parakeet]"`)
- Clear documentation on installation options
- Keep Whisper as lightweight default

### Risk 2: GPU Availability

**Risk**: Parakeet is optimized for GPU, may be slow on CPU.

**Mitigation**:
- Document GPU requirements clearly
- Provide CPU performance benchmarks
- Recommend Whisper for CPU-only environments

### Risk 3: Limited Language Support

**Risk**: Only 25 European languages vs Whisper's 99.

**Mitigation**:
- Document language limitations
- Recommend Whisper for non-European languages
- Support provider switching per user needs

### Risk 4: Model Download Size

**Risk**: First use requires downloading 600MB-1.1GB model.

**Mitigation**:
- Show progress indicator during download
- Document model sizes in advance
- Cache models after first download

## Success Criteria

- ✅ `ParakeetProvider` implements all `STTProvider` methods
- ✅ Configuration supports Parakeet via env vars and code
- ✅ >80% test coverage maintained
- ✅ All tests pass (including existing Whisper tests)
- ✅ Demo script shows Parakeet features
- ✅ Documentation complete and accurate
- ✅ Interview orchestrator works with both providers
- ✅ No breaking changes to existing code

## Future Enhancements

### Short-term (Next Phase)
- Streaming transcription support
- Real-time audio processing
- Voice activity detection integration
- Custom model fine-tuning guide

### Long-term
- Additional Parakeet models (RNNT, CTC variants)
- Quantized models for faster inference
- Multi-GPU support
- Custom vocabulary support

## Related Documentation

- [Phase 3: STT Implementation](../docs/phases/phase-03-stt-implementation.md)
- [Architecture Overview](../docs/architecture/overview.md)
- [STT Provider Interface](../src/conversation_agent/providers/stt/base.py)
- [Nvidia Parakeet Blog](https://developer.nvidia.com/blog/pushing-the-boundaries-of-speech-recognition-with-nemo-parakeet-asr-models/)

## Estimated Effort

- **Development**: 3-4 days
- **Testing**: 1 day
- **Documentation**: 1 day
- **Total**: 5-6 days

## Code Statistics Estimate

- **New Files**: 3 (provider, tests, demo)
- **Modified Files**: 3 (config, __init__, existing tests)
- **New Lines**: ~1,050 lines
  - ParakeetProvider: 250 lines
  - Tests: 180 lines
  - Config updates: 40 lines
  - Demo script: 200 lines
  - Documentation: 400 lines
- **Modified Lines**: ~50 lines

---

**Plan Status**: 📋 Ready for Implementation
**Next Step**: Review plan → Get approval → Begin Phase 1 implementation
