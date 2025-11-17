"""Pydantic models for interview data structures."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Question(BaseModel):
    """Represents a single interview question.

    Attributes:
        id: Unique identifier for the question (auto-generated UUID)
        number: Sequential question number (1-indexed)
        text: The question text
        source_line: Original line number from PDF (for debugging)
    """

    id: UUID = Field(default_factory=uuid4)
    number: int = Field(ge=1, description="Question number (1-indexed)")
    text: str = Field(min_length=1, description="Question text")
    source_line: Optional[int] = Field(  # noqa: UP045
        default=None, description="Line number from source PDF"
    )

    model_config = ConfigDict(frozen=False)


class Response(BaseModel):
    """Represents a user's response to a question.

    Attributes:
        text: Transcribed response text
        confidence: Transcription confidence score (0.0 to 1.0)
        timestamp: When the response was captured
        retry_count: Number of attempts to capture this response
        clarification_requested: Whether user asked for clarification
    """

    text: str = Field(description="Transcribed response text")
    confidence: float = Field(
        ge=0.0, le=1.0, default=1.0, description="Transcription confidence"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    retry_count: int = Field(default=0, ge=0, description="Number of retries")
    clarification_requested: bool = Field(
        default=False, description="User requested clarification"
    )

    model_config = ConfigDict(frozen=False)


class ConversationTurn(BaseModel):
    """Represents a complete question-answer exchange.

    Attributes:
        question: The question that was asked
        response: The user's response (None if skipped/unanswered)
        duration_seconds: Time taken for this turn
        skipped: Whether this question was skipped
    """

    question: Question
    response: Optional[Response] = None  # noqa: UP045
    duration_seconds: float = Field(
        default=0.0, ge=0.0, description="Turn duration in seconds"
    )
    skipped: bool = Field(default=False, description="Question was skipped")

    model_config = ConfigDict(frozen=False)


class InterviewSession(BaseModel):
    """Represents a complete interview session.

    Attributes:
        id: Unique session identifier
        questionnaire_path: Path to the source PDF questionnaire
        turns: List of conversation turns in order
        start_time: When the interview started
        end_time: When the interview ended (None if in progress)
        completed: Whether the interview was completed
    """

    id: UUID = Field(default_factory=uuid4)
    questionnaire_path: str = Field(description="Path to source PDF")
    turns: list[ConversationTurn] = Field(
        default_factory=list, description="Conversation turns"
    )
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None  # noqa: UP045
    completed: bool = Field(default=False, description="Interview completed")

    model_config = ConfigDict(frozen=False)

    def add_turn(self, turn: ConversationTurn) -> None:
        """Add a conversation turn to the session.

        Args:
            turn: The conversation turn to add
        """
        self.turns.append(turn)

    def mark_completed(self) -> None:
        """Mark the interview session as completed."""
        self.completed = True
        self.end_time = datetime.now()

    @property
    def total_questions(self) -> int:
        """Get total number of questions in the session."""
        return len(self.turns)

    @property
    def answered_questions(self) -> int:
        """Get number of questions that were answered."""
        return sum(1 for turn in self.turns if turn.response and not turn.skipped)

    @property
    def skipped_questions(self) -> int:
        """Get number of questions that were skipped."""
        return sum(1 for turn in self.turns if turn.skipped)

    @property
    def total_duration_seconds(self) -> float:
        """Get total interview duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()
