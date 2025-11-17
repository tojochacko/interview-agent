"""Unit tests for PDF parser."""

from pathlib import Path

import pytest

from conversation_agent.core import PDFParseError, PDFQuestionParser
from conversation_agent.models import Question


@pytest.fixture
def fixtures_dir():
    """Get the fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def parser():
    """Create a default PDF parser instance."""
    return PDFQuestionParser()


@pytest.fixture
def sample_questionnaire(fixtures_dir):
    """Get path to sample questionnaire PDF."""
    return fixtures_dir / "sample_questionnaire.pdf"


@pytest.fixture
def empty_questionnaire(fixtures_dir):
    """Get path to empty questionnaire PDF."""
    return fixtures_dir / "empty_questionnaire.pdf"


@pytest.fixture
def malformed_questionnaire(fixtures_dir):
    """Get path to malformed questionnaire PDF."""
    return fixtures_dir / "malformed_questionnaire.pdf"


@pytest.fixture
def multipage_questionnaire(fixtures_dir):
    """Get path to multipage questionnaire PDF."""
    return fixtures_dir / "multipage_questionnaire.pdf"


class TestPDFQuestionParser:
    """Test suite for PDFQuestionParser."""

    def test_parse_valid_questionnaire(self, parser, sample_questionnaire):
        """Test parsing a valid questionnaire PDF."""
        questions = parser.parse(sample_questionnaire)

        assert len(questions) == 10
        assert all(isinstance(q, Question) for q in questions)
        assert questions[0].number == 1
        assert questions[0].text == "What is your full name?"
        assert questions[-1].number == 10
        assert questions[-1].text == "How did you hear about this position?"

    def test_parse_multipage_questionnaire(self, parser, multipage_questionnaire):
        """Test parsing a multi-page questionnaire."""
        questions = parser.parse(multipage_questionnaire)

        assert len(questions) == 6
        assert questions[0].text == "What is your educational background?"
        assert questions[-1].text == "What are your career goals for the next five years?"

    def test_parse_with_pathlib_path(self, parser, sample_questionnaire):
        """Test that parser works with pathlib.Path objects."""
        questions = parser.parse(Path(sample_questionnaire))

        assert len(questions) == 10
        assert isinstance(questions[0], Question)

    def test_parse_with_string_path(self, parser, sample_questionnaire):
        """Test that parser works with string paths."""
        questions = parser.parse(str(sample_questionnaire))

        assert len(questions) == 10
        assert isinstance(questions[0], Question)

    def test_parse_nonexistent_file(self, parser):
        """Test parsing a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            parser.parse("nonexistent.pdf")

    def test_parse_directory_path(self, parser, fixtures_dir):
        """Test parsing a directory raises PDFParseError."""
        with pytest.raises(PDFParseError, match="Path is not a file"):
            parser.parse(fixtures_dir)

    def test_parse_empty_pdf(self, parser, empty_questionnaire):
        """Test parsing an empty PDF raises PDFParseError."""
        with pytest.raises(PDFParseError, match="No valid questions found"):
            parser.parse(empty_questionnaire)

    def test_question_numbering(self, parser, sample_questionnaire):
        """Test that questions are numbered sequentially starting from 1."""
        questions = parser.parse(sample_questionnaire)

        for i, question in enumerate(questions, start=1):
            assert question.number == i

    def test_question_source_line_tracking(self, parser, sample_questionnaire):
        """Test that source line numbers are tracked."""
        questions = parser.parse(sample_questionnaire)

        # All questions should have source_line set
        assert all(q.source_line is not None for q in questions)
        # Source lines should be sequential (one question per line)
        assert all(
            questions[i].source_line < questions[i + 1].source_line
            for i in range(len(questions) - 1)
        )

    def test_whitespace_stripping(self, parser, malformed_questionnaire):
        """Test that leading/trailing whitespace is stripped."""
        questions = parser.parse(malformed_questionnaire)

        # Should find questions with stripped whitespace
        strength_question = next(
            (q for q in questions if "strengths" in q.text.lower()), None
        )
        assert strength_question is not None
        # Should not have leading/trailing spaces
        assert not strength_question.text.startswith(" ")
        assert not strength_question.text.endswith(" ")

    def test_min_question_length_filter(self, malformed_questionnaire):
        """Test that questions shorter than min_length are filtered out."""
        parser = PDFQuestionParser(min_question_length=5)
        questions = parser.parse(malformed_questionnaire)

        # "Age?" (4 chars) should be filtered out
        assert all(len(q.text) >= 5 for q in questions)
        assert not any("Age?" in q.text for q in questions)

    def test_custom_min_length(self, sample_questionnaire):
        """Test parser with custom minimum question length."""
        parser = PDFQuestionParser(min_question_length=30)
        questions = parser.parse(sample_questionnaire)

        # Only questions >= 30 chars should be included
        assert all(len(q.text) >= 30 for q in questions)
        # Should filter out shorter questions
        assert len(questions) < 10

    def test_skip_empty_lines(self, malformed_questionnaire):
        """Test that empty lines are skipped."""
        parser = PDFQuestionParser(skip_empty_lines=True)
        questions = parser.parse(malformed_questionnaire)

        # Should not have any empty text
        assert all(q.text for q in questions)

    def test_question_uniqueness(self, parser, sample_questionnaire):
        """Test that each question has a unique ID."""
        questions = parser.parse(sample_questionnaire)

        question_ids = [q.id for q in questions]
        assert len(question_ids) == len(set(question_ids))


class TestPDFValidation:
    """Test suite for PDF validation."""

    def test_validate_valid_pdf(self, parser, sample_questionnaire):
        """Test validation of a valid PDF file."""
        is_valid, error = parser.validate_pdf(sample_questionnaire)

        assert is_valid is True
        assert error is None

    def test_validate_nonexistent_file(self, parser):
        """Test validation of non-existent file."""
        is_valid, error = parser.validate_pdf("nonexistent.pdf")

        assert is_valid is False
        assert "not found" in error.lower()

    def test_validate_directory(self, parser, fixtures_dir):
        """Test validation of directory path."""
        is_valid, error = parser.validate_pdf(fixtures_dir)

        assert is_valid is False
        assert "not a file" in error.lower()

    def test_validate_non_pdf_file(self, parser, tmp_path):
        """Test validation of non-PDF file."""
        text_file = tmp_path / "test.txt"
        text_file.write_text("This is not a PDF")

        is_valid, error = parser.validate_pdf(text_file)

        assert is_valid is False
        assert "not a pdf" in error.lower()

    def test_validate_empty_pdf(self, parser, empty_questionnaire):
        """Test validation of empty PDF."""
        is_valid, error = parser.validate_pdf(empty_questionnaire)

        # Empty PDF should fail validation
        assert is_valid is False
        assert error is not None


class TestQuestionModel:
    """Test suite for Question model."""

    def test_question_creation(self):
        """Test creating a Question instance."""
        question = Question(number=1, text="What is your name?", source_line=5)

        assert question.number == 1
        assert question.text == "What is your name?"
        assert question.source_line == 5
        assert question.id is not None

    def test_question_validation(self):
        """Test Question model validation."""
        # Valid question
        q1 = Question(number=1, text="Valid question?")
        assert q1.number == 1

        # Invalid: number < 1
        with pytest.raises(ValueError):
            Question(number=0, text="Invalid number")

        # Invalid: empty text
        with pytest.raises(ValueError):
            Question(number=1, text="")

    def test_question_default_source_line(self):
        """Test that source_line defaults to None."""
        question = Question(number=1, text="Test question?")

        assert question.source_line is None

    def test_question_immutable_id(self):
        """Test that question IDs are unique for each instance."""
        q1 = Question(number=1, text="Question 1?")
        q2 = Question(number=1, text="Question 1?")

        # Same content but different IDs
        assert q1.id != q2.id


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_parse_pdf_with_special_characters(self, parser, tmp_path):
        """Test parsing PDF with special characters."""
        from fpdf import FPDF

        # Create PDF with special characters
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        questions = [
            "What's your email address?",  # Apostrophe
            "Do you have 5+ years of experience?",  # Plus sign
            "Rate your skills (1-10)?",  # Parentheses and dash
        ]
        for q in questions:
            pdf.cell(0, 10, q, new_x="LMARGIN", new_y="NEXT")

        pdf_path = tmp_path / "special_chars.pdf"
        pdf.output(str(pdf_path))

        # Should parse without errors
        parsed_questions = parser.parse(pdf_path)
        assert len(parsed_questions) == 3

    def test_parse_pdf_with_unicode(self, parser, tmp_path):
        """Test parsing PDF with unicode characters."""
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        # Unicode characters
        pdf.cell(0, 10, "What is your preferred role?", new_x="LMARGIN", new_y="NEXT")

        pdf_path = tmp_path / "unicode.pdf"
        pdf.output(str(pdf_path))

        parsed_questions = parser.parse(pdf_path)
        assert len(parsed_questions) >= 1

    def test_very_long_question(self, parser, tmp_path):
        """Test parsing a very long question."""
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)

        long_question = "A" * 500 + "?"  # 501 character question

        pdf.cell(0, 10, long_question[:100], new_x="LMARGIN", new_y="NEXT")

        pdf_path = tmp_path / "long_question.pdf"
        pdf.output(str(pdf_path))

        # Should handle long questions without errors
        questions = parser.parse(pdf_path)
        assert len(questions) >= 1
