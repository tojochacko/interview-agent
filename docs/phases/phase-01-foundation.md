# Phase 1: Foundation & PDF Processing

**Status**: ✅ COMPLETE
**Completed**: 2025-11-17
**Duration**: ~4 hours
**Test Coverage**: 84%

## Overview

Phase 1 establishes the foundation of the Voice Interview Agent by implementing PDF questionnaire parsing and core data models. This phase enables the system to read interview questions from PDF files and represent interview sessions with structured data.

## Objectives

- ✅ Parse PDF questionnaires (one question per line format)
- ✅ Define Pydantic data models for interview structure
- ✅ Implement comprehensive error handling
- ✅ Achieve >80% test coverage
- ✅ Follow CLAUDE.md coding standards

## Implementation Details

### 1. Project Structure

```
src/conversation_agent/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── interview.py          # Pydantic data models (132 lines)
└── core/
    ├── __init__.py
    └── pdf_parser.py         # PDF parsing logic (180 lines)

tests/
├── fixtures/
│   ├── generate_test_pdfs.py           # Test PDF generator
│   ├── sample_questionnaire.pdf        # 10 questions
│   ├── empty_questionnaire.pdf         # Empty PDF
│   ├── malformed_questionnaire.pdf     # Edge cases
│   └── multipage_questionnaire.pdf     # Multi-page test
└── test_pdf_parser.py        # 26 test cases (308 lines)

examples/
├── README.md                  # Demo documentation
├── demo_pdf_parser.py         # Interactive demo (9.5 KB)
├── create_demo_pdf.py         # PDF generator
└── job_interview_questionnaire.pdf  # Sample (30 questions)
```

### 2. Data Models (`models/interview.py`)

#### Question Model

Represents a single interview question with metadata.

```python
class Question(BaseModel):
    id: UUID                    # Auto-generated unique identifier
    number: int                 # Sequential question number (1-indexed)
    text: str                   # Question text (min 1 char)
    source_line: Optional[int]  # Line number from PDF (for debugging)
```

**Validation Rules:**
- `number`: Must be >= 1
- `text`: Must have at least 1 character
- `id`: Auto-generated UUID4
- `source_line`: Optional, defaults to None

**Example:**
```python
q = Question(
    number=1,
    text="What is your full name?",
    source_line=5
)
print(q.id)  # UUID('...')
```

#### Response Model

Represents a user's response to a question with transcription metadata.

```python
class Response(BaseModel):
    text: str                         # Transcribed response text
    confidence: float                 # Transcription confidence (0.0-1.0)
    timestamp: datetime               # When response was captured
    retry_count: int                  # Number of retry attempts
    clarification_requested: bool     # User asked for clarification
```

**Validation Rules:**
- `confidence`: 0.0 <= confidence <= 1.0
- `retry_count`: Must be >= 0
- `timestamp`: Auto-generated on creation
- Defaults: confidence=1.0, retry_count=0, clarification_requested=False

**Example:**
```python
r = Response(
    text="John Smith",
    confidence=0.95,
    retry_count=0
)
```

#### ConversationTurn Model

Represents a complete question-answer exchange.

```python
class ConversationTurn(BaseModel):
    question: Question              # The question asked
    response: Optional[Response]    # User's response (None if skipped)
    duration_seconds: float         # Time taken for this turn
    skipped: bool                   # Whether question was skipped
```

**Validation Rules:**
- `duration_seconds`: Must be >= 0.0
- `response`: Can be None for skipped questions
- Defaults: duration_seconds=0.0, skipped=False

**Usage Pattern:**
```python
turn = ConversationTurn(
    question=question,
    response=response,
    duration_seconds=3.5,
    skipped=False
)
```

#### InterviewSession Model

Represents a complete interview session with statistics.

```python
class InterviewSession(BaseModel):
    id: UUID                           # Session identifier
    questionnaire_path: str            # Path to source PDF
    turns: list[ConversationTurn]      # All conversation turns
    start_time: datetime               # Session start time
    end_time: Optional[datetime]       # Session end time
    completed: bool                    # Whether interview is complete
```

**Methods:**
- `add_turn(turn: ConversationTurn)` - Add a conversation turn
- `mark_completed()` - Mark session as complete

**Properties (computed):**
- `total_questions: int` - Total number of questions
- `answered_questions: int` - Number of answered questions
- `skipped_questions: int` - Number of skipped questions
- `total_duration_seconds: float` - Total interview duration

**Example:**
```python
session = InterviewSession(questionnaire_path="interview.pdf")
session.add_turn(turn1)
session.add_turn(turn2)
session.mark_completed()

print(f"Answered: {session.answered_questions}/{session.total_questions}")
print(f"Duration: {session.total_duration_seconds:.1f}s")
```

### 3. PDF Parser (`core/pdf_parser.py`)

#### PDFQuestionParser Class

Main class for parsing questionnaire PDFs.

**Constructor:**
```python
PDFQuestionParser(
    min_question_length: int = 5,
    strip_whitespace: bool = True,
    skip_empty_lines: bool = True
)
```

**Parameters:**
- `min_question_length` - Minimum character length for valid questions
- `strip_whitespace` - Remove leading/trailing whitespace
- `skip_empty_lines` - Skip empty or whitespace-only lines

**Methods:**

##### `parse(pdf_path: Union[str, Path]) -> list[Question]`

Parse questions from a PDF file.

**Returns:** List of Question objects

**Raises:**
- `FileNotFoundError` - PDF file doesn't exist
- `PDFParseError` - PDF cannot be read or has no valid questions

**Example:**
```python
parser = PDFQuestionParser(min_question_length=5)
questions = parser.parse("questionnaire.pdf")

for q in questions:
    print(f"Q{q.number}: {q.text}")
```

##### `validate_pdf(pdf_path: Union[str, Path]) -> tuple[bool, Optional[str]]`

Validate a PDF file without fully parsing it.

**Returns:** `(is_valid: bool, error_message: Optional[str])`

**Example:**
```python
is_valid, error = parser.validate_pdf("questionnaire.pdf")
if not is_valid:
    print(f"Invalid PDF: {error}")
```

**Validation Checks:**
- File exists
- Path is a file (not directory)
- File has .pdf extension
- PDF has pages
- PDF contains extractable text

#### PDFParseError Exception

Custom exception for PDF parsing failures.

```python
try:
    questions = parser.parse("invalid.pdf")
except PDFParseError as e:
    print(f"Parse error: {e}")
```

### 4. Implementation Notes

#### Python 3.9 Compatibility

The code is compatible with Python 3.9+:

```python
from __future__ import annotations  # Enable modern type hints
from typing import Optional          # Use Optional for None unions

# Use list[T] instead of List[T] (requires __future__ annotations)
turns: list[ConversationTurn]

# Use Optional[T] instead of T | None for Pydantic compatibility
response: Optional[Response] = None  # noqa: UP045
```

**Why:** Pydantic in Python 3.9 doesn't support `T | None` syntax even with `from __future__ import annotations`.

#### Pydantic V2 Migration

All models use Pydantic V2 syntax:

```python
from pydantic import BaseModel, ConfigDict, Field

class Question(BaseModel):
    text: str = Field(min_length=1, description="Question text")

    model_config = ConfigDict(frozen=False)  # V2 syntax
```

**Deprecated V1 syntax (removed):**
```python
class Config:  # ❌ Deprecated
    frozen = False
```

#### Source Line Tracking

Each question tracks its source line number from the PDF:

```python
# In pdf_parser.py
global_line_number = 0
for page in reader.pages:
    lines = page.extract_text().split("\n")
    for line in lines:
        global_line_number += 1
        # ... process line
        question = Question(
            number=question_number,
            text=line,
            source_line=global_line_number
        )
```

**Use Case:** Debugging malformed PDFs, identifying which line caused issues.

### 5. Testing Strategy

#### Test Coverage

26 test cases covering:

1. **Valid PDF Parsing** (4 tests)
   - Single-page PDFs
   - Multi-page PDFs
   - String and Path objects
   - Question extraction accuracy

2. **Error Handling** (5 tests)
   - Non-existent files
   - Directory paths
   - Empty PDFs
   - Invalid PDF formats

3. **Question Processing** (6 tests)
   - Sequential numbering
   - Source line tracking
   - Whitespace stripping
   - Min length filtering
   - Empty line skipping
   - Unique ID generation

4. **PDF Validation** (5 tests)
   - Valid PDF validation
   - Non-existent files
   - Directory validation
   - Non-PDF files
   - Empty PDF detection

5. **Data Models** (4 tests)
   - Question creation
   - Pydantic validation
   - Default values
   - UUID uniqueness

6. **Edge Cases** (3 tests)
   - Special characters
   - Unicode support
   - Very long questions

#### Running Tests

```bash
# Run all Phase 1 tests
python -m pytest tests/test_pdf_parser.py -v

# With coverage report
python -m pytest tests/test_pdf_parser.py --cov=src --cov-report=term-missing

# Run specific test class
python -m pytest tests/test_pdf_parser.py::TestPDFQuestionParser -v
```

#### Test Fixtures

Generated test PDFs:

```bash
# Generate test fixtures
python tests/fixtures/generate_test_pdfs.py
```

Creates:
- `sample_questionnaire.pdf` - 10 valid questions
- `empty_questionnaire.pdf` - No content
- `malformed_questionnaire.pdf` - Edge cases (empty lines, short text)
- `multipage_questionnaire.pdf` - 6 questions across 2 pages

### 6. Code Quality Standards

#### CLAUDE.md Compliance

✅ **File Length Limits:**
- `interview.py`: 132 lines (max 500) ✅
- `pdf_parser.py`: 180 lines (max 500) ✅
- `test_pdf_parser.py`: 308 lines (max 500) ✅

✅ **Function Length:**
- All functions under 50 lines ✅
- Most functions 10-30 lines

✅ **Class Length:**
- All classes under 100 lines ✅

✅ **Line Length:**
- Max 100 characters (Ruff configured) ✅

✅ **Code Style:**
- All Ruff checks passing ✅
- Proper type hints ✅
- Comprehensive docstrings ✅

#### Ruff Configuration

```toml
[tool.ruff]
line-length = 100
target-version = "py39"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP"]
```

**Disabled rules:**
- `UP045` - Allow `Optional[T]` for Pydantic compatibility

### 7. Dependencies Added

```toml
[project]
dependencies = [
    "pypdf>=4.0.0",  # PDF parsing
]

[project.optional-dependencies]
dev = [
    "pytest-mock>=3.12.0",  # Mocking for tests
    "fpdf2>=2.7.0",         # Test PDF generation
]
```

### 8. Usage Examples

#### Basic PDF Parsing

```python
from conversation_agent.core import PDFQuestionParser

parser = PDFQuestionParser()
questions = parser.parse("questionnaire.pdf")

for q in questions:
    print(f"Q{q.number}: {q.text}")
```

#### With Validation

```python
from conversation_agent.core import PDFQuestionParser, PDFParseError

parser = PDFQuestionParser()

# Validate first
is_valid, error = parser.validate_pdf("questionnaire.pdf")
if not is_valid:
    print(f"Invalid PDF: {error}")
    exit(1)

# Then parse
try:
    questions = parser.parse("questionnaire.pdf")
except PDFParseError as e:
    print(f"Parse error: {e}")
```

#### Custom Configuration

```python
# Strict: longer questions only
strict_parser = PDFQuestionParser(
    min_question_length=20,
    strip_whitespace=True,
    skip_empty_lines=True
)

# Lenient: accept short questions
lenient_parser = PDFQuestionParser(
    min_question_length=3
)
```

#### Building Interview Sessions

```python
from conversation_agent.models import (
    InterviewSession,
    ConversationTurn,
    Question,
    Response
)

# Create session
session = InterviewSession(questionnaire_path="interview.pdf")

# Parse questions
parser = PDFQuestionParser()
questions = parser.parse("interview.pdf")

# Simulate interview
for question in questions:
    # In real implementation, TTS speaks question and STT captures response
    response = Response(
        text="Sample answer",
        confidence=0.9
    )

    turn = ConversationTurn(
        question=question,
        response=response,
        duration_seconds=5.0
    )

    session.add_turn(turn)

# Complete interview
session.mark_completed()

# View statistics
print(f"Completed: {session.completed}")
print(f"Questions answered: {session.answered_questions}/{session.total_questions}")
print(f"Duration: {session.total_duration_seconds:.1f}s")
```

## Known Limitations

1. **PDF Format Requirements**
   - Requires selectable text (not scanned images)
   - One question per line format
   - No support for complex formatting (tables, multi-column)

2. **Question Identification**
   - All non-empty lines treated as questions
   - No automatic detection of titles/headers
   - Relies on `min_question_length` filtering

3. **Multi-line Questions**
   - Questions spanning multiple lines will be split
   - Users must manually combine if needed

## Future Enhancements

Potential improvements for future phases:

1. **Structured PDF Parsing**
   - Detect question numbers (e.g., "1.", "Q1:")
   - Handle multi-line questions
   - Identify sections/categories

2. **OCR Support**
   - Parse scanned PDFs
   - Image-based questionnaires

3. **Question Types**
   - Multiple choice questions
   - Rating scales
   - Required vs optional

4. **Metadata Extraction**
   - Interview title
   - Categories/sections
   - Question types

## Lessons Learned

1. **Python 3.9 Type Hints**
   - Use `from __future__ import annotations` for modern syntax
   - Pydantic doesn't support `T | None` in 3.9, use `Optional[T]`
   - Disable `UP045` Ruff rule with `# noqa: UP045`

2. **Pydantic V2 Migration**
   - Replace `class Config` with `model_config = ConfigDict(...)`
   - Update deprecated settings
   - Test thoroughly after migration

3. **Test PDF Generation**
   - fpdf2 has deprecation warnings (use `new_x`/`new_y` instead of `ln`)
   - Generate comprehensive test fixtures
   - Include edge cases in test data

4. **Code Organization**
   - Keep models separate from business logic
   - Single Responsibility Principle aids testing
   - Comprehensive type hints improve IDE experience

## Acceptance Criteria: VERIFIED ✅

- ✅ Can parse PDF and extract questions
- ✅ Questions stored in structured Pydantic format
- ✅ Tests cover edge cases (empty PDF, malformed text, unicode, etc.)
- ✅ Code follows CLAUDE.md principles
- ✅ Test coverage >80% (achieved 84%)
- ✅ All Ruff checks passing
- ✅ Comprehensive documentation
- ✅ Working demo script

## Next Phase

**Phase 2: TTS Integration (pyttsx3)**

Will implement:
- Text-to-Speech provider abstraction
- pyttsx3 implementation (offline TTS)
- Voice configuration (rate, volume, voice selection)
- Integration with Question model
- Tests for TTS functionality

See: `features/voice-interview-agent.md` for full plan.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
**Author**: Claude Code
**Related Documents**:
- [Feature Plan](../../features/voice-interview-agent.md)
- [Architecture Overview](../architecture/overview.md)
- [API Reference](../api/models.md)
