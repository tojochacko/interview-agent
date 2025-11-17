"""Tests for interview orchestrator."""

from unittest.mock import Mock, patch

import pytest

from conversation_agent.core.conversation_state import ConversationState
from conversation_agent.core.interview import InterviewOrchestrator
from conversation_agent.models.interview import InterviewSession


class TestInterviewOrchestrator:
    """Test InterviewOrchestrator."""

    @pytest.fixture
    def mock_tts(self):
        """Create mock TTS provider."""
        tts = Mock()
        tts.speak = Mock()
        return tts

    @pytest.fixture
    def mock_stt(self):
        """Create mock STT provider."""
        stt = Mock()
        stt.transcribe_audio_data = Mock(return_value={"text": "", "language": "en"})
        return stt

    @pytest.fixture
    def sample_pdf_path(self, tmp_path):
        """Create a sample PDF for testing."""
        # Use existing test fixture
        return "tests/fixtures/sample_questionnaire.pdf"

    def test_initialization_success(self, mock_tts, mock_stt, sample_pdf_path):
        """Test successful initialization."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        assert orchestrator.tts == mock_tts
        assert orchestrator.stt == mock_stt
        assert orchestrator.enable_confirmation is True
        assert orchestrator.max_retries == 3
        assert len(orchestrator.questions) > 0
        assert orchestrator.current_question_index == 0
        assert isinstance(orchestrator.session, InterviewSession)
        assert orchestrator.state_machine.current_state == ConversationState.INIT

    def test_initialization_custom_settings(
        self, mock_tts, mock_stt, sample_pdf_path
    ):
        """Test initialization with custom settings."""
        custom_greeting = "Custom greeting"
        custom_closing = "Custom closing"

        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts,
            stt_provider=mock_stt,
            pdf_path=sample_pdf_path,
            enable_confirmation=False,
            max_retries=5,
            greeting=custom_greeting,
            closing=custom_closing,
        )

        assert orchestrator.enable_confirmation is False
        assert orchestrator.max_retries == 5
        assert orchestrator.greeting == custom_greeting
        assert orchestrator.closing == custom_closing

    def test_initialization_pdf_not_found(self, mock_tts, mock_stt):
        """Test initialization fails with non-existent PDF."""
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            InterviewOrchestrator(
                tts_provider=mock_tts,
                stt_provider=mock_stt,
                pdf_path="nonexistent.pdf",
            )

    def test_initialization_invalid_max_retries(
        self, mock_tts, mock_stt, sample_pdf_path
    ):
        """Test initialization fails with invalid max_retries."""
        with pytest.raises(ValueError, match="max_retries must be at least 1"):
            InterviewOrchestrator(
                tts_provider=mock_tts,
                stt_provider=mock_stt,
                pdf_path=sample_pdf_path,
                max_retries=0,
            )

    def test_initialization_empty_pdf(self, mock_tts, mock_stt):
        """Test initialization fails with empty PDF."""
        from conversation_agent.core.pdf_parser import PDFParseError

        with pytest.raises(PDFParseError, match="No valid questions found"):
            InterviewOrchestrator(
                tts_provider=mock_tts,
                stt_provider=mock_stt,
                pdf_path="tests/fixtures/empty_questionnaire.pdf",
            )

    def test_get_progress_initial(self, mock_tts, mock_stt, sample_pdf_path):
        """Test get_progress at start."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        progress = orchestrator.get_progress()

        assert "total_questions" in progress
        assert "completed" in progress
        assert "remaining" in progress
        assert "percent_complete" in progress

        assert progress["completed"] == 0
        assert progress["remaining"] == progress["total_questions"]
        assert progress["percent_complete"] == 0.0

    def test_get_progress_partial(self, mock_tts, mock_stt, sample_pdf_path):
        """Test get_progress with some questions completed."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        # Simulate progress
        total = len(orchestrator.questions)
        orchestrator.current_question_index = total // 2

        progress = orchestrator.get_progress()

        assert progress["completed"] == total // 2
        assert progress["remaining"] == total - (total // 2)
        assert 0 < progress["percent_complete"] < 100

    def test_get_progress_complete(self, mock_tts, mock_stt, sample_pdf_path):
        """Test get_progress when all questions done."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        # Complete all questions
        total = len(orchestrator.questions)
        orchestrator.current_question_index = total

        progress = orchestrator.get_progress()

        assert progress["completed"] == total
        assert progress["remaining"] == 0
        assert progress["percent_complete"] == 100.0

    def test_handle_greeting_calls_tts(self, mock_tts, mock_stt, sample_pdf_path):
        """Test greeting state calls TTS."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        # Mock STT to return "start"
        mock_stt.transcribe_audio_data.return_value = {
            "text": "yes I'm ready",
            "language": "en",
        }

        orchestrator._handle_greeting()

        # Should have called TTS with greeting
        assert mock_tts.speak.called
        call_args = mock_tts.speak.call_args[0][0]
        assert "ready to begin" in call_args.lower()

    def test_ask_question_formats_correctly(
        self, mock_tts, mock_stt, sample_pdf_path
    ):
        """Test _ask_question formats question text."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        orchestrator.current_question = orchestrator.questions[0]
        orchestrator._ask_question()

        # Should call TTS with formatted question
        assert mock_tts.speak.called
        call_args = mock_tts.speak.call_args[0][0]
        assert "Question" in call_args
        assert str(orchestrator.current_question.number) in call_args

    def test_session_initialization(self, mock_tts, mock_stt, sample_pdf_path):
        """Test session is properly initialized."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        assert orchestrator.session.questionnaire_path == sample_pdf_path
        assert len(orchestrator.session.turns) == 0
        assert orchestrator.session.completed is False
        assert orchestrator.session.end_time is None

    def test_state_machine_initialization(self, mock_tts, mock_stt, sample_pdf_path):
        """Test state machine is properly initialized."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        assert orchestrator.state_machine.current_state == ConversationState.INIT
        assert orchestrator.state_machine.is_terminal() is False

    def test_intent_recognizer_initialization(
        self, mock_tts, mock_stt, sample_pdf_path
    ):
        """Test intent recognizer is properly initialized."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        assert orchestrator.intent_recognizer is not None
        assert orchestrator.intent_recognizer.confidence_threshold == 0.7

    def test_questions_loaded_from_pdf(self, mock_tts, mock_stt, sample_pdf_path):
        """Test questions are loaded from PDF."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        assert len(orchestrator.questions) > 0
        assert all(hasattr(q, "text") for q in orchestrator.questions)
        assert all(hasattr(q, "number") for q in orchestrator.questions)

    def test_keyboard_interrupt_handling(self, mock_tts, mock_stt, sample_pdf_path):
        """Test graceful handling of keyboard interrupt."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        # Mock greeting to raise KeyboardInterrupt
        with patch.object(orchestrator, "_handle_greeting", side_effect=KeyboardInterrupt):
            session = orchestrator.run()

            # Session should be marked completed
            assert session.completed is True
            assert orchestrator.state_machine.current_state == ConversationState.ERROR

    def test_default_greeting_message(self, mock_tts, mock_stt, sample_pdf_path):
        """Test default greeting message is set."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        assert "interview assistant" in orchestrator.greeting.lower()
        assert "ready to begin" in orchestrator.greeting.lower()

    def test_default_closing_message(self, mock_tts, mock_stt, sample_pdf_path):
        """Test default closing message is set."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        assert "thank you" in orchestrator.closing.lower()
        assert "recorded" in orchestrator.closing.lower()

    def test_save_turn_creates_turn(self, mock_tts, mock_stt, sample_pdf_path):
        """Test _save_turn creates conversation turn."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        orchestrator.current_question = orchestrator.questions[0]
        orchestrator.current_response_text = "Test answer"
        orchestrator.retry_count = 1

        import time

        start_time = time.time()
        orchestrator._save_turn(start_time)

        assert len(orchestrator.session.turns) == 1
        turn = orchestrator.session.turns[0]
        assert turn.question == orchestrator.current_question
        assert turn.response is not None
        assert turn.response.text == "Test answer"
        assert turn.response.retry_count == 1
        assert turn.skipped is False

    def test_skip_question_creates_skipped_turn(
        self, mock_tts, mock_stt, sample_pdf_path
    ):
        """Test _skip_question creates skipped turn."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        orchestrator.current_question = orchestrator.questions[0]

        import time

        start_time = time.time()
        orchestrator._skip_question(start_time)

        assert len(orchestrator.session.turns) == 1
        turn = orchestrator.session.turns[0]
        assert turn.question == orchestrator.current_question
        assert turn.response is None
        assert turn.skipped is True

    def test_handle_closing_calls_tts(self, mock_tts, mock_stt, sample_pdf_path):
        """Test _handle_closing calls TTS with closing message."""
        orchestrator = InterviewOrchestrator(
            tts_provider=mock_tts, stt_provider=mock_stt, pdf_path=sample_pdf_path
        )

        orchestrator._handle_closing()

        # Should call TTS with closing message
        assert mock_tts.speak.called
        call_args = mock_tts.speak.call_args[0][0]
        assert call_args == orchestrator.closing
