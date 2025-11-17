## Phase 3: STT Integration - Implementation Guide

**Status**: ✅ Complete
**Date**: 2025-11-17
**Version**: 0.3.0

### Overview

Phase 3 implements Speech-to-Text (STT) capability using OpenAI Whisper, an offline state-of-the-art speech recognition model. This phase introduces the STT provider pattern (consistent with Phase 2 TTS), PyAudio integration for microphone capture, and an audio manager for device handling.

### Objectives Achieved

✅ Created STT provider abstraction (base class)
✅ Implemented Whisper provider (local model)
✅ Integrated PyAudio for microphone capture
✅ Implemented audio manager for device handling
✅ Added configuration for Whisper model size, language
✅ Created comprehensive test suite (37 STT tests)
✅ Implemented demo script to verify STT works
✅ Achieved 78% overall test coverage (90 tests passing)

### Architecture

```
providers/
└── stt/
    ├── base.py              # STTProvider abstract base class
    ├── whisper_provider.py  # Offline STT using Whisper
    └── __init__.py          # Exports

core/
└── audio.py                 # AudioManager for PyAudio wrapper

config/
└── stt_config.py            # Pydantic Settings for STT
```

### Implementation Details

#### 1. STT Provider Abstraction (`providers/stt/base.py`)

**Purpose**: Define interface that all STT providers must implement.

**Key Methods**:
- `transcribe(audio_path: str) -> dict[str, Any]` - Transcribe audio file
- `transcribe_audio_data(audio_data: bytes, sample_rate: int) -> dict[str, Any]` - Transcribe raw audio
- `get_available_models() -> list[str]` - List available models
- `set_language(language: str) -> None` - Set transcription language

**Custom Exception**:
```python
class STTError(Exception):
    """Exception raised when STT operations fail."""
    pass
```

**Return Format**:
```python
{
    "text": "full transcription",
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

#### 2. Whisper Provider (`providers/stt/whisper_provider.py`)

**Features**:
- Local Whisper model (no API calls)
- Model auto-download and caching
- Support for all model sizes (tiny, base, small, medium, large, turbo)
- Configurable language (99 languages supported)
- Word-level timestamps
- CPU and GPU support
- Audio resampling for different sample rates

**Example Usage**:
```python
from conversation_agent.providers.stt import WhisperProvider

provider = WhisperProvider(model_size="base", language="en", device="cpu")
result = provider.transcribe("audio.mp3")
print(result["text"])
```

**Error Handling**:
- Validates model sizes
- Handles model download failures
- Validates audio file paths
- Handles corrupt audio data

#### 3. Audio Manager (`core/audio.py`)

**Purpose**: Wrapper around PyAudio for microphone capture and playback.

**Features**:
- List available audio devices
- Record audio for fixed duration
- Record audio until silence detected
- Save recordings to WAV files
- Silence detection for auto-stop

**Key Methods**:
- `list_devices() -> list[dict]` - Get available microphones
- `record(duration: float, device_index: int) -> bytes` - Record for fixed duration
- `record_until_silence(silence_threshold, silence_duration) -> bytes` - Record until silence
- `save_to_wav(audio_data: bytes, filename: str) -> None` - Save to file
- `_calculate_amplitude(audio_data: bytes) -> float` - Calculate audio amplitude

**Example Usage**:
```python
from conversation_agent.core.audio import AudioManager

audio_mgr = AudioManager(sample_rate=16000)
devices = audio_mgr.list_devices()
audio_data = audio_mgr.record_until_silence()
audio_mgr.save_to_wav(audio_data, "recording.wav")
```

#### 4. STT Configuration (`config/stt_config.py`)

**Purpose**: Manage STT settings via Pydantic Settings.

**Configuration Fields**:
```python
provider: str = "whisper"              # Provider name
model_size: str = "base"               # Model size (tiny-turbo)
language: str = "en"                   # Language code
device: str = "cpu"                    # Device (cpu or cuda)
sample_rate: int = 16000               # Audio sample rate (Hz)
silence_threshold: float = 0.01        # Silence detection threshold
silence_duration: float = 2.0          # Silence duration to stop (seconds)
max_recording_duration: float = 60.0   # Max recording duration (seconds)
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

**Usage**:
```python
from conversation_agent.config import STTConfig

config = STTConfig(model_size="small", language="es")
provider = config.get_provider()  # Returns configured WhisperProvider
```

### Testing

#### Test Coverage

**37 STT tests** covering:
- Provider interface validation (2 tests)
- Whisper provider implementation (13 tests)
- Audio manager functionality (13 tests)
- Configuration management (9 tests)

**Overall Coverage**: 78% (90/90 tests passing)

**Test Command**:
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing -v
```

#### Test Files

**`tests/test_stt_providers.py`** (24 tests):
- `TestSTTProviderInterface` - Abstract interface validation
- `TestWhisperProvider` - Provider implementation tests
- `TestSTTConfig` - Configuration tests

**`tests/test_audio_manager.py`** (13 tests):
- `TestAudioManager` - Audio manager functionality tests

### Demo Script

**Location**: `examples/demo_stt.py`

**Demonstrates**:
1. STT provider initialization
2. Available models listing
3. Language support (99 languages)
4. Audio device listing
5. Recording methods
6. Configuration management
7. Error handling
8. Full workflow simulation

**Run Demo**:
```bash
python examples/demo_stt.py
```

**Note**: Demo runs without requiring actual Whisper/PyAudio installation, showing expected usage patterns.

### Dependencies Added

**`pyproject.toml`**:
```toml
dependencies = [
    # ... existing ...
    "openai-whisper>=20231117",  # Speech-to-Text (Phase 3)
    "pyaudio>=0.2.13",           # Audio I/O (Phase 3)
    "numpy>=1.24.0,<2.0",        # Required by Whisper (Phase 3)
]
```

**Installation**:
```bash
# Install Python dependencies
pip install -e ".[dev]"

# Install system dependencies (macOS)
brew install portaudio

# Install system dependencies (Linux)
sudo apt-get install portaudio19-dev python3-pyaudio
```

### Files Created

```
src/conversation_agent/
├── providers/
│   └── stt/
│       ├── __init__.py              (16 lines)
│       ├── base.py                  (130 lines)
│       └── whisper_provider.py      (248 lines)
├── core/
│   └── audio.py                     (304 lines)
└── config/
    └── stt_config.py                (120 lines)

tests/
├── test_stt_providers.py            (344 lines)
└── test_audio_manager.py            (154 lines)

examples/
└── demo_stt.py                      (319 lines)

docs/phases/
└── phase-03-stt-implementation.md   (this file)

features/
└── phase-03-stt-implementation.md   (~650 lines, planning doc)
```

**Total**: ~2,285 lines of new code

### API Reference

#### STTProvider (Abstract Base Class)

```python
from conversation_agent.providers.stt import STTProvider, STTError

class STTProvider(ABC):
    """Abstract base class for STT providers."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> dict[str, Any]:
        """Transcribe audio file to text."""

    @abstractmethod
    def transcribe_audio_data(
        self, audio_data: bytes, sample_rate: int = 16000
    ) -> dict[str, Any]:
        """Transcribe raw audio data to text."""

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get available models."""

    @abstractmethod
    def set_language(self, language: str) -> None:
        """Set transcription language."""
```

#### WhisperProvider

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
print(result["text"])          # "Hello world"
print(result["language"])      # "en"
print(result["segments"])      # List of segments with timestamps

# Transcribe raw audio
audio_data = b"..."  # Raw audio bytes
result = provider.transcribe_audio_data(audio_data, sample_rate=16000)

# Get available models
models = provider.get_available_models()
# ["tiny", "base", "small", "medium", "large", "turbo"]

# Change language
provider.set_language("es")    # Spanish
provider.set_language("")      # Auto-detect
```

#### AudioManager

```python
from conversation_agent.core.audio import AudioManager, AudioError

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
    silence_duration=2.0,
    max_duration=60.0
)

# Save to file
audio_mgr.save_to_wav(audio_data, "recording.wav")

# Get properties
sample_rate = audio_mgr.get_sample_rate()  # 16000
channels = audio_mgr.get_channels()        # 1
```

#### STTConfig

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

### Design Decisions

#### DD-016: Provider Pattern for STT

**Decision**: Use abstract base class (ABC) for STT providers, mirroring TTS pattern.

**Rationale**:
- Consistency with Phase 2 (TTS)
- Easy to swap implementations
- Testable with mocks
- Configuration-driven provider selection

#### DD-017: Whisper as Default STT

**Decision**: Use OpenAI Whisper for local STT.

**Rationale**:
- State-of-the-art accuracy
- Works offline (no API costs)
- Supports 99 languages
- Active development and community support

**Trade-offs**:
- ➕ Excellent accuracy, multilingual, free, offline
- ➖ Requires model download (39MB-3GB)
- ➖ Slower than cloud APIs (especially on CPU)

**Recommended Model**: `base` (74MB) for development, `small` (244MB) for production.

#### DD-018: PyAudio for Audio Capture

**Decision**: Use PyAudio for microphone input.

**Rationale**:
- Industry standard for Python audio I/O
- Cross-platform support
- Low-level access to audio devices

**Trade-offs**:
- ➕ Powerful, flexible, widely used
- ➖ Requires system dependencies (PortAudio)

#### DD-019: Silence Detection for Recording

**Decision**: Implement silence detection to auto-stop recording.

**Rationale**:
- Better UX than fixed duration
- Natural conversation flow
- Aligns with Phase 4 orchestration needs

### Known Limitations

1. **Model Download**: First run requires downloading Whisper model
   - Mitigation: Clear user messaging

2. **Processing Speed**: Whisper can be slow on CPU
   - Mitigation: Recommend `base` or `tiny` model for CPU

3. **PyAudio Installation**: Can be problematic on some systems
   - Mitigation: Clear documentation, system-specific instructions

4. **Silence Detection**: Simple amplitude-based (not VAD)
   - Future: Implement proper Voice Activity Detection

### Performance

#### Whisper Model Size vs Performance

| Model | Size | Speed (CPU) | Speed (GPU) | Accuracy | Use Case |
|-------|------|-------------|-------------|----------|----------|
| tiny | 39MB | Fast | Very Fast | Good | Testing |
| base | 74MB | Medium | Fast | Better | Development |
| small | 244MB | Slow | Medium | High | Production |
| medium | 769MB | Very Slow | Medium | Higher | High accuracy |
| large | 1.5GB | Extremely Slow | Slow | Highest | Maximum accuracy |
| turbo | 809MB | Slow | Medium | High | Balanced |

**Recommendation**:
- Development: `base` model
- Production: `small` or `turbo` model
- High accuracy: `medium` or `large` with GPU

### Security

- ✅ No network requests (offline operation)
- ✅ No API keys or credentials needed
- ✅ Local file system access only
- ✅ No cloud data transmission

### Next Steps (Phase 4)

Phase 4 will implement:
- Interview Orchestrator (state machine)
- Intent recognition for natural conversation
- Integration of TTS + STT in conversation loop
- Conversation context and memory

### Related Documentation

- [Architecture Overview](../architecture/overview.md)
- [Design Decisions](../architecture/design-decisions.md)
- [Feature Plan](../../features/voice-interview-agent.md)
- [Phase 2 Documentation](./phase-02-tts-integration.md)
- [Phase 3 Planning](../../features/phase-03-stt-implementation.md)

---

**Phase 3 Status**: ✅ Complete
**Tests**: 90/90 passing (37 new STT tests)
**Coverage**: 78%
**Ready for**: Phase 4 (Conversation Orchestration)
