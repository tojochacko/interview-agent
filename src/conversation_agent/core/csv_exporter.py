"""CSV export functionality for interview transcripts."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from conversation_agent.config import ExportConfig
from conversation_agent.models import ConversationTurn, InterviewSession


class CSVExporter:
    """Exports interview sessions to CSV format.

    Attributes:
        config: Export configuration settings
    """

    def __init__(self, config: Optional[ExportConfig] = None):  # noqa: UP045
        """Initialize the CSV exporter.

        Args:
            config: Export configuration (uses defaults if not provided)
        """
        self.config = config or ExportConfig()

    def export_session(
        self, session: InterviewSession, output_path: Optional[Path] = None  # noqa: UP045
    ) -> Path:
        """Export an interview session to CSV.

        Args:
            session: The interview session to export
            output_path: Optional custom output path (overrides config)

        Returns:
            Path to the created CSV file

        Raises:
            OSError: If file cannot be written
        """
        # Determine output path
        if output_path is None:
            output_path = self._generate_output_path(session)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write CSV
        with open(output_path, "w", newline="", encoding=self.config.csv_encoding) as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(self._get_header())

            # Write data rows
            for turn in session.turns:
                writer.writerow(self._turn_to_row(turn, session))

        return output_path

    def _generate_output_path(self, session: InterviewSession) -> Path:
        """Generate output file path based on configuration.

        Args:
            session: The interview session

        Returns:
            Generated file path
        """
        # Format timestamp for filename
        timestamp = session.start_time.strftime("%Y%m%d_%H%M%S")

        # Format filename
        filename = self.config.filename_format.format(
            timestamp=timestamp, session_id=str(session.id)
        )

        return self.config.output_directory / filename

    def _get_header(self) -> list[str]:
        """Get CSV header row.

        Returns:
            List of column names
        """
        header = [
            "question_number",
            "question_id",
            "question_text",
            "response_text",
            "timestamp",
        ]

        if self.config.include_metadata:
            header.extend(
                [
                    "confidence",
                    "retry_count",
                    "clarification_requested",
                    "skipped",
                    "duration_seconds",
                ]
            )

        return header

    def _turn_to_row(
        self, turn: ConversationTurn, session: InterviewSession
    ) -> list[str]:
        """Convert a conversation turn to a CSV row.

        Args:
            turn: The conversation turn
            session: The parent session (for context)

        Returns:
            List of values for CSV row
        """
        # Basic fields
        row = [
            str(turn.question.number),
            str(turn.question.id),
            turn.question.text,
            turn.response.text if turn.response else "",
            turn.response.timestamp.isoformat() if turn.response else "",
        ]

        # Metadata fields
        if self.config.include_metadata:
            row.extend(
                [
                    str(turn.response.confidence) if turn.response else "",
                    str(turn.response.retry_count) if turn.response else "0",
                    str(turn.response.clarification_requested)
                    if turn.response
                    else "False",
                    str(turn.skipped),
                    str(turn.duration_seconds),
                ]
            )

        return row


def export_interview(
    session: InterviewSession,
    output_path: Optional[Path] = None,  # noqa: UP045
    config: Optional[ExportConfig] = None,  # noqa: UP045
) -> Path:
    """Convenience function to export an interview session.

    Args:
        session: The interview session to export
        output_path: Optional custom output path
        config: Optional export configuration

    Returns:
        Path to the created CSV file

    Raises:
        OSError: If file cannot be written
    """
    exporter = CSVExporter(config=config)
    return exporter.export_session(session, output_path)
