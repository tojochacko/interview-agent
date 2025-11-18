"""CLI commands for conducting voice interviews.

This module provides Click-based command-line interface for:
- Starting interviews from PDF questionnaires
- Configuring TTS/STT settings
- Testing audio devices
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click

from conversation_agent.config import ExportConfig, STTConfig, TTSConfig
from conversation_agent.core import InterviewOrchestrator, export_interview
from conversation_agent.core.audio import AudioManager
from conversation_agent.utils.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


@click.group()
@click.option(
    "--verbose", "-v", is_flag=True, help="Enable verbose logging (DEBUG level)"
)
@click.option(
    "--log-file",
    type=click.Path(path_type=Path),  # type: ignore[type-var]
    help="Log to file for debugging",
)
def cli(verbose: bool, log_file: Optional[Path]) -> None:  # noqa: UP045
    """Voice Interview Agent - Conduct interviews using speech.

    This tool allows you to conduct voice-based interviews using PDF questionnaires.
    The agent speaks questions to you and records your spoken responses.
    """
    level = "DEBUG" if verbose else "INFO"
    setup_logging(level=level, log_file=log_file)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True, path_type=Path))  # noqa: UP007
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),  # type: ignore[type-var]
    help="Output directory for transcripts (default: ./interview_transcripts)",
)
@click.option(
    "--no-confirmation",
    is_flag=True,
    help="Disable answer confirmation prompts",
)
@click.option(
    "--no-metadata",
    is_flag=True,
    help="Exclude metadata from CSV export",
)
@click.option(
    "--tts-rate",
    type=int,
    help="TTS speech rate in words per minute (default: 150)",
)
@click.option(
    "--stt-model",
    type=click.Choice(["tiny", "base", "small", "medium", "large"]),
    help="Whisper model size (default: base)",
)
def start(
    pdf_path: Path,
    output_dir: Optional[Path],  # noqa: UP045
    no_confirmation: bool,
    no_metadata: bool,
    tts_rate: Optional[int],  # noqa: UP045
    stt_model: Optional[str],  # noqa: UP045
) -> None:
    """Start a new voice interview from a PDF questionnaire.

    PDF_PATH: Path to the PDF file containing interview questions (one per line)

    Example:
        interview start questionnaire.pdf

        interview start questionnaire.pdf --output-dir ./my_transcripts

        interview start questionnaire.pdf --no-confirmation --stt-model small
    """
    try:
        logger.info("Starting Voice Interview Agent...")
        logger.info(f"Loading questionnaire: {pdf_path}")

        # Configure TTS
        tts_config = TTSConfig(voice="com.apple.voice.Aman")
        if tts_rate:
            tts_config.rate = tts_rate
        logger.debug(f"TTS config: rate={tts_config.rate}, volume={tts_config.volume}")

        # Configure STT
        stt_config = STTConfig(
            model_size="small"
            )
        if stt_model:
            stt_config.model_size = stt_model
        logger.debug(f"STT config: model={stt_config.model_size}, language={stt_config.language}")  # noqa: E501

        # Initialize providers
        click.echo("\nInitializing speech systems...")
        tts_provider = tts_config.get_provider()
        stt_provider = stt_config.get_provider()

        # Configure export
        export_config = ExportConfig()
        if output_dir:
            export_config.output_directory = output_dir
        if no_metadata:
            export_config.include_metadata = False

        # Create orchestrator (it will load the PDF internally)
        click.echo("Loading questionnaire...")
        orchestrator = InterviewOrchestrator(
            tts_provider=tts_provider,
            stt_provider=stt_provider,
            pdf_path=str(pdf_path),
            enable_confirmation=not no_confirmation,
        )

        logger.info(f"Loaded {len(orchestrator.questions)} questions from PDF")

        # Display instructions
        click.echo("\n" + "=" * 70)
        click.echo("VOICE INTERVIEW - INSTRUCTIONS")
        click.echo("=" * 70)
        click.echo("• Speak clearly into your microphone")
        click.echo("• The agent will ask you questions from the questionnaire")
        click.echo("• You can say 'repeat' to hear the question again")
        click.echo("• You can say 'clarify' to get more context")
        click.echo("• Say 'skip' to skip a question")
        click.echo("• Press Ctrl+C to exit early (partial transcript will be saved)")
        click.echo("=" * 70)
        click.echo()

        # Ask user to confirm
        if not click.confirm("Ready to begin the interview?", default=True):
            click.echo("Interview cancelled.")
            sys.exit(0)

        click.echo()

        # Run the interview
        try:
            orchestrator.run()
        except KeyboardInterrupt:
            click.echo("\n\nInterview interrupted by user.")
            logger.info("Interview interrupted, saving partial transcript...")

        # Export results
        session = orchestrator.session
        if session.turns:
            click.echo("\nSaving transcript...")
            output_path = export_interview(session, config=export_config)
            click.echo(f"\n✓ Transcript saved to: {output_path}")

            # Show summary
            progress = orchestrator.get_progress()
            click.echo("\n" + "=" * 70)
            click.echo("INTERVIEW SUMMARY")
            click.echo("=" * 70)
            click.echo(f"Questions answered: {progress['answered']}/{progress['total']}")
            click.echo(f"Questions skipped: {progress['skipped']}")
            click.echo(f"Duration: {session.total_duration_seconds:.1f} seconds")
            status_text = "completed" if session.completed else "incomplete"
            click.echo(f"Status: {status_text}")
            click.echo("=" * 70)
        else:
            click.echo("\nNo responses recorded. Transcript not saved.")

        click.echo("\nThank you for using Voice Interview Agent!")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Interview failed: {e}")
        logger.debug("Full traceback:", exc_info=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--show-tts",
    is_flag=True,
    help="Show available TTS voices",
)
@click.option(
    "--show-stt",
    is_flag=True,
    help="Show available Whisper models",
)
@click.option(
    "--show-all",
    is_flag=True,
    help="Show all configuration options",
)
def config(show_tts: bool, show_stt: bool, show_all: bool) -> None:
    """Display and configure TTS/STT settings.

    Use this command to view current configuration and available options.
    Settings can be changed via environment variables or config files.

    Example:
        interview config --show-all

        interview config --show-tts

        interview config --show-stt
    """
    try:
        # Show all if no specific flag
        if not (show_tts or show_stt) or show_all:
            show_tts = show_stt = True

        if show_tts:
            click.echo("\n" + "=" * 70)
            click.echo("TEXT-TO-SPEECH (TTS) CONFIGURATION")
            click.echo("=" * 70)

            tts_config = TTSConfig()
            click.echo(f"Provider: {tts_config.provider}")
            click.echo(f"Voice: {tts_config.voice}")
            click.echo(f"Rate: {tts_config.rate} words/min")
            click.echo(f"Volume: {tts_config.volume}")

            # Show available voices
            click.echo("\nAvailable voices:")
            try:
                tts_provider = tts_config.get_provider()
                voices = tts_provider.list_voices()
                for i, voice in enumerate(voices[:10], 1):  # Show first 10
                    click.echo(f"  {i}. {voice}")
                if len(voices) > 10:
                    click.echo(f"  ... and {len(voices) - 10} more")
            except Exception as e:
                click.echo(f"  Error listing voices: {e}")

            click.echo("\nTo configure TTS, set environment variables:")
            click.echo("  export TTS_RATE=150")
            click.echo("  export TTS_VOLUME=0.9")
            click.echo("  export TTS_VOICE='voice_id'")

        if show_stt:
            click.echo("\n" + "=" * 70)
            click.echo("SPEECH-TO-TEXT (STT) CONFIGURATION")
            click.echo("=" * 70)

            stt_config = STTConfig()
            click.echo(f"Provider: {stt_config.provider}")
            click.echo(f"Model Size: {stt_config.model_size}")
            click.echo(f"Language: {stt_config.language}")
            click.echo(f"Device: {stt_config.device}")

            click.echo("\nAvailable Whisper models:")
            models = ["tiny", "base", "small", "medium", "large"]
            model_info = {
                "tiny": "~1GB RAM, Very fast, Lower accuracy",
                "base": "~1GB RAM, Fast, Good accuracy (recommended)",
                "small": "~2GB RAM, Medium speed, Better accuracy",
                "medium": "~5GB RAM, Slower, High accuracy",
                "large": "~10GB RAM, Slowest, Highest accuracy",
            }
            for model in models:
                marker = " (current)" if model == stt_config.model_size else ""
                click.echo(f"  • {model:<8} - {model_info[model]}{marker}")

            click.echo("\nTo configure STT, set environment variables:")
            click.echo("  export STT_MODEL_SIZE=base")
            click.echo("  export STT_LANGUAGE=en")
            click.echo("  export STT_DEVICE=cpu  # or 'cuda' for GPU")

        # Export configuration
        click.echo("\n" + "=" * 70)
        click.echo("CSV EXPORT CONFIGURATION")
        click.echo("=" * 70)

        export_config = ExportConfig()
        click.echo(f"Output Directory: {export_config.output_directory}")
        click.echo(f"Filename Format: {export_config.filename_format}")
        click.echo(f"Include Metadata: {export_config.include_metadata}")
        click.echo(f"CSV Encoding: {export_config.csv_encoding}")

        click.echo("\nTo configure export, set environment variables:")
        click.echo("  export EXPORT_OUTPUT_DIRECTORY='./transcripts'")
        click.echo("  export EXPORT_INCLUDE_METADATA=true")
        click.echo()

    except Exception as e:
        logger.error(f"Failed to display configuration: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--tts-test",
    is_flag=True,
    help="Test text-to-speech output",
)
@click.option(
    "--stt-test",
    is_flag=True,
    help="Test speech-to-text input",
)
@click.option(
    "--test-all",
    is_flag=True,
    help="Test both TTS and STT",
)
def test_audio(tts_test: bool, stt_test: bool, test_all: bool) -> None:
    """Test audio devices and speech systems.

    Use this command to verify your microphone and speakers are working
    before starting an interview.

    Example:
        interview test-audio --test-all

        interview test-audio --tts-test

        interview test-audio --stt-test
    """
    try:
        # Test all if no specific flag
        if not (tts_test or stt_test) or test_all:
            tts_test = stt_test = True

        if tts_test:
            click.echo("\n" + "=" * 70)
            click.echo("TESTING TEXT-TO-SPEECH")
            click.echo("=" * 70)
            click.echo("Initializing TTS system...")

            tts_config = TTSConfig()
            tts_provider = tts_config.get_provider()

            test_message = "Hello! This is a test of the text to speech system."
            click.echo(f"\nSpeaking: '{test_message}'")
            tts_provider.speak(test_message)

            click.echo("✓ TTS test complete")

            if not click.confirm("\nDid you hear the test message?", default=True):
                click.echo("\nTroubleshooting tips:")
                click.echo("  • Check your speaker volume")
                click.echo("  • Ensure speakers/headphones are connected")
                click.echo("  • Try a different TTS voice (use 'interview config --show-tts')")

        if stt_test:
            click.echo("\n" + "=" * 70)
            click.echo("TESTING SPEECH-TO-TEXT")
            click.echo("=" * 70)
            click.echo("Initializing STT system (this may take a moment)...")

            stt_config = STTConfig()
            stt_provider = stt_config.get_provider()

            click.echo("\nMicrophone test:")
            click.echo("When you're ready, speak a short phrase (e.g., 'Hello world')")
            click.echo("Recording will start after you press Enter...")

            if not click.confirm("Ready?", default=True):
                click.echo("Test cancelled.")
                return

            click.echo("\n🎤 Recording... (speak now, then wait for silence)")

            # Use AudioManager to record audio
            audio_manager = AudioManager()
            audio_data = audio_manager.record_until_silence()

            # Transcribe the recorded audio
            result = stt_provider.transcribe_audio_data(
                audio_data, audio_manager.get_sample_rate()
            )

            if result and result.get("text"):
                text = result["text"]
                confidence = result.get("confidence", 0.0)
                click.echo(f"\n✓ Transcription: '{text}'")
                click.echo(f"  Confidence: {confidence:.2f}")

                if not click.confirm("\nIs the transcription accurate?", default=True):
                    click.echo("\nTroubleshooting tips:")
                    click.echo("  • Check your microphone is connected and enabled")
                    click.echo("  • Speak clearly and closer to the microphone")
                    click.echo("  • Reduce background noise")
                    click.echo("  • Try a different Whisper model size")
                    click.echo("    (use 'interview config --show-stt')")
            else:
                click.echo("\n✗ No speech detected or transcription failed")
                click.echo("\nTroubleshooting tips:")
                click.echo("  • Ensure your microphone is connected")
                click.echo("  • Check system microphone permissions")
                click.echo("  • Speak louder and more clearly")
                click.echo("  • Check microphone input level in system settings")

        click.echo("\n" + "=" * 70)
        click.echo("Audio test complete!")
        click.echo("=" * 70)
        click.echo()

    except Exception as e:
        logger.error(f"Audio test failed: {e}")
        logger.debug("Full traceback:", exc_info=True)
        click.echo(f"\n✗ Test failed: {e}")
        click.echo("\nPlease check your audio devices and try again.")
        sys.exit(1)


if __name__ == "__main__":
    cli()
