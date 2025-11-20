# Voice Interview Agent - User Guide

## Overview

The Voice Interview Agent is a command-line tool that conducts voice-based interviews using PDF questionnaires. The agent speaks questions to you and records your spoken responses, then exports the conversation to CSV format for analysis.

## Installation

```bash
# Install the package
pip install -e .

# Verify installation
python -m conversation_agent.cli --help
```

## Quick Start

### 1. Prepare a PDF Questionnaire

Create a PDF with one question per line:

```
What is your name?
What is your current role?
What are your career goals?
```

### 2. Test Audio Devices

Before starting an interview, test your microphone and speakers:

```bash
python -m conversation_agent.cli test-audio --test-all
```

### 3. Start an Interview

```bash
python -m conversation_agent.cli start path/to/questionnaire.pdf
```

The agent will:
1. Load questions from the PDF
2. Initialize speech systems (TTS/STT)
3. Ask you to confirm you're ready
4. Conduct the interview question by question
5. Save the transcript to CSV

## CLI Commands

### `interview` (Main Command)

The main entry point with global options:

```bash
python -m conversation_agent.cli [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose      Enable debug logging
  --log-file PATH    Log to file for debugging
  --help            Show help message
```

### `start` - Start Interview

Start a new voice interview from a PDF questionnaire.

```bash
python -m conversation_agent.cli start PDF_PATH [OPTIONS]
```

**Required Arguments:**
- `PDF_PATH`: Path to PDF file containing questions

**Options:**
- `-o, --output-dir PATH`: Custom output directory for transcripts (default: `./interview_transcripts`)
- `--no-confirmation`: Disable answer confirmation prompts
- `--no-metadata`: Exclude metadata from CSV export
- `--tts-rate INT`: TTS speech rate in words/min (default: 150)
- `--stt-model CHOICE`: Whisper model size: `tiny|base|small|medium|large` (default: `base`)

**Examples:**

```bash
# Basic usage
python -m conversation_agent.cli start questionnaire.pdf

# With custom settings
python -m conversation_agent.cli start questionnaire.pdf \
  --output-dir ./my_transcripts \
  --stt-model small \
  --tts-rate 175

# Skip confirmation prompts
python -m conversation_agent.cli start questionnaire.pdf --no-confirmation
```

**During the Interview:**

You can say:
- `"repeat"` - Hear the question again
- `"clarify"` - Get more context about the question
- `"skip"` - Skip to the next question
- Press `Ctrl+C` - Exit early (partial transcript will be saved)

### `config` - View Configuration

Display current TTS/STT settings and available options.

```bash
python -m conversation_agent.cli config [OPTIONS]
```

**Options:**
- `--show-tts`: Show only TTS settings
- `--show-stt`: Show only STT settings
- `--show-all`: Show all settings (default)

**Examples:**

```bash
# View all configuration
python -m conversation_agent.cli config

# View only TTS settings
python -m conversation_agent.cli config --show-tts

# View available Whisper models
python -m conversation_agent.cli config --show-stt
```

### `test-audio` - Test Audio Devices

Test your microphone and speakers before starting an interview.

```bash
python -m conversation_agent.cli test-audio [OPTIONS]
```

**Options:**
- `--tts-test`: Test text-to-speech only
- `--stt-test`: Test speech-to-text only
- `--test-all`: Test both TTS and STT (default)

**Examples:**

```bash
# Test all audio systems
python -m conversation_agent.cli test-audio

# Test microphone only
python -m conversation_agent.cli test-audio --stt-test
```

## Configuration

### Environment Variables

Customize settings via environment variables:

```bash
# TTS Configuration (Piper - default, high-quality neural voice)
export TTS_PROVIDER=piper                    # Provider: piper (default) or pyttsx3 (fallback)
export TTS_VOLUME=0.9                        # Volume (0.0-1.0)
export TTS_PIPER_MODEL_PATH=models/tts/piper/en_US-lessac-medium.onnx
export TTS_PIPER_SAMPLE_RATE=22050           # Sample rate in Hz

# TTS Configuration (pyttsx3 - fallback, system TTS)
export TTS_PROVIDER=pyttsx3                  # Switch to system TTS if needed
export TTS_RATE=150                          # Words per minute (50-400, pyttsx3 only)
export TTS_VOICE="voice_id"                  # Specific voice ID (pyttsx3 only)

# STT Configuration
export STT_MODEL_SIZE=base          # tiny|base|small|medium|large
export STT_LANGUAGE=en              # Language code
export STT_DEVICE=cpu               # cpu or cuda (for GPU)

# Export Configuration
export EXPORT_OUTPUT_DIRECTORY="./transcripts"
export EXPORT_INCLUDE_METADATA=true
export EXPORT_CSV_ENCODING=utf-8
```

### TTS Provider Selection

The agent supports two TTS providers:

| Provider | Quality | Speed | Notes |
|----------|---------|-------|-------|
| **Piper** (default) | 9/10 - Neural, natural | Fast (RTF ~0.5) | High-quality neural voice, ~60MB model |
| **pyttsx3** (fallback) | 1/10 - Robotic | Very fast | System TTS, no downloads needed |

**Switching providers:**
```bash
# Use Piper (default, high-quality)
export TTS_PROVIDER=piper

# Use pyttsx3 (if Piper has issues)
export TTS_PROVIDER=pyttsx3
```

**Note**: Piper models are automatically included in `models/tts/piper/`. On first use, the agent will use the pre-downloaded `en_US-lessac-medium` voice.

### Whisper Model Selection

Choose based on your needs:

| Model | Speed | Accuracy | Memory | Best For |
|-------|-------|----------|--------|----------|
| `tiny` | Very fast | Lower | ~1GB | Quick testing |
| `base` | Fast | Good | ~1GB | Most use cases (**recommended**) |
| `small` | Medium | Better | ~2GB | Higher accuracy needs |
| `medium` | Slower | High | ~5GB | Professional transcription |
| `large` | Slowest | Highest | ~10GB | Maximum accuracy (GPU recommended) |

## Output Format

Interviews are exported to CSV with the following structure:

### With Metadata (default):

| Column | Description |
|--------|-------------|
| `question_number` | Sequential question number (1-indexed) |
| `question_id` | Unique question UUID |
| `question_text` | The question text |
| `response_text` | Transcribed user response |
| `timestamp` | Response timestamp (ISO 8601) |
| `confidence` | Transcription confidence (0.0-1.0) |
| `retry_count` | Number of retry attempts |
| `clarification_requested` | Boolean flag |
| `skipped` | Whether question was skipped |
| `duration_seconds` | Time taken for the turn |

### Without Metadata (`--no-metadata`):

| Column | Description |
|--------|-------------|
| `question_number` | Sequential number |
| `question_id` | Unique UUID |
| `question_text` | Question |
| `response_text` | Response |
| `timestamp` | Timestamp |

## Troubleshooting

### "No microphone detected"

**Problem**: System cannot find your microphone

**Solutions**:
1. Check microphone is plugged in and enabled in system settings
2. Ensure microphone permissions are granted to Terminal/Python
3. Try `python -m conversation_agent.cli test-audio --stt-test` to diagnose
4. Check system audio input device is set correctly

### "No speech detected" or Poor Transcription

**Problem**: Whisper cannot transcribe your speech accurately

**Solutions**:
1. Speak louder and more clearly
2. Move closer to the microphone
3. Reduce background noise
4. Use a larger Whisper model: `--stt-model small` or `--stt-model medium`
5. Check microphone input level in system settings

### "TTS not working" or No Audio Output

**Problem**: Cannot hear the agent speaking

**Solutions**:
1. Check speaker volume and connections
2. Verify output device in system sound settings
3. Try different TTS voice: `python -m conversation_agent.cli config --show-tts`
4. Test with `python -m conversation_agent.cli test-audio --tts-test`

### Slow Performance

**Problem**: Long delays between questions or during transcription

**Solutions**:
1. Use smaller Whisper model: `--stt-model tiny` or `--stt-model base`
2. Ensure you're using CPU mode if no GPU: `export STT_DEVICE=cpu`
3. Close other applications to free up resources
4. For persistent issues, consider using GPU acceleration with CUDA

### "Failed to parse PDF"

**Problem**: Cannot extract questions from PDF

**Solutions**:
1. Ensure PDF contains actual text (not scanned images)
2. Verify one question per line format
3. Try exporting/recreating the PDF
4. Check PDF is not password-protected

## Advanced Usage

### Debugging with Verbose Logging

```bash
python -m conversation_agent.cli -v start questionnaire.pdf
```

### Logging to File

```bash
python -m conversation_agent.cli --log-file debug.log start questionnaire.pdf
```

### Custom CSV Filename

The default filename format is `interview_{timestamp}.csv`. To customize:

```bash
export EXPORT_FILENAME_FORMAT="session_{session_id}.csv"
python -m conversation_agent.cli start questionnaire.pdf
```

## Tips for Best Results

1. **Quiet Environment**: Conduct interviews in a quiet room with minimal background noise
2. **Quality Microphone**: Use a decent microphone for better transcription accuracy
3. **Clear Speech**: Speak clearly and at a moderate pace
4. **Test First**: Always run `test-audio` before important interviews
5. **Model Selection**: Start with `base` model, upgrade to `small` if accuracy is insufficient
6. **Save Regularly**: The tool auto-saves after each question, so Ctrl+C is safe
7. **Review Transcripts**: Always review CSV output for accuracy

## Example Workflow

```bash
# 1. Set up environment
export STT_MODEL_SIZE=small
export EXPORT_OUTPUT_DIRECTORY="./job_interviews"

# 2. Test audio
python -m conversation_agent.cli test-audio

# 3. Start interview
python -m conversation_agent.cli start job_questionnaire.pdf

# 4. Review output
ls -lh ./job_interviews/
cat ./job_interviews/interview_*.csv
```

## Getting Help

- View command help: `python -m conversation_agent.cli --help`
- View subcommand help: `python -m conversation_agent.cli start --help`
- Check configuration: `python -m conversation_agent.cli config`
- Report issues: https://github.com/anthropics/claude-code/issues

## Next Steps

- See `docs/phases/phase-06-cli.md` for technical implementation details
- Check `examples/` directory for sample questionnaires
- Review `docs/TROUBLESHOOTING.md` for additional help
