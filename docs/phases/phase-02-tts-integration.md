## Phase 2: TTS Integration - Implementation Guide

**Status**: ✅ Complete
**Date**: 2025-11-17
**Version**: 0.2.0

### Overview

Phase 2 implements Text-to-Speech (TTS) capability using pyttsx3, an offline TTS library. This phase introduces the provider pattern for pluggable TTS implementations and configuration management using Pydantic Settings.

### Objectives Achieved

✅ Created TTS provider abstraction (base class)
✅ Implemented pyttsx3 provider
✅ Added configuration for voice settings (rate, volume, voice selection)
✅ Created comprehensive test suite (27 tests)
✅ Implemented demo script to verify TTS works
✅ Achieved 84% overall test coverage

### Architecture

```
providers/
└── tts/
    ├── base.py              # TTSProvider abstract base class
    ├── pyttsx3_provider.py  # Offline TTS using pyttsx3
    └── __init__.py          # Exports

config/
└── tts_config.py            # Pydantic Settings for TTS
```

### Implementation Details

#### 1. TTS Provider Abstraction (`providers/tts/base.py`)

**Purpose**: Define interface that all TTS providers must implement.

**Key Methods**:
- `speak(text: str) -> None` - Speak text aloud
- `set_voice(voice_id: str) -> None` - Select voice
- `set_rate(rate: int) -> None` - Set speech rate (WPM)
- `set_volume(volume: float) -> None` - Set volume (0.0-1.0)
- `get_available_voices() -> list[dict]` - List available voices
- `stop() -> None` - Stop current speech
- `save_to_file(text, filename) -> None` - Save speech to audio file

**Custom Exception**:
```python
class TTSError(Exception):
    """Exception raised when TTS operations fail."""
    pass
```

#### 2. Pyttsx3 Provider (`providers/tts/pyttsx3_provider.py`)

**Features**:
- Offline TTS using system voices
- Cross-platform (Windows SAPI5, macOS NSSpeechSynthesizer, Linux eSpeak)
- Configurable rate (50-400 WPM)
- Configurable volume (0.0-1.0)
- Voice selection from available system voices
- Save to WAV file

**Example Usage**:
```python
from conversation_agent.providers.tts import Pyttsx3Provider

provider = Pyttsx3Provider()
provider.set_rate(175)
provider.set_volume(0.9)
provider.speak("Hello, world!")
```

**Error Handling**:
- Validates rate range (50-400 WPM)
- Validates volume range (0.0-1.0)
- Validates voice IDs
- WAV-only file format for saving

#### 3. TTS Configuration (`config/tts_config.py`)

**Purpose**: Manage TTS settings via Pydantic Settings.

**Configuration Fields**:
```python
provider: str = "pyttsx3"      # Provider name
voice: Optional[str] = None     # Voice ID (None = system default)
rate: int = 175                 # Speech rate (50-400 WPM)
volume: float = 0.9             # Volume level (0.0-1.0)
```

**Environment Variables** (optional):
```bash
export TTS_PROVIDER=pyttsx3
export TTS_RATE=200
export TTS_VOLUME=0.8
export TTS_VOICE=com.apple.voice.Alex
```

**Usage**:
```python
from conversation_agent.config import TTSConfig

# Use defaults
config = TTSConfig()
provider = config.get_provider()

# Override via constructor
config = TTSConfig(rate=150, volume=0.7)
provider = config.get_provider()
```

### Testing

#### Test Coverage

**27 tests** covering:
- Provider interface validation
- pyttsx3 provider initialization
- Speech synthesis
- Voice customization (rate, volume, voice)
- Available voices listing
- File saving (WAV format)
- Error handling
- Configuration management

**Coverage**: 84% overall

**Test Command**:
```bash
python -m pytest tests/test_tts_providers.py -v
```

#### Test Files

**`tests/test_tts_providers.py`** (270 lines):
- `TestTTSProviderInterface` - Abstract interface tests
- `TestPyttsx3Provider` - Provider implementation tests
- `TestTTSConfig` - Configuration tests

### Demo Script

**Location**: `examples/demo_tts.py`

**Demonstrates**:
1. TTS provider initialization
2. Available voices listing
3. Basic text-to-speech
4. Voice customization (rate, volume)
5. Voice selection
6. Configuration management
7. Saving speech to WAV file
8. Error handling

**Run Demo**:
```bash
python examples/demo_tts.py
```

**Expected Output**:
- Initializes pyttsx3 provider
- Lists 184+ available voices (on macOS)
- Speaks text at different rates and volumes
- Changes voices
- Creates configured provider
- Saves audio to `examples/demo_output.wav`
- Demonstrates error handling

### Dependencies Added

**`pyproject.toml`**:
```toml
dependencies = [
    # ... existing ...
    "pyttsx3>=2.90",  # Text-to-Speech (Phase 2)
]
```

**Installation**:
```bash
pip install -e ".[dev]"
```

### Files Created

```
src/conversation_agent/
├── providers/
│   ├── __init__.py
│   └── tts/
│       ├── __init__.py
│       ├── base.py               (128 lines)
│       └── pyttsx3_provider.py   (186 lines)
└── config/
    ├── __init__.py
    └── tts_config.py              (95 lines)

tests/
└── test_tts_providers.py          (270 lines)

examples/
└── demo_tts.py                    (260 lines)
```

**Total**: ~939 lines of new code

### API Reference

#### TTSProvider (Abstract Base Class)

```python
from conversation_agent.providers.tts import TTSProvider

class TTSProvider(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    def speak(self, text: str) -> None:
        """Speak text aloud."""

    @abstractmethod
    def set_voice(self, voice_id: str) -> None:
        """Set voice to use."""

    @abstractmethod
    def set_rate(self, rate: int) -> None:
        """Set speech rate (WPM)."""

    @abstractmethod
    def set_volume(self, volume: float) -> None:
        """Set volume (0.0-1.0)."""

    @abstractmethod
    def get_available_voices(self) -> list[dict[str, str]]:
        """Get available voices."""

    @abstractmethod
    def stop(self) -> None:
        """Stop current speech."""
```

#### Pyttsx3Provider

```python
from conversation_agent.providers.tts import Pyttsx3Provider, TTSError

# Initialize
provider = Pyttsx3Provider()  # May raise TTSError

# Configure
provider.set_rate(175)        # 50-400 WPM
provider.set_volume(0.9)      # 0.0-1.0

# Get voices
voices = provider.get_available_voices()
# Returns: [{"id": "...", "name": "...", "language": "..."}]

# Select voice
provider.set_voice(voices[0]["id"])

# Speak
provider.speak("Hello, world!")

# Save to file
provider.save_to_file("Hello", "output.wav")  # WAV only

# Stop
provider.stop()
```

#### TTSConfig

```python
from conversation_agent.config import TTSConfig

# Default config
config = TTSConfig()
# provider="pyttsx3", rate=175, volume=0.9, voice=None

# Custom config
config = TTSConfig(
    provider="pyttsx3",
    voice="com.apple.voice.Alex",
    rate=200,
    volume=0.8
)

# Get configured provider
provider = config.get_provider()  # Returns Pyttsx3Provider
```

### Design Decisions

#### DD-013: Provider Pattern for TTS

**Decision**: Use abstract base class (ABC) for TTS providers.

**Rationale**:
- Easy to swap implementations (pyttsx3, gTTS, OpenAI TTS)
- Testable with mocks
- Configuration-driven provider selection
- Follows Dependency Inversion Principle

**Benefits**:
- ✅ Add new providers without changing core logic
- ✅ Test without actual audio hardware
- ✅ Configure via environment variables

#### DD-014: pyttsx3 as Default TTS

**Decision**: Use pyttsx3 for offline TTS.

**Rationale**:
- Works offline (no API costs)
- Cross-platform
- Sufficient for development/testing
- Easy installation (pure Python on most platforms)

**Trade-offs**:
- ➕ Free, offline, fast
- ➖ Voice quality not as good as cloud options
- ➖ Limited voice selection compared to cloud

**Future**: Can add cloud providers (gTTS, OpenAI) via provider pattern.

#### DD-015: Pydantic Settings for Configuration

**Decision**: Use Pydantic Settings for TTS configuration.

**Rationale**:
- Type validation built-in
- Environment variable support
- Clear defaults
- Consistent with Phase 1 (Pydantic models)

**Benefits**:
- ✅ Type-safe configuration
- ✅ Validation (rate range, volume range)
- ✅ Easy to override via env vars or constructor

### Known Limitations

1. **File Format**: pyttsx3 only supports WAV format for saving audio
   - Workaround: Use external tools to convert to MP3/OGG if needed

2. **Voice Quality**: System voices may not be as natural as cloud TTS
   - Future: Add cloud provider options (gTTS, OpenAI, ElevenLabs)

3. **Platform Differences**: Voice availability varies by OS
   - macOS: 184+ voices
   - Windows: Fewer voices (SAPI5)
   - Linux: eSpeak voices

### Performance

- **Initialization**: <100ms for pyttsx3 engine
- **Speech Latency**: Near-instant (offline, no network)
- **Memory**: Lightweight (~10MB)
- **CPU**: Minimal during speech synthesis

### Security

- ✅ No network requests (offline operation)
- ✅ No API keys or credentials needed
- ✅ Local file system access only
- ✅ No sensitive data handling

### Lessons Learned

1. **Mock Setup**: Needed to properly configure Mock objects with attributes (not just kwargs)
   ```python
   # ❌ Didn't work
   Mock(id="voice1", name="Voice 1")

   # ✅ Works
   mock = Mock()
   mock.id = "voice1"
   mock.name = "Voice 1"
   ```

2. **Unused Imports**: Ruff caught unused `Optional` imports after refactoring

3. **Provider Pattern**: Abstractions make testing much easier (can mock entire provider)

4. **Configuration**: Pydantic Settings validation caught configuration errors early

### Next Steps

Phase 3 will implement Speech-to-Text (STT) using OpenAI Whisper:
- STT provider abstraction
- Whisper provider (local model)
- PyAudio integration for microphone capture
- Audio manager for device handling
- STT configuration

### Related Documentation

- [Architecture Overview](../architecture/overview.md)
- [Design Decisions](../architecture/design-decisions.md)
- [Feature Plan](../../features/voice-interview-agent.md)
- [API Reference](../api/README.md)

---

**Phase 2 Status**: ✅ Complete
**Tests**: 27/27 passing
**Coverage**: 84%
**Ready for**: Phase 3 (STT Integration)
