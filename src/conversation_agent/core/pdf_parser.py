"""PDF questionnaire parser for extracting interview questions."""

import logging
from pathlib import Path
from typing import Optional, Union

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from conversation_agent.models import Question


class PDFParseError(Exception):
    """Exception raised when PDF parsing fails."""

    pass


class PDFQuestionParser:
    """Parser for extracting questions from PDF questionnaires.

    Expects PDF format: one question per line.
    Only sentences ending with '?' are considered as questions.
    Empty lines and lines not ending with '?' are skipped.
    """

    def __init__(
        self,
        min_question_length: int = 5,
        strip_whitespace: bool = True,
        skip_empty_lines: bool = True,
    ):
        """Initialize the PDF parser.

        Args:
            min_question_length: Minimum character length for valid question
            strip_whitespace: Whether to strip leading/trailing whitespace
            skip_empty_lines: Whether to skip empty lines
        """
        self.min_question_length = min_question_length
        self.strip_whitespace = strip_whitespace
        self.skip_empty_lines = skip_empty_lines

    def parse(self, pdf_path: Union[str, Path]) -> list[Question]:
        """Parse questions from a PDF file.

        Args:
            pdf_path: Path to the PDF questionnaire file

        Returns:
            List of Question objects extracted from the PDF

        Raises:
            PDFParseError: If PDF cannot be read or parsed
            FileNotFoundError: If PDF file doesn't exist
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not pdf_path.is_file():
            raise PDFParseError(f"Path is not a file: {pdf_path}")

        try:
            reader = PdfReader(str(pdf_path))
        except PdfReadError as e:
            raise PDFParseError(f"Failed to read PDF: {e}") from e
        except Exception as e:
            raise PDFParseError(f"Unexpected error reading PDF: {e}") from e

        if len(reader.pages) == 0:
            raise PDFParseError("PDF file has no pages")

        questions = self._extract_questions(reader)
        logger = logging.getLogger(__name__)
        logger.debug(f"Questions to ask: {questions}")

        if not questions:
            raise PDFParseError("No valid questions found in PDF")

        return questions

    def _extract_questions(self, reader: PdfReader) -> list[Question]:
        """Extract questions from all pages of the PDF.

        Args:
            reader: PdfReader instance

        Returns:
            List of Question objects
        """
        questions = []
        question_number = 1
        global_line_number = 0

        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
            except Exception as e:
                # Log warning but continue with other pages
                print(f"Warning: Failed to extract text from page {page_num + 1}: {e}")
                continue

            lines = text.split("\n")

            for _line_num, line in enumerate(lines):
                global_line_number += 1

                processed_line = self._process_line(line)

                if processed_line is None:
                    continue

                if len(processed_line) < self.min_question_length:
                    continue

                question = Question(
                    number=question_number,
                    text=processed_line,
                    source_line=global_line_number,
                )
                questions.append(question)
                question_number += 1

        return questions

    def _process_line(self, line: str) -> Optional[str]:
        """Process a single line from the PDF.

        Args:
            line: Raw line text

        Returns:
            Processed line text, or None if line should be skipped
        """
        if self.strip_whitespace:
            line = line.strip()

        if self.skip_empty_lines and not line:
            return None

        # Only accept lines ending with '?'
        if not line.endswith('?'):
            return None

        return line

    def validate_pdf(self, pdf_path: Union[str, Path]) -> tuple[bool, Optional[str]]:
        """Validate a PDF file without fully parsing it.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Tuple of (is_valid, error_message)
            If valid: (True, None)
            If invalid: (False, "error description")
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            return False, f"File not found: {pdf_path}"

        if not pdf_path.is_file():
            return False, f"Path is not a file: {pdf_path}"

        if pdf_path.suffix.lower() != ".pdf":
            return False, f"File is not a PDF: {pdf_path.suffix}"

        try:
            reader = PdfReader(str(pdf_path))

            if len(reader.pages) == 0:
                return False, "PDF has no pages"

            # Try to extract text from first page
            first_page_text = reader.pages[0].extract_text()

            if not first_page_text or not first_page_text.strip():
                return False, "PDF appears to be empty or contains no text"

            return True, None

        except PdfReadError as e:
            return False, f"Invalid PDF format: {e}"
        except Exception as e:
            return False, f"Error validating PDF: {e}"
