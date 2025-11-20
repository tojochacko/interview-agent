"""Interview orchestrator for managing conversation flow."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from conversation_agent.core.audio import AudioManager
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

logger = logging.getLogger(__name__)


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
        self.audio_manager = AudioManager()
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
        self.last_audio_size = 0  # Track last audio size for duplicate detection
        self.duplicate_audio_count = 0  # Count consecutive duplicate audio captures

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
                # Check if user quit early
                if self.state_machine.is_terminal():
                    return self.session

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
            # Record audio from microphone with shorter silence detection
            audio_data = self.audio_manager.record_until_silence(
                silence_threshold=0.005,  # Slightly less sensitive to noise
                silence_duration=2.0,     # 2 seconds of silence (faster response)
            )
            # Log audio data details
            audio_duration = len(audio_data) / (
                self.audio_manager.get_sample_rate()
                * self.audio_manager.channels
                * 2
            )
            logger.info(
                f"🎤 Recorded audio: {len(audio_data)} bytes, "
                f"{audio_duration:.2f}s duration"
            )

            result = self.stt.transcribe_audio_data(
                audio_data,
                self.audio_manager.get_sample_rate()
            )
            # Log transcription result
            logger.info(f"📝 Transcription result: {result}")
            user_text = result.get("text", "")

            intent, confidence = self.intent_recognizer.recognize(
                user_text, context_intent=UserIntent.START
            )
            logger.info(
                f"🎯 Intent recognized: {intent.value}, "
                f"confidence: {confidence:.2f}, "
                f"text: '{user_text}'"
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

        logger.info(
            f"📋 Processing question {self.current_question_index + 1}/"
            f"{len(self.questions)}: '{self.current_question.text[:50]}...'"
        )

        # Ask question
        self._ask_question()

        # Wait for TTS audio to fully finish and dissipate
        # Prevents microphone from picking up speaker output
        logger.info("⏳ Waiting for audio to settle before listening...")
        time.sleep(1.0)  # 1 second delay to prevent echo/feedback
        logger.info("🎧 Ready to listen for response")

        # Get answer
        loop_iteration = 0
        while self.retry_count < self.max_retries:
            loop_iteration += 1
            logger.info(
                f"🔄 Loop iteration {loop_iteration}, "
                f"retry_count={self.retry_count}/{self.max_retries}"
            )

            user_text = self._listen_for_response()

            if not user_text:
                self.retry_count += 1
                logger.warning(
                    f"⚠️ Empty transcription, retry_count={self.retry_count}/"
                    f"{self.max_retries}"
                )
                if self.retry_count < self.max_retries:
                    self.tts.speak("I didn't hear that. Could you please repeat?")
                    time.sleep(1.5)  # Wait for audio to settle
                continue

            # Recognize intent
            intent, confidence = self.intent_recognizer.recognize(user_text)
            logger.info(
                f"🎯 Intent: {intent.value}, confidence: {confidence:.2f}, "
                f"text: '{user_text}'"
            )

            # Handle intent
            if intent == UserIntent.ANSWER:
                logger.info("✅ Recognized as ANSWER intent")
                self.current_response_text = user_text
                if self.enable_confirmation:
                    logger.info("🔍 Confirmation enabled, requesting confirmation...")
                    confirmed = self._confirm_answer()
                    logger.info(
                        f"🔍 Confirmation result: {confirmed}, "
                        f"retry_count={self.retry_count}/{self.max_retries}"
                    )
                    if confirmed:
                        logger.info("✅ Answer confirmed, breaking loop")
                        break  # Answer confirmed
                    # Check if max retries reached after failed confirmation
                    if self.retry_count >= self.max_retries:
                        logger.warning(
                            "⚠️ Max retries reached after failed confirmation, "
                            "breaking loop"
                        )
                        break  # Give up, save whatever we have
                    logger.info("🔄 Confirmation failed, retrying...")
                    # else: Loop to retry
                else:
                    logger.info("✅ No confirmation needed, breaking loop")
                    break  # No confirmation needed

            elif intent == UserIntent.REPEAT:
                logger.info("🔁 REPEAT intent, asking question again")
                self._ask_question()
                time.sleep(1.5)  # Wait for audio to settle

            elif intent == UserIntent.CLARIFY:
                logger.info("❓ CLARIFY intent, providing clarification")
                self._provide_clarification()
                time.sleep(1.5)  # Wait for audio to settle

            elif intent == UserIntent.SKIP:
                logger.info("⏭️ SKIP intent, skipping question")
                self._skip_question(turn_start)
                return

            elif intent == UserIntent.QUIT:
                logger.info("🛑 QUIT intent, exiting interview")
                self._handle_early_exit()
                return

            else:
                # Treat as answer attempt
                logger.info(
                    f"❔ UNKNOWN/OTHER intent ({intent.value}), "
                    "treating as answer attempt"
                )
                self.current_response_text = user_text
                if self.enable_confirmation:
                    logger.info("🔍 Confirmation enabled, requesting confirmation...")
                    confirmed = self._confirm_answer()
                    logger.info(
                        f"🔍 Confirmation result: {confirmed}, "
                        f"retry_count={self.retry_count}/{self.max_retries}"
                    )
                    if confirmed:
                        logger.info("✅ Answer confirmed, breaking loop")
                        break
                    # Check if max retries reached after failed confirmation
                    if self.retry_count >= self.max_retries:
                        logger.warning(
                            "⚠️ Max retries reached after failed confirmation, "
                            "breaking loop"
                        )
                        break  # Give up, save whatever we have
                    logger.info("🔄 Confirmation failed, retrying...")
                else:
                    logger.info("✅ No confirmation needed, breaking loop")
                    break

        logger.info(
            f"🏁 Exited loop after {loop_iteration} iterations, "
            f"final retry_count={self.retry_count}"
        )

        # Save turn
        self._save_turn(turn_start)
        self.current_question_index += 1

    def _ask_question(self) -> None:
        """Speak current question via TTS."""
        if self.current_question:
            question_text = f"Question {self.current_question.number}. "
            question_text += self.current_question.text
            logger.info(f"🔊 Speaking question: '{question_text}'")
            logger.info(f"📢 TTS provider: {self.tts.__class__.__name__}")
            self.tts.speak(question_text)
            logger.info("✅ TTS completed speaking question")

    def _listen_for_response(self) -> str:
        """Listen for user response via STT.

        Returns:
            Transcribed text
        """
        logger.info("👂 Entering _listen_for_response, starting audio recording...")
        # Record audio from microphone with high silence threshold
        # This reduces false positives from echo/feedback and ambient noise
        audio_data = self.audio_manager.record_until_silence(
            silence_threshold=0.05,   # Very high threshold = much less sensitive
            silence_duration=3.0,     # 3 seconds of silence to ensure speech ended
        )
        # Log audio data details
        audio_duration = len(audio_data) / (
            self.audio_manager.get_sample_rate()
            * self.audio_manager.channels
            * 2
        )
        logger.info(
            f"🎤 Recorded audio: {len(audio_data)} bytes, "
            f"{audio_duration:.2f}s duration"
        )

        # Check for duplicate audio (possible echo/feedback issue)
        if len(audio_data) == self.last_audio_size and self.last_audio_size > 0:
            self.duplicate_audio_count += 1
            logger.warning(
                f"⚠️ DUPLICATE AUDIO DETECTED! Same audio size as previous: "
                f"{len(audio_data)} bytes (count: {self.duplicate_audio_count}). "
                "This may indicate microphone is picking up TTS echo/feedback "
                "or ambient noise."
            )
        else:
            self.duplicate_audio_count = 0  # Reset counter
        self.last_audio_size = len(audio_data)

        # Check audio quality - reject if too short (likely just noise)
        MIN_VALID_AUDIO_DURATION = 0.5  # At least 0.5 seconds of audio
        if audio_duration < MIN_VALID_AUDIO_DURATION:
            logger.warning(
                f"⚠️ Audio too short ({audio_duration:.2f}s < "
                f"{MIN_VALID_AUDIO_DURATION}s), likely noise. Treating as silence."
            )
            return ""

        # Check audio energy level - reject if too quiet (just ambient noise)
        import struct
        audio_samples = struct.unpack(f"{len(audio_data) // 2}h", audio_data)
        avg_amplitude = sum(abs(sample) for sample in audio_samples) / len(
            audio_samples
        )
        MIN_AMPLITUDE = 100  # Minimum average amplitude for valid speech
        if avg_amplitude < MIN_AMPLITUDE:
            logger.warning(
                f"⚠️ Audio amplitude too low ({avg_amplitude:.0f} < "
                f"{MIN_AMPLITUDE}), likely ambient noise. Treating as silence."
            )
            return ""

        logger.info(
            f"✅ Audio quality check passed: duration={audio_duration:.2f}s, "
            f"amplitude={avg_amplitude:.0f}"
        )

        # Transcribe the recorded audio
        logger.info("🔊 Transcribing recorded audio...")
        result = self.stt.transcribe_audio_data(
            audio_data,
            self.audio_manager.get_sample_rate()
        )
        # Log transcription result
        logger.info(f"📝 Transcription result: {result}")

        user_text = result.get("text", "").strip()

        # Check for Whisper hallucinations (common false positives)
        WHISPER_HALLUCINATIONS = [
            "you", "thank you", "thanks", ".", "...",
            "bye", "goodbye", "music", "subscribe"
        ]
        if user_text.lower() in WHISPER_HALLUCINATIONS and audio_duration < 2.0:
            logger.warning(
                f"⚠️ Potential Whisper hallucination detected: '{user_text}' "
                f"with short audio ({audio_duration:.2f}s). Treating as silence."
            )
            return ""

        if user_text:
            logger.info(
                f"✅ User response: '{user_text}' (length: {len(user_text)})"
            )
        else:
            logger.warning("⚠️ Empty transcription received")

        return user_text

    def _confirm_answer(self) -> bool:
        """Confirm user's answer.

        Returns:
            True if user confirms, False if wants to retry
        """
        logger.info(
            f"🔍 Entering _confirm_answer, current_response_text="
            f"'{self.current_response_text}', retry_count={self.retry_count}"
        )
        self.state_machine.transition_to(ConversationState.CONFIRMING)

        # Repeat answer back
        confirmation_prompt = (
            f"You said: {self.current_response_text}. Is that correct?"
        )
        logger.info(f"💬 Asking for confirmation: '{confirmation_prompt}'")
        self.tts.speak(confirmation_prompt)

        # Wait for TTS audio to settle
        logger.info("⏳ Waiting for audio to settle before listening...")
        time.sleep(1.5)  # 1.5 second delay to prevent echo/feedback
        logger.info("🎧 Ready to listen for confirmation")

        # Get confirmation
        user_text = self._listen_for_response()
        logger.info(f"📥 Received confirmation response: '{user_text}'")

        intent, confidence = self.intent_recognizer.recognize(
            user_text, context_intent=UserIntent.CONFIRM_YES
        )
        logger.info(
            f"🎯 Confirmation intent: {intent.value}, confidence: {confidence:.2f}"
        )

        self.state_machine.transition_to(ConversationState.QUESTIONING)

        if intent == UserIntent.CONFIRM_YES:
            logger.info("✅ Confirmation: YES, returning True")
            return True
        elif intent == UserIntent.CONFIRM_NO:
            logger.info(
                f"❌ Confirmation: NO, incrementing retry_count to "
                f"{self.retry_count + 1}"
            )
            self.tts.speak("Okay, let's try again.")
            self.retry_count += 1
            logger.info(f"🔄 retry_count after increment: {self.retry_count}")
            return False
        else:
            logger.warning(
                f"❔ Confirmation: UNCLEAR ({intent.value}), incrementing "
                f"retry_count to {self.retry_count + 1}"
            )
            self.tts.speak("I didn't understand. Let's try again.")
            self.retry_count += 1
            logger.info(f"🔄 retry_count after increment: {self.retry_count}")
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
