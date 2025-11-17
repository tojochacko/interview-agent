"""Generate test PDF files for unit testing."""

from pathlib import Path

from fpdf import FPDF


def create_sample_questionnaire(output_path: Path) -> None:
    """Create a sample questionnaire PDF with valid questions.

    Args:
        output_path: Path where the PDF should be saved
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    questions = [
        "What is your full name?",
        "What is your email address?",
        "What is your current job title?",
        "How many years of experience do you have?",
        "What programming languages are you proficient in?",
        "What is your preferred work environment?",
        "Are you available to start immediately?",
        "What are your salary expectations?",
        "Do you have any questions for us?",
        "How did you hear about this position?",
    ]

    for question in questions:
        pdf.cell(0, 10, question, ln=True)

    pdf.output(str(output_path))


def create_empty_pdf(output_path: Path) -> None:
    """Create an empty PDF with no text.

    Args:
        output_path: Path where the PDF should be saved
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.output(str(output_path))


def create_malformed_questionnaire(output_path: Path) -> None:
    """Create a questionnaire with various edge cases.

    Args:
        output_path: Path where the PDF should be saved
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Mix of valid questions, empty lines, and short text
    lines = [
        "What is your name?",
        "",  # Empty line
        "Age?",  # Very short (should be filtered by min_length)
        "   ",  # Whitespace only
        "What is your current position and what are your main responsibilities?",
        "",
        "Why do you want to work here?",
        "   What are your strengths?   ",  # Leading/trailing whitespace
    ]

    for line in lines:
        if line or line == "":  # Include empty lines
            pdf.cell(0, 10, line, ln=True)

    pdf.output(str(output_path))


def create_multipage_questionnaire(output_path: Path) -> None:
    """Create a multi-page questionnaire.

    Args:
        output_path: Path where the PDF should be saved
    """
    pdf = FPDF()

    # Page 1
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "What is your educational background?", ln=True)
    pdf.cell(0, 10, "What certifications do you hold?", ln=True)
    pdf.cell(0, 10, "What is your greatest professional achievement?", ln=True)

    # Page 2
    pdf.add_page()
    pdf.cell(0, 10, "Describe a challenging project you worked on.", ln=True)
    pdf.cell(0, 10, "How do you handle tight deadlines?", ln=True)
    pdf.cell(0, 10, "What are your career goals for the next five years?", ln=True)

    pdf.output(str(output_path))


if __name__ == "__main__":
    fixtures_dir = Path(__file__).parent

    create_sample_questionnaire(fixtures_dir / "sample_questionnaire.pdf")
    create_empty_pdf(fixtures_dir / "empty_questionnaire.pdf")
    create_malformed_questionnaire(fixtures_dir / "malformed_questionnaire.pdf")
    create_multipage_questionnaire(fixtures_dir / "multipage_questionnaire.pdf")

    print("Test PDF files generated successfully!")
