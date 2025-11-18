# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with Python code in this repository.

## Core Development Philosophy

### KISS (Keep It Simple, Stupid)

Simplicity should be a key goal in design. Choose straightforward solutions over complex ones whenever possible. Simple solutions are easier to understand, maintain, and debug.

### YAGNI (You Aren't Gonna Need It)

Avoid building functionality on speculation. Implement features only when they are needed, not when you anticipate they might be useful in the future.

### Design Principles

- **Dependency Inversion**: High-level modules should not depend on low-level modules. Both should depend on abstractions.
- **Open/Closed Principle**: Software entities should be open for extension but closed for modification.
- **Single Responsibility**: Each function, class, and module should have one clear purpose.
- **Fail Fast**: Check for potential errors early and raise exceptions immediately when issues occur.

## 🧱 Code Structure & Modularity

### File and Function Limits

- **Never create a file longer than 500 lines of code**. If approaching this limit, refactor by splitting into modules.
- **Functions should be under 50 lines** with a single, clear responsibility.
- **Classes should be under 100 lines** and represent a single concept or entity.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
- **Line lenght should be max 100 characters** ruff rule in pyproject.toml

claude mcp add --transport http context7 https://mcp.context7.com/mcp --header "CONTEXT7_API_KEY: CONTEXT7_API_KEY"

## Feature Planning Phase

### Things to do while feature planning
- Code Analysis using Serena mcp and documentation in the 'docs' folder
- Create clear todos for feature implementation
- Identify all the necessary files to reference in the Plan document
- Use Phases for complex implementations
- Use the context7 mcp for researching on code library documentation. If not found, then feel free to do a web search
- Implementation examples (Github/StackOverflow/blogs)
- Ask for clarification if you need it
- Identify gaps that need additional research
- After planning completion, use the 'features' directory to create the plan document for review

### Output
- Save as: `{feature-name}.md`

## Repository Overview

A production-ready **Voice Interview Agent** that conducts voice-based interviews using PDF questionnaires. The agent speaks questions via TTS, listens to responses via STT, and exports transcripts to CSV. All processing is local/offline. This is a CLI tool with modular provider architecture supporting different TTS/STT implementations.

**Current Status**: Phase 6/7 Complete - CLI Interface & End-to-End Integration
**Next**: Phase 7 - Polish & Production Readiness

⚠️ **Read `docs/` folder for all context** - See `docs/README.md` for navigation.

## Project Structure

```
conversation-agent-v11/
├── src/conversation_agent/     # Main package
│   ├── cli/                    # ✅ CLI interface (Phase 6)
│   ├── models/                 # ✅ Pydantic models (Phase 1)
│   ├── core/                   # ✅ Business logic (Phases 1,4,5)
│   │   ├── pdf_parser.py       # Parse PDF questionnaires
│   │   ├── interview.py        # Interview orchestration
│   │   ├── csv_exporter.py     # CSV export
│   │   └── intent_recognizer.py, conversation_state.py, audio.py
│   ├── providers/              # ✅ TTS/STT implementations (Phases 2-3)
│   │   ├── tts/                # pyttsx3 provider
│   │   └── stt/                # Whisper provider
│   ├── config/                 # ✅ Configuration (Phases 2-5)
│   └── utils/                  # ✅ Logging (Phase 6)
├── tests/                      # ✅ 205 tests, 79% coverage
├── docs/                       # ⚠️ READ THIS FIRST for full context
│   ├── phases/                 # Per-phase implementation docs
│   ├── architecture/           # System design & decisions
│   ├── interview_agent_guide.md # User guide
│   └── README.md               # Documentation index
├── examples/                   # Demo scripts and sample PDFs
└── features/                   # Feature plans
```

**Status**: Phase 6/7 Complete ✅ (CLI Interface & Integration)
**Coverage**: 79% overall, 81% CLI module
**Documentation**: `docs/README.md` → `docs/phases/phase-06-cli.md` for latest

**Import convention**: Always use absolute imports
```python
from conversation_agent.models import Question  # ✅
from ..models import Question  # ❌
```

## Development Commands

### Essential Commands

```bash
# Setup
pip install -e ".[dev]"                              # Install with dev dependencies
source .venv/bin/activate                             # Activate venv (macOS/Linux)

# Testing
python -m pytest tests/ -v                            # Run tests
python -m pytest tests/ --cov=src --cov-report=term   # With coverage (need >80%)
python -m pytest tests/test_pdf_parser.py::TestClass::test_name -v  # Specific test

# Code Quality
python -m ruff check src/ tests/                      # Check style
python -m ruff check --fix src/ tests/                # Auto-fix issues

# CLI Commands (Phase 6 ✅)
python -m conversation_agent.cli start questionnaire.pdf  # Start interview
python -m conversation_agent.cli config                    # View settings
python -m conversation_agent.cli test-audio                # Test audio devices

# Workflow
# 1. Make changes → 2. Test → 3. Ruff check → 4. Commit (if tests pass & coverage >79%)
```

### Troubleshooting

```bash
python --version                                      # Verify Python 3.9+
python -c "import conversation_agent"                 # Verify installation
rm -rf .pytest_cache                                  # Clear test cache
pip install -e ".[dev]"                               # Reinstall if imports fail
```

See `docs/TROUBLESHOOTING.md` for detailed solutions.

## Architecture Notes

**Core System**: Modular CLI for voice-based interviews using PDF questionnaires
**See `docs/architecture/overview.md` for complete architecture details**

### Layer Structure

```
CLI → Business Logic (Parser, Orchestrator, Exporter) → Providers (TTS/STT) → Data Models
Phase: 6✅         1✅        4✅          5✅              2✅     3✅          1✅
```

**All phases 1-6 complete.** Phase 7 (polish) remains.

### Key Patterns

- **Provider Pattern**: Abstract TTS/STT providers (swap via config)
- **Dependency Inversion**: High-level depends on abstractions, not implementations
- **Single Responsibility**: One clear purpose per module
- **Fail Fast**: Validate early, raise exceptions immediately

### Module Rules

**models/** - Pure Pydantic data (Question, Response, Turn, Session)
- No imports from `core` or `providers`
- Validation only, no business logic

**core/** - Business logic (parser, orchestrator, exporters)
- Can import `models`, not `providers`
- Use abstractions for providers

**providers/** - Pluggable TTS/STT implementations
- Each implements abstract base class
- Self-contained, configured via Pydantic Settings

**cli/** - Command-line interface (Phase 6)
- Click-based commands: start, config, test-audio
- Integrates all components for end-to-end workflow
- See `docs/phases/phase-06-cli.md` for details

**utils/** - Utilities (Phase 6)
- Colored logging with file output support

### Exceptions

```
Exception
├── FileNotFoundError, ValueError (stdlib)
└── Custom: PDFParseError, TTSError, STTError (future)
```

Pattern: Catch low-level errors, wrap in custom exceptions with helpful messages.

### Testing

- 205 unit tests passing (26 CLI, 179 other phases)
- 79% overall coverage (81% CLI, 91% STT, 82% TTS)
- Comprehensive mocking for hardware-free testing
- Target: >80% coverage maintained per phase

### Python 3.9 Compatibility

```python
from __future__ import annotations  # Required at top of file

def parse(self) -> list[Question]:  # ✅ Works
    pass

response: Optional[Response] = None  # ✅ Use Optional[X], not X | None
                                     # noqa: UP045 to suppress Ruff warning
```

### Code Quality Checklist

- Files <500 lines | Functions <50 lines | Classes <100 lines | Line length <100 chars
- Test coverage >80% | All Ruff checks pass | Type hints everywhere | Docstrings on public APIs

### Implemented Architecture (Phases 1-6)

- ✅ **Config**: Pydantic Settings with env vars (TTS_RATE, STT_MODEL_SIZE, etc.)
- ✅ **Providers**: Abstract base + concrete (pyttsx3 TTS, Whisper STT)
- ✅ **Security**: Local-only processing, no network requests
- ✅ **CLI**: Full user interface with start, config, test-audio commands
- ✅ **Export**: CSV with metadata, configurable output

### Phase 7 Enhancements (Planned)

- **Performance**: Pre-load Whisper model, streaming audio, Voice Activity Detection
- **Features**: Pause/resume, progress indicators, session management
- **Extensibility**: Additional providers, export formats, multi-language support

### Documentation for Future Agents

⚠️ **Before implementing features**: Read `docs/README.md` → relevant phase docs → design decisions

**Quick Links:**
- 📖 [Architecture Overview](docs/architecture/overview.md)
- 📝 [Design Decisions](docs/architecture/design-decisions.md)
- 🚀 [User Guide](docs/interview_agent_guide.md) - How to run the CLI
- 📋 [Phase 6 (Latest)](docs/phases/phase-06-cli.md) - CLI implementation details
- ❓ [Troubleshooting](docs/TROUBLESHOOTING.md)

**Phase Documentation:**
- Phase 1: [Foundation](docs/phases/phase-01-foundation.md) ✅
- Phase 2: [TTS Integration](docs/phases/phase-02-tts-integration.md) ✅
- Phase 3: [STT Implementation](docs/phases/phase-03-stt-implementation.md) ✅
- Phase 4: [Orchestration](docs/phases/phase-04-orchestration.md) ✅
- Phase 5: [CSV Export](docs/phases/phase-05-csv-export.md) ✅
- Phase 6: [CLI Interface](docs/phases/phase-06-cli.md) ✅
- Phase 7: Polish (planned)
