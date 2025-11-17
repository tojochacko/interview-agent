#!/usr/bin/env python3
"""Demo script for Phase 1: PDF Parser and Data Models.

This script demonstrates:
1. PDF validation
2. Question extraction from PDFs
3. Working with Question and InterviewSession models
4. Error handling
"""

from pathlib import Path

from conversation_agent.core import PDFParseError, PDFQuestionParser
from conversation_agent.models import ConversationTurn, InterviewSession, Question, Response


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_pdf_validation() -> None:
    """Demonstrate PDF validation."""
    print_section("1. PDF Validation")

    parser = PDFQuestionParser()
    test_pdfs = [
        ("Sample Questionnaire", "examples/job_interview_questionnaire.pdf"),
        ("Non-existent File", "examples/does_not_exist.pdf"),
        ("Directory (invalid)", "examples/"),
    ]

    for name, path in test_pdfs:
        is_valid, error = parser.validate_pdf(path)
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"{status} - {name}")
        if error:
            print(f"  Error: {error}")
        print()


def demo_question_parsing() -> None:
    """Demonstrate parsing questions from PDF."""
    print_section("2. Parsing Questions from PDF")

    parser = PDFQuestionParser(min_question_length=5)
    pdf_path = "examples/job_interview_questionnaire.pdf"

    try:
        questions = parser.parse(pdf_path)
        print(f"✅ Successfully parsed {len(questions)} questions from PDF\n")

        # Display first 5 questions
        print("First 5 questions:")
        for q in questions[:5]:
            print(f"\n  Q{q.number}. {q.text}")
            print(f"     ID: {q.id}")
            print(f"     Source Line: {q.source_line}")

        if len(questions) > 5:
            print(f"\n  ... and {len(questions) - 5} more questions")

    except PDFParseError as e:
        print(f"❌ Failed to parse PDF: {e}")
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")


def demo_question_model() -> None:
    """Demonstrate Question model features."""
    print_section("3. Working with Question Model")

    # Create questions manually
    q1 = Question(number=1, text="What is your name?", source_line=1)
    q2 = Question(number=2, text="What is your email address?", source_line=2)

    print("Created two Question objects:")
    print(f"  Q1: {q1.text}")
    print(f"      ID: {q1.id}")
    print(f"  Q2: {q2.text}")
    print(f"      ID: {q2.id}")

    print("\n✅ Each question has a unique UUID")
    print(f"  Q1 ID != Q2 ID: {q1.id != q2.id}")

    # Demonstrate validation
    print("\nQuestion Model Validation:")
    try:
        invalid_q = Question(number=0, text="Invalid")  # number must be >= 1
        print("  ❌ Should not reach here")
    except ValueError as e:
        print(f"  ✅ Validation caught invalid number: {e}")

    try:
        invalid_q = Question(number=1, text="")  # text cannot be empty
        print("  ❌ Should not reach here")
    except ValueError as e:
        print(f"  ✅ Validation caught empty text: {e}")


def demo_response_model() -> None:
    """Demonstrate Response model features."""
    print_section("4. Working with Response Model")

    # Create sample responses
    response1 = Response(
        text="John Smith",
        confidence=0.95,
        retry_count=0,
        clarification_requested=False,
    )

    response2 = Response(
        text="john.smith@email.com",
        confidence=0.82,
        retry_count=1,
        clarification_requested=True,
    )

    print("Response 1:")
    print(f"  Text: {response1.text}")
    print(f"  Confidence: {response1.confidence:.0%}")
    print(f"  Timestamp: {response1.timestamp}")
    print(f"  Retries: {response1.retry_count}")
    print(f"  Clarification: {response1.clarification_requested}")

    print("\nResponse 2:")
    print(f"  Text: {response2.text}")
    print(f"  Confidence: {response2.confidence:.0%}")
    print(f"  Timestamp: {response2.timestamp}")
    print(f"  Retries: {response2.retry_count}")
    print(f"  Clarification: {response2.clarification_requested}")


def demo_interview_session() -> None:
    """Demonstrate InterviewSession with conversation turns."""
    print_section("5. Building an Interview Session")

    # Create a mock interview session
    session = InterviewSession(questionnaire_path="examples/job_interview_questionnaire.pdf")

    print(f"Created Interview Session:")
    print(f"  ID: {session.id}")
    print(f"  Started: {session.start_time}")
    print(f"  Questionnaire: {session.questionnaire_path}")
    print(f"  Completed: {session.completed}")

    # Add some conversation turns
    print("\nAdding conversation turns...\n")

    # Turn 1: Question answered
    q1 = Question(number=1, text="What is your full name?")
    r1 = Response(text="Alice Johnson", confidence=0.98)
    turn1 = ConversationTurn(question=q1, response=r1, duration_seconds=3.5)
    session.add_turn(turn1)
    print(f"  ✅ Turn 1: Answered in {turn1.duration_seconds}s")

    # Turn 2: Question answered after retry
    q2 = Question(number=2, text="What is your email address?")
    r2 = Response(text="alice.johnson@email.com", confidence=0.85, retry_count=1)
    turn2 = ConversationTurn(question=q2, response=r2, duration_seconds=5.2)
    session.add_turn(turn2)
    print(f"  ✅ Turn 2: Answered in {turn2.duration_seconds}s (1 retry)")

    # Turn 3: Question skipped
    q3 = Question(number=3, text="What is your current salary?")
    turn3 = ConversationTurn(question=q3, response=None, skipped=True, duration_seconds=2.0)
    session.add_turn(turn3)
    print(f"  ⏭️  Turn 3: Skipped")

    # Turn 4: Question answered
    q4 = Question(number=4, text="How many years of experience do you have?")
    r4 = Response(text="Five years", confidence=0.92)
    turn4 = ConversationTurn(question=q4, response=r4, duration_seconds=4.1)
    session.add_turn(turn4)
    print(f"  ✅ Turn 4: Answered in {turn4.duration_seconds}s")

    # Mark session as completed
    session.mark_completed()

    # Display session statistics
    print(f"\n📊 Interview Session Statistics:")
    print(f"  Total Questions: {session.total_questions}")
    print(f"  Answered: {session.answered_questions}")
    print(f"  Skipped: {session.skipped_questions}")
    print(f"  Total Duration: {session.total_duration_seconds:.1f}s")
    print(f"  Completed: {session.completed}")
    print(f"  End Time: {session.end_time}")


def demo_error_handling() -> None:
    """Demonstrate error handling."""
    print_section("6. Error Handling")

    parser = PDFQuestionParser()

    # Test 1: Non-existent file
    print("Test 1: Non-existent file")
    try:
        parser.parse("does_not_exist.pdf")
        print("  ❌ Should have raised FileNotFoundError")
    except FileNotFoundError as e:
        print(f"  ✅ Caught FileNotFoundError: {e}")

    # Test 2: Directory instead of file
    print("\nTest 2: Directory path")
    try:
        parser.parse("examples/")
        print("  ❌ Should have raised PDFParseError")
    except PDFParseError as e:
        print(f"  ✅ Caught PDFParseError: {e}")

    # Test 3: Empty PDF (if it exists)
    empty_pdf = Path("tests/fixtures/empty_questionnaire.pdf")
    if empty_pdf.exists():
        print("\nTest 3: Empty PDF")
        try:
            parser.parse(empty_pdf)
            print("  ❌ Should have raised PDFParseError")
        except PDFParseError as e:
            print(f"  ✅ Caught PDFParseError: {e}")


def demo_parser_configuration() -> None:
    """Demonstrate parser configuration options."""
    print_section("7. Parser Configuration Options")

    # Test different configurations
    configs = [
        {
            "name": "Default Config",
            "parser": PDFQuestionParser(),
        },
        {
            "name": "Strict (min 20 chars)",
            "parser": PDFQuestionParser(min_question_length=20),
        },
        {
            "name": "Lenient (min 3 chars)",
            "parser": PDFQuestionParser(min_question_length=3),
        },
        {
            "name": "No whitespace stripping",
            "parser": PDFQuestionParser(strip_whitespace=False),
        },
    ]

    test_pdf = Path("tests/fixtures/malformed_questionnaire.pdf")
    if not test_pdf.exists():
        print("⚠️  Test PDF not found, skipping configuration demo")
        return

    for config in configs:
        try:
            questions = config["parser"].parse(test_pdf)
            print(f"{config['name']}:")
            print(f"  Extracted {len(questions)} questions")
            if questions:
                print(f"  First question: {questions[0].text[:50]}...")
        except PDFParseError as e:
            print(f"{config['name']}:")
            print(f"  ❌ Failed: {e}")
        print()


def main() -> None:
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  PHASE 1 DEMO: PDF Parser & Data Models")
    print("  Voice Interview Agent - Conversation Agent v11")
    print("=" * 70)

    demo_pdf_validation()
    demo_question_parsing()
    demo_question_model()
    demo_response_model()
    demo_interview_session()
    demo_error_handling()
    demo_parser_configuration()

    print_section("Demo Complete!")
    print("Phase 1 components are working correctly. ✅")
    print("\nNext Phase: TTS Integration (pyttsx3)")
    print()


if __name__ == "__main__":
    main()
