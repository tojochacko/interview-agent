"""Interview orchestrator for managing conversation flow."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from conversation_agent.core.conversation_state import (
    ConversationState,
    ConversationStateMachine,
    UserIntent,
)
from conversation_agent.core.intent_recognizer import IntentRecognizer
from conversation_agent.core.pdf_parser import PDFQuestionParser
from conversation_agent.models.interview import (
    ConversationTurn,
    InterviewSession,
    Question,
    Response,
)
from conversation_agent.providers.stt.base import STTProvider
from conversation_agent.providers.tts.base import TTSProvider


class InterviewOrchestrator:
    """Orchestrates the interview conversation flow.

    Manages the complete interview lifecycle from greeting to closing,
    coordinating TTS, STT, state machine, and intent recognition.

    Attributes:
        tts: Text-to-speech provider
        stt: Speech-to-text provider
        state_machine: Conversation state manager
        intent_recognizer: User intent recognizer
        session: Current interview session
        questions: List of questions to ask
        current_question_index: Index of current question
        enable_confirmation: Whether to confirm answers
        max_retries: Maximum retry attempts per question
    """

    DEFAULT_GREETING = (
        "Hello! I'm your interview assistant. "
        "I'll ask you some questions from the questionnaire. "
        "You can ask me to repeat or clarify at any time. "
        "Are you ready to begin?"
    )

    DEFAULT_CLOSING = (
        "Thank you for your time! Your responses have been recorded."
    )

    def __init__(
        self,
        tts_provider: TTSProvider,
        stt_provider: STTProvider,
        pdf_path: str,
        enable_confirmation: bool = True,
        max_retries: int = 3,
        greeting: Optional[str] = None,  # noqa: UP045
        closing: Optional[str] = None,  # noqa: UP045
    ):
        """Initialize interview orchestrator.

        Args:
            tts_provider: Text-to-speech provider
            stt_provider: Speech-to-text provider
            pdf_path: Path to questionnaire PDF
            enable_confirmation: Enable answer confirmation (default: True)
            max_retries: Max retry attempts per question (default: 3)
            greeting: Custom greeting message
            closing: Custom closing message

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If max_retries < 1
        """
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")

        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        self.tts = tts_provider
        self.stt = stt_provider
        self.state_machine = ConversationStateMachine()
        self.intent_recognizer = IntentRecognizer()

        # Load questions from PDF
        parser = PDFQuestionParser()
        self.questions = parser.parse(pdf_path)

        if not self.questions:
            raise ValueError(f"No questions found in PDF: {pdf_path}")

        # Initialize session
        self.session = InterviewSession(questionnaire_path=pdf_path)

        # Configuration
        self.enable_confirmation = enable_confirmation
        self.max_retries = max_retries
        self.greeting = greeting or self.DEFAULT_GREETING
        self.closing = closing or self.DEFAULT_CLOSING

        # State tracking
        self.current_question_index = 0
        self.current_question: Optional[Question] = None  # noqa: UP045
        self.current_response_text: Optional[str] = None  # noqa: UP045
        self.retry_count = 0

    def run(self) -> InterviewSession:
        """Run the complete interview.

        Returns:
            Completed InterviewSession with all turns

        Raises:
            Exception: If critical error occurs during interview
        """
        try:
            # Start interview
            self.state_machine.transition_to(ConversationState.GREETING)
            self._handle_greeting()

            # Process questions
            self.state_machine.transition_to(ConversationState.QUESTIONING)
            while self.current_question_index < len(self.questions):
                self._process_question()

            # Close interview
            self.state_machine.transition_to(ConversationState.CLOSING)
            self._handle_closing()

            # Mark complete
            self.state_machine.transition_to(ConversationState.COMPLETE)
            self.session.mark_completed()

            return self.session

        except KeyboardInterrupt:
            # User interrupted (Ctrl+C)
            self.state_machine.set_error("Interview interrupted by user")
            self.session.mark_completed()
            return self.session

        except Exception as e:
            # Unexpected error
            self.state_machine.set_error(f"Interview failed: {e}")
            raise

    def _handle_greeting(self) -> None:
        """Handle greeting state."""
        self.tts.speak(self.greeting)

        # Wait for user to confirm ready
        while True:
            result = self.stt.transcribe_audio_data(b"", 16000)  # Placeholder
            user_text = result.get("text", "")

            intent, confidence = self.intent_recognizer.recognize(
                user_text, context_intent=UserIntent.START
            )

            if intent == UserIntent.START:
                break
            elif intent == UserIntent.QUIT:
                # User quit before starting
                self.session.mark_completed()
                self.state_machine.transition_to(ConversationState.COMPLETE)
                return
            else:
                # Repeat greeting
                self.tts.speak("I didn't catch that. Are you ready to begin?")

    def _process_question(self) -> None:
        """Process a single question."""
        self.current_question = self.questions[self.current_question_index]
        self.retry_count = 0
        turn_start = time.time()

        # Ask question
        self._ask_question()

        # Get answer
        while self.retry_count < self.max_retries:
            user_text = self._listen_for_response()

            if not user_text:
                self.retry_count += 1
                if self.retry_count < self.max_retries:
                    self.tts.speak("I didn't hear that. Could you please repeat?")
                continue

            # Recognize intent
            intent, _ = self.intent_recognizer.recognize(user_text)

            # Handle intent
            if intent == UserIntent.ANSWER:
                self.current_response_text = user_text
                if self.enable_confirmation:
                    if self._confirm_answer():
                        break  # Answer confirmed
                    # else: Loop to retry
                else:
                    break  # No confirmation needed

            elif intent == UserIntent.REPEAT:
                self._ask_question()

            elif intent == UserIntent.CLARIFY:
                self._provide_clarification()

            elif intent == UserIntent.SKIP:
                self._skip_question(turn_start)
                return

            elif intent == UserIntent.QUIT:
                self._handle_early_exit()
                return

            else:
                # Treat as answer attempt
                self.current_response_text = user_text
                if self.enable_confirmation:
                    if self._confirm_answer():
                        break
                else:
                    break

        # Save turn
        self._save_turn(turn_start)
        self.current_question_index += 1

    def _ask_question(self) -> None:
        """Speak current question via TTS."""
        if self.current_question:
            question_text = f"Question {self.current_question.number}. "
            question_text += self.current_question.text
            self.tts.speak(question_text)

    def _listen_for_response(self) -> str:
        """Listen for user response via STT.

        Returns:
            Transcribed text
        """
        # Placeholder: In real implementation, use AudioManager
        # to record from microphone
        result = self.stt.transcribe_audio_data(b"", 16000)
        return result.get("text", "")

    def _confirm_answer(self) -> bool:
        """Confirm user's answer.

        Returns:
            True if user confirms, False if wants to retry
        """
        self.state_machine.transition_to(ConversationState.CONFIRMING)

        # Repeat answer back
        self.tts.speak(f"You said: {self.current_response_text}. Is that correct?")

        # Get confirmation
        user_text = self._listen_for_response()
        intent, _ = self.intent_recognizer.recognize(
            user_text, context_intent=UserIntent.CONFIRM_YES
        )

        self.state_machine.transition_to(ConversationState.QUESTIONING)

        if intent == UserIntent.CONFIRM_YES:
            return True
        elif intent == UserIntent.CONFIRM_NO:
            self.tts.speak("Okay, let's try again.")
            self.retry_count += 1
            return False
        else:
            # Unclear, ask again
            self.tts.speak("I didn't understand. Let's try again.")
            self.retry_count += 1
            return False

    def _provide_clarification(self) -> None:
        """Provide clarification for current question."""
        # For now, just repeat the question
        # Could be enhanced with additional context
        self.tts.speak("Let me repeat the question.")
        self._ask_question()

    def _skip_question(self, turn_start: float) -> None:
        """Skip current question.

        Args:
            turn_start: Timestamp when turn started
        """
        if self.current_question:
            duration = time.time() - turn_start
            turn = ConversationTurn(
                question=self.current_question,
                response=None,
                duration_seconds=duration,
                skipped=True,
            )
            self.session.add_turn(turn)

        self.current_question_index += 1
        self.tts.speak("Okay, moving to the next question.")

    def _save_turn(self, turn_start: float) -> None:
        """Save completed conversation turn.

        Args:
            turn_start: Timestamp when turn started
        """
        if not self.current_question:
            return

        duration = time.time() - turn_start

        response = None
        if self.current_response_text:
            response = Response(
                text=self.current_response_text,
                confidence=0.9,  # Placeholder
                retry_count=self.retry_count,
            )

        turn = ConversationTurn(
            question=self.current_question,
            response=response,
            duration_seconds=duration,
            skipped=False,
        )

        self.session.add_turn(turn)

    def _handle_closing(self) -> None:
        """Handle closing state."""
        self.tts.speak(self.closing)

    def _handle_early_exit(self) -> None:
        """Handle user quitting early."""
        self.tts.speak("Okay, ending the interview. Thank you!")
        self.session.mark_completed()
        self.state_machine.transition_to(ConversationState.COMPLETE)

    def get_progress(self) -> dict[str, int | float]:
        """Get interview progress statistics.

        Returns:
            Dictionary with progress metrics
        """
        total = len(self.questions)
        completed = self.current_question_index
        remaining = total - completed
        percent = (completed / total * 100) if total > 0 else 0

        return {
            "total_questions": total,
            "completed": completed,
            "remaining": remaining,
            "percent_complete": round(percent, 1),
        }
