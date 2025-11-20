# Nvidia Parakeet STT Provider Guide

**Status**: Production Ready
**Version**: 1.0
**Last Updated**: 2025-11-20

## Overview

The Parakeet STT provider integrates Nvidia's state-of-the-art Parakeet-TDT speech recognition model into the conversation agent. Parakeet offers significantly faster transcription with better accuracy compared to Whisper, especially on GPU-accelerated hardware.

### Key Benefits

- **50x faster** than Whisper on GPU-accelerated hardware
- **6.05% WER** (Word Error Rate) - industry-leading accuracy
- **Multilingual support**: 25 European languages with auto-detection
- **Automatic punctuation and capitalization**
- **Word-level and segment-level timestamps**
- **Open source**: CC BY 4.0 license
- **Production-ready**: Built on Nvidia NeMo framework

## Installation

### Prerequisites

- **Python**: 3.9 or higher
- **Platform**: **Linux or Windows only** (macOS not supported due to Triton dependency)
- **PyTorch**: Latest version (installed automatically with NeMo)
- **GPU** (recommended): Nvidia GPU with CUDA support
  - Tested GPUs: A10, A100, H100, T4, V100, L4, L40
  - Minimum VRAM: 2GB
- **CPU** (fallback): Works but significantly slower

### Install Parakeet Support

**⚠️ Platform Limitation**: Parakeet requires the NeMo toolkit, which depends on Triton. Triton is **not available for macOS**. Parakeet can only be installed on **Linux or Windows**.

**On Linux/Windows:**
```bash
# Option 1: Install with Parakeet support
pip install -e ".[dev,parakeet]"

# Option 2: Add Parakeet to existing installation
pip install nemo_toolkit[asr]
```

**On macOS:**
Parakeet cannot be installed on macOS due to platform limitations. Use Whisper provider instead:
```bash
# Whisper works on all platforms including macOS
export STT_PROVIDER=whisper
export STT_MODEL_SIZE=base
```

The NeMo toolkit is approximately 500MB and will download additional models (600MB-1.1GB) on first use.

## Quick Start

### Basic Usage

```python
from conversation_agent.providers.stt import ParakeetProvider

# Initialize provider
provider = ParakeetProvider(
    model_name="nvidia/parakeet-tdt-0.6b-v3",
    language="en",
    enable_timestamps=True
)

# Transcribe audio file
result = provider.transcribe("interview_response.wav")

print(result["text"])  # "This is the transcribed text with punctuation."
print(result["language"])  # "en"
print(result["segments"])  # List of timestamped segments
```

### Using Configuration

```python
from conversation_agent.config import STTConfig

# Configure via code
config = STTConfig(
    provider="parakeet",
    parakeet_model="nvidia/parakeet-tdt-0.6b-v3",
    language="en",
    parakeet_enable_timestamps=True
)

# Get provider instance
provider = config.get_provider()
```

### Environment Variables

```bash
# Set Parakeet as STT provider
export STT_PROVIDER=parakeet
export STT_PARAKEET_MODEL=nvidia/parakeet-tdt-0.6b-v3
export STT_LANGUAGE=en
export STT_PARAKEET_ENABLE_TIMESTAMPS=true
export STT_PARAKEET_LOCAL_ATTENTION=false

# Run the interview agent
python -m conversation_agent.cli start questionnaire.pdf
```

## Available Models

### Parakeet-TDT 0.6B v3 (Recommended)

```python
provider = ParakeetProvider(model_name="nvidia/parakeet-tdt-0.6b-v3")
```

- **Size**: 600M parameters
- **Languages**: 25 European languages
- **Features**: Auto-detection, punctuation, capitalization
- **WER**: ~6.05%
- **Best for**: Production use, multilingual support

### Parakeet-TDT 0.6B v2

```python
provider = ParakeetProvider(model_name="nvidia/parakeet-tdt-0.6b-v2")
```

- **Size**: 600M parameters
- **Languages**: English only
- **Features**: Punctuation, capitalization
- **Best for**: English-only applications

### Parakeet-RNNT 1.1B

```python
provider = ParakeetProvider(model_name="nvidia/parakeet-rnnt-1.1b")
```

- **Size**: 1.1B parameters
- **Languages**: English only
- **Features**: Highest accuracy
- **WER**: ~5.5%
- **Best for**: Maximum accuracy requirements

## Supported Languages

Parakeet v3 supports 25 European languages:

```
en (English)    es (Spanish)     fr (French)      de (German)      it (Italian)
pt (Portuguese) pl (Polish)      nl (Dutch)       cs (Czech)       ro (Romanian)
hu (Hungarian)  el (Greek)       bg (Bulgarian)   hr (Croatian)    da (Danish)
fi (Finnish)    sk (Slovak)      sl (Slovenian)   sv (Swedish)     et (Estonian)
lt (Lithuanian) lv (Latvian)     mt (Maltese)     ga (Irish)       cy (Welsh)
```

### Language Detection

```python
# Auto-detect language (v3 model only)
provider = ParakeetProvider(language="")

# Or specify explicitly
provider.set_language("es")
print(provider.get_language())  # "es"
```

## Features

### Timestamps

Extract word-level and segment-level timestamps:

```python
provider = ParakeetProvider(enable_timestamps=True)
result = provider.transcribe("audio.wav")

for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")
```

Output:
```
[0.00s - 3.50s] Hello, how are you today?
[3.50s - 6.20s] I'm doing well, thank you for asking.
```

### Long-Form Audio

Process audio longer than 24 minutes using local attention:

```python
provider = ParakeetProvider(use_local_attention=True)

# Can now process up to 3 hours of audio
result = provider.transcribe("long_interview.wav")
```

- **Full attention**: Up to 24 minutes
- **Local attention**: Up to 3 hours
- **Context size**: [256, 256]

### Raw Audio Data

Transcribe from raw audio bytes:

```python
import numpy as np

# Generate or capture audio data
audio_data = np.random.randint(-32768, 32767, size=16000, dtype=np.int16).tobytes()

# Transcribe
result = provider.transcribe_audio_data(audio_data, sample_rate=16000)
```

## Performance Benchmarks

### Speed Comparison (GPU)

| Model             | Speed        | Real-time Factor |
|-------------------|--------------|------------------|
| Whisper (base)    | 5-10x        | 5-10x            |
| Parakeet (v3)     | 50x          | 50x              |
| **Speedup**       | **5-10x**    | **5-10x faster** |

### Accuracy Comparison

| Model             | WER    | Language Support |
|-------------------|--------|------------------|
| Whisper (base)    | ~8-10% | 99 languages     |
| Parakeet (v3)     | ~6.05% | 25 languages     |
| Parakeet (RNNT)   | ~5.5%  | English only     |

### Resource Usage

| Model             | Model Size | VRAM  | Download Size |
|-------------------|------------|-------|---------------|
| Whisper (base)    | 74MB       | 1GB   | 142MB         |
| Parakeet (v3)     | 600MB      | 2GB   | 600MB         |
| Parakeet (RNNT)   | 1.1GB      | 3GB   | 1.1GB         |

## Migration Guide

### From Whisper to Parakeet

**Option 1: Environment Variables**

```bash
# Before (Whisper)
export STT_PROVIDER=whisper
export STT_MODEL_SIZE=base

# After (Parakeet)
export STT_PROVIDER=parakeet
export STT_PARAKEET_MODEL=nvidia/parakeet-tdt-0.6b-v3
```

**Option 2: Configuration Code**

```python
# Before
config = STTConfig(provider="whisper", model_size="base")

# After
config = STTConfig(
    provider="parakeet",
    parakeet_model="nvidia/parakeet-tdt-0.6b-v3"
)
```

**Option 3: Direct Provider**

```python
# Before
from conversation_agent.providers.stt import WhisperProvider
provider = WhisperProvider(model_size="base")

# After
from conversation_agent.providers.stt import ParakeetProvider
provider = ParakeetProvider(model_name="nvidia/parakeet-tdt-0.6b-v3")
```

### Backward Compatibility

- ✅ All existing code continues to work
- ✅ Whisper remains default provider
- ✅ No breaking changes to `STTProvider` interface
- ✅ Interview orchestrator works with both providers

## Use Case Recommendations

### Use Parakeet When:

- ✅ You have Nvidia GPU available
- ✅ Speed is critical (production, real-time transcription)
- ✅ You need automatic punctuation/capitalization
- ✅ Working with European languages
- ✅ High accuracy (low WER) is required
- ✅ Processing large volumes of audio

### Use Whisper When:

- ✅ CPU-only environment
- ✅ Need non-European languages (e.g., Chinese, Arabic, Hindi)
- ✅ Smaller model size preferred
- ✅ Development/testing (faster setup)
- ✅ Model download bandwidth is limited

## Troubleshooting

### Installation Issues

**Problem**: `ERROR: No matching distribution found for triton` (macOS)

**Solution**:
Parakeet/NeMo is not supported on macOS due to the Triton dependency. Use Whisper instead:
```bash
# Use Whisper on macOS
export STT_PROVIDER=whisper
export STT_MODEL_SIZE=base
python -m conversation_agent.cli start questionnaire.pdf
```

**Problem**: `ModuleNotFoundError: No module named 'nemo'` (Linux/Windows)

**Solution**:
```bash
pip install nemo_toolkit[asr]
```

**Problem**: CUDA out of memory

**Solution**:
- Use smaller model: `nvidia/parakeet-tdt-0.6b-v2` instead of RNNT
- Enable local attention for long audio
- Reduce batch size if processing multiple files

### Model Loading Issues

**Problem**: Model download fails or is slow

**Solution**:
- Check internet connection
- Models are cached in `~/.cache/huggingface/`
- Manually download from HuggingFace if needed

**Problem**: `Failed to load Parakeet model`

**Solution**:
- Verify CUDA installation: `python -c "import torch; print(torch.cuda.is_available())"`
- Update PyTorch: `pip install --upgrade torch`
- Check model name is correct

### Transcription Issues

**Problem**: Poor transcription quality

**Solution**:
- Ensure audio is 16kHz, mono, WAV format
- Check language setting matches audio
- Try higher accuracy model (RNNT)

**Problem**: "Transcription failed for audio data"

**Solution**:
- Verify audio format (16-bit PCM)
- Check sample rate is correct
- Ensure audio data is not corrupted

## API Reference

### ParakeetProvider Class

```python
class ParakeetProvider(STTProvider):
    """Nvidia Parakeet-TDT Speech-to-Text provider."""

    def __init__(
        self,
        model_name: str = "nvidia/parakeet-tdt-0.6b-v3",
        language: str = "en",
        enable_timestamps: bool = True,
        use_local_attention: bool = False,
    ):
        """Initialize Parakeet provider."""
        ...

    def transcribe(self, audio_path: str) -> dict[str, Any]:
        """Transcribe audio file to text."""
        ...

    def transcribe_audio_data(
        self, audio_data: bytes, sample_rate: int = 16000
    ) -> dict[str, Any]:
        """Transcribe raw audio data to text."""
        ...

    def get_available_models(self) -> list[str]:
        """Get list of available Parakeet models."""
        ...

    def set_language(self, language: str) -> None:
        """Set the language for transcription."""
        ...

    def get_model_size(self) -> str:
        """Get current model name."""
        ...

    def get_language(self) -> str:
        """Get current language setting."""
        ...
```

### Return Format

```python
{
    "text": "Full transcription with punctuation.",
    "language": "en",
    "segments": [
        {
            "start": 0.0,
            "end": 3.5,
            "text": "Segment text."
        },
        ...
    ]
}
```

## Examples

### Example 1: Interview Transcription

```python
from conversation_agent.providers.stt import ParakeetProvider

provider = ParakeetProvider(language="en", enable_timestamps=True)

# Transcribe interview responses
questions = ["question1.wav", "question2.wav", "question3.wav"]
transcriptions = []

for audio_file in questions:
    result = provider.transcribe(audio_file)
    transcriptions.append({
        "file": audio_file,
        "text": result["text"],
        "duration": result["segments"][-1]["end"]
    })

# Export to CSV
import csv
with open("interview_transcript.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=["file", "text", "duration"])
    writer.writeheader()
    writer.writerows(transcriptions)
```

### Example 2: Real-time Transcription

```python
import sounddevice as sd
import numpy as np
from conversation_agent.providers.stt import ParakeetProvider

provider = ParakeetProvider()

# Record audio
duration = 5  # seconds
sample_rate = 16000
audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
sd.wait()

# Convert to bytes
audio_data = (audio * 32768).astype(np.int16).tobytes()

# Transcribe
result = provider.transcribe_audio_data(audio_data, sample_rate=sample_rate)
print(result["text"])
```

### Example 3: Multilingual Support

```python
from conversation_agent.providers.stt import ParakeetProvider

provider = ParakeetProvider(model_name="nvidia/parakeet-tdt-0.6b-v3")

# Process audio in different languages
audio_files = {
    "english.wav": "en",
    "spanish.wav": "es",
    "french.wav": "fr",
    "german.wav": "de"
}

for audio_file, lang in audio_files.items():
    provider.set_language(lang)
    result = provider.transcribe(audio_file)
    print(f"{lang}: {result['text']}")
```

## Related Documentation

- [Phase 3: STT Implementation](phases/phase-03-stt-implementation.md)
- [Architecture Overview](architecture/overview.md)
- [STT Provider Interface](../src/conversation_agent/providers/stt/base.py)
- [Nvidia Parakeet Blog](https://developer.nvidia.com/blog/pushing-the-boundaries-of-speech-recognition-with-nemo-parakeet-asr-models/)
- [NeMo Toolkit Documentation](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/index.html)

## Support

For issues or questions:

1. Check this guide's Troubleshooting section
2. Review the [main troubleshooting guide](TROUBLESHOOTING.md)
3. Check Nvidia NeMo documentation
4. Open an issue on GitHub

## License

Parakeet models are licensed under CC BY 4.0. See Nvidia's license terms for details.
