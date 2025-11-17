# Architecture Overview

**Version**: 1.0 (Phase 1)
**Last Updated**: 2025-11-17

## System Purpose

The Voice Interview Agent is a command-line tool for conducting voice-based interviews using questionnaires from PDF files. It speaks questions to users, captures responses via speech recognition, and exports structured conversation transcripts.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                         │
│                    (conversation_agent/cli)                  │
│              Future Phase 6: Click commands                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Interview Orchestrator                     │
│              (conversation_agent/core/interview)             │
│  • Manages conversation flow                                 │
│  • Handles state machine (greeting → questions → closing)    │
│  • Natural language understanding for intents                │
│              Future Phase 4: Implementation                  │
└──┬──────────┬──────────────┬───────────────┬────────────────┘
   │          │              │               │
   ▼          ▼              ▼               ▼
┌──────┐  ┌──────┐      ┌────────┐      ┌────────┐
│ PDF  │  │ TTS  │      │  STT   │      │  CSV   │
│Parser│  │Engine│      │ Engine │      │Exporter│
│      │  │      │      │        │      │        │
│Phase │  │Phase │      │ Phase  │      │ Phase  │
│  1   │  │  2   │      │   3    │      │   5    │
│  ✅  │  │  📋  │      │  📋   │      │  📋   │
└──────┘  └──────┘      └────────┘      └────────┘
   │          │              │               │
   │      ┌───▼──────────────▼───┐           │
   │      │   Audio Manager       │           │
   │      │ (PyAudio wrapper)     │           │
   │      │     Future Phase 3    │           │
   │      └───────────────────────┘           │
   │                                          │
   └────────────► Data Models ◄───────────────┘
              (Pydantic models)
                  Phase 1 ✅
```

## Component Overview

### Phase 1: Foundation ✅ (IMPLEMENTED)

#### Data Models (`models/interview.py`)

Core data structures using Pydantic for validation:

- **Question**: Interview question with metadata
- **Response**: User response with confidence and timestamps
- **ConversationTurn**: Question-response pair
- **InterviewSession**: Complete interview with statistics

**Key Features:**
- UUID-based identification
- Automatic timestamp generation
- Built-in validation
- Computed statistics (answered, skipped, duration)

#### PDF Parser (`core/pdf_parser.py`)

Extracts questions from PDF questionnaires:

- **PDFQuestionParser**: Main parsing class
- **PDFParseError**: Custom exception
- Configurable filtering (min length, whitespace)
- Source line tracking for debugging

**Key Features:**
- One question per line format
- Multi-page support
- Validation before parsing
- Comprehensive error handling

### Phase 2: TTS Integration 📋 (PLANNED)

#### TTS Provider Abstraction

```python
# Future: conversation_agent/providers/tts/base.py
class TTSProvider(ABC):
    @abstractmethod
    def speak(self, text: str) -> None:
        """Speak the given text."""
        pass

    @abstractmethod
    def set_voice(self, voice_id: str) -> None:
        """Set the voice to use."""
        pass

    @abstractmethod
    def set_rate(self, rate: int) -> None:
        """Set speech rate (words per minute)."""
        pass
```

#### pyttsx3 Implementation

- Offline TTS using system voices
- Cross-platform (macOS, Linux, Windows)
- Configurable rate, volume, voice

### Phase 3: STT Integration 📋 (PLANNED)

#### STT Provider Abstraction

```python
# Future: conversation_agent/providers/stt/base.py
class STTProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_data: bytes) -> tuple[str, float]:
        """Transcribe audio to text.

        Returns:
            (transcription, confidence_score)
        """
        pass
```

#### Whisper Implementation

- Local OpenAI Whisper model
- Multiple model sizes (tiny to large)
- High accuracy, no API costs
- Configurable language

#### Audio Manager

- PyAudio wrapper for microphone capture
- Device selection and configuration
- Recording controls (start, stop, pause)
- Silence detection for auto-stop

### Phase 4: Orchestration 📋 (PLANNED)

#### Interview Orchestrator

State machine for conversation flow:

```
INIT → GREETING → QUESTIONING → CLOSING → COMPLETE
         ↓            ↓↑             ↓
         └────── Error Recovery ─────┘
```

#### Intent Recognition

Natural language understanding:
- "repeat" → Repeat last question
- "clarify" → Provide context
- "skip" → Skip to next question
- "yes"/"no" → Confirm answers

### Phase 5: CSV Export 📋 (PLANNED)

#### CSV Exporter

Export conversation to structured CSV:

```csv
question_id,question_number,question_text,response_text,confidence,timestamp,retry_count,duration_seconds
uuid-123,1,"What is your name?","John Smith",0.95,2025-11-17T10:00:00,0,3.5
```

**Features:**
- UTF-8 encoding
- Metadata inclusion
- Session tracking
- Auto-save on interruption

### Phase 6: CLI Interface 📋 (PLANNED)

#### Click-based Commands

```bash
# Start interview
conversation-agent interview start questionnaire.pdf

# Configure settings
conversation-agent interview config

# Test audio devices
conversation-agent interview test-audio
```

### Phase 7: Polish 📋 (PLANNED)

- Performance optimization
- Enhanced error handling
- Progress indicators
- Pause/resume functionality
- Code refactoring
- Documentation updates

## Design Principles

### 1. Modularity

Each component has a single, clear responsibility:

```
PDF Parser    → Extract questions from PDFs
TTS Engine    → Speak text to user
STT Engine    → Convert speech to text
Orchestrator  → Manage conversation flow
CSV Exporter  → Export conversation data
```

**Benefits:**
- Easy to test in isolation
- Easy to swap implementations
- Clear boundaries

### 2. Provider Pattern

TTS and STT use abstract base classes:

```python
# Easy to swap implementations
tts_provider = Pyttsx3Provider()  # Offline
# tts_provider = GoogleTTSProvider()  # Online (future)
# tts_provider = ElevenLabsProvider()  # Premium (future)
```

**Benefits:**
- Configuration-based provider selection
- Add new providers without changing core logic
- Test with mock providers

### 3. Dependency Inversion

High-level modules depend on abstractions:

```
Interview Orchestrator (high-level)
        ↓ depends on
    TTSProvider (abstraction)
        ↑ implemented by
  Pyttsx3Provider (low-level)
```

**Benefits:**
- Loose coupling
- Easy to add new implementations
- Better testability

### 4. Data-Driven Configuration

All settings configurable via Pydantic Settings:

```python
class TTSConfig(BaseSettings):
    provider: str = "pyttsx3"
    voice: str = "default"
    rate: int = 150
    volume: float = 0.9
```

**Benefits:**
- Environment variable support
- Type validation
- Clear defaults
- Easy to override

### 5. Fail Fast

Check for errors early:

```python
# Validate PDF before parsing
is_valid, error = parser.validate_pdf(path)
if not is_valid:
    raise PDFParseError(error)

# Validate Pydantic models on creation
question = Question(number=0, text="Invalid")  # Raises ValueError
```

**Benefits:**
- Clear error messages
- Easier debugging
- Prevents cascading failures

## Data Flow

### Current (Phase 1)

```
PDF File
   ↓
PDFQuestionParser.parse()
   ↓
list[Question]
   ↓
Manual InterviewSession creation
   ↓
InterviewSession with turns
```

### Future (All Phases)

```
1. Load PDF
   ↓
2. Parse Questions → list[Question]
   ↓
3. Create Session → InterviewSession
   ↓
4. For each question:
   ├─ TTS speaks question
   ├─ STT captures response
   ├─ Intent recognition (repeat/skip/answer)
   └─ Create ConversationTurn
   ↓
5. Mark session complete
   ↓
6. Export to CSV
```

## Error Handling Strategy

### Exception Hierarchy

```
Exception
├── FileNotFoundError (built-in)
│   └── Used for missing PDFs
└── PDFParseError (custom)
    └── Used for parsing failures
```

### Error Propagation

1. **Low-level errors** → Caught and wrapped in custom exceptions
2. **Custom exceptions** → Include helpful error messages
3. **Top-level** → Caught by CLI, displayed to user

**Example:**

```python
try:
    reader = PdfReader(pdf_path)
except PdfReadError as e:
    raise PDFParseError(f"Failed to read PDF: {e}") from e
```

### Validation Strategy

- **Input validation**: Pydantic models
- **Pre-conditions**: Check before operations (e.g., `validate_pdf()`)
- **Post-conditions**: Verify results (e.g., "no questions found")

## Testing Strategy

### Test Pyramid

```
        E2E Tests
       (CLI Tests)
      ┌──────────┐
     /            \
    /  Integration \
   /     Tests      \
  /  (Full Sessions) \
 ┌────────────────────┐
 │                    │
 │   Unit Tests       │
 │  (Models, Parser)  │
 │                    │
 └────────────────────┘
```

### Current Coverage (Phase 1)

- **Unit Tests**: 26 tests for models and parser
- **Test Fixtures**: Generated PDFs for various scenarios
- **Edge Cases**: Special chars, unicode, empty files
- **Coverage**: 84%

### Future Testing

- **Integration Tests**: Full conversation flows
- **Mock Providers**: Test without audio hardware
- **E2E Tests**: CLI command testing
- **Performance Tests**: Response latency

## Technology Choices

### PDF Parsing: pypdf

**Chosen**: pypdf (formerly PyPDF2)

**Alternatives Considered:**
- PyMuPDF (more features, heavier)
- pdfplumber (better for tables)

**Reasons:**
- Pure Python (no binary dependencies)
- High reputation (281+ code examples)
- Sufficient for text extraction
- Well-documented

### TTS: pyttsx3 (Phase 2)

**Chosen**: pyttsx3

**Alternatives Considered:**
- gTTS (requires internet)
- OpenAI TTS (costs per character)
- ElevenLabs (premium, costly)

**Reasons:**
- Offline (no API costs)
- Cross-platform
- Good for development/testing
- Provider pattern allows future swaps

### STT: OpenAI Whisper (Phase 3)

**Chosen**: OpenAI Whisper (local)

**Alternatives Considered:**
- Google Speech-to-Text (cloud, costs)
- OpenAI Whisper API (cloud, costs)

**Reasons:**
- State-of-the-art accuracy
- Local processing (privacy)
- No ongoing costs
- Configurable model size

### Data Validation: Pydantic

**Why Pydantic:**
- Type validation
- Automatic serialization
- IDE autocomplete
- Already in dependencies

### CLI Framework: Click (Future)

**Why Click:**
- Already in dependencies
- Simple, intuitive API
- Good documentation
- Auto-generated help

## Security Considerations

### Phase 1

- ✅ PDF parsing from trusted sources only
- ✅ No user input sanitization needed (PDF content)
- ✅ No sensitive data handling yet

### Future Phases

- 🔒 Audio data stays local (Whisper is local)
- 🔒 No network requests (except optional cloud providers)
- 🔒 CSV export permissions (file system access only)
- 🔒 Interview data privacy (stored locally)

## Performance Considerations

### Phase 1

- PDF parsing: Fast for typical questionnaires (<100 questions)
- Memory: Low (Pydantic models are lightweight)
- No performance bottlenecks identified

### Future Phases

- **Whisper**: Pre-load model at startup (avoid per-question loading)
- **TTS**: Minimal latency (pyttsx3 is fast)
- **Streaming**: Capture audio while TTS speaks (reduce wait time)
- **VAD**: Voice Activity Detection to reduce silence processing

## Scalability

### Current Scope

- Single user, local execution
- One interview at a time
- Small to medium questionnaires (1-100 questions)

### Not Designed For

- ❌ Multi-user/concurrent interviews
- ❌ Web/API service
- ❌ Large-scale data processing
- ❌ Real-time collaboration

### Future Extensibility

Possible extensions (outside current scope):
- Web UI for non-CLI users
- Cloud storage integration
- Multi-language support
- Interview analytics

## Code Organization

### Directory Structure Philosophy

```
src/conversation_agent/
├── models/          # Pure data models (no business logic)
├── core/            # Business logic (parser, orchestrator)
├── providers/       # Pluggable implementations (TTS, STT)
├── config/          # Configuration management
├── cli/             # User interface (Click commands)
└── utils/           # Shared utilities
```

**Rules:**
- Models don't import from core or providers
- Core imports models, not providers
- Providers are isolated (can be swapped)
- CLI is thin (delegates to core)

### Import Convention

```python
# Absolute imports from package root
from conversation_agent.models import Question
from conversation_agent.core import PDFQuestionParser

# Not relative imports
# from ..models import Question  # ❌ Avoid
```

## Future Architecture Evolution

### Phase 2-3 Dependencies

```
Phase 2 (TTS) ─┐
               ├─► Phase 4 (Orchestration)
Phase 3 (STT) ─┘
```

Phase 4 requires both TTS and STT to be complete.

### Phase 4-6 Dependencies

```
Phase 4 (Orchestration) ──► Phase 5 (CSV Export) ──► Phase 6 (CLI)
                                                         │
                                                         ▼
                                                    Phase 7 (Polish)
```

## Conventions for Future Development

### Adding New Models

1. Define in `models/` directory
2. Add to `models/__init__.py`
3. Include comprehensive docstrings
4. Add Pydantic validation
5. Write unit tests

### Adding New Providers

1. Create abstract base class in `providers/{type}/base.py`
2. Implement concrete provider in `providers/{type}/{name}_provider.py`
3. Add configuration in `config/{type}_config.py`
4. Write tests with mocks
5. Update provider factory

### Adding New Features

1. Review feature plan in `features/`
2. Create phase documentation in `docs/phases/`
3. Implement with tests (TDD preferred)
4. Update architecture docs
5. Update CHANGELOG.md

---

**Related Documents:**
- [Phase 1 Implementation](../phases/phase-01-foundation.md)
- [Feature Plan](../../features/voice-interview-agent.md)
- [Data Models Reference](./data-models.md)
