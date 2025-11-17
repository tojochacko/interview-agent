# API Reference

Complete API documentation for the Voice Interview Agent.

## Available APIs

### Core Modules

- **[PDF Parser](pdf-parser.md)** - `conversation_agent.core.pdf_parser`
  - `PDFQuestionParser` - Main PDF parsing class
  - `PDFParseError` - Custom exception for parsing errors

- **[Data Models](models.md)** - `conversation_agent.models`
  - `Question` - Interview question model
  - `Response` - User response model
  - `ConversationTurn` - Question-answer pair
  - `InterviewSession` - Complete interview session

### Future APIs (Planned)

- **TTS Providers** (Phase 2)
  - `TTSProvider` (abstract)
  - `Pyttsx3Provider`

- **STT Providers** (Phase 3)
  - `STTProvider` (abstract)
  - `WhisperProvider`

- **Core Logic** (Phase 4)
  - `InterviewOrchestrator`
  - `IntentRecognizer`

- **Export** (Phase 5)
  - `CSVExporter`

- **CLI** (Phase 6)
  - Click commands

## Quick Reference

### Import Patterns

```python
# Import models
from conversation_agent.models import (
    Question,
    Response,
    ConversationTurn,
    InterviewSession
)

# Import PDF parser
from conversation_agent.core import PDFQuestionParser, PDFParseError

# Import everything
from conversation_agent.models import *
from conversation_agent.core import *
```

### Common Operations

#### Parse a PDF

```python
from conversation_agent.core import PDFQuestionParser

parser = PDFQuestionParser()
questions = parser.parse("questionnaire.pdf")
```

#### Create an Interview Session

```python
from conversation_agent.models import InterviewSession

session = InterviewSession(questionnaire_path="interview.pdf")
```

#### Add a Conversation Turn

```python
from conversation_agent.models import ConversationTurn, Question, Response

question = Question(number=1, text="What is your name?")
response = Response(text="John Smith", confidence=0.95)
turn = ConversationTurn(question=question, response=response)

session.add_turn(turn)
```

## Type Hints

All APIs use comprehensive type hints:

```python
def parse(self, pdf_path: Union[str, Path]) -> list[Question]:
    ...

def validate_pdf(
    self,
    pdf_path: Union[str, Path]
) -> tuple[bool, Optional[str]]:
    ...
```

## Error Handling

```python
from conversation_agent.core import PDFParseError

try:
    questions = parser.parse("file.pdf")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except PDFParseError as e:
    print(f"Parse error: {e}")
```

## Documentation Conventions

### Parameter Documentation

- **Required parameters** are listed first
- **Optional parameters** have defaults shown
- **Type hints** show expected types

### Return Values

- Simple returns: `-> ReturnType`
- Tuples: `-> tuple[Type1, Type2]`
- Optional: `-> Optional[Type]`

### Examples

Every API includes usage examples showing:
- Basic usage
- Common patterns
- Error handling

---

See individual API pages for detailed documentation:
- [PDF Parser API](pdf-parser.md)
- [Data Models API](models.md)
