# Design Decisions

This document records key architectural and implementation decisions made during development.

## Format

Each decision follows this structure:

- **Decision**: What was decided
- **Context**: Why the decision was needed
- **Alternatives**: What other options were considered
- **Rationale**: Why this option was chosen
- **Consequences**: Trade-offs and implications
- **Status**: Current (Active/Superseded/Deprecated)

---

## DD-001: Use Pydantic for Data Models

**Date**: 2025-11-17
**Phase**: 1
**Status**: Active

### Decision

Use Pydantic V2 for all data model definitions (Question, Response, ConversationTurn, InterviewSession).

### Context

Need structured data with validation for interview sessions. Must support:
- Type validation
- Serialization (for CSV export)
- Clear API for future agents

### Alternatives

1. **Plain Python dataclasses**
   - Pros: Simpler, no dependency
   - Cons: No validation, manual serialization

2. **attrs**
   - Pros: Lighter than Pydantic
   - Cons: Less validation, fewer features

3. **Custom classes**
   - Pros: Full control
   - Cons: Reinventing the wheel, more code

### Rationale

- Pydantic already in project dependencies
- Excellent validation out of the box
- JSON/dict serialization built-in (useful for CSV export)
- IDE autocomplete support
- Well-documented

### Consequences

**Positive:**
- Strong type safety
- Automatic validation
- Better developer experience
- Future-proof (easy to add fields)

**Negative:**
- Slightly larger dependency
- Learning curve for Pydantic-specific features

---

## DD-002: pypdf for PDF Parsing

**Date**: 2025-11-17
**Phase**: 1
**Status**: Active

### Decision

Use pypdf (formerly PyPDF2) for PDF text extraction.

### Context

Need to extract text from PDF questionnaires. Requirements:
- Simple text extraction
- Pure Python (avoid binary dependencies)
- Well-maintained
- Cross-platform

### Alternatives

1. **PyMuPDF**
   - Pros: More features, faster
   - Cons: Binary dependency, larger, overkill for simple text

2. **pdfplumber**
   - Pros: Better table extraction
   - Cons: Slower, more complex, we don't need tables

3. **pdfminer.six**
   - Pros: Pure Python, detailed extraction
   - Cons: Complex API, harder to use

### Rationale

- pypdf is pure Python (easy install)
- Simple API for basic text extraction
- High reputation (281+ code snippets on Context7)
- Active maintenance
- Sufficient for our needs (plain text only)

### Consequences

**Positive:**
- Easy installation on all platforms
- Simple, readable code
- No binary dependencies to manage

**Negative:**
- Not optimal for complex PDFs
- Limited to text extraction (no layout analysis)

**Mitigation:**
- Document PDF format requirements
- Provide example PDFs
- Offer validation before parsing

---

## DD-003: One Question Per Line PDF Format

**Date**: 2025-11-17
**Phase**: 1
**Status**: Active

### Decision

Require questionnaire PDFs to have one question per line.

### Context

Need a simple, reliable way to identify questions in PDFs without complex NLP.

### Alternatives

1. **Automatic question detection (NLP)**
   - Pros: More flexible for users
   - Cons: Complex, error-prone, overkill (YAGNI)

2. **Numbered questions (1., 2., etc.)**
   - Pros: Clear structure
   - Cons: Requires parsing logic, varies by format

3. **Section-based (headers)**
   - Pros: Better organization
   - Cons: Complex parsing, hard to validate

### Rationale

- KISS principle: Simplest solution that works
- Easy to validate and parse
- Clear expectations for users
- Documented with examples
- Can enhance later if needed (YAGNI)

### Consequences

**Positive:**
- Simple, reliable parsing
- Fast implementation
- Easy to test
- Clear documentation

**Negative:**
- Users must format PDFs correctly
- Multi-line questions are split
- Headers/titles parsed as questions

**Mitigation:**
- Provide PDF generation script
- Document best practices
- Offer `min_question_length` filtering
- Examples and templates

---

## DD-004: Provider Pattern for TTS/STT

**Date**: 2025-11-17
**Phase**: 1 (planned for Phase 2-3)
**Status**: Planned

### Decision

Use abstract base classes for TTS and STT providers with concrete implementations.

### Context

Multiple TTS/STT options exist (pyttsx3, gTTS, OpenAI, etc.). Need flexibility to:
- Swap implementations via configuration
- Test without actual audio hardware
- Add new providers later

### Alternatives

1. **Direct implementation**
   - Pros: Simpler initially
   - Cons: Hard to swap, hard to test

2. **Plugin system**
   - Pros: Very flexible
   - Cons: Over-engineered (YAGNI)

### Rationale

- Dependency Inversion Principle
- Easy to test with mocks
- Configuration-based selection
- Open/Closed Principle (open for extension)
- Not over-engineered (simple ABC)

### Consequences

**Positive:**
- Testable without hardware
- Easy to add providers
- Configuration-driven
- Clean separation of concerns

**Negative:**
- Slight abstraction overhead
- More files/classes

---

## DD-005: pyttsx3 for Initial TTS

**Date**: 2025-11-17
**Phase**: 2 (planned)
**Status**: Planned

### Decision

Start with pyttsx3 (offline TTS) as the default TTS provider.

### Context

Need TTS for Phase 2. Requirements:
- Works offline (no API costs)
- Cross-platform
- Good enough for development

### Alternatives

1. **gTTS (Google)**
   - Pros: Natural voices
   - Cons: Requires internet, usage limits

2. **OpenAI TTS**
   - Pros: Best quality
   - Cons: Costs money, requires API key

3. **ElevenLabs**
   - Pros: Premium quality
   - Cons: Expensive, requires account

### Rationale

- Start simple (pyttsx3 is offline, free)
- Provider pattern allows easy swaps later
- Good for development and testing
- No API keys needed
- Cross-platform

### Consequences

**Positive:**
- No costs
- Works offline
- Fast implementation
- Easy to test

**Negative:**
- Voice quality not as good as cloud options
- Limited voice selection

**Future Path:**
- Can add cloud providers later
- Users can choose via configuration

---

## DD-006: OpenAI Whisper (Local) for STT

**Date**: 2025-11-17
**Phase**: 3 (planned)
**Status**: Planned

### Decision

Use OpenAI Whisper running locally for speech recognition.

### Context

Need STT for Phase 3. User preferences:
- Offline operation
- Good accuracy
- Privacy (local processing)

### Alternatives

1. **Google Speech-to-Text**
   - Pros: High accuracy, cloud-based
   - Cons: Requires internet, costs

2. **OpenAI Whisper API**
   - Pros: Easy setup
   - Cons: Costs money, requires API key

3. **CMU Sphinx**
   - Pros: Offline, free
   - Cons: Lower accuracy, outdated

### Rationale

- State-of-the-art accuracy
- Local processing (privacy)
- No API costs
- Configurable model size (tiny to large)
- Active development

### Consequences

**Positive:**
- Excellent accuracy
- Privacy-friendly
- No recurring costs
- Works offline

**Negative:**
- Requires model download (~40MB-10GB)
- GPU recommended for larger models
- Slower than cloud APIs

**Mitigation:**
- Default to "base" model (good balance)
- Document system requirements
- Provide model size options

---

## DD-007: Python 3.9 Target Version

**Date**: 2025-11-17
**Phase**: 1
**Status**: Active

### Decision

Target Python 3.9+ as minimum version.

### Context

Need to choose minimum Python version. Considerations:
- macOS system Python is 3.9.6
- Modern features desired
- Wide compatibility

### Alternatives

1. **Python 3.10+**
   - Pros: `X | Y` union syntax, pattern matching
   - Cons: Not available on many systems

2. **Python 3.8+**
   - Pros: Wider compatibility
   - Cons: Missing some features

### Rationale

- Balances modernity and compatibility
- Available on current macOS
- Supports `from __future__ import annotations`
- Still widely supported

### Consequences

**Positive:**
- Good feature set
- Wide compatibility
- Modern enough for clean code

**Negative:**
- Can't use `X | None` syntax directly
- Need `Optional[X]` for Pydantic

**Workaround:**
- Use `from __future__ import annotations`
- Use `Optional[X]` with `# noqa: UP045`
- Document Python 3.9 specifics

---

## DD-008: UUID for Question/Session IDs

**Date**: 2025-11-17
**Phase**: 1
**Status**: Active

### Decision

Use UUID4 for Question and InterviewSession identifiers.

### Context

Need unique identifiers for questions and sessions.

### Alternatives

1. **Auto-increment integers**
   - Pros: Simpler, smaller
   - Cons: Not globally unique, requires coordination

2. **Timestamp-based**
   - Pros: Sortable
   - Cons: Not guaranteed unique, clock issues

3. **Hash-based**
   - Pros: Deterministic
   - Cons: Complex, collision risks

### Rationale

- Globally unique (no coordination needed)
- Standard library support
- Pydantic Field default_factory support
- Future-proof for distributed scenarios

### Consequences

**Positive:**
- Guaranteed unique
- Easy to generate
- No state management
- Standard format

**Negative:**
- Larger than integers (36 chars)
- Not human-readable
- Not sortable by creation time

**Note:** Human-readable question numbers still available via `question.number` field.

---

## DD-009: CSV for Export Format

**Date**: 2025-11-17
**Phase**: 5 (planned)
**Status**: Planned

### Decision

Export interview transcripts to CSV format.

### Context

Need structured output format for interview data. Requirements:
- Readable by humans
- Importable to Excel/Google Sheets
- Simple structure

### Alternatives

1. **JSON**
   - Pros: Structured, no schema
   - Cons: Not spreadsheet-friendly

2. **Excel (.xlsx)**
   - Pros: Native spreadsheet
   - Cons: Binary format, library complexity

3. **SQLite**
   - Pros: Queryable
   - Cons: Overkill, not user-friendly

### Rationale

- Universal compatibility
- Human-readable
- Simple to generate (stdlib `csv`)
- Easy to import to spreadsheets
- Flat structure matches our data

### Consequences

**Positive:**
- No additional dependencies
- Universal compatibility
- Easy to implement
- User-friendly

**Negative:**
- Flat structure (no nesting)
- Encoding issues possible
- Limited types

**Mitigation:**
- UTF-8 encoding
- Clear column headers
- Metadata in separate columns

---

## DD-010: Click for CLI Framework

**Date**: 2025-11-17
**Phase**: 6 (planned)
**Status**: Planned

### Decision

Use Click for command-line interface.

### Context

Need CLI framework for Phase 6. Already in dependencies.

### Alternatives

1. **argparse (stdlib)**
   - Pros: No dependency
   - Cons: More verbose, less user-friendly

2. **typer**
   - Pros: Type hints, modern
   - Cons: New dependency, less mature

### Rationale

- Already in project dependencies
- Simple, intuitive API
- Excellent documentation
- Auto-generated help
- Wide adoption

### Consequences

**Positive:**
- No new dependency
- Clean API
- Good docs
- Subcommands support

**Negative:**
- (none significant)

---

## DD-011: No Docker for This Project

**Date**: 2025-11-17
**Phase**: All
**Status**: Active

### Decision

Use Python virtual environment (.venv), not Docker containers.

### Context

Per project requirements: "No Docker container will be used for this code but should use a Python virtual environment for maintaining dependencies and python environment."

### Rationale

- Project requirement
- Simpler for single-user CLI tool
- No deployment complexity needed
- Local audio devices easier to access

### Consequences

**Positive:**
- Simpler setup
- Direct audio device access
- Native performance

**Negative:**
- Users must manage Python environment
- Platform-specific issues possible

**Mitigation:**
- Clear installation docs
- Virtual environment instructions
- Platform-specific notes

---

## DD-012: Test Coverage Target: 80%+

**Date**: 2025-11-17
**Phase**: All
**Status**: Active

### Decision

Maintain minimum 80% test coverage for all code.

### Context

Need quality standard for testing. Balance thoroughness with practicality.

### Rationale

- Industry standard
- Catches most bugs
- Not overly burdensome
- Phase 1 achieved 84%

### Consequences

**Positive:**
- High confidence in code
- Easy refactoring
- Documented behavior

**Negative:**
- Time investment
- Some edge cases hard to test

**Enforcement:**
- pytest-cov in CI
- Coverage reports in tests

---

## Template for Future Decisions

```markdown
## DD-XXX: [Decision Title]

**Date**: YYYY-MM-DD
**Phase**: X
**Status**: Planned/Active/Superseded/Deprecated

### Decision

What was decided.

### Context

Why the decision was needed.

### Alternatives

What other options were considered.

### Rationale

Why this option was chosen.

### Consequences

**Positive:**
- Benefits

**Negative:**
- Trade-offs

**Mitigation:**
- How to address negatives
```

---

**Related Documents:**
- [Architecture Overview](overview.md)
- [Phase 1 Implementation](../phases/phase-01-foundation.md)
- [Feature Plan](../../features/voice-interview-agent.md)
