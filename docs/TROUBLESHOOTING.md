# Troubleshooting Guide

Common issues and solutions for the Voice Interview Agent.

## Phase 1: PDF Parsing

### "PDF file not found"

**Error:**
```
FileNotFoundError: PDF file not found: questionnaire.pdf
```

**Cause:** The PDF file doesn't exist at the specified path.

**Solution:**
1. Check the file path is correct
2. Use absolute path or verify current working directory
3. Verify file extension is `.pdf`

```python
from pathlib import Path

# Use absolute path
pdf_path = Path("/full/path/to/questionnaire.pdf")

# Or verify it exists first
if not pdf_path.exists():
    print(f"File not found: {pdf_path}")
```

---

### "Path is not a file"

**Error:**
```
PDFParseError: Path is not a file: /path/to/directory/
```

**Cause:** Provided a directory path instead of a file path.

**Solution:**
Ensure you're pointing to a specific PDF file, not a directory.

```python
# Wrong
parser.parse("examples/")  # ❌ Directory

# Correct
parser.parse("examples/questionnaire.pdf")  # ✅ File
```

---

### "No valid questions found in PDF"

**Error:**
```
PDFParseError: No valid questions found in PDF
```

**Causes:**
1. PDF is empty or has no text
2. All text is shorter than `min_question_length`
3. PDF contains only images (scanned document)

**Solutions:**

**If PDF has text but all filtered out:**
```python
# Lower the minimum question length
parser = PDFQuestionParser(min_question_length=3)
questions = parser.parse("questionnaire.pdf")
```

**If PDF is scanned (images only):**
- Use OCR to convert images to text first
- Or recreate PDF with actual text content

**Verify PDF has text:**
```python
parser = PDFQuestionParser()
is_valid, error = parser.validate_pdf("questionnaire.pdf")

if not is_valid:
    print(f"Validation failed: {error}")
```

---

### "PDF appears to be empty or contains no text"

**Error:**
```
Validation error: PDF appears to be empty or contains no text
```

**Cause:** PDF contains images or has no extractable text.

**Solution:**
1. Open PDF and try to select text. If you can't select it, it's scanned.
2. Use OCR software to convert scanned PDF to text PDF
3. Or recreate the PDF with actual text

**Programmatic check:**
```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
text = reader.pages[0].extract_text()

if not text.strip():
    print("PDF has no extractable text - likely scanned")
```

---

### Title/Headers Parsed as Questions

**Problem:** PDF title and headers are being parsed as questions.

**Example:**
```
Q1: Job Interview Questionnaire
Q2: Instructions: Please answer...
Q3: What is your name?
```

**Cause:** Parser treats all non-empty lines as questions.

**Solutions:**

**Option 1: Skip title lines after parsing**
```python
questions = parser.parse("questionnaire.pdf")

# Skip first 2 lines (title + instructions)
actual_questions = questions[2:]
```

**Option 2: Remove title from PDF**
- Recreate PDF with only questions

**Option 3: Use stricter filtering**
```python
# Only accept longer lines (titles usually shorter)
parser = PDFQuestionParser(min_question_length=20)
```

---

### Multi-line Questions Split

**Problem:** Questions spanning multiple lines are split into separate questions.

**Example PDF:**
```
What is your current position and what are
your main responsibilities in this role?
```

**Parsed as:**
```
Q1: What is your current position and what are
Q2: your main responsibilities in this role?
```

**Cause:** Parser uses one question per line format.

**Solutions:**

**Option 1: Reformat PDF**
Put entire question on one line:
```
What is your current position and what are your main responsibilities?
```

**Option 2: Manually combine after parsing**
```python
questions = parser.parse("questionnaire.pdf")

# Manually combine questions 1 and 2
combined_text = f"{questions[0].text} {questions[1].text}"
questions[0].text = combined_text
questions.pop(1)
```

**Option 3: Pre-process PDF**
Use a PDF editor to combine lines before parsing.

---

## Installation Issues

### "pypdf not found"

**Error:**
```
ModuleNotFoundError: No module named 'pypdf'
```

**Cause:** Dependencies not installed.

**Solution:**
```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or just the package
pip install -e .
```

---

### "pytest not found"

**Error:**
```
bash: pytest: command not found
```

**Cause:** Not using virtual environment or dev dependencies not installed.

**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dev dependencies
pip install -e ".[dev]"

# Run pytest
python -m pytest tests/test_pdf_parser.py
```

---

### "ruff: command not found"

**Error:**
```
bash: ruff: command not found
```

**Cause:** Ruff not in PATH or not installed.

**Solution:**
```bash
# Use python -m instead
python -m ruff check src/ tests/

# Or install dev dependencies
pip install -e ".[dev]"
```

---

## Testing Issues

### "Import error in tests"

**Error:**
```
ImportError: cannot import name 'PDFQuestionParser' from 'conversation_agent.core'
```

**Cause:** Package not installed in editable mode.

**Solution:**
```bash
# Install in editable mode
pip install -e .

# Then run tests
python -m pytest tests/
```

---

### "Test PDF fixtures not found"

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'tests/fixtures/sample_questionnaire.pdf'
```

**Cause:** Test PDFs not generated.

**Solution:**
```bash
# Generate test PDFs
python tests/fixtures/generate_test_pdfs.py

# Verify they exist
ls tests/fixtures/*.pdf
```

---

### "Coverage command not working"

**Error:**
```
pytest: error: unrecognized arguments: --cov
```

**Cause:** pytest-cov not installed.

**Solution:**
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Or install pytest-cov directly
pip install pytest-cov

# Run with coverage
python -m pytest tests/ --cov=src
```

---

## Type Hint Issues

### "unsupported operand type(s) for |"

**Error:**
```
TypeError: unsupported operand type(s) for |: 'type' and 'type'
```

**Cause:** Using `X | Y` union syntax in Python 3.9 without `from __future__ import annotations`.

**Solution:**
```python
# Add at top of file
from __future__ import annotations

# Then you can use
def func(param: str | Path) -> list[Question]:
    ...
```

**Note:** For Pydantic models, use `Optional[X]` instead:
```python
response: Optional[Response] = None  # ✅ Works
response: Response | None = None     # ❌ Fails in Pydantic
```

---

### "List is not subscriptable"

**Error:**
```
TypeError: 'type' object is not subscriptable
```

**Cause:** Using `list[X]` without `from __future__ import annotations` in Python 3.9.

**Solution:**
```python
from __future__ import annotations

# Now this works
def parse(self) -> list[Question]:
    ...
```

---

## Pydantic Issues

### "class-based config is deprecated"

**Warning:**
```
PydanticDeprecatedSince20: Support for class-based `config` is deprecated
```

**Cause:** Using Pydantic V1 syntax in V2.

**Solution:**
```python
# Old V1 syntax ❌
class Question(BaseModel):
    class Config:
        frozen = False

# New V2 syntax ✅
from pydantic import ConfigDict

class Question(BaseModel):
    model_config = ConfigDict(frozen=False)
```

---

## Development Issues

### "Ruff UP045 warnings"

**Warning:**
```
UP045: Use `X | None` for type annotations
```

**Cause:** Ruff wants modern syntax, but Pydantic needs `Optional[X]` in Python 3.9.

**Solution:**
Add `# noqa: UP045` to suppress:
```python
response: Optional[Response] = None  # noqa: UP045
```

Or configure in `pyproject.toml`:
```toml
[tool.ruff.lint]
ignore = ["UP045"]
```

---

## Performance Issues

### "PDF parsing is slow"

**Cause:** Large PDF with many pages.

**Solutions:**

1. **Use smaller PDFs for testing**
2. **Pre-validate before parsing:**
```python
is_valid, error = parser.validate_pdf("large.pdf")
if not is_valid:
    # Don't waste time parsing invalid PDF
    print(f"Skip: {error}")
```

3. **Optimize configuration:**
```python
# Skip empty lines and short text
parser = PDFQuestionParser(
    min_question_length=10,
    skip_empty_lines=True
)
```

---

## Getting Help

If your issue isn't listed here:

1. **Check documentation:**
   - [Phase 1 Implementation](phases/phase-01-foundation.md)
   - [Architecture Overview](architecture/overview.md)
   - [API Reference](api/README.md)

2. **Review examples:**
   - Run `python examples/demo_pdf_parser.py`
   - Check `examples/README.md`

3. **Verify setup:**
   ```bash
   # Check Python version
   python --version  # Should be 3.9+

   # Check installation
   pip list | grep conversation-agent

   # Run tests
   python -m pytest tests/ -v
   ```

4. **Report issue:**
   - Include error message
   - Include Python version
   - Include steps to reproduce
   - Include sample PDF (if applicable)

---

**Last Updated**: 2025-11-17
**Version**: 1.0 (Phase 1)
