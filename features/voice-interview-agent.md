# Voice Interview Agent - Feature Plan

## Overview

A voice-based conversational agent that conducts interviews based on questions from a PDF questionnaire. The agent speaks questions to the user, listens to responses, and records the entire conversation in a structured CSV format.

## Requirements

### Functional Requirements

1. **PDF Input**: Load and parse questionnaire from PDF (one question per line format)
2. **Voice Output (TTS)**: Speak questions to the user using text-to-speech
3. **Voice Input (STT)**: Capture and transcribe user responses using speech-to-text
4. **Natural Conversation**: Support conversational flow including:
   - Question repetition on user request
   - Clarification requests
   - Interruption handling
   - Confirmation of answers
5. **CSV Output**: Export conversation transcript with structured data:
   - Question number/ID
   - Question text
   - User response (transcribed)
   - Timestamp
   - Metadata (e.g., retry count, clarifications)

### Non-Functional Requirements

1. **Offline Operation**: All processing happens locally (no cloud dependencies)
2. **Cross-Platform**: Support macOS, Linux, Windows
3. **Modularity**: Easy to swap TTS/STT providers via configuration
4. **Performance**: Real-time response (minimal latency between user speech and agent response)
5. **Error Handling**: Graceful handling of audio device issues, unclear speech, etc.

## Technology Stack

### Core Dependencies

| Component | Library | Version | Justification |
|-----------|---------|---------|---------------|
| PDF Parsing | pypdf | 2.0+ | High reputation, 281+ code examples, pure Python |
| Text-to-Speech | pyttsx3 | 2.99+ | Offline, cross-platform, no API costs |
| Speech-to-Text | openai-whisper | latest | State-of-the-art accuracy, local processing |
| Audio I/O | PyAudio | 0.2.13+ | Standard for audio capture in Python |
| CSV Export | csv (stdlib) | - | Built-in, no external dependency |
| CLI Interface | Click | 8.1.0+ | Already in project dependencies |
| Config | Pydantic Settings | 2.0+ | Already in project dependencies |

### Development Dependencies

| Component | Library | Purpose |
|-----------|---------|---------|
| Testing | pytest, pytest-asyncio | Unit and integration tests |
| Audio Mocking | unittest.mock | Test audio I/O without hardware |
| Fixtures | pytest-fixtures | Sample PDFs, audio files for tests |

## Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                         │
│                    (conversation_agent/cli)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Interview Orchestrator                     │
│              (conversation_agent/core/interview)             │
│  - Manages conversation flow                                 │
│  - Handles state machine (greeting → questions → closing)    │
│  - Natural language understanding for intents                │
└──┬──────────┬──────────────┬───────────────┬────────────────┘
   │          │              │               │
   ▼          ▼              ▼               ▼
┌──────┐  ┌──────┐      ┌────────┐      ┌────────┐
│ PDF  │  │ TTS  │      │  STT   │      │  CSV   │
│Parser│  │Engine│      │ Engine │      │Exporter│
└──────┘  └──────┘      └────────┘      └────────┘
   │          │              │               │
   │      ┌───▼──────────────▼───┐           │
   │      │   Audio Manager       │           │
   │      │ (PyAudio wrapper)     │           │
   │      └───────────────────────┘           │
   │                                          │
   └────────────► Data Models ◄───────────────┘
              (Pydantic models)
```

### Component Responsibilities

#### 1. PDF Parser (`conversation_agent/core/pdf_parser.py`)
- Read PDF file using pypdf
- Extract text content
- Parse questions (one per line)
- Return structured Question objects
- Handle malformed PDFs gracefully

#### 2. TTS Engine (`conversation_agent/providers/tts/`)
- **Base Interface** (`base.py`): Abstract TTS provider
- **pyttsx3 Implementation** (`pyttsx3_provider.py`): Concrete implementation
- Speak text with configurable voice, rate, volume
- Provide feedback when speech completes

#### 3. STT Engine (`conversation_agent/providers/stt/`)
- **Base Interface** (`base.py`): Abstract STT provider
- **Whisper Implementation** (`whisper_provider.py`): Local Whisper
- Capture audio from microphone
- Transcribe audio to text
- Return transcription with confidence scores

#### 4. Audio Manager (`conversation_agent/core/audio.py`)
- Wrapper around PyAudio
- Manage audio input/output devices
- Handle device selection and configuration
- Provide recording controls (start, stop, pause)

#### 5. Interview Orchestrator (`conversation_agent/core/interview.py`)
- Main conversation state machine
- Intent recognition for natural conversation:
  - "repeat that" → repeat last question
  - "can you clarify" → provide more context
  - user answer → capture and move to next
- Manage conversation context
- Coordinate TTS/STT interactions

#### 6. CSV Exporter (`conversation_agent/core/csv_exporter.py`)
- Structure conversation data
- Write to CSV with proper formatting
- Include metadata (timestamps, retries, etc.)
- Handle file I/O errors

#### 7. Data Models (`conversation_agent/models/`)
- `Question`: Question text, ID, metadata
- `Response`: Transcribed text, confidence, timestamp
- `ConversationTurn`: Question + Response + metadata
- `InterviewSession`: Complete conversation record

## Implementation Phases

### Phase 1: Foundation & PDF Processing
**Goal**: Set up project structure and basic PDF question extraction

**Tasks**:
1. Create directory structure for new modules
2. Implement PDF parser with pypdf
3. Define Pydantic data models (Question, Response, etc.)
4. Write unit tests for PDF parsing
5. Create sample questionnaire PDFs for testing

**Files to Create**:
- `src/conversation_agent/models/__init__.py`
- `src/conversation_agent/models/interview.py`
- `src/conversation_agent/core/__init__.py`
- `src/conversation_agent/core/pdf_parser.py`
- `tests/test_pdf_parser.py`
- `tests/fixtures/sample_questionnaire.pdf`

**Acceptance Criteria**:
- Can parse PDF and extract questions
- Questions stored in structured format
- Tests cover edge cases (empty PDF, malformed text)

---

### Phase 2: TTS Integration (pyttsx3)
**Goal**: Implement text-to-speech capability

**Tasks**:
1. Create TTS provider abstraction (base class)
2. Implement pyttsx3 provider
3. Add configuration for voice settings (rate, volume, voice selection)
4. Create simple test script to verify TTS works
5. Add TTS provider tests (mocked audio output)

**Files to Create**:
- `src/conversation_agent/providers/__init__.py`
- `src/conversation_agent/providers/tts/__init__.py`
- `src/conversation_agent/providers/tts/base.py`
- `src/conversation_agent/providers/tts/pyttsx3_provider.py`
- `src/conversation_agent/config/tts_config.py`
- `tests/test_tts_providers.py`

**Acceptance Criteria**:
- pyttsx3 successfully speaks text
- Voice settings configurable via Pydantic Settings
- Provider architecture allows easy swapping
- Tests verify provider interface contract

---

### Phase 3: STT Integration (Whisper)
**Goal**: Implement speech-to-text capability

**Tasks**:
1. Create STT provider abstraction (base class)
2. Implement Whisper provider (local model)
3. Integrate PyAudio for microphone capture
4. Add audio manager for device handling
5. Handle Whisper model download/caching
6. Add configuration for Whisper model size, language
7. Create STT tests with sample audio files

**Files to Create**:
- `src/conversation_agent/providers/stt/__init__.py`
- `src/conversation_agent/providers/stt/base.py`
- `src/conversation_agent/providers/stt/whisper_provider.py`
- `src/conversation_agent/core/audio.py`
- `src/conversation_agent/config/stt_config.py`
- `tests/test_stt_providers.py`
- `tests/fixtures/sample_audio.wav`

**Acceptance Criteria**:
- Whisper model loads successfully
- Can transcribe recorded audio
- Audio manager handles device selection
- Configuration allows model size selection (tiny, base, small, medium, large)
- Tests verify transcription accuracy on sample audio

---

### Phase 4: Conversation Orchestration
**Goal**: Build the interview state machine with natural conversation support

**Tasks**:
1. Design conversation state machine
   - States: INIT → GREETING → QUESTIONING → CLOSING → COMPLETE
2. Implement intent recognition for natural language
   - "repeat", "clarify", "yes", "no", "next", etc.
3. Create Interview Orchestrator class
4. Integrate TTS + STT in conversation loop
5. Handle conversation context and memory
6. Add error recovery (unclear audio, silence, etc.)
7. Write integration tests for full conversation flows

**Files to Create**:
- `src/conversation_agent/core/interview.py`
- `src/conversation_agent/core/intent_recognizer.py`
- `src/conversation_agent/core/conversation_state.py`
- `tests/test_interview_orchestrator.py`
- `tests/test_intent_recognition.py`

**Acceptance Criteria**:
- Agent can conduct full interview from greeting to closing
- Natural conversation features work:
  - Repeat question on request
  - Clarify questions
  - Confirm answers
- State transitions handled correctly
- Error recovery works (silence timeout, unclear speech)
- Tests cover all conversation paths

---

### Phase 5: CSV Export & Data Persistence
**Goal**: Save conversation transcripts to structured CSV

**Tasks**:
1. Implement CSV exporter
2. Define CSV schema (columns: question_id, question_text, response_text, timestamp, metadata)
3. Add conversation session tracking
4. Handle file naming (timestamps, session IDs)
5. Add export configuration (output directory, filename format)
6. Create tests for CSV generation

**Files to Create**:
- `src/conversation_agent/core/csv_exporter.py`
- `src/conversation_agent/models/session.py`
- `src/conversation_agent/config/export_config.py`
- `tests/test_csv_exporter.py`

**Acceptance Criteria**:
- Conversation exported to well-formatted CSV
- CSV includes all required fields
- Metadata captured correctly
- File naming is clear and consistent
- Tests verify CSV structure and content

---

### Phase 6: CLI Interface & End-to-End Integration
**Goal**: Create user-facing CLI and complete the feature

**Tasks**:
1. Create Click-based CLI commands:
   - `interview start <pdf_path>` - Start new interview
   - `interview config` - Configure TTS/STT settings
   - `interview test-audio` - Test audio devices
2. Integrate all components in CLI
3. Add comprehensive logging
4. Create user documentation
5. Perform end-to-end testing
6. Create demo questionnaire and walkthrough

**Files to Create**:
- `src/conversation_agent/cli/interview.py`
- `src/conversation_agent/utils/logging_config.py`
- `docs/interview_agent_guide.md`
- `examples/sample_questionnaire.pdf`
- `tests/test_cli_interview.py`

**Acceptance Criteria**:
- CLI commands work end-to-end
- User can run complete interview session
- Logging provides clear feedback
- Documentation explains usage
- Demo works on all supported platforms

---

### Phase 7: Polish & Production Readiness
**Goal**: Refine for production use

**Tasks**:
1. Performance optimization (reduce latency)
2. Comprehensive error handling and user feedback
3. Add progress indicators (e.g., "Question 3 of 10")
4. Implement conversation pause/resume
5. Add audio level indicators (visual feedback for recording)
6. Code review and refactoring per KISS/YAGNI principles
7. Final testing on all platforms
8. Update project README

**Files to Modify/Create**:
- Refactor existing modules as needed
- `README.md` - Update with interview agent info
- `docs/troubleshooting.md` - Common issues and solutions

**Acceptance Criteria**:
- All modules under line limits (files <500, functions <50, classes <100)
- Response latency < 1 second
- Error messages are helpful and actionable
- Code follows CLAUDE.md principles
- Full test coverage (>80%)

## Project Structure

```
conversation-agent-v11/
├── src/
│   └── conversation_agent/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   └── interview.py              # Click commands for interview
│       ├── config/
│       │   ├── __init__.py
│       │   ├── tts_config.py            # TTS settings
│       │   ├── stt_config.py            # STT settings
│       │   └── export_config.py         # CSV export settings
│       ├── core/
│       │   ├── __init__.py
│       │   ├── pdf_parser.py            # PDF question extraction
│       │   ├── audio.py                 # PyAudio wrapper
│       │   ├── interview.py             # Interview orchestrator
│       │   ├── intent_recognizer.py     # Natural language intents
│       │   ├── conversation_state.py    # State machine
│       │   └── csv_exporter.py          # CSV export logic
│       ├── models/
│       │   ├── __init__.py
│       │   ├── interview.py             # Question, Response models
│       │   └── session.py               # Interview session model
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── tts/
│       │   │   ├── __init__.py
│       │   │   ├── base.py              # Abstract TTS interface
│       │   │   └── pyttsx3_provider.py  # pyttsx3 implementation
│       │   └── stt/
│       │       ├── __init__.py
│       │       ├── base.py              # Abstract STT interface
│       │       └── whisper_provider.py  # Whisper implementation
│       └── utils/
│           ├── __init__.py
│           └── logging_config.py        # Logging setup
├── tests/
│   ├── __init__.py
│   ├── fixtures/
│   │   ├── sample_questionnaire.pdf     # Test PDF
│   │   └── sample_audio.wav             # Test audio
│   ├── test_pdf_parser.py
│   ├── test_tts_providers.py
│   ├── test_stt_providers.py
│   ├── test_audio_manager.py
│   ├── test_interview_orchestrator.py
│   ├── test_intent_recognition.py
│   ├── test_csv_exporter.py
│   └── test_cli_interview.py
├── examples/
│   └── sample_questionnaire.pdf         # Demo questionnaire
├── docs/
│   ├── interview_agent_guide.md         # User guide
│   └── troubleshooting.md               # Common issues
├── features/
│   └── voice-interview-agent.md         # This document
├── pyproject.toml                        # Updated with new dependencies
└── README.md                             # Updated with feature info
```

## Dependencies

### New Dependencies to Add

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "pypdf>=4.0.0",           # PDF parsing
    "pyttsx3>=2.99",          # Text-to-speech (offline)
    "openai-whisper>=20231117", # Speech-to-text (local)
    "pyaudio>=0.2.13",        # Audio I/O
    "numpy>=1.24.0",          # Required by Whisper
    "torch>=2.0.0",           # Required by Whisper
    "torchaudio>=2.0.0",      # Required by Whisper
]

[project.optional-dependencies]
dev = [
    # ... existing dev dependencies ...
    "pytest-mock>=3.12.0",    # Mocking for tests
    "soundfile>=0.12.1",      # Audio file I/O for tests
]
```

### System Dependencies

**macOS**:
```bash
brew install portaudio  # Required by PyAudio
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**Windows**:
- PyAudio wheels available on PyPI (should work out of box)

## Configuration

### Example Configuration (`config/interview_config.yaml` or environment variables)

```yaml
tts:
  provider: "pyttsx3"
  voice: "default"  # or specific voice ID
  rate: 150         # words per minute
  volume: 0.9       # 0.0 to 1.0

stt:
  provider: "whisper"
  model_size: "base"  # tiny, base, small, medium, large
  language: "en"
  device: "cpu"       # or "cuda" if GPU available

audio:
  input_device: null   # null = default microphone
  sample_rate: 16000   # Hz
  silence_timeout: 3   # seconds of silence before auto-stop

interview:
  greeting: "Hello! I'm your interview assistant. I'll ask you some questions from the questionnaire. You can ask me to repeat or clarify at any time. Are you ready to begin?"
  closing: "Thank you for your time! Your responses have been recorded."
  confirmation_enabled: true  # Ask "Did I get that right?" after answers

export:
  output_directory: "./interview_transcripts"
  filename_format: "interview_{timestamp}.csv"
  include_metadata: true
```

## Testing Strategy

### Unit Tests
- **PDF Parser**: Various PDF formats, edge cases
- **TTS Providers**: Mock audio output, test interface
- **STT Providers**: Sample audio files, test transcription
- **Audio Manager**: Mock PyAudio, device handling
- **Intent Recognizer**: Various user inputs
- **CSV Exporter**: Data formatting, file I/O

### Integration Tests
- **TTS + STT**: Round-trip (speak → listen → transcribe)
- **Interview Flow**: Complete conversation simulation
- **End-to-End**: Full interview from PDF to CSV

### Manual Tests
- Test on all platforms (macOS, Linux, Windows)
- Test with different microphones/audio devices
- Test with different voices and accents
- Test with background noise
- Test Whisper model sizes (performance vs accuracy trade-offs)

## Error Handling & Edge Cases

### Potential Issues & Mitigations

| Issue | Mitigation |
|-------|------------|
| No microphone detected | Graceful error, list available devices, exit with clear message |
| Whisper model download fails | Check internet, provide manual download instructions |
| User speech unclear | Ask for repetition, show transcription confidence |
| Silence timeout | Prompt user, offer to repeat question |
| PDF parsing failure | Validate PDF format, provide error with line number |
| Audio device busy | Detect and suggest closing other applications |
| Disk space full (CSV write) | Check space before interview, fail gracefully |
| Interruption (Ctrl+C) | Save partial transcript, allow resume option |

## Performance Considerations

### Whisper Model Size vs Performance

| Model | Speed | Accuracy | Memory | Use Case |
|-------|-------|----------|--------|----------|
| tiny | Very fast | Lower | ~1GB | Quick testing, low-end hardware |
| base | Fast | Good | ~1GB | Development, most use cases |
| small | Medium | Better | ~2GB | Production (recommended) |
| medium | Slower | High | ~5GB | High accuracy needs |
| large | Slow | Highest | ~10GB | Maximum accuracy (GPU recommended) |

**Recommendation**: Start with `base` model, allow configuration for user preference.

### Latency Optimization
- Pre-load Whisper model at startup (avoid loading per question)
- Use streaming audio capture (start recording before TTS finishes)
- Consider Voice Activity Detection (VAD) to reduce silence processing

## Future Enhancements (Post-MVP)

These are NOT part of the initial implementation but should be considered for the architecture:

1. **Multi-language Support**
   - Detect questionnaire language from PDF
   - Auto-configure Whisper and TTS for that language

2. **Advanced PDF Parsing**
   - Support structured PDFs with question IDs, types
   - Multiple choice questions with validation
   - Conditional logic (skip questions based on answers)

3. **Cloud TTS/STT Options**
   - Google Cloud Speech-to-Text
   - OpenAI TTS/Whisper API
   - ElevenLabs for premium voices

4. **GUI Interface**
   - Simple web UI for non-CLI users
   - Visual waveform display
   - Progress bar and navigation

5. **Answer Validation**
   - Type checking (expecting number, got text)
   - Required vs optional questions
   - Answer length limits

6. **Session Management**
   - Save/resume interviews
   - Edit answers before finalizing
   - Multiple output formats (JSON, Excel, etc.)

7. **Analytics**
   - Interview duration tracking
   - Question difficulty (retry rate)
   - Common transcription errors

## Open Questions & Clarifications

### Resolved
✅ **TTS Provider**: pyttsx3 (offline)
✅ **STT Provider**: Whisper (local)
✅ **PDF Format**: One question per line
✅ **Conversation Mode**: Natural conversation with clarifications

### Remaining Questions

1. **Question Numbering**: Should questions be auto-numbered, or should the PDF include numbers?
   - **Recommendation**: Auto-number extracted questions for simplicity

2. **Audio Recording Trigger**: How should the agent know when user finishes speaking?
   - **Recommendation**: Use silence detection (3 seconds of silence = done)
   - **Alternative**: Press-to-talk mode (user presses key to start/stop)

3. **Error Threshold**: After how many failed transcription attempts should the agent skip a question?
   - **Recommendation**: 3 attempts, then offer to skip or retry

4. **CSV Encoding**: What encoding for CSV output?
   - **Recommendation**: UTF-8 (supports all languages)

5. **Whisper Model Storage**: Where to store downloaded models?
   - **Recommendation**: User's home directory (`~/.cache/whisper/`)

6. **Interview Interruption**: Should partial interviews be saved automatically?
   - **Recommendation**: Yes, auto-save after each question (allow resume)

## Success Criteria

This feature will be considered complete when:

1. ✅ User can start interview with: `conversation-agent interview start <pdf_path>`
2. ✅ Agent speaks all questions from PDF clearly
3. ✅ Agent accurately transcribes user responses (>90% accuracy on clear audio)
4. ✅ Natural conversation works (repeat, clarify, confirm)
5. ✅ Complete transcript saved to CSV with all required fields
6. ✅ Works on macOS, Linux, and Windows
7. ✅ All tests pass (unit, integration, manual)
8. ✅ Code follows CLAUDE.md principles (KISS, YAGNI, file/function limits)
9. ✅ Documentation complete (user guide, troubleshooting)
10. ✅ Demo questionnaire works end-to-end

## Timeline Estimate

| Phase | Estimated Time | Complexity |
|-------|---------------|------------|
| Phase 1: PDF Processing | 4-6 hours | Low |
| Phase 2: TTS Integration | 4-6 hours | Low-Medium |
| Phase 3: STT Integration | 8-12 hours | Medium-High |
| Phase 4: Orchestration | 12-16 hours | High |
| Phase 5: CSV Export | 3-4 hours | Low |
| Phase 6: CLI Integration | 6-8 hours | Medium |
| Phase 7: Polish | 8-12 hours | Medium |
| **Total** | **45-64 hours** | - |

*Note: Times assume single developer, include testing and documentation*

## Next Steps

1. **Review this plan** with stakeholders/users
2. **Answer remaining open questions**
3. **Set up development environment** (install system dependencies)
4. **Begin Phase 1** (PDF processing foundation)
5. **Iterate** through phases, testing incrementally

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
**Author**: Claude Code
**Status**: Ready for Review
