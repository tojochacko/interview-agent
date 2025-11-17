# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned - Phase 5 (CSV Export)
- CSV exporter implementation
- Session data serialization
- Metadata inclusion

### Planned - Phase 6 (CLI)
- Click-based CLI commands
- Configuration management
- Audio device testing

### Planned - Phase 7 (Polish)
- Performance optimization
- Enhanced error messages
- Progress indicators
- Pause/resume functionality

## [0.4.0] - 2025-11-17

### Added - Phase 4 (Conversation Orchestration)

#### Conversation State Machine
- `ConversationStateMachine` class for managing interview states
- 7 states: INIT, GREETING, QUESTIONING, CONFIRMING, CLOSING, COMPLETE, ERROR
- Validated state transitions with fail-fast error handling
- Error state with recovery mechanism
- Terminal state detection
- `ConversationState` enum for type-safe state values
- `UserIntent` enum for user action classification

#### Intent Recognition
- `IntentRecognizer` class for natural language understanding
- Pattern-based intent matching (regex)
- 9 user intents: ANSWER, REPEAT, CLARIFY, SKIP, CONFIRM_YES, CONFIRM_NO, START, QUIT, UNKNOWN
- Case-insensitive matching with 20+ patterns per intent
- Context-aware recognition (confidence boost for expected intents)
- Configurable confidence threshold (default: 0.7)
- State-aware expected intents

#### Interview Orchestrator
- `InterviewOrchestrator` class coordinating conversation flow
- Full interview lifecycle management (greeting → questions → closing)
- TTS/STT provider integration
- Natural conversation features:
  - Repeat question on user request
  - Clarification requests
  - Skip questions
  - Answer confirmation
  - Early exit support
- Retry logic (configurable max attempts)
- Progress tracking (percent complete, questions remaining)
- Keyboard interrupt handling (Ctrl+C)
- Error recovery mechanisms
- Customizable greeting/closing messages

#### Testing
- 73 new comprehensive unit tests
- 163 total tests passing
- 77% overall code coverage
- Test files:
  - `test_conversation_state.py` (26 tests, 100% coverage)
  - `test_intent_recognizer.py` (29 tests, 100% coverage)
  - `test_interview_orchestrator.py` (18 tests, 53% coverage)

#### Examples & Documentation
- Interactive orchestration demo (`examples/demo_orchestration.py`)
- 5 demo sections (state machine, intent recognition, full simulation)
- Phase 4 implementation guide (750 lines)
- Updated architecture documentation

### Changed
- Updated project version to 0.4.0
- Extended `core/__init__.py` with new exports
- Enhanced integration between Phases 1-3

### Code Quality
- All files under 500 lines (CLAUDE.md compliant)
- All functions under 50 lines
- Orchestrator class 156 lines (acceptable for coordinator class)
- Line length max 100 characters
- 100% Ruff compliance
- Type hints throughout
- Comprehensive docstrings

## [0.2.0] - 2025-11-17

### Added - Phase 2 (TTS Integration)

#### TTS Provider Architecture
- `TTSProvider` abstract base class with complete interface
- Provider pattern for pluggable TTS implementations
- `TTSError` custom exception for TTS failures

#### pyttsx3 Provider
- `Pyttsx3Provider` for offline text-to-speech
- Cross-platform support (Windows SAPI5, macOS NSSpeechSynthesizer, Linux eSpeak)
- Voice customization (rate 50-400 WPM, volume 0.0-1.0)
- Voice selection from system voices
- Save speech to WAV file format

#### Configuration
- `TTSConfig` Pydantic Settings for TTS management
- Environment variable support (`TTS_PROVIDER`, `TTS_RATE`, `TTS_VOLUME`, `TTS_VOICE`)
- Configuration-based provider instantiation
- Default settings (provider=pyttsx3, rate=175, volume=0.9)

#### Testing
- 27 comprehensive unit tests for TTS providers
- Test coverage: 84% overall
- Mock-based testing (no audio hardware required)
- Edge case testing (invalid rates, volumes, voices, file formats)

#### Examples & Documentation
- Interactive TTS demo script (`examples/demo_tts.py`)
- 8 demonstration sections (initialization, voices, customization, etc.)
- Phase 2 implementation guide (886 lines)
- Updated architecture documentation

#### Dependencies
- Added `pyttsx3>=2.90` for text-to-speech
- Includes pyobjc dependencies on macOS

### Changed
- Updated project version to 0.2.0
- Extended provider architecture for future TTS/STT implementations

### Code Quality
- All files under 500 lines (CLAUDE.md compliant)
- All functions under 50 lines
- 100% Ruff compliance
- Type hints throughout

## [0.1.0] - 2025-11-17

### Added - Phase 1 (Foundation)

#### Data Models
- `Question` model with UUID, number, text, and source line tracking
- `Response` model with text, confidence, timestamp, and retry count
- `ConversationTurn` model for question-answer pairs
- `InterviewSession` model with statistics and turn management
- Pydantic V2 validation for all models
- Comprehensive docstrings for all model fields

#### PDF Parser
- `PDFQuestionParser` class for extracting questions from PDFs
- `PDFParseError` custom exception
- Configurable parsing options:
  - `min_question_length` filter
  - `strip_whitespace` option
  - `skip_empty_lines` option
- `validate_pdf()` method for pre-parsing validation
- Source line tracking for debugging
- Multi-page PDF support

#### Testing
- 26 comprehensive unit tests
- Test coverage: 84%
- Test fixtures:
  - `sample_questionnaire.pdf` (10 questions)
  - `empty_questionnaire.pdf`
  - `malformed_questionnaire.pdf`
  - `multipage_questionnaire.pdf` (2 pages, 6 questions)
- Test PDF generator script
- Edge case testing (unicode, special chars, long questions)

#### Examples & Documentation
- Interactive demo script (`examples/demo_pdf_parser.py`)
- Demo PDF generator (`examples/create_demo_pdf.py`)
- Sample job interview questionnaire (30 questions)
- Examples README with best practices

#### Documentation
- Comprehensive Phase 1 implementation guide
- Architecture overview document
- Design decisions log (12 decisions documented)
- API reference structure
- Troubleshooting guide
- Development changelog (this file)

#### Project Infrastructure
- Project structure created
- `pyproject.toml` configured
- Ruff linting configured (line length 100)
- pytest configuration
- Virtual environment setup
- Git repository initialized

#### Dependencies
- Added `pypdf>=4.0.0` for PDF parsing
- Added `fpdf2>=2.7.0` (dev) for test PDF generation
- Added `pytest-mock>=3.12.0` (dev) for testing

### Changed
- Updated to Pydantic V2 syntax (`model_config = ConfigDict(...)`)
- Migrated from `typing.List` to `list` with `from __future__ import annotations`
- Organized imports (Ruff auto-sorting)

### Fixed
- Python 3.9 compatibility for type hints
- Pydantic V2 migration (deprecated `class Config`)
- Unused variable warnings (renamed to `_variable`)
- Import sorting issues

### Code Quality
- All files under 500 lines (CLAUDE.md compliant)
- All functions under 50 lines
- All classes under 100 lines
- 100% Ruff compliance
- Type hints throughout
- Comprehensive docstrings

## Version History

- **0.1.0** (2025-11-17) - Phase 1: Foundation & PDF Processing ✅

## Future Versions

- **0.2.0** - Phase 2: TTS Integration
- **0.3.0** - Phase 3: STT Integration
- **0.4.0** - Phase 4: Conversation Orchestration
- **0.5.0** - Phase 5: CSV Export
- **0.6.0** - Phase 6: CLI Interface
- **1.0.0** - Phase 7: Production Ready

## How to Update This File

When implementing new features:

1. **Add entries under [Unreleased]** section
2. **Categorize changes:**
   - `Added` - New features
   - `Changed` - Changes to existing functionality
   - `Deprecated` - Soon-to-be removed features
   - `Removed` - Removed features
   - `Fixed` - Bug fixes
   - `Security` - Security fixes

3. **Be specific** - Link to issues/PRs where relevant
4. **On release** - Move [Unreleased] items to new version section

## Format Example

```markdown
### Added
- Feature X with capability Y
- New API endpoint for Z

### Changed
- Updated configuration format from A to B
- Modified behavior of function C

### Fixed
- Resolved issue with D when E occurs
- Fixed memory leak in F

### Deprecated
- Method G will be removed in version 1.0
```

---

**Related Documents:**
- [Phase 1 Implementation](phases/phase-01-foundation.md)
- [Architecture Overview](architecture/overview.md)
- [Feature Plan](../features/voice-interview-agent.md)
