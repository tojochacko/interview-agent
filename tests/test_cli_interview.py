"""Tests for CLI interview commands.

This module tests the Click-based CLI interface for conducting interviews,
configuring settings, and testing audio devices.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from conversation_agent.cli.interview import cli
from conversation_agent.models import InterviewSession, Question, Response


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a sample PDF file for testing."""
    pdf_path = tmp_path / "test_questionnaire.pdf"
    pdf_path.write_text("dummy pdf content")
    return pdf_path


@pytest.fixture
def mock_pdf_parser():
    """Mock PDF parser."""
    with patch("conversation_agent.cli.interview.PDFQuestionParser") as mock:
        questions = [
            Question(number=1, text="What is your name?"),
            Question(number=2, text="What is your role?"),
        ]
        mock.return_value.parse.return_value = questions
        yield mock


@pytest.fixture
def mock_tts_provider():
    """Mock TTS provider."""
    with patch("conversation_agent.cli.interview.Pyttsx3Provider") as mock:
        provider = MagicMock()
        provider.list_voices.return_value = ["Voice 1", "Voice 2", "Voice 3"]
        mock.return_value = provider
        yield mock


@pytest.fixture
def mock_stt_provider():
    """Mock STT provider."""
    with patch("conversation_agent.cli.interview.WhisperProvider") as mock:
        provider = MagicMock()
        provider.listen.return_value = Response(
            text="Hello world",
            confidence=0.95,
        )
        mock.return_value = provider
        yield mock


@pytest.fixture
def mock_orchestrator():
    """Mock interview orchestrator."""
    with patch("conversation_agent.cli.interview.InterviewOrchestrator") as mock:
        # Create a mock session
        session = InterviewSession(questionnaire_path="test.pdf")
        session.mark_completed()  # Sets completed=True and end_time

        orchestrator = MagicMock()
        orchestrator.session = session
        orchestrator.get_progress.return_value = {
            "answered": 2,
            "total": 2,
            "skipped": 0,
        }
        mock.return_value = orchestrator
        yield mock


class TestCLIHelp:
    """Test CLI help messages."""

    def test_main_help(self, cli_runner: CliRunner):
        """Test main CLI help message."""
        result = cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Voice Interview Agent" in result.output
        assert "start" in result.output
        assert "config" in result.output
        assert "test-audio" in result.output

    def test_start_help(self, cli_runner: CliRunner):
        """Test start command help."""
        result = cli_runner.invoke(cli, ["start", "--help"])
        assert result.exit_code == 0
        assert "Start a new voice interview" in result.output
        assert "PDF_PATH" in result.output

    def test_config_help(self, cli_runner: CliRunner):
        """Test config command help."""
        result = cli_runner.invoke(cli, ["config", "--help"])
        assert result.exit_code == 0
        assert "Display and configure" in result.output

    def test_test_audio_help(self, cli_runner: CliRunner):
        """Test test-audio command help."""
        result = cli_runner.invoke(cli, ["test-audio", "--help"])
        assert result.exit_code == 0
        assert "Test audio devices" in result.output


class TestStartCommand:
    """Test the 'start' command."""

    def test_start_requires_pdf_path(self, cli_runner: CliRunner):
        """Test that start command requires PDF path."""
        result = cli_runner.invoke(cli, ["start"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "PDF_PATH" in result.output

    def test_start_with_nonexistent_file(self, cli_runner: CliRunner):
        """Test start with non-existent PDF file."""
        result = cli_runner.invoke(cli, ["start", "nonexistent.pdf"])
        assert result.exit_code != 0

    @patch("conversation_agent.cli.interview.export_interview")
    def test_start_with_valid_pdf(
        self,
        mock_export: Mock,
        cli_runner: CliRunner,
        sample_pdf: Path,
        mock_pdf_parser: Mock,
        mock_tts_provider: Mock,
        mock_stt_provider: Mock,
        mock_orchestrator: Mock,
        tmp_path: Path,
    ):
        """Test successful interview start."""
        mock_export.return_value = tmp_path / "transcript.csv"

        result = cli_runner.invoke(
            cli,
            ["start", str(sample_pdf), "--no-confirmation"],
            input="y\n",  # Confirm ready
        )

        assert mock_pdf_parser.called
        assert mock_orchestrator.called
        assert mock_orchestrator.return_value.run.called

        # Check output contains expected messages
        assert "Loading questionnaire" in result.output
        assert "questions from PDF" in result.output

    @patch("conversation_agent.cli.interview.export_interview")
    def test_start_with_custom_output_dir(
        self,
        mock_export: Mock,
        cli_runner: CliRunner,
        sample_pdf: Path,
        mock_pdf_parser: Mock,
        mock_tts_provider: Mock,
        mock_stt_provider: Mock,
        mock_orchestrator: Mock,
        tmp_path: Path,
    ):
        """Test start with custom output directory."""
        output_dir = tmp_path / "custom_output"
        mock_export.return_value = output_dir / "transcript.csv"

        cli_runner.invoke(
            cli,
            [
                "start",
                str(sample_pdf),
                "--output-dir",
                str(output_dir),
                "--no-confirmation",
            ],
            input="y\n",
        )

        # Test passes if command runs without error
        assert mock_orchestrator.called

    @patch("conversation_agent.cli.interview.export_interview")
    def test_start_with_tts_rate_option(
        self,
        mock_export: Mock,
        cli_runner: CliRunner,
        sample_pdf: Path,
        mock_pdf_parser: Mock,
        mock_tts_provider: Mock,
        mock_stt_provider: Mock,
        mock_orchestrator: Mock,
        tmp_path: Path,
    ):
        """Test start with custom TTS rate."""
        mock_export.return_value = tmp_path / "transcript.csv"

        cli_runner.invoke(
            cli,
            [
                "start",
                str(sample_pdf),
                "--tts-rate",
                "200",
                "--no-confirmation",
            ],
            input="y\n",
        )

        assert mock_tts_provider.called
        # TTSConfig should have rate=200

    @patch("conversation_agent.cli.interview.export_interview")
    def test_start_with_stt_model_option(
        self,
        mock_export: Mock,
        cli_runner: CliRunner,
        sample_pdf: Path,
        mock_pdf_parser: Mock,
        mock_tts_provider: Mock,
        mock_stt_provider: Mock,
        mock_orchestrator: Mock,
        tmp_path: Path,
    ):
        """Test start with custom STT model."""
        mock_export.return_value = tmp_path / "transcript.csv"

        cli_runner.invoke(
            cli,
            [
                "start",
                str(sample_pdf),
                "--stt-model",
                "small",
                "--no-confirmation",
            ],
            input="y\n",
        )

        assert mock_stt_provider.called

    @patch("conversation_agent.cli.interview.export_interview")
    def test_start_cancelled_by_user(
        self,
        mock_export: Mock,
        cli_runner: CliRunner,
        sample_pdf: Path,
        mock_pdf_parser: Mock,
        mock_tts_provider: Mock,
        mock_stt_provider: Mock,
        mock_orchestrator: Mock,
    ):
        """Test interview cancelled by user at confirmation."""
        result = cli_runner.invoke(
            cli,
            ["start", str(sample_pdf)],
            input="n\n",  # Decline to start
        )

        assert "cancelled" in result.output.lower()
        assert not mock_orchestrator.return_value.run.called

    def test_start_with_empty_pdf(
        self,
        cli_runner: CliRunner,
        sample_pdf: Path,
    ):
        """Test start with PDF containing no questions."""
        with patch("conversation_agent.cli.interview.PDFQuestionParser") as mock_parser:
            mock_parser.return_value.parse.return_value = []

            result = cli_runner.invoke(cli, ["start", str(sample_pdf)])

            assert result.exit_code != 0
            assert "No questions found" in result.output


class TestConfigCommand:
    """Test the 'config' command."""

    def test_config_show_all(
        self,
        cli_runner: CliRunner,
        mock_tts_provider: Mock,
    ):
        """Test config command shows all settings."""
        result = cli_runner.invoke(cli, ["config", "--show-all"])

        assert result.exit_code == 0
        assert "TEXT-TO-SPEECH" in result.output
        assert "SPEECH-TO-TEXT" in result.output
        assert "CSV EXPORT" in result.output

    def test_config_show_tts(
        self,
        cli_runner: CliRunner,
        mock_tts_provider: Mock,
    ):
        """Test config command shows TTS settings."""
        result = cli_runner.invoke(cli, ["config", "--show-tts"])

        assert result.exit_code == 0
        assert "TEXT-TO-SPEECH" in result.output
        assert "Provider:" in result.output
        assert "Rate:" in result.output
        assert "Volume:" in result.output
        assert "Available voices:" in result.output

    def test_config_show_stt(self, cli_runner: CliRunner):
        """Test config command shows STT settings."""
        result = cli_runner.invoke(cli, ["config", "--show-stt"])

        assert result.exit_code == 0
        assert "SPEECH-TO-TEXT" in result.output
        assert "Model Size:" in result.output
        assert "Language:" in result.output
        assert "Available Whisper models:" in result.output
        assert "tiny" in result.output
        assert "base" in result.output
        assert "small" in result.output

    def test_config_default_shows_all(
        self,
        cli_runner: CliRunner,
        mock_tts_provider: Mock,
    ):
        """Test config command without flags shows all settings."""
        result = cli_runner.invoke(cli, ["config"])

        assert result.exit_code == 0
        assert "TEXT-TO-SPEECH" in result.output
        assert "SPEECH-TO-TEXT" in result.output
        assert "CSV EXPORT" in result.output

    def test_config_shows_env_var_instructions(
        self,
        cli_runner: CliRunner,
        mock_tts_provider: Mock,
    ):
        """Test config shows environment variable instructions."""
        result = cli_runner.invoke(cli, ["config"])

        assert result.exit_code == 0
        assert "export" in result.output  # Environment variable instructions


class TestTestAudioCommand:
    """Test the 'test-audio' command."""

    def test_test_audio_tts(
        self,
        cli_runner: CliRunner,
        mock_tts_provider: Mock,
    ):
        """Test TTS audio test."""
        result = cli_runner.invoke(
            cli,
            ["test-audio", "--tts-test"],
            input="y\n",  # Confirm heard message
        )

        assert result.exit_code == 0
        assert "TESTING TEXT-TO-SPEECH" in result.output
        assert mock_tts_provider.return_value.speak.called

    def test_test_audio_stt(
        self,
        cli_runner: CliRunner,
        mock_stt_provider: Mock,
    ):
        """Test STT audio test."""
        result = cli_runner.invoke(
            cli,
            ["test-audio", "--stt-test"],
            input="y\ny\n",  # Ready, then confirm accuracy
        )

        assert result.exit_code == 0
        assert "TESTING SPEECH-TO-TEXT" in result.output
        assert mock_stt_provider.return_value.listen.called
        assert "Transcription:" in result.output
        assert "Hello world" in result.output

    def test_test_audio_all(
        self,
        cli_runner: CliRunner,
        mock_tts_provider: Mock,
        mock_stt_provider: Mock,
    ):
        """Test all audio systems."""
        result = cli_runner.invoke(
            cli,
            ["test-audio", "--test-all"],
            input="y\ny\ny\n",  # Heard TTS, ready for STT, STT accurate
        )

        assert result.exit_code == 0
        assert "TESTING TEXT-TO-SPEECH" in result.output
        assert "TESTING SPEECH-TO-TEXT" in result.output
        assert mock_tts_provider.return_value.speak.called
        assert mock_stt_provider.return_value.listen.called

    def test_test_audio_default_tests_all(
        self,
        cli_runner: CliRunner,
        mock_tts_provider: Mock,
        mock_stt_provider: Mock,
    ):
        """Test that no flags tests all audio systems."""
        result = cli_runner.invoke(
            cli,
            ["test-audio"],
            input="y\ny\ny\n",
        )

        assert result.exit_code == 0
        assert "TESTING TEXT-TO-SPEECH" in result.output
        assert "TESTING SPEECH-TO-TEXT" in result.output

    def test_test_audio_stt_no_speech_detected(
        self,
        cli_runner: CliRunner,
    ):
        """Test STT when no speech is detected."""
        with patch("conversation_agent.cli.interview.WhisperProvider") as mock_stt:
            mock_stt.return_value.listen.return_value = None

            result = cli_runner.invoke(
                cli,
                ["test-audio", "--stt-test"],
                input="y\n",  # Ready
            )

            # CLI should handle gracefully and show error message
            assert "No speech detected" in result.output or "failed" in result.output.lower()

    def test_test_audio_tts_cancelled(
        self,
        cli_runner: CliRunner,
        mock_tts_provider: Mock,
    ):
        """Test TTS test when user reports not hearing."""
        result = cli_runner.invoke(
            cli,
            ["test-audio", "--tts-test"],
            input="n\n",  # Did not hear message
        )

        assert result.exit_code == 0
        assert "Troubleshooting" in result.output


class TestVerboseLogging:
    """Test verbose logging flag."""

    def test_verbose_flag_enables_debug_logging(
        self,
        cli_runner: CliRunner,
        mock_tts_provider: Mock,
    ):
        """Test that -v flag enables debug logging."""
        with patch("conversation_agent.cli.interview.setup_logging") as mock_logging:
            result = cli_runner.invoke(cli, ["-v", "config"])

            assert result.exit_code == 0
            mock_logging.assert_called_once()
            call_kwargs = mock_logging.call_args.kwargs
            assert call_kwargs["level"] == "DEBUG"

    def test_no_verbose_uses_info_logging(
        self,
        cli_runner: CliRunner,
        mock_tts_provider: Mock,
    ):
        """Test that no -v flag uses INFO logging."""
        with patch("conversation_agent.cli.interview.setup_logging") as mock_logging:
            result = cli_runner.invoke(cli, ["config"])

            assert result.exit_code == 0
            mock_logging.assert_called_once()
            call_kwargs = mock_logging.call_args.kwargs
            assert call_kwargs["level"] == "INFO"


class TestLogFile:
    """Test log file option."""

    def test_log_file_option(
        self,
        cli_runner: CliRunner,
        mock_tts_provider: Mock,
        tmp_path: Path,
    ):
        """Test that --log-file option works."""
        log_file = tmp_path / "test.log"

        with patch("conversation_agent.cli.interview.setup_logging") as mock_logging:
            result = cli_runner.invoke(
                cli,
                ["--log-file", str(log_file), "config"],
            )

            assert result.exit_code == 0
            mock_logging.assert_called_once()
            call_kwargs = mock_logging.call_args.kwargs
            assert call_kwargs["log_file"] == log_file
