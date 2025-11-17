# Voice Interview Agent - Documentation

This directory contains comprehensive documentation for the Voice Interview Agent project.

## Documentation Structure

### Phase Documentation (`phases/`)
Detailed implementation records for each development phase:
- **phase-01-foundation.md** - PDF parsing and data models (COMPLETED)
- **phase-02-tts.md** - Text-to-Speech integration (PLANNED)
- **phase-03-stt.md** - Speech-to-Text integration (PLANNED)
- **phase-04-orchestration.md** - Conversation orchestration (PLANNED)
- **phase-05-csv-export.md** - CSV export functionality (PLANNED)
- **phase-06-cli.md** - CLI interface (PLANNED)
- **phase-07-polish.md** - Production readiness (PLANNED)

### Architecture Documentation (`architecture/`)
Design decisions and system architecture:
- **overview.md** - System architecture overview
- **data-models.md** - Pydantic model specifications
- **design-decisions.md** - Key architectural choices

### API Reference (`api/`)
Code-level API documentation:
- **pdf-parser.md** - PDFQuestionParser API
- **models.md** - Data model API reference

### Other Documentation
- **CHANGELOG.md** - Development changelog
- **TROUBLESHOOTING.md** - Common issues and solutions

## For Future Claude Code Agents

When working on this project, please:

1. **Read the relevant phase documentation** to understand what has been implemented
2. **Review architecture decisions** before making significant changes
3. **Update documentation** as you implement new features
4. **Follow CLAUDE.md principles** (KISS, YAGNI, file/function limits)
5. **Maintain test coverage** above 80%
6. **Update CHANGELOG.md** with your changes

## Quick Reference

### Project Status (as of 2025-11-17)

| Phase | Status | Coverage | Files |
|-------|--------|----------|-------|
| Phase 1: Foundation | ✅ COMPLETE | 84% | 6 files, 620 LOC |
| Phase 2: TTS | 📋 PLANNED | - | - |
| Phase 3: STT | 📋 PLANNED | - | - |
| Phase 4: Orchestration | 📋 PLANNED | - | - |
| Phase 5: CSV Export | 📋 PLANNED | - | - |
| Phase 6: CLI | 📋 PLANNED | - | - |
| Phase 7: Polish | 📋 PLANNED | - | - |

### Technology Stack

- **Python**: 3.9+
- **PDF Parsing**: pypdf 4.0+
- **Data Validation**: Pydantic 2.0+
- **TTS**: pyttsx3 (Phase 2)
- **STT**: OpenAI Whisper (Phase 3)
- **Testing**: pytest, pytest-cov
- **Linting**: Ruff

### Key Principles

From `CLAUDE.md`:
- **KISS** - Keep It Simple, Stupid
- **YAGNI** - You Aren't Gonna Need It
- **Files**: Max 500 lines
- **Functions**: Max 50 lines
- **Classes**: Max 100 lines
- **Line length**: Max 100 characters

## Getting Started

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/test_pdf_parser.py -v

# Run demo
python examples/demo_pdf_parser.py

# Check code quality
python -m ruff check src/ tests/
```

## Navigation

- 📖 [Phase 1 Implementation](phases/phase-01-foundation.md)
- 🏗️ [Architecture Overview](architecture/overview.md)
- 🔧 [API Reference](api/README.md)
- 📝 [Changelog](CHANGELOG.md)
- ❓ [Troubleshooting](TROUBLESHOOTING.md)
