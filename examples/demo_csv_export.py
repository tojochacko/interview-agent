#!/usr/bin/env python3
"""Demo script for CSV export functionality.

This script demonstrates how to use the CSV exporter to save interview
transcripts to CSV files.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from conversation_agent.config import ExportConfig
from conversation_agent.core import export_interview
from conversation_agent.models import (
    ConversationTurn,
    InterviewSession,
    Question,
    Response,
)


def create_sample_session() -> InterviewSession:
    """Create a sample interview session with some turns."""
    session = InterviewSession(
        questionnaire_path="examples/sample_questionnaire.pdf",
        start_time=datetime.now(),
    )

    # Question 1: Name
    q1 = Question(number=1, text="What is your name?", source_line=1)
    r1 = Response(
        text="Alice Johnson",
        confidence=0.95,
        timestamp=datetime.now(),
        retry_count=0,
    )
    turn1 = ConversationTurn(question=q1, response=r1, duration_seconds=15.5)
    session.add_turn(turn1)

    # Question 2: Age
    q2 = Question(number=2, text="What is your age?", source_line=2)
    r2 = Response(
        text="28 years old",
        confidence=0.92,
        timestamp=datetime.now(),
        retry_count=0,
    )
    turn2 = ConversationTurn(question=q2, response=r2, duration_seconds=12.0)
    session.add_turn(turn2)

    # Question 3: Occupation (with clarification)
    q3 = Question(number=3, text="What is your occupation?", source_line=3)
    r3 = Response(
        text="Software Engineer",
        confidence=0.88,
        timestamp=datetime.now(),
        retry_count=1,
        clarification_requested=True,
    )
    turn3 = ConversationTurn(question=q3, response=r3, duration_seconds=20.0)
    session.add_turn(turn3)

    # Question 4: Skipped
    q4 = Question(number=4, text="What is your home address?", source_line=4)
    turn4 = ConversationTurn(question=q4, skipped=True, duration_seconds=5.0)
    session.add_turn(turn4)

    # Question 5: Hobbies
    q5 = Question(number=5, text="What are your hobbies?", source_line=5)
    r5 = Response(
        text="Reading, hiking, and coding",
        confidence=0.94,
        timestamp=datetime.now(),
        retry_count=0,
    )
    turn5 = ConversationTurn(question=q5, response=r5, duration_seconds=18.0)
    session.add_turn(turn5)

    session.mark_completed()
    return session


def main():
    """Run the demo."""
    print("CSV Export Demo")
    print("=" * 50)

    # Create sample session
    print("\n1. Creating sample interview session...")
    session = create_sample_session()
    print(f"   - Session ID: {session.id}")
    print(f"   - Total questions: {session.total_questions}")
    print(f"   - Answered: {session.answered_questions}")
    print(f"   - Skipped: {session.skipped_questions}")

    # Export with default settings
    print("\n2. Exporting with default settings...")
    config1 = ExportConfig(output_directory=Path("./demo_exports"))
    output_path1 = export_interview(session, config=config1)
    print(f"   - Exported to: {output_path1}")

    # Export without metadata
    print("\n3. Exporting without metadata...")
    config2 = ExportConfig(
        output_directory=Path("./demo_exports"),
        filename_format="interview_no_metadata_{timestamp}.csv",
        include_metadata=False,
    )
    output_path2 = export_interview(session, config=config2)
    print(f"   - Exported to: {output_path2}")

    # Export to custom path
    print("\n4. Exporting to custom path...")
    custom_path = Path("./demo_exports/custom_interview.csv")
    output_path3 = export_interview(session, output_path=custom_path)
    print(f"   - Exported to: {output_path3}")

    print("\n" + "=" * 50)
    print("Demo complete! Check the ./demo_exports directory.")
    print("\nTo view the CSV files:")
    print("  cat ./demo_exports/*.csv")


if __name__ == "__main__":
    main()
