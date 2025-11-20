# Piper TTS Migration Plan

**Feature:** Migrate from pyttsx3 to Piper TTS provider
**Status:** Planning Phase
**Created:** 2025-11-20
**Complexity:** Medium
**Estimated Impact:** High - Significant voice quality improvement

## Executive Summary

Migrate the conversation agent from pyttsx3 (robotic, 1/10 quality) to Piper TTS (neural,
9/10 quality) while maintaining backward compatibility and following the existing provider
architecture pattern.

## Goals

1. **Primary:** Replace pyttsx3 with Piper TTS as the default provider
2. **Quality:** Achieve 9/10 voice quality (vs current 1/10)
3. **Performance:** Maintain real-time speech (RTF ~0.5)
4. **Compatibility:** Keep pyttsx3 as fallback option
5. **Architecture:** Follow existing provider pattern and design principles

## Non-Goals

- Voice cloning or custom voice training
- Multi-language support (focus on English first)
- Cloud-based TTS providers
- GPU acceleration (CPU-only for broader compatibility)

## Background

### Current State

- **Provider:** pyttsx3 (system TTS wrapper)
- **Quality:** 1/10 - robotic, mechanical
- **Issues:** Poor naturalness, limited expressiveness
- **Architecture:** Well-defined provider pattern with TTSProvider base class

### Proposed State

- **Provider:** Piper TTS (neural TTS)
- **Quality:** 9/10 - natural, conversational
- **Speed:** RTF ~0.5 (real-time capable)
- **Model:** en_US-lessac-medium (30MB, balanced quality/speed)

### Why Piper?

From research (docs/tts-alternatives-comparison.md):
- Best CPU-only neural TTS available
- Fast enough for real-time conversation
- Offline/local processing (project requirement)
- MIT license, actively maintained
- Cross-platform (macOS/Linux/Windows)

## Architecture

### Provider Pattern Compliance

Current architecture (Phase 2 completed):
```
TTSProvider (abstract base)
├── Pyttsx3Provider (current implementation)
└── PiperTTSProvider (new implementation) ← TO ADD
```

### Key Components

1. **PiperTTSProvider** - New provider implementing TTSProvider interface
2. **TTSConfig** - Extended config with Piper-specific settings
3. **Factory Method** - Update get_provider() to support Piper
4. **Tests** - Unit and integration tests for new provider

### Interface Mapping

| TTSProvider Method | Piper Implementation |
|-------------------|---------------------|
| `speak(text)` | `voice.synthesize()` + pyaudio playback |
| `set_voice(voice_id)` | Load different model file |
| `set_rate(rate)` | Not supported (model-specific) → NOP |
| `set_volume(volume)` | Adjust audio amplitude during playback |
| `get_available_voices()` | List downloaded model files |
| `stop()` | Interrupt audio stream |
| `save_to_file()` | `voice.synthesize()` + wave file write |

### Design Decisions

#### 1. Model Loading Strategy

**Decision:** Lazy initialization on first speak()
**Rationale:**
- Avoids startup delay if provider not used
- Consistent with pyttsx3 provider pattern
- Model loading is one-time cost (~100ms)

#### 2. Rate Control

**Decision:** Rate control not supported (warn user, use default model rate)
**Rationale:**
- Piper models have fixed prosody/rate
- Better to use natural model rate than attempt manipulation
- Can document model selection for different speeds if needed

#### 3. Voice Selection

**Decision:** Voice = model file path (one model = one voice)
**Rationale:**
- Piper uses separate models per voice
- `set_voice()` will require model reload
- Document as "heavy" operation in docstring

#### 4. Volume Control

**Decision:** Implement via audio amplitude scaling during playback
**Rationale:**
- Simple to implement with numpy
- Preserves audio quality
- Consistent with TTSProvider interface

## Implementation Plan

### Phase 1: Setup & Dependencies

**Goal:** Install Piper and download models

**Tasks:**

1. Update `pyproject.toml` dependencies
   ```toml
   dependencies = [
       "pyttsx3>=2.90",
       "piper-tts>=1.2.0",  # NEW
       "pyaudio>=0.2.14",   # Already used for STT
       # ... existing deps
   ]
   ```

2. Create model directory structure
   ```bash
   mkdir -p models/tts/piper
   ```

3. Download Piper models (integration test fixture + user guide)
   - en_US-lessac-medium.onnx (default, 30MB)
   - en_US-lessac-medium.onnx.json (config)
   - Document in setup instructions

4. Update .gitignore
   ```gitignore
   # TTS Models (large binary files)
   models/tts/piper/*.onnx
   models/tts/piper/*.onnx.json
   ```

**Acceptance Criteria:**
- [ ] Piper installed in venv
- [ ] Models downloaded and verified
- [ ] Directory structure created
- [ ] Dependencies documented

### Phase 2: Core Provider Implementation

**Goal:** Implement PiperTTSProvider class

**File:** `src/conversation_agent/providers/tts/piper_provider.py`

**Implementation Details:**

```python
"""Piper TTS provider implementation."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pyaudio
import wave

from conversation_agent.providers.tts.base import TTSProvider, TTSError

logger = logging.getLogger(__name__)


class PiperTTSProvider(TTSProvider):
    """Piper neural TTS provider.

    High-quality neural text-to-speech using ONNX models.
    Models are CPU-based and run efficiently without GPU.

    Note: Unlike pyttsx3, voice selection requires model reload (expensive).
    Rate control is not supported - models have fixed prosody.
    """

    def __init__(
        self,
        model_path: str,
        config_path: Optional[str] = None,  # noqa: UP045
        sample_rate: int = 22050
    ) -> None:
        """Initialize Piper TTS provider.

        Args:
            model_path: Path to ONNX model file (.onnx)
            config_path: Path to config file (.onnx.json).
                        If None, uses model_path + '.json'
            sample_rate: Audio sample rate (default: 22050 Hz)

        Raises:
            TTSError: If model files not found
        """
        # Implementation from integration guide
        # ... (see docs/research/piper-integration-guide.md lines 157-184)

    def initialize(self) -> None:
        """Load the Piper voice model (lazy initialization)."""
        # Implementation lines 186-193

    def speak(self, text: str) -> None:
        """Synthesize and play text.

        Args:
            text: Text to speak

        Raises:
            TTSError: If synthesis or playback fails
        """
        # Implementation lines 195-208

    def set_voice(self, voice_id: str) -> None:
        """Set voice by loading a different model.

        Warning: This is an expensive operation as it requires reloading
        the ONNX model from disk (~100ms).

        Args:
            voice_id: Path to .onnx model file

        Raises:
            TTSError: If model file not found or load fails
        """
        # Reload model with new path

    def set_rate(self, rate: int) -> None:
        """Rate control not supported for Piper.

        Piper models have fixed prosody. This method logs a warning
        and does nothing.

        Args:
            rate: Ignored
        """
        logger.warning(
            "Rate control not supported for Piper TTS. "
            "Models have fixed prosody. Ignoring set_rate(%d)", rate
        )

    def set_volume(self, volume: float) -> None:
        """Set playback volume.

        Args:
            volume: Volume level 0.0-1.0

        Raises:
            TTSError: If volume out of range
        """
        if not 0.0 <= volume <= 1.0:
            raise TTSError(f"Volume {volume} out of range (0.0-1.0)")

        self._volume = volume
        logger.info(f"Volume set to {volume}")

    def get_available_voices(self) -> list[dict[str, str]]:
        """Get list of available Piper models.

        Scans models/tts/piper/ for .onnx files.

        Returns:
            List of voice dictionaries with 'id', 'name', 'language' keys
        """
        # Scan models directory for .onnx files

    def stop(self) -> None:
        """Stop current speech immediately."""
        # Interrupt pyaudio stream

    def save_to_file(self, text: str, filename: str) -> None:
        """Save speech to WAV file.

        Args:
            text: Text to synthesize
            filename: Output path (.wav)

        Raises:
            TTSError: If save fails
        """
        # Implementation lines 210-230

    def _play_audio(self, audio_data: bytes) -> None:
        """Play PCM audio with volume control.

        Args:
            audio_data: Raw PCM audio bytes (16-bit mono)
        """
        # Apply volume scaling
        # Play via pyaudio
        # Implementation lines 232-251

    def shutdown(self) -> None:
        """Clean up resources."""
        # Implementation lines 253-256
```

**Key Implementation Notes:**

1. **Volume Control:** Use numpy to scale audio amplitude before playback
   ```python
   audio_array = np.frombuffer(audio_data, dtype=np.int16)
   audio_array = (audio_array * self._volume).astype(np.int16)
   scaled_audio = audio_array.tobytes()
   ```

2. **Error Handling:** Wrap all Piper API calls in try/except, raise TTSError
3. **Logging:** Use conversation_agent.utils.logging_config colored logger
4. **Python 3.9:** Use `Optional[X]` not `X | None`, add `# noqa: UP045`

**Acceptance Criteria:**
- [ ] PiperTTSProvider class implements all TTSProvider abstract methods
- [ ] Lazy model loading in initialize()
- [ ] Volume control via amplitude scaling
- [ ] Rate control logs warning (unsupported)
- [ ] Voice selection reloads model
- [ ] Proper error handling with TTSError
- [ ] Comprehensive docstrings
- [ ] Type hints throughout
- [ ] File <500 lines

### Phase 3: Configuration Integration

**Goal:** Extend TTSConfig to support Piper

**File:** `src/conversation_agent/config/tts_config.py`

**Changes:**

```python
class TTSConfig(BaseSettings):
    """Configuration for Text-to-Speech providers.

    Settings can be configured via environment variables with TTS_ prefix.

    Environment Variables:
        TTS_PROVIDER: Provider name (default: "piper")  # CHANGED
        TTS_VOICE: Voice ID (pyttsx3) or model path (piper)
        TTS_RATE: Speech rate (pyttsx3 only)
        TTS_VOLUME: Volume level 0.0-1.0
        TTS_PIPER_MODEL_PATH: Path to Piper .onnx model  # NEW
        TTS_PIPER_CONFIG_PATH: Path to Piper config (optional)  # NEW
        TTS_PIPER_SAMPLE_RATE: Sample rate (default: 22050)  # NEW
    """

    # ... existing config ...

    provider: str = Field(
        default="piper",  # CHANGED from "pyttsx3"
        description="TTS provider to use (pyttsx3, piper)",
    )

    # New Piper-specific fields
    piper_model_path: Optional[str] = Field(  # noqa: UP045
        default="models/tts/piper/en_US-lessac-medium.onnx",
        description="Path to Piper ONNX model file",
    )

    piper_config_path: Optional[str] = Field(  # noqa: UP045
        default=None,  # Auto-detected from model_path
        description="Path to Piper config JSON (auto-detected if None)",
    )

    piper_sample_rate: int = Field(
        default=22050,
        description="Piper audio sample rate in Hz",
    )

    def get_provider(self):
        """Get configured TTS provider instance.

        Returns:
            TTSProvider instance configured with current settings.

        Raises:
            ValueError: If provider name not recognized or setup fails.
        """
        from conversation_agent.providers.tts import (
            Pyttsx3Provider,
            PiperTTSProvider,  # NEW IMPORT
            TTSError
        )

        if self.provider.lower() == "pyttsx3":
            # ... existing pyttsx3 logic ...
        elif self.provider.lower() == "piper":  # NEW
            try:
                provider = PiperTTSProvider(
                    model_path=self.piper_model_path,
                    config_path=self.piper_config_path,
                    sample_rate=self.piper_sample_rate,
                )
                provider.initialize()  # Load model
                provider.set_volume(self.volume)

                # Note: rate not supported, voice requires model path
                return provider
            except TTSError as e:
                raise ValueError(f"Failed to initialize Piper provider: {e}") from e
        else:
            raise ValueError(
                f"Unknown TTS provider: {self.provider}. "
                f"Supported: pyttsx3, piper"
            )
```

**Acceptance Criteria:**
- [ ] New Piper config fields added
- [ ] Default provider changed to "piper"
- [ ] get_provider() supports both pyttsx3 and piper
- [ ] Proper error handling and messages
- [ ] Environment variable documentation updated

### Phase 4: Module Exports

**Goal:** Update package exports

**File:** `src/conversation_agent/providers/tts/__init__.py`

**Changes:**

```python
"""Text-to-Speech provider implementations."""

from __future__ import annotations

from conversation_agent.providers.tts.base import TTSError, TTSProvider
from conversation_agent.providers.tts.pyttsx3_provider import Pyttsx3Provider
from conversation_agent.providers.tts.piper_provider import PiperTTSProvider  # NEW

__all__ = [
    "TTSProvider",
    "TTSError",
    "Pyttsx3Provider",
    "PiperTTSProvider",  # NEW
]
```

**Acceptance Criteria:**
- [ ] PiperTTSProvider exported
- [ ] Import structure clean

### Phase 5: Testing

**Goal:** Achieve >80% test coverage for new provider

**File:** `tests/providers/tts/test_piper_provider.py`

**Test Cases:**

```python
"""Tests for Piper TTS provider."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from conversation_agent.providers.tts.piper_provider import PiperTTSProvider
from conversation_agent.providers.tts.base import TTSError


class TestPiperProviderInitialization:
    """Test provider initialization."""

    def test_provider_initializes_with_valid_paths(self, mock_model_files):
        """Test provider initializes with valid model files."""
        model_path, config_path = mock_model_files
        provider = PiperTTSProvider(model_path=model_path, config_path=config_path)

        assert provider.voice is None  # Lazy loading
        assert provider.sample_rate == 22050
        assert provider.model_path == Path(model_path)

    def test_missing_model_file_raises_error(self):
        """Test error when model file missing."""
        with pytest.raises(TTSError, match="Model not found"):
            PiperTTSProvider(model_path="nonexistent.onnx")

    def test_missing_config_file_raises_error(self, tmp_path):
        """Test error when config file missing."""
        model_path = tmp_path / "model.onnx"
        model_path.write_bytes(b"fake")

        with pytest.raises(TTSError, match="Config not found"):
            PiperTTSProvider(model_path=str(model_path))

    def test_auto_detect_config_path(self, tmp_path):
        """Test config path auto-detection."""
        model_path = tmp_path / "model.onnx"
        config_path = tmp_path / "model.onnx.json"
        model_path.write_bytes(b"fake")
        config_path.write_text("{}")

        provider = PiperTTSProvider(model_path=str(model_path))
        assert provider.config_path == config_path


class TestPiperProviderSpeech:
    """Test speech synthesis."""

    @patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
    @patch.object(PiperTTSProvider, "_play_audio")
    def test_speak_synthesizes_and_plays(
        self, mock_play, mock_piper_voice, piper_provider
    ):
        """Test speak() synthesizes and plays audio."""
        mock_voice = Mock()
        mock_voice.synthesize.return_value = b"audio data"
        mock_piper_voice.load.return_value = mock_voice

        piper_provider.speak("Hello world")

        mock_voice.synthesize.assert_called_once_with("Hello world")
        mock_play.assert_called_once_with(b"audio data")

    def test_speak_empty_text_does_nothing(self, piper_provider):
        """Test speak() with empty text does nothing."""
        # Should not raise, just log warning
        piper_provider.speak("")
        piper_provider.speak("   ")

    @patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
    def test_speak_lazy_initializes_model(
        self, mock_piper_voice, piper_provider
    ):
        """Test speak() initializes model on first call."""
        mock_voice = Mock()
        mock_voice.synthesize.return_value = b"audio"
        mock_piper_voice.load.return_value = mock_voice

        assert piper_provider.voice is None
        piper_provider.speak("Test")
        assert piper_provider.voice is not None


class TestPiperProviderVoiceControl:
    """Test voice and rate control."""

    def test_set_rate_logs_warning(self, piper_provider, caplog):
        """Test set_rate() logs warning (not supported)."""
        piper_provider.set_rate(150)
        assert "not supported" in caplog.text.lower()

    @patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
    def test_set_voice_reloads_model(
        self, mock_piper_voice, piper_provider, mock_model_files
    ):
        """Test set_voice() reloads model with new path."""
        new_model, _ = mock_model_files
        mock_voice = Mock()
        mock_piper_voice.load.return_value = mock_voice

        piper_provider.set_voice(new_model)

        assert mock_piper_voice.load.call_count >= 1

    def test_set_voice_invalid_path_raises_error(self, piper_provider):
        """Test set_voice() with invalid path raises error."""
        with pytest.raises(TTSError):
            piper_provider.set_voice("nonexistent.onnx")


class TestPiperProviderVolumeControl:
    """Test volume control."""

    def test_set_volume_valid(self, piper_provider):
        """Test set_volume() with valid volume."""
        piper_provider.set_volume(0.5)
        assert piper_provider._volume == 0.5

    def test_set_volume_out_of_range_raises_error(self, piper_provider):
        """Test set_volume() out of range raises error."""
        with pytest.raises(TTSError, match="out of range"):
            piper_provider.set_volume(1.5)

        with pytest.raises(TTSError, match="out of range"):
            piper_provider.set_volume(-0.1)

    @patch("conversation_agent.providers.tts.piper_provider.pyaudio.PyAudio")
    def test_play_audio_applies_volume(self, mock_pyaudio, piper_provider):
        """Test _play_audio() applies volume scaling."""
        # Create test audio data (16-bit mono)
        audio_data = (np.ones(100, dtype=np.int16) * 1000).tobytes()

        piper_provider.set_volume(0.5)
        piper_provider._play_audio(audio_data)

        # Verify audio was scaled
        # (detailed verification depends on implementation)


class TestPiperProviderFileOperations:
    """Test file save operations."""

    @patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
    def test_save_to_file_creates_wav(
        self, mock_piper_voice, piper_provider, tmp_path
    ):
        """Test save_to_file() creates WAV file."""
        mock_voice = Mock()
        mock_voice.synthesize.return_value = b"\x00\x01" * 100
        mock_piper_voice.load.return_value = mock_voice

        output_path = tmp_path / "output.wav"
        piper_provider.save_to_file("Test", str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0


class TestPiperProviderAvailableVoices:
    """Test available voices discovery."""

    def test_get_available_voices_lists_models(self, piper_provider, tmp_path):
        """Test get_available_voices() lists .onnx files."""
        # Create fake model files
        models_dir = tmp_path / "models/tts/piper"
        models_dir.mkdir(parents=True)
        (models_dir / "voice1.onnx").write_bytes(b"fake")
        (models_dir / "voice2.onnx").write_bytes(b"fake")

        # Mock models directory
        # ... implementation depends on how we scan for models


class TestPiperProviderCleanup:
    """Test resource cleanup."""

    def test_stop_interrupts_playback(self, piper_provider):
        """Test stop() interrupts playback."""
        # Implementation depends on playback mechanism

    def test_shutdown_cleans_resources(self, piper_provider):
        """Test shutdown() cleans up resources."""
        piper_provider.shutdown()
        assert piper_provider.voice is None


# Fixtures
@pytest.fixture
def mock_model_files(tmp_path):
    """Create mock model files."""
    model_path = tmp_path / "test_model.onnx"
    config_path = tmp_path / "test_model.onnx.json"

    model_path.write_bytes(b"fake model data")
    config_path.write_text('{"sample_rate": 22050}')

    return str(model_path), str(config_path)


@pytest.fixture
def piper_provider(mock_model_files):
    """Create PiperTTSProvider instance."""
    model_path, config_path = mock_model_files
    return PiperTTSProvider(model_path=model_path, config_path=config_path)
```

**Integration Tests:**

File: `tests/integration/test_piper_integration.py`

```python
"""Integration tests for Piper TTS (requires real model)."""
import pytest
from pathlib import Path

from conversation_agent.providers.tts.piper_provider import PiperTTSProvider


@pytest.mark.integration
@pytest.mark.skipif(
    not Path("models/tts/piper/en_US-lessac-medium.onnx").exists(),
    reason="Piper model not available"
)
class TestPiperIntegration:
    """Integration tests with real Piper model."""

    def test_real_synthesis(self, tmp_path):
        """Test synthesis with real model."""
        provider = PiperTTSProvider(
            model_path="models/tts/piper/en_US-lessac-medium.onnx"
        )
        provider.initialize()

        output_path = tmp_path / "test_output.wav"
        provider.save_to_file(
            "This is a test of the Piper TTS system.",
            str(output_path)
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 1000

    def test_quality_comparison(self):
        """Manual test for voice quality comparison."""
        # Documented test case for user to run manually
        # comparing pyttsx3 vs Piper output
        pytest.skip("Manual quality test - run interactively")
```

**Coverage Targets:**
- PiperTTSProvider: >85%
- Overall tts module: >80%

**Acceptance Criteria:**
- [ ] All unit tests pass
- [ ] Integration tests pass (with model present)
- [ ] Coverage >80%
- [ ] Mocking prevents hardware dependencies
- [ ] Tests follow existing patterns in tests/providers/tts/

### Phase 6: Documentation

**Goal:** Update all documentation

**Files to Update:**

1. **CLAUDE.md**
   - Update dependencies list
   - Add Piper setup instructions
   - Update default provider to Piper

2. **docs/interview_agent_guide.md**
   - Add Piper model download instructions
   - Update TTS configuration section
   - Add troubleshooting for Piper

3. **README.md**
   - Update features list (highlight improved voice quality)
   - Add model setup to installation instructions

4. **New: docs/phases/phase-07-piper-migration.md**
   - Implementation details
   - Design decisions
   - Migration guide for existing users
   - Performance benchmarks

**Key Documentation Points:**

- Model download instructions (with wget/curl examples)
- Configuration via environment variables
- Switching between pyttsx3 and Piper
- Model quality comparison (lessac-medium vs lessac-high)
- Troubleshooting common issues

**Acceptance Criteria:**
- [ ] All documentation updated
- [ ] Setup instructions clear and complete
- [ ] Migration guide for existing users
- [ ] Phase 7 documentation created

### Phase 7: CLI Integration & Testing

**Goal:** Test end-to-end with CLI

**Tasks:**

1. Test CLI commands with Piper
   ```bash
   python -m conversation_agent.cli config  # Should show piper as default
   python -m conversation_agent.cli test-audio  # Test Piper playback
   python -m conversation_agent.cli start sample.pdf  # Full interview
   ```

2. Test environment variable override
   ```bash
   TTS_PROVIDER=pyttsx3 python -m conversation_agent.cli start sample.pdf
   TTS_PROVIDER=piper python -m conversation_agent.cli start sample.pdf
   ```

3. Test config command shows Piper settings
   ```bash
   python -m conversation_agent.cli config
   # Should display:
   # TTS Provider: piper
   # Model: models/tts/piper/en_US-lessac-medium.onnx
   # Volume: 0.9
   ```

4. User acceptance testing
   - Run full interview with Piper
   - Compare voice quality to pyttsx3
   - Verify naturalness and intelligibility
   - Check performance (no lag/stuttering)

**Acceptance Criteria:**
- [ ] All CLI commands work with Piper
- [ ] Provider switching via env var works
- [ ] Config command shows Piper settings
- [ ] User testing confirms quality improvement
- [ ] No performance degradation

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Model download fails | Medium | High | Provide manual download instructions, host mirror |
| Playback issues on macOS | Low | Medium | Use same pyaudio as STT (already tested) |
| Volume control degradation | Low | Low | Test with various audio samples |
| Rate control expected by users | Medium | Low | Document limitation, log clear warnings |
| Large model files in repo | High | Medium | Add to .gitignore, document download process |
| Integration test failures (no model) | High | Low | Use pytest.mark.skipif for optional tests |

### Migration Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking existing installations | Low | High | Keep pyttsx3 as fallback, clear migration docs |
| Config incompatibility | Low | Medium | Backward compatible config (pyttsx3 still works) |
| Performance regression | Low | High | Benchmark before/after, Piper is faster |

## Success Metrics

### Quantitative

- [ ] Voice quality: 9/10 (from 1/10)
- [ ] Test coverage: >80%
- [ ] Synthesis speed: <0.5s per sentence (RTF ~0.5)
- [ ] All tests passing
- [ ] Zero regressions in existing functionality

### Qualitative

- [ ] Natural, conversational voice quality
- [ ] Clear pronunciation and prosody
- [ ] No robotic artifacts
- [ ] Positive user feedback on voice quality
- [ ] Documentation clear and complete

## Timeline Estimate

- Phase 1 (Setup): 0.5 hours
- Phase 2 (Implementation): 2-3 hours
- Phase 3 (Config): 0.5 hours
- Phase 4 (Exports): 0.25 hours
- Phase 5 (Testing): 2-3 hours
- Phase 6 (Documentation): 1-2 hours
- Phase 7 (Integration): 1 hour

**Total: 7-10 hours** (can be split across multiple sessions)

## Dependencies

### External

- piper-tts>=1.2.0 (PyPI)
- pyaudio>=0.2.14 (already installed for STT)
- numpy (for volume control, likely already installed via torch for Whisper)

### Model Files

- en_US-lessac-medium.onnx (~30MB)
- en_US-lessac-medium.onnx.json (~2KB)

### Internal

- Existing TTSProvider interface (Phase 2)
- TTSConfig system (Phase 2)
- pyaudio for audio playback (Phase 3 STT)

## Rollback Plan

If Piper integration fails or causes issues:

1. **Immediate rollback:**
   ```bash
   export TTS_PROVIDER=pyttsx3
   ```
   OR edit .env:
   ```
   TTS_PROVIDER=pyttsx3
   ```

2. **Code rollback:**
   - pyttsx3 remains in codebase (not removed)
   - TTSConfig defaults can be reverted in one line
   - Git revert possible at any phase

3. **User communication:**
   - Document rollback in README and troubleshooting guide
   - Provide clear instructions for switching providers

## Open Questions

1. **Model Distribution:** Should we host models ourselves or rely on Hugging Face?
   - **Recommendation:** Document Hugging Face download, add troubleshooting

2. **Multiple Models:** Should we support multiple Piper models out of the box?
   - **Recommendation:** Start with lessac-medium, document how to add more

3. **Voice Selection UX:** How should users select different voices?
   - **Recommendation:** Document env var approach for now, CLI option in Phase 8

4. **Performance Monitoring:** Should we add synthesis time logging?
   - **Recommendation:** Yes, add debug logs for synthesis duration

5. **Model Caching:** Should we pre-load models at startup?
   - **Recommendation:** No, keep lazy loading for faster CLI startup

## Future Enhancements (Post-Migration)

- Multi-language support (Spanish, French models)
- Voice selection CLI command
- Streaming audio (reduce latency further)
- Custom voice training guide
- Performance optimizations (ONNX Runtime GPU if available)
- Voice variety (multiple English voices)

## References

- **Integration Guide:** docs/research/piper-integration-guide.md
- **Alternatives Research:** docs/tts-alternatives-comparison.md
- **Piper GitHub:** https://github.com/rhasspy/piper
- **Voice Models:** https://huggingface.co/rhasspy/piper-voices
- **Phase 2 Docs:** docs/phases/phase-02-tts-integration.md

## Approval Checklist

Before implementation begins:

- [ ] Plan reviewed and approved
- [ ] Architecture decisions validated
- [ ] Testing strategy confirmed
- [ ] Risk mitigation acceptable
- [ ] Timeline realistic
- [ ] Dependencies available
- [ ] Model download tested

---

**Next Steps:**
1. Review this plan
2. Download and test Piper model manually
3. Begin Phase 1 implementation
4. Create feature branch: `feature/piper-tts-migration`
