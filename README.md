# Voice Interview Agent

A voice-based conversational agent that conducts interviews using PDF questionnaires. The agent speaks questions to you and records your spoken responses, then exports the conversation to CSV format.

## Features

- 🎤 **Voice-based interviews** using speech-to-text and text-to-speech
- 📄 **PDF questionnaire parsing** (one question per line format)
- 🗣️ **Natural conversation** with support for repeat, clarify, and skip commands
- 💾 **CSV export** with structured data and metadata
- 🔧 **Configurable** TTS/STT settings via environment variables
- 🖥️ **CLI interface** with three main commands: start, config, test-audio
- 🎯 **Offline operation** - all processing happens locally

## Quick Start

### Prerequisites

- **Python 3.9 or higher**
- **Microphone and speakers** (or headset)
- **macOS/Linux/Windows** (tested on macOS)

### System Dependencies

**macOS:**
```bash
brew install portaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**Windows:**
- PyAudio wheels available on PyPI (should work out of box)

### Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create and activate virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# Or on Windows: .venv\Scripts\activate
```

3. **Install the package:**
```bash
pip install -e ".[dev]"
```

This installs all dependencies including:
- `pypdf` - PDF parsing
- `pyttsx3` - Text-to-speech (offline)
- `openai-whisper` - Speech-to-text (local)
- `pyaudio` - Audio I/O
- `click` - CLI interface

## Usage

### Test Audio Devices First

Before starting your first interview, test your audio setup:

```bash
python -m conversation_agent.cli test-audio
```

This will test both your microphone (STT) and speakers (TTS).

### Start an Interview

```bash
python -m conversation_agent.cli start path/to/questionnaire.pdf
```

**During the interview, you can:**
- Say **"repeat"** to hear the question again
- Say **"clarify"** to get more context
- Say **"skip"** to skip the current question
- Press **Ctrl+C** to exit early (partial transcript will be saved)

**Example session:**
```bash
$ python -m conversation_agent.cli start examples/job_interview_questionnaire.pdf

Starting Voice Interview Agent...
Loading questionnaire: examples/job_interview_questionnaire.pdf
Loaded 10 questions from PDF

Initializing speech systems...

======================================================================
VOICE INTERVIEW - INSTRUCTIONS
======================================================================
• Speak clearly into your microphone
• The agent will ask you questions from the questionnaire
• You can say 'repeat' to hear the question again
• You can say 'clarify' to get more context
• Say 'skip' to skip a question
• Press Ctrl+C to exit early (partial transcript will be saved)
======================================================================

Ready to begin the interview? [Y/n]: y

[Agent conducts interview...]

✓ Transcript saved to: ./interview_transcripts/interview_20251117_143052.csv

======================================================================
INTERVIEW SUMMARY
======================================================================
Questions answered: 8/10
Questions skipped: 2
Duration: 245.3 seconds
Status: completed
======================================================================
```

### Command Options

**Customize output directory:**
```bash
python -m conversation_agent.cli start questionnaire.pdf \
  --output-dir ./my_interviews
```

**Use different Whisper model for better accuracy:**
```bash
python -m conversation_agent.cli start questionnaire.pdf \
  --stt-model small
```

**Adjust TTS speech rate:**
```bash
python -m conversation_agent.cli start questionnaire.pdf \
  --tts-rate 175
```

**Skip confirmation prompts:**
```bash
python -m conversation_agent.cli start questionnaire.pdf \
  --no-confirmation
```

**Export without metadata (simpler CSV):**
```bash
python -m conversation_agent.cli start questionnaire.pdf \
  --no-metadata
```

### View Configuration

Check current TTS/STT settings and available options:

```bash
python -m conversation_agent.cli config
```

View specific settings:
```bash
python -m conversation_agent.cli config --show-tts   # TTS settings only
python -m conversation_agent.cli config --show-stt   # STT settings only
```

### Enable Debug Logging

```bash
python -m conversation_agent.cli -v start questionnaire.pdf
```

Or log to file:
```bash
python -m conversation_agent.cli --log-file debug.log start questionnaire.pdf
```

## Configuration

### Environment Variables

Customize settings using environment variables:

```bash
# TTS Configuration
export TTS_RATE=150                 # Speech rate (50-400 words/min)
export TTS_VOLUME=0.9               # Volume (0.0-1.0)
export TTS_VOICE="voice_id"         # Specific voice ID

# STT Configuration
export STT_MODEL_SIZE=base          # tiny|base|small|medium|large
export STT_LANGUAGE=en              # Language code
export STT_DEVICE=cpu               # cpu or cuda (for GPU)

# Export Configuration
export EXPORT_OUTPUT_DIRECTORY="./transcripts"
export EXPORT_INCLUDE_METADATA=true
```

### Whisper Model Selection

Choose based on your needs:

| Model | Speed | Accuracy | Memory | Best For |
|-------|-------|----------|--------|----------|
| `tiny` | Very fast | Lower | ~1GB | Quick testing |
| **`base`** | Fast | Good | ~1GB | **Most use cases (recommended)** |
| `small` | Medium | Better | ~2GB | Higher accuracy needs |
| `medium` | Slower | High | ~5GB | Professional transcription |
| `large` | Slowest | Highest | ~10GB | Maximum accuracy (GPU recommended) |

## Creating Questionnaires

Create a PDF with **one question per line**:

```
What is your name?
What is your current role?
What are your career goals?
Why are you interested in this position?
What are your greatest strengths?
```

See `examples/job_interview_questionnaire.pdf` for a sample.

## Output Format

Interviews are exported to CSV with the following columns:

**With metadata (default):**
- `question_number` - Sequential number (1-indexed)
- `question_id` - Unique UUID
- `question_text` - The question
- `response_text` - Transcribed response
- `timestamp` - ISO 8601 timestamp
- `confidence` - Transcription confidence (0.0-1.0)
- `retry_count` - Number of retries
- `clarification_requested` - Boolean flag
- `skipped` - Whether question was skipped
- `duration_seconds` - Time taken

**Without metadata (`--no-metadata`):**
- `question_number`, `question_id`, `question_text`, `response_text`, `timestamp`

## Troubleshooting

### "No microphone detected"

**Solutions:**
1. Check microphone is connected and enabled
2. Grant microphone permissions to Terminal/Python
3. Test with: `python -m conversation_agent.cli test-audio --stt-test`

### Poor transcription accuracy

**Solutions:**
1. Speak louder and more clearly
2. Reduce background noise
3. Use larger Whisper model: `--stt-model small`
4. Check microphone input level in system settings

### No audio output (TTS not working)

**Solutions:**
1. Check speaker volume and connections
2. Verify output device in system settings
3. Test with: `python -m conversation_agent.cli test-audio --tts-test`

### Slow performance

**Solutions:**
1. Use smaller Whisper model: `--stt-model tiny` or `--stt-model base`
2. Ensure CPU mode if no GPU: `export STT_DEVICE=cpu`
3. Close other applications

See [docs/interview_agent_guide.md](docs/interview_agent_guide.md) for detailed troubleshooting.

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_cli_interview.py -v
```

### Code Quality

```bash
# Check code style
python -m ruff check src/ tests/

# Auto-fix issues
python -m ruff check --fix src/ tests/
```

### Project Structure

```
conversation-agent-v11/
├── src/conversation_agent/
│   ├── cli/                   # CLI commands (Phase 6)
│   │   ├── interview.py       # Main CLI implementation
│   │   └── __main__.py        # Entry point
│   ├── config/                # Configuration modules
│   │   ├── tts_config.py      # TTS settings
│   │   ├── stt_config.py      # STT settings
│   │   └── export_config.py   # Export settings
│   ├── core/                  # Business logic
│   │   ├── pdf_parser.py      # PDF question extraction (Phase 1)
│   │   ├── interview.py       # Interview orchestration (Phase 4)
│   │   ├── intent_recognizer.py
│   │   ├── conversation_state.py
│   │   ├── csv_exporter.py    # CSV export (Phase 5)
│   │   └── audio.py           # Audio management
│   ├── models/                # Data models (Phase 1)
│   │   └── interview.py       # Question, Response, Turn, Session
│   ├── providers/             # TTS/STT providers
│   │   ├── tts/               # Text-to-speech (Phase 2)
│   │   │   ├── base.py
│   │   │   └── pyttsx3_provider.py
│   │   └── stt/               # Speech-to-text (Phase 3)
│   │       ├── base.py
│   │       └── whisper_provider.py
│   └── utils/                 # Utilities
│       └── logging_config.py  # Colored logging
├── tests/                     # 205 tests, 79% coverage
├── docs/                      # Documentation
│   ├── interview_agent_guide.md    # User guide
│   ├── phases/                     # Phase documentation
│   └── architecture/               # Design docs
├── examples/                  # Demo scripts and sample PDFs
└── features/                  # Feature planning documents
```

## Documentation

- **[User Guide](docs/interview_agent_guide.md)** - Complete usage instructions
- **[Phase 6 Documentation](docs/phases/phase-06-cli.md)** - CLI implementation details
- **[Architecture Overview](docs/architecture/overview.md)** - System design
- **[Development Guidelines](CLAUDE.md)** - Code standards and principles

## Project Status

**Current Phase: 6 of 7 COMPLETE** ✅

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Foundation & PDF Processing (84% coverage) |
| Phase 2 | ✅ Complete | TTS Integration (pyttsx3) (82% coverage) |
| Phase 3 | ✅ Complete | STT Integration (Whisper) (91% coverage) |
| Phase 4 | ✅ Complete | Conversation Orchestration (53% coverage) |
| Phase 5 | ✅ Complete | CSV Export & Data Persistence (100% coverage) |
| **Phase 6** | **✅ Complete** | **CLI Interface & Integration (81% coverage)** |
| Phase 7 | 📋 Planned | Polish & Production Readiness |

**Overall Test Coverage: 79%** (205 tests passing)

## Contributing

See [CLAUDE.md](CLAUDE.md) for:
- Code structure guidelines (KISS, YAGNI principles)
- File/function/class size limits
- Import conventions
- Testing requirements

## License

This is a demo/testing project for conversational agent development.

## Acknowledgments

- **pyttsx3** - Offline text-to-speech
- **OpenAI Whisper** - Local speech-to-text
- **pypdf** - PDF parsing
- **Click** - CLI framework
