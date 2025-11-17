"""Tests for CSV exporter functionality."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import pytest

from conversation_agent.config import ExportConfig
from conversation_agent.core import CSVExporter, export_interview
from conversation_agent.models import (
    ConversationTurn,
    InterviewSession,
    Question,
    Response,
)


@pytest.fixture
def sample_session() -> InterviewSession:
    """Create a sample interview session for testing."""
    session = InterviewSession(
        questionnaire_path="/tmp/test_questionnaire.pdf",
        start_time=datetime(2025, 1, 1, 10, 0, 0),
    )

    # Add some conversation turns
    q1 = Question(number=1, text="What is your name?", source_line=1)
    r1 = Response(
        text="John Doe",
        confidence=0.95,
        timestamp=datetime(2025, 1, 1, 10, 0, 10),
        retry_count=0,
    )
    turn1 = ConversationTurn(question=q1, response=r1, duration_seconds=15.5)
    session.add_turn(turn1)

    q2 = Question(number=2, text="What is your age?", source_line=2)
    r2 = Response(
        text="30 years old",
        confidence=0.88,
        timestamp=datetime(2025, 1, 1, 10, 0, 30),
        retry_count=1,
        clarification_requested=True,
    )
    turn2 = ConversationTurn(question=q2, response=r2, duration_seconds=20.0)
    session.add_turn(turn2)

    # Add a skipped question
    q3 = Question(number=3, text="What is your address?", source_line=3)
    turn3 = ConversationTurn(question=q3, skipped=True, duration_seconds=5.0)
    session.add_turn(turn3)

    session.mark_completed()
    return session


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output_dir = tmp_path / "exports"
    output_dir.mkdir()
    return output_dir


class TestExportConfig:
    """Tests for ExportConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ExportConfig()

        assert config.output_directory == Path("./interview_transcripts")
        assert config.filename_format == "interview_{timestamp}.csv"
        assert config.include_metadata is True
        assert config.csv_encoding == "utf-8"

    def test_custom_config(self, temp_output_dir: Path):
        """Test custom configuration values."""
        config = ExportConfig(
            output_directory=temp_output_dir,
            filename_format="custom_{session_id}.csv",
            include_metadata=False,
            csv_encoding="utf-16",
        )

        assert config.output_directory == temp_output_dir
        assert config.filename_format == "custom_{session_id}.csv"
        assert config.include_metadata is False
        assert config.csv_encoding == "utf-16"


class TestCSVExporter:
    """Tests for CSVExporter."""

    def test_init_default_config(self):
        """Test initialization with default config."""
        exporter = CSVExporter()
        assert isinstance(exporter.config, ExportConfig)

    def test_init_custom_config(self, temp_output_dir: Path):
        """Test initialization with custom config."""
        config = ExportConfig(output_directory=temp_output_dir)
        exporter = CSVExporter(config=config)
        assert exporter.config.output_directory == temp_output_dir

    def test_export_session_basic(
        self, sample_session: InterviewSession, temp_output_dir: Path
    ):
        """Test basic session export."""
        config = ExportConfig(output_directory=temp_output_dir)
        exporter = CSVExporter(config=config)

        output_path = exporter.export_session(sample_session)

        # Verify file was created
        assert output_path.exists()
        assert output_path.parent == temp_output_dir
        assert output_path.suffix == ".csv"

    def test_export_session_custom_path(
        self, sample_session: InterviewSession, temp_output_dir: Path
    ):
        """Test export with custom output path."""
        exporter = CSVExporter()
        custom_path = temp_output_dir / "custom_export.csv"

        output_path = exporter.export_session(sample_session, output_path=custom_path)

        assert output_path == custom_path
        assert output_path.exists()

    def test_export_creates_directory(
        self, sample_session: InterviewSession, temp_output_dir: Path
    ):
        """Test that export creates output directory if it doesn't exist."""
        nested_dir = temp_output_dir / "nested" / "path"
        config = ExportConfig(output_directory=nested_dir)
        exporter = CSVExporter(config=config)

        output_path = exporter.export_session(sample_session)

        assert nested_dir.exists()
        assert output_path.exists()

    def test_csv_content_with_metadata(
        self, sample_session: InterviewSession, temp_output_dir: Path
    ):
        """Test CSV content includes metadata."""
        config = ExportConfig(output_directory=temp_output_dir, include_metadata=True)
        exporter = CSVExporter(config=config)

        output_path = exporter.export_session(sample_session)

        # Read and verify CSV content
        with open(output_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Verify header
        assert "question_number" in rows[0]
        assert "question_id" in rows[0]
        assert "question_text" in rows[0]
        assert "response_text" in rows[0]
        assert "timestamp" in rows[0]
        assert "confidence" in rows[0]
        assert "retry_count" in rows[0]
        assert "clarification_requested" in rows[0]
        assert "skipped" in rows[0]
        assert "duration_seconds" in rows[0]

        # Verify first row content
        assert rows[0]["question_number"] == "1"
        assert rows[0]["question_text"] == "What is your name?"
        assert rows[0]["response_text"] == "John Doe"
        assert rows[0]["confidence"] == "0.95"
        assert rows[0]["retry_count"] == "0"
        assert rows[0]["clarification_requested"] == "False"
        assert rows[0]["skipped"] == "False"
        assert rows[0]["duration_seconds"] == "15.5"

        # Verify second row content
        assert rows[1]["question_number"] == "2"
        assert rows[1]["retry_count"] == "1"
        assert rows[1]["clarification_requested"] == "True"

        # Verify skipped question
        assert rows[2]["question_number"] == "3"
        assert rows[2]["response_text"] == ""
        assert rows[2]["skipped"] == "True"

    def test_csv_content_without_metadata(
        self, sample_session: InterviewSession, temp_output_dir: Path
    ):
        """Test CSV content without metadata."""
        config = ExportConfig(output_directory=temp_output_dir, include_metadata=False)
        exporter = CSVExporter(config=config)

        output_path = exporter.export_session(sample_session)

        # Read and verify CSV content
        with open(output_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Verify header (should not have metadata columns)
        assert "question_number" in rows[0]
        assert "question_text" in rows[0]
        assert "response_text" in rows[0]
        assert "timestamp" in rows[0]
        assert "confidence" not in rows[0]
        assert "retry_count" not in rows[0]
        assert "clarification_requested" not in rows[0]

    def test_filename_generation_with_timestamp(
        self, sample_session: InterviewSession, temp_output_dir: Path
    ):
        """Test filename generation includes timestamp."""
        config = ExportConfig(
            output_directory=temp_output_dir,
            filename_format="interview_{timestamp}.csv",
        )
        exporter = CSVExporter(config=config)

        output_path = exporter.export_session(sample_session)

        # Verify filename contains timestamp
        assert "interview_20250101_100000.csv" in output_path.name

    def test_filename_generation_with_session_id(
        self, sample_session: InterviewSession, temp_output_dir: Path
    ):
        """Test filename generation includes session ID."""
        config = ExportConfig(
            output_directory=temp_output_dir, filename_format="{session_id}.csv"
        )
        exporter = CSVExporter(config=config)

        output_path = exporter.export_session(sample_session)

        # Verify filename contains session ID
        assert str(sample_session.id) in output_path.name

    def test_csv_encoding_utf8(
        self, sample_session: InterviewSession, temp_output_dir: Path
    ):
        """Test CSV export with UTF-8 encoding."""
        # Add a question with unicode characters
        q_unicode = Question(number=4, text="¿Cómo estás?", source_line=4)
        r_unicode = Response(text="Très bien, merci!", confidence=0.9)
        turn_unicode = ConversationTurn(
            question=q_unicode, response=r_unicode, duration_seconds=10.0
        )
        sample_session.add_turn(turn_unicode)

        config = ExportConfig(output_directory=temp_output_dir, csv_encoding="utf-8")
        exporter = CSVExporter(config=config)

        output_path = exporter.export_session(sample_session)

        # Read and verify unicode content
        with open(output_path, encoding="utf-8") as f:
            content = f.read()

        assert "¿Cómo estás?" in content
        assert "Très bien, merci!" in content

    def test_empty_session(self, temp_output_dir: Path):
        """Test export of session with no turns."""
        session = InterviewSession(
            questionnaire_path="/tmp/empty.pdf",
            start_time=datetime.now(),
        )
        session.mark_completed()

        config = ExportConfig(output_directory=temp_output_dir)
        exporter = CSVExporter(config=config)

        output_path = exporter.export_session(session)

        # Verify file exists with header only
        with open(output_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert len(rows) == 1  # Header only
        assert "question_number" in rows[0][0]


class TestExportInterview:
    """Tests for export_interview convenience function."""

    def test_export_interview_default(
        self, sample_session: InterviewSession, temp_output_dir: Path
    ):
        """Test export_interview with default config."""
        config = ExportConfig(output_directory=temp_output_dir)
        output_path = export_interview(sample_session, config=config)

        assert output_path.exists()

    def test_export_interview_custom_path(
        self, sample_session: InterviewSession, temp_output_dir: Path
    ):
        """Test export_interview with custom path."""
        custom_path = temp_output_dir / "custom.csv"
        output_path = export_interview(sample_session, output_path=custom_path)

        assert output_path == custom_path
        assert output_path.exists()

    def test_export_interview_custom_config(
        self, sample_session: InterviewSession, temp_output_dir: Path
    ):
        """Test export_interview with custom config."""
        config = ExportConfig(
            output_directory=temp_output_dir, include_metadata=False
        )
        output_path = export_interview(sample_session, config=config)

        # Verify metadata is not included
        with open(output_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert "confidence" not in rows[0]
