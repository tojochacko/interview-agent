# Phase 3: Speech-to-Text (STT) Integration - Implementation Plan

**Status**: 🚧 In Progress
**Date**: 2025-11-17
**Version**: 0.3.0

## Overview

Phase 3 implements Speech-to-Text (STT) capability using OpenAI Whisper, a state-of-the-art local speech recognition model. This phase introduces the STT provider pattern (mirroring the TTS pattern from Phase 2), PyAudio integration for microphone capture, and an audio manager for device handling.

## Objectives

- [ ] Create STT provider abstraction (base class)
- [ ] Implement Whisper provider (local model)
- [ ] Integrate PyAudio for microphone capture
- [ ] Implement audio manager for device handling
- [ ] Handle Whisper model download/caching
- [ ] Add configuration for Whisper model size, language
- [ ] Create comprehensive test suite
- [ ] Implement demo script to verify STT works
- [ ] Achieve >80% test coverage

## Architecture

```
providers/
└── stt/
    ├── base.py              # STTProvider abstract base class
    ├── whisper_provider.py  # Local Whisper STT implementation
    └── __init__.py          # Exports

core/
└── audio.py                 # AudioManager for PyAudio wrapper

config/
└── stt_config.py            # Pydantic Settings for STT
```

## Implementation Plan

### 1. STT Provider Abstraction (`providers/stt/base.py`)

**Purpose**: Define interface that all STT providers must implement.

**Key Components**:

```python
from abc import ABC, abstractmethod

class STTError(Exception):
    """Exception raised when STT operations fail."""
    pass

class STTProvider(ABC):
    """Abstract base class for Speech-to-Text providers."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> dict[str, any]:
        """Transcribe audio file to text."""
        pass

    @abstractmethod
    def transcribe_audio_data(self, audio_data: bytes, sample_rate: int = 16000) -> dict[str, any]:
        """Transcribe raw audio data to text."""
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of available models."""
        pass

    @abstractmethod
    def set_language(self, language: str) -> None:
        """Set the language for transcription."""
        pass
```

**Return Format** (aligned with Whisper's output):
```python
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
```

**Key Methods**:
- `transcribe(audio_path: str) -> dict` - Transcribe from file
- `transcribe_audio_data(audio_data: bytes, sample_rate: int) -> dict` - Transcribe from raw audio
- `get_available_models() -> list[str]` - List available models (tiny, base, small, medium, large)
- `set_language(language: str) -> None` - Set transcription language

**Custom Exception**:
```python
class STTError(Exception):
    """Exception raised when STT operations fail."""
    pass
```

### 2. Whisper Provider (`providers/stt/whisper_provider.py`)

**Features**:
- Local Whisper model (no API calls)
- Model auto-download and caching
- Support for all model sizes (tiny, base, small, medium, large, turbo)
- Configurable language
- Word-level timestamps (optional)
- CPU and GPU support

**Key Implementation Details**:

```python
import whisper
from conversation_agent.providers.stt.base import STTProvider, STTError

class WhisperProvider(STTProvider):
    def __init__(self, model_size: str = "base", language: str = "en", device: str = "cpu"):
        """Initialize Whisper provider.

        Args:
            model_size: Model size (tiny, base, small, medium, large, turbo)
            language: Language code (en, es, fr, etc.)
            device: Device to use (cpu or cuda)
        """
        try:
            self.model = whisper.load_model(model_size, device=device)
        except Exception as e:
            raise STTError(f"Failed to load Whisper model: {e}")

        self.model_size = model_size
        self.language = language
        self.device = device

    def transcribe(self, audio_path: str) -> dict:
        """Transcribe audio file."""
        try:
            result = self.model.transcribe(
                audio_path,
                language=self.language,
                fp16=(self.device == "cuda")
            )
            return result
        except Exception as e:
            raise STTError(f"Transcription failed: {e}")

    def transcribe_audio_data(self, audio_data: bytes, sample_rate: int = 16000) -> dict:
        """Transcribe raw audio data."""
        # Convert bytes to numpy array
        # Process and transcribe
        pass
```

**Error Handling**:
- Validates model sizes
- Handles model download failures
- Validates audio file paths
- Handles corrupt audio data

### 3. Audio Manager (`core/audio.py`)

**Purpose**: Wrapper around PyAudio for microphone capture and playback.

**Features**:
- List available audio devices
- Record audio from microphone
- Save recordings to WAV files
- Voice Activity Detection (VAD) - optional for Phase 3
- Silence detection for auto-stop

**Key Components**:

```python
import pyaudio
import wave
import numpy as np

class AudioManager:
    """Manager for audio input/output operations."""

    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024):
        """Initialize audio manager."""
        self.audio = pyaudio.PyAudio()
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size

    def list_devices(self) -> list[dict]:
        """List available audio devices."""
        devices = []
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            devices.append({
                "index": i,
                "name": device_info["name"],
                "channels": device_info["maxInputChannels"],
                "sample_rate": int(device_info["defaultSampleRate"])
            })
        return devices

    def record(self, duration: float, device_index: int = None) -> bytes:
        """Record audio for specified duration."""
        pass

    def record_until_silence(self, silence_threshold: float = 0.01,
                            silence_duration: float = 2.0,
                            device_index: int = None) -> bytes:
        """Record until silence is detected."""
        pass

    def save_to_wav(self, audio_data: bytes, filename: str) -> None:
        """Save audio data to WAV file."""
        pass
```

**Key Methods**:
- `list_devices() -> list[dict]` - Get available microphones
- `record(duration: float, device_index: int) -> bytes` - Record for fixed duration
- `record_until_silence(silence_threshold, silence_duration) -> bytes` - Record until silence
- `save_to_wav(audio_data: bytes, filename: str) -> None` - Save to file

### 4. STT Configuration (`config/stt_config.py`)

**Purpose**: Manage STT settings via Pydantic Settings.

**Configuration Fields**:
```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class STTConfig(BaseSettings):
    """Configuration for Speech-to-Text providers."""

    model_config = SettingsConfigDict(
        env_prefix="STT_",
        case_sensitive=False,
        frozen=False,
    )

    provider: str = Field(
        default="whisper",
        description="STT provider to use (whisper, etc.)"
    )

    model_size: str = Field(
        default="base",
        description="Whisper model size (tiny, base, small, medium, large, turbo)"
    )

    language: str = Field(
        default="en",
        description="Language code for transcription"
    )

    device: str = Field(
        default="cpu",
        description="Device to use (cpu or cuda)"
    )

    sample_rate: int = Field(
        default=16000,
        ge=8000,
        le=48000,
        description="Audio sample rate in Hz"
    )

    silence_threshold: float = Field(
        default=0.01,
        ge=0.0,
        le=1.0,
        description="Silence detection threshold (0.0-1.0)"
    )

    silence_duration: float = Field(
        default=2.0,
        ge=0.5,
        le=10.0,
        description="Duration of silence to stop recording (seconds)"
    )

    def get_provider(self):
        """Get configured STT provider instance."""
        from conversation_agent.providers.stt import WhisperProvider, STTError

        if self.provider.lower() == "whisper":
            try:
                provider = WhisperProvider(
                    model_size=self.model_size,
                    language=self.language,
                    device=self.device
                )
                return provider
            except STTError as e:
                raise ValueError(f"Failed to initialize Whisper provider: {e}")
        else:
            raise ValueError(
                f"Unknown STT provider: {self.provider}. Supported: whisper"
            )
```

**Environment Variables** (optional):
```bash
export STT_PROVIDER=whisper
export STT_MODEL_SIZE=base
export STT_LANGUAGE=en
export STT_DEVICE=cpu
export STT_SAMPLE_RATE=16000
export STT_SILENCE_THRESHOLD=0.01
export STT_SILENCE_DURATION=2.0
```

## Testing Strategy

### Test Files

**`tests/test_stt_providers.py`** - STT provider tests
- `TestSTTProviderInterface` - Abstract interface validation
- `TestWhisperProvider` - Provider implementation tests
  - Model loading
  - File transcription
  - Audio data transcription
  - Language detection
  - Error handling
- `TestSTTConfig` - Configuration tests

**`tests/test_audio_manager.py`** - Audio manager tests
- Device listing
- Recording functionality (mocked)
- Silence detection
- WAV file saving

**Test Fixtures**:
- `tests/fixtures/sample_audio.wav` - Sample audio file for testing
- Generator for creating test audio data

### Coverage Target

- Overall: >80%
- Critical paths: 100% (provider initialization, transcription)

## Demo Script

**Location**: `examples/demo_stt.py`

**Demonstrates**:
1. STT provider initialization
2. Available models listing
3. Transcribing audio file
4. Recording from microphone
5. Transcribing recorded audio
6. Configuration management
7. Audio device listing
8. Error handling

## Dependencies to Add

### pyproject.toml Updates

```toml
[project]
dependencies = [
    # ... existing ...
    "openai-whisper>=20231117",  # Speech-to-Text (Phase 3)
    "pyaudio>=0.2.13",           # Audio I/O (Phase 3)
    "numpy>=1.24.0,<2.0",        # Required by Whisper (Phase 3)
]

[project.optional-dependencies]
dev = [
    # ... existing ...
    "pytest-mock>=3.12.0",      # Mocking for tests
]
```

### System Dependencies

**macOS**:
```bash
brew install portaudio
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**Windows**:
- PyAudio wheels available on PyPI (should work out of box)

## Files to Create

```
src/conversation_agent/
├── providers/
│   └── stt/
│       ├── __init__.py              (~20 lines)
│       ├── base.py                  (~120 lines)
│       └── whisper_provider.py      (~180 lines)
├── core/
│   └── audio.py                     (~250 lines)
└── config/
    └── stt_config.py                (~110 lines)

tests/
├── test_stt_providers.py            (~300 lines)
├── test_audio_manager.py            (~200 lines)
└── fixtures/
    └── sample_audio.wav             (audio file)

examples/
└── demo_stt.py                      (~280 lines)
```

**Total**: ~1,460 lines of new code

## API Reference

### STTProvider (Abstract Base Class)

```python
from conversation_agent.providers.stt import STTProvider

class STTProvider(ABC):
    """Abstract base class for STT providers."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> dict[str, any]:
        """Transcribe audio file to text."""

    @abstractmethod
    def transcribe_audio_data(self, audio_data: bytes, sample_rate: int) -> dict[str, any]:
        """Transcribe raw audio data to text."""

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get available models."""

    @abstractmethod
    def set_language(self, language: str) -> None:
        """Set transcription language."""
```

### WhisperProvider

```python
from conversation_agent.providers.stt import WhisperProvider, STTError

# Initialize
provider = WhisperProvider(
    model_size="base",  # tiny, base, small, medium, large, turbo
    language="en",
    device="cpu"        # or "cuda"
)

# Transcribe file
result = provider.transcribe("audio.mp3")
print(result["text"])
print(result["language"])

# Transcribe raw audio
audio_data = b"..."  # Raw audio bytes
result = provider.transcribe_audio_data(audio_data, sample_rate=16000)

# Get available models
models = provider.get_available_models()
# Returns: ["tiny", "base", "small", "medium", "large", "turbo"]

# Change language
provider.set_language("es")
```

### AudioManager

```python
from conversation_agent.core.audio import AudioManager

# Initialize
audio_mgr = AudioManager(sample_rate=16000, chunk_size=1024)

# List devices
devices = audio_mgr.list_devices()
for device in devices:
    print(f"{device['index']}: {device['name']}")

# Record for 5 seconds
audio_data = audio_mgr.record(duration=5.0, device_index=0)

# Record until silence
audio_data = audio_mgr.record_until_silence(
    silence_threshold=0.01,
    silence_duration=2.0
)

# Save to file
audio_mgr.save_to_wav(audio_data, "recording.wav")
```

### STTConfig

```python
from conversation_agent.config import STTConfig

# Default config
config = STTConfig()

# Custom config
config = STTConfig(
    model_size="small",
    language="es",
    device="cuda"
)

# Get configured provider
provider = config.get_provider()  # Returns WhisperProvider
```

## Design Decisions

### DD-016: Provider Pattern for STT

**Decision**: Use abstract base class (ABC) for STT providers, mirroring TTS pattern.

**Rationale**:
- Consistency with Phase 2 (TTS)
- Easy to swap implementations (Whisper, Google Cloud STT, etc.)
- Testable with mocks
- Configuration-driven provider selection

**Benefits**:
- ✅ Add new providers without changing core logic
- ✅ Test without actual audio hardware
- ✅ Configure via environment variables

### DD-017: Whisper as Default STT

**Decision**: Use OpenAI Whisper for local STT.

**Rationale**:
- State-of-the-art accuracy
- Works offline (no API costs)
- Supports 99 languages
- Active development and community support

**Trade-offs**:
- ➕ Excellent accuracy, multilingual, free, offline
- ➖ Requires model download (39MB-3GB depending on size)
- ➖ Slower than cloud APIs (especially on CPU)

**Recommended Model**: `base` (74MB) for development, `small` (244MB) for production.

### DD-018: PyAudio for Audio Capture

**Decision**: Use PyAudio for microphone input.

**Rationale**:
- Industry standard for Python audio I/O
- Cross-platform support
- Low-level access to audio devices
- Well-documented

**Trade-offs**:
- ➕ Powerful, flexible, widely used
- ➖ Requires system dependencies (PortAudio)
- ➖ Can be tricky to install on some systems

**Alternative Considered**: sounddevice (easier install, but less mature)

### DD-019: Silence Detection for Recording

**Decision**: Implement silence detection to auto-stop recording.

**Rationale**:
- Better UX than fixed duration or manual stop
- Natural conversation flow
- Aligns with Phase 4 orchestration needs

**Implementation**:
- Monitor audio amplitude
- Stop after N seconds of silence (configurable)
- Threshold-based detection

## Known Limitations

1. **Model Download**: First run requires downloading Whisper model
   - Mitigation: Clear user messaging, progress indication

2. **Processing Speed**: Whisper can be slow on CPU
   - Mitigation: Recommend `base` or `tiny` model for CPU, GPU for larger models

3. **PyAudio Installation**: Can be problematic on some systems
   - Mitigation: Clear documentation, system-specific instructions

4. **Silence Detection**: Simple amplitude-based (not VAD)
   - Future: Implement proper Voice Activity Detection

## Performance Considerations

### Whisper Model Size vs Performance

| Model | Size | Speed (CPU) | Speed (GPU) | Accuracy | Use Case |
|-------|------|-------------|-------------|----------|----------|
| tiny | 39MB | Fast | Very Fast | Good | Quick testing |
| base | 74MB | Medium | Fast | Better | Development |
| small | 244MB | Slow | Medium | High | Production |
| medium | 769MB | Very Slow | Medium | Higher | High accuracy |
| large | 1.5GB | Extremely Slow | Slow | Highest | Maximum accuracy |
| turbo | 809MB | Slow | Medium | High | Balanced |

**Recommendation**:
- Development: `base` model
- Production: `small` or `turbo` model
- High accuracy: `medium` or `large` with GPU

### Latency Optimization

- Pre-load model at startup (avoid loading per transcription)
- Use appropriate model size for hardware
- Consider streaming/chunked processing for long audio (future enhancement)

## Security Considerations

- ✅ No network requests (offline operation)
- ✅ No API keys or credentials needed
- ✅ Local file system access only
- ✅ No cloud data transmission

## Error Handling

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Model download failure | No internet, disk space | Check connection, free space |
| PyAudio not found | Missing system dependency | Install PortAudio |
| No microphone detected | Device not available | List devices, check permissions |
| Audio file corrupt | Invalid format | Validate file before processing |
| CUDA not available | No GPU or drivers | Fall back to CPU |

## Next Steps (Phase 4)

After Phase 3 completion, Phase 4 will implement:
- Interview Orchestrator (state machine)
- Intent recognition for natural conversation
- Integration of TTS + STT in conversation loop
- Conversation context and memory

## Success Criteria

Phase 3 will be considered complete when:

- [ ] All files created and integrated
- [ ] STT provider abstraction works with Whisper
- [ ] Audio manager can record from microphone
- [ ] Whisper successfully transcribes audio files
- [ ] Whisper transcribes recorded audio
- [ ] Configuration works via Pydantic Settings
- [ ] All tests pass (unit, integration)
- [ ] Test coverage >80%
- [ ] Demo script works end-to-end
- [ ] Code follows CLAUDE.md principles
- [ ] Documentation complete

## Related Documentation

- [Architecture Overview](../docs/architecture/overview.md)
- [Design Decisions](../docs/architecture/design-decisions.md)
- [Feature Plan](./voice-interview-agent.md)
- [Phase 2 Documentation](../docs/phases/phase-02-tts-integration.md)

---

**Phase 3 Status**: 🚧 In Progress
**Estimated Completion**: 8-12 hours
**Next Phase**: Phase 4 (Conversation Orchestration)
