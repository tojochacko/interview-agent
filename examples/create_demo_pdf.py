#!/usr/bin/env python3
"""Generate a sample job interview questionnaire PDF for the demo."""

from pathlib import Path

from fpdf import FPDF


def create_job_interview_questionnaire() -> None:
    """Create a realistic job interview questionnaire PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Job Interview Questionnaire", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Instructions
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(
        0,
        5,
        "Please answer the following questions during your interview. "
        "The interviewer will ask each question and record your response.",
    )
    pdf.ln(5)

    # Questions
    pdf.set_font("Helvetica", size=12)

    questions = [
        # Personal Information
        "What is your full name?",
        "What is your email address?",
        "What is your phone number?",
        "What is your current location?",
        # Professional Background
        "What is your current job title?",
        "What company do you currently work for?",
        "How many years of professional experience do you have?",
        "What is your highest level of education?",
        "What degree or certification did you earn?",
        # Technical Skills
        "What programming languages are you proficient in?",
        "What frameworks or libraries do you use regularly?",
        "What version control systems are you familiar with?",
        "Have you worked with cloud platforms like AWS or Azure?",
        "What development tools and IDEs do you prefer?",
        # Experience & Achievements
        "Describe your most significant professional achievement.",
        "Tell me about a challenging project you worked on recently.",
        "Have you ever led a team or mentored other developers?",
        "What open source projects have you contributed to?",
        # Work Preferences
        "What type of work environment do you prefer?",
        "Are you comfortable with remote work?",
        "What is your preferred work schedule?",
        "How do you handle tight deadlines and pressure?",
        # Career Goals
        "What are your career goals for the next two years?",
        "Why are you interested in this position?",
        "What attracted you to our company?",
        "What is your expected salary range?",
        # Availability
        "When are you available to start?",
        "Do you have any upcoming commitments we should know about?",
        # Closing
        "Do you have any questions for us?",
        "Is there anything else you would like us to know about you?",
    ]

    for question in questions:
        pdf.cell(0, 10, question, new_x="LMARGIN", new_y="NEXT")

    # Save PDF
    output_path = Path(__file__).parent / "job_interview_questionnaire.pdf"
    pdf.output(str(output_path))
    print(f"✅ Created: {output_path}")
    print(f"   Questions: {len(questions)}")


if __name__ == "__main__":
    create_job_interview_questionnaire()
