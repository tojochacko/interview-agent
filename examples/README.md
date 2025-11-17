# Examples - Voice Interview Agent

This directory contains example scripts and sample files demonstrating the functionality of the Voice Interview Agent.

## Phase 1 Demo: PDF Parser & Data Models

### Quick Start

```bash
# Generate the sample questionnaire PDF
python examples/create_demo_pdf.py

# Run the interactive demo
python examples/demo_pdf_parser.py
```

### What the Demo Shows

The `demo_pdf_parser.py` script demonstrates all Phase 1 features:

1. **PDF Validation** - Check if a PDF is valid before parsing
2. **Question Parsing** - Extract questions from PDF questionnaires
3. **Question Model** - Working with structured question data
4. **Response Model** - Representing user responses with metadata
5. **Interview Sessions** - Building complete interview transcripts
6. **Error Handling** - Graceful handling of invalid inputs
7. **Parser Configuration** - Customizing parser behavior

### Files

- `demo_pdf_parser.py` - Interactive demo script (run this!)
- `create_demo_pdf.py` - Generates sample questionnaire PDF
- `job_interview_questionnaire.pdf` - Sample questionnaire (30 questions)

## Creating Your Own Questionnaire PDFs

### Best Practices

For optimal parsing results, follow these guidelines when creating questionnaire PDFs:

#### ✅ Do:
- **One question per line** - Each question should be on its own line
- **Clear, complete sentences** - Write full question text
- **Consistent formatting** - Use the same font and size throughout
- **Plain text** - Avoid images, tables, or complex formatting

#### ❌ Don't:
- **Multi-line questions** - Questions spanning multiple lines may be split
- **Mixed content** - Avoid mixing instructions with questions
- **Empty lines** - These will be skipped (which is usually fine)
- **Very short text** - Lines shorter than `min_question_length` are filtered

### Example: Good PDF Format

```
What is your full name?
What is your email address?
What is your phone number?
How many years of experience do you have?
What programming languages are you proficient in?
```

### Example: Poor PDF Format

```
Job Interview Questions
=======================

1. What is your full name? (Please provide
your complete legal name as it appears on
official documents)

2. Email: _______________

For the next question, please describe...
What is your background?
```

**Issues with the above:**
- Title and formatting lines will be parsed as "questions"
- Question 1 is split across multiple lines
- Question 2 is incomplete (just "Email:")
- Instructions mixed with questions

### Creating PDFs Programmatically

You can use the `fpdf2` library (included in dev dependencies) to generate PDFs:

```python
from fpdf import FPDF
from pathlib import Path

def create_questionnaire(questions: list[str], output_path: Path) -> None:
    """Create a questionnaire PDF from a list of questions."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    for question in questions:
        pdf.cell(0, 10, question, new_x="LMARGIN", new_y="NEXT")

    pdf.output(str(output_path))

# Example usage
questions = [
    "What is your name?",
    "What is your favorite programming language?",
    "How many years of experience do you have?",
]

create_questionnaire(questions, Path("my_questionnaire.pdf"))
```

## Parser Configuration Options

Customize the PDF parser for different use cases:

```python
from conversation_agent.core import PDFQuestionParser

# Strict parsing (longer questions only)
strict_parser = PDFQuestionParser(
    min_question_length=20,  # Ignore short text
    strip_whitespace=True,    # Remove leading/trailing spaces
    skip_empty_lines=True     # Skip blank lines
)

# Lenient parsing (accept short questions)
lenient_parser = PDFQuestionParser(
    min_question_length=3,    # Accept very short questions
    strip_whitespace=True,
    skip_empty_lines=True
)

# Parse with chosen configuration
questions = strict_parser.parse("questionnaire.pdf")
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_question_length` | `5` | Minimum character length for valid questions |
| `strip_whitespace` | `True` | Remove leading/trailing whitespace from text |
| `skip_empty_lines` | `True` | Skip lines that are empty or only whitespace |

## Tips for Better Results

1. **Preview your PDF** - Open it and verify text can be selected/copied
2. **Test with validation** - Use `parser.validate_pdf()` before parsing
3. **Start with examples** - Use `create_demo_pdf.py` as a template
4. **Adjust min_length** - If questions are being filtered, lower the threshold
5. **Check source lines** - Each question tracks its line number for debugging

## Troubleshooting

### "No valid questions found in PDF"

**Cause:** All text in the PDF is shorter than `min_question_length` or the PDF is empty.

**Solution:**
```python
parser = PDFQuestionParser(min_question_length=3)  # Lower threshold
questions = parser.parse("questionnaire.pdf")
```

### "PDF appears to be empty or contains no text"

**Cause:** The PDF contains images or scanned text, not selectable text.

**Solution:** Use a PDF with actual text content, not scanned images. If you have a scanned PDF, you'll need to use OCR (Optical Character Recognition) first.

### Questions are split across multiple lines

**Cause:** The PDF has multi-line questions.

**Solution:** Reformat your PDF to have one question per line, or manually combine the parsed questions.

### Title/headers being parsed as questions

**Cause:** The parser treats all non-empty lines as potential questions.

**Solution:**
- Remove title/header lines from the PDF
- Or filter them out after parsing:
```python
questions = parser.parse("questionnaire.pdf")
# Skip first line if it's a title
actual_questions = questions[1:]
```

## Next Steps

This demo covers **Phase 1** only. Future phases will add:

- **Phase 2:** Text-to-Speech (TTS) to speak questions
- **Phase 3:** Speech-to-Text (STT) to capture responses
- **Phase 4:** Conversation orchestration with natural language
- **Phase 5:** CSV export of interview transcripts
- **Phase 6:** CLI interface for end-users
- **Phase 7:** Polish and production readiness

Stay tuned! 🚀
