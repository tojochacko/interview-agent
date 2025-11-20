# Piper TTS Integration Guide

**Target:** conversation-agent-v11 Voice Interview Agent
**Current:** pyttsx3 (basic, robotic voices)
**Proposed:** Piper TTS (neural, natural voices)

## Quick Reference

**Installation:** `pip install piper-tts`
**License:** MIT
**Python:** 3.9+
**Platform:** macOS, Linux, Windows
**GPU Required:** No

---

## Installation

### Basic Installation

```bash
# Activate project virtual environment
source .venv/bin/activate

# Install Piper
pip install piper-tts

# Verify installation
python -c "import piper; print('Piper installed successfully')"
```

### Download Voice Models

Piper requires ONNX models and configuration files. Download from:
https://github.com/rhasspy/piper/releases

**Recommended for English Interview Agent:**
- `en_US-lessac-medium.onnx` (balanced quality/speed)
- `en_US-lessac-high.onnx` (highest quality)
- `en_GB-alba-medium.onnx` (British English alternative)

```bash
# Create models directory
mkdir -p models/tts/piper

# Download model and config (example for lessac-medium)
cd models/tts/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

**Model Size Reference:**
- Low quality: ~10 MB (fast, acceptable quality)
- Medium quality: ~30 MB (balanced, recommended)
- High quality: ~60 MB (best quality, slower)

---

## Python API Usage

### Basic Example

```python
from piper import PiperVoice
import wave
import pyaudio

# Load voice model
voice = PiperVoice.load(
    model_path="models/tts/piper/en_US-lessac-medium.onnx",
    config_path="models/tts/piper/en_US-lessac-medium.onnx.json"
)

# Synthesize text to audio
text = "Hello, I'm your interview assistant. Let's begin with the first question."
audio_data = voice.synthesize(text)

# audio_data contains raw PCM audio
# Play or save as needed
```

### Save to WAV File

```python
import wave

def save_to_wav(audio_data, sample_rate, output_path):
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)

# Get audio from Piper
text = "This is a test of the Piper TTS system."
audio_bytes = voice.synthesize(text)

# Piper typically outputs at 22050 Hz
save_to_wav(audio_bytes, 22050, "output.wav")
```

### Play Audio Directly

```python
import pyaudio

def play_audio(audio_data, sample_rate=22050):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        output=True
    )

    stream.write(audio_data)
    stream.stop_stream()
    stream.close()
    p.terminate()

# Synthesize and play
audio = voice.synthesize("Welcome to your interview.")
play_audio(audio)
```

---

## Integration with Conversation Agent

### Provider Implementation

Following the existing provider pattern in `src/conversation_agent/providers/tts/`:

```python
# src/conversation_agent/providers/tts/piper_provider.py
"""Piper TTS provider implementation."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from piper import PiperVoice

from conversation_agent.providers.tts.base import TTSProvider

logger = logging.getLogger(__name__)


class PiperTTSProvider(TTSProvider):
    """Piper neural TTS provider.

    Provides high-quality neural text-to-speech using Piper models.
    Models are ONNX-based and run efficiently on CPU.
    """

    def __init__(
        self,
        model_path: str,
        config_path: Optional[str] = None,
        sample_rate: int = 22050
    ) -> None:
        """Initialize Piper TTS provider.

        Args:
            model_path: Path to ONNX model file (.onnx)
            config_path: Path to config file (.onnx.json). If None, assumes
                        same name as model_path with .json extension.
            sample_rate: Audio sample rate (default: 22050 Hz)
        """
        self.model_path = Path(model_path)
        if config_path is None:
            self.config_path = Path(f"{model_path}.json")
        else:
            self.config_path = Path(config_path)

        self.sample_rate = sample_rate
        self.voice: Optional[PiperVoice] = None

        # Validate files exist
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")

    def initialize(self) -> None:
        """Initialize the Piper voice model."""
        logger.info(f"Loading Piper model: {self.model_path}")
        self.voice = PiperVoice.load(
            str(self.model_path),
            str(self.config_path)
        )
        logger.info("Piper model loaded successfully")

    def speak(self, text: str) -> None:
        """Synthesize and play text.

        Args:
            text: Text to speak
        """
        if self.voice is None:
            self.initialize()

        logger.debug(f"Speaking: {text[:50]}...")
        audio_data = self.voice.synthesize(text)

        # Use existing audio playback infrastructure
        self._play_audio(audio_data)

    def synthesize_to_file(self, text: str, output_path: str) -> None:
        """Synthesize text and save to WAV file.

        Args:
            text: Text to synthesize
            output_path: Path to output WAV file
        """
        if self.voice is None:
            self.initialize()

        import wave

        audio_data = self.voice.synthesize(text)

        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data)

        logger.info(f"Audio saved to: {output_path}")

    def _play_audio(self, audio_data: bytes) -> None:
        """Play audio data.

        Args:
            audio_data: Raw PCM audio bytes
        """
        import pyaudio

        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            output=True
        )

        stream.write(audio_data)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def shutdown(self) -> None:
        """Clean up resources."""
        logger.info("Shutting down Piper TTS provider")
        self.voice = None
```

### Configuration Updates

```python
# src/conversation_agent/config/settings.py
from __future__ import annotations

from typing import Literal, Optional
from pydantic_settings import BaseSettings


class TTSConfig(BaseSettings):
    """TTS provider configuration."""

    provider: Literal["pyttsx3", "piper"] = "piper"

    # Piper-specific settings
    piper_model_path: Optional[str] = "models/tts/piper/en_US-lessac-medium.onnx"
    piper_config_path: Optional[str] = None  # Auto-detected if None
    piper_sample_rate: int = 22050

    # Legacy pyttsx3 settings (for backward compatibility)
    rate: int = 150
    volume: float = 0.9

    class Config:
        env_prefix = "TTS_"
```

### Provider Factory Update

```python
# src/conversation_agent/providers/tts/__init__.py
from __future__ import annotations

from typing import TYPE_CHECKING

from conversation_agent.config.settings import TTSConfig
from conversation_agent.providers.tts.base import TTSProvider
from conversation_agent.providers.tts.pyttsx3_provider import Pyttsx3TTSProvider
from conversation_agent.providers.tts.piper_provider import PiperTTSProvider

if TYPE_CHECKING:
    from conversation_agent.config.settings import TTSConfig


def create_tts_provider(config: TTSConfig) -> TTSProvider:
    """Factory function to create TTS provider based on config.

    Args:
        config: TTS configuration

    Returns:
        Configured TTS provider instance

    Raises:
        ValueError: If provider type is unknown
    """
    if config.provider == "pyttsx3":
        return Pyttsx3TTSProvider(
            rate=config.rate,
            volume=config.volume
        )
    elif config.provider == "piper":
        if config.piper_model_path is None:
            raise ValueError("piper_model_path must be set for Piper provider")
        return PiperTTSProvider(
            model_path=config.piper_model_path,
            config_path=config.piper_config_path,
            sample_rate=config.piper_sample_rate
        )
    else:
        raise ValueError(f"Unknown TTS provider: {config.provider}")


__all__ = [
    "TTSProvider",
    "Pyttsx3TTSProvider",
    "PiperTTSProvider",
    "create_tts_provider",
]
```

---

## Testing

### Unit Tests

```python
# tests/providers/tts/test_piper_provider.py
"""Tests for Piper TTS provider."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from conversation_agent.providers.tts.piper_provider import PiperTTSProvider


@pytest.fixture
def mock_model_files(tmp_path):
    """Create mock model files."""
    model_path = tmp_path / "test_model.onnx"
    config_path = tmp_path / "test_model.onnx.json"

    model_path.write_bytes(b"fake model data")
    config_path.write_text('{"sample_rate": 22050}')

    return str(model_path), str(config_path)


@pytest.fixture
def piper_provider(mock_model_files):
    """Create PiperTTSProvider instance."""
    model_path, config_path = mock_model_files
    return PiperTTSProvider(model_path=model_path, config_path=config_path)


def test_provider_initialization(piper_provider):
    """Test provider initializes correctly."""
    assert piper_provider.voice is None
    assert piper_provider.sample_rate == 22050


def test_missing_model_file():
    """Test error when model file missing."""
    with pytest.raises(FileNotFoundError, match="Model not found"):
        PiperTTSProvider(model_path="nonexistent.onnx")


@patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
def test_initialize_loads_model(mock_piper_voice, piper_provider, mock_model_files):
    """Test initialize loads Piper model."""
    model_path, config_path = mock_model_files
    mock_voice = Mock()
    mock_piper_voice.load.return_value = mock_voice

    piper_provider.initialize()

    mock_piper_voice.load.assert_called_once_with(model_path, config_path)
    assert piper_provider.voice == mock_voice


@patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
@patch.object(PiperTTSProvider, "_play_audio")
def test_speak(mock_play_audio, mock_piper_voice, piper_provider):
    """Test speak synthesizes and plays audio."""
    mock_voice = Mock()
    mock_voice.synthesize.return_value = b"audio data"
    mock_piper_voice.load.return_value = mock_voice

    piper_provider.speak("Hello world")

    mock_voice.synthesize.assert_called_once_with("Hello world")
    mock_play_audio.assert_called_once_with(b"audio data")


@patch("conversation_agent.providers.tts.piper_provider.PiperVoice")
def test_synthesize_to_file(mock_piper_voice, piper_provider, tmp_path):
    """Test synthesize_to_file creates WAV file."""
    mock_voice = Mock()
    mock_voice.synthesize.return_value = b"\x00\x01" * 100  # Fake audio
    mock_piper_voice.load.return_value = mock_voice

    output_path = tmp_path / "output.wav"
    piper_provider.synthesize_to_file("Test", str(output_path))

    assert output_path.exists()
    mock_voice.synthesize.assert_called_once_with("Test")


def test_shutdown(piper_provider):
    """Test shutdown cleans up resources."""
    piper_provider.voice = Mock()
    piper_provider.shutdown()
    assert piper_provider.voice is None
```

### Integration Test

```python
# tests/integration/test_piper_integration.py
"""Integration test for Piper TTS (requires actual model)."""
import pytest
from pathlib import Path

from conversation_agent.providers.tts.piper_provider import PiperTTSProvider


@pytest.mark.integration
@pytest.mark.skipif(
    not Path("models/tts/piper/en_US-lessac-medium.onnx").exists(),
    reason="Piper model not available"
)
def test_piper_real_synthesis(tmp_path):
    """Test Piper with real model (integration test)."""
    provider = PiperTTSProvider(
        model_path="models/tts/piper/en_US-lessac-medium.onnx"
    )

    provider.initialize()

    output_path = tmp_path / "test_output.wav"
    provider.synthesize_to_file(
        "This is a test of the Piper TTS system.",
        str(output_path)
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 1000  # Has audio data
```

---

## Performance Benchmarks

### Latency Test

```python
# scripts/benchmark_piper.py
"""Benchmark Piper TTS performance."""
import time
from conversation_agent.providers.tts.piper_provider import PiperTTSProvider


def benchmark_piper(num_iterations=10):
    """Benchmark Piper synthesis speed."""
    provider = PiperTTSProvider(
        model_path="models/tts/piper/en_US-lessac-medium.onnx"
    )
    provider.initialize()

    test_sentences = [
        "What is your name?",
        "Tell me about your previous work experience.",
        "How do you handle challenging situations at work?",
        "Where do you see yourself in five years?",
    ]

    results = []
    for sentence in test_sentences:
        start = time.time()
        for _ in range(num_iterations):
            audio = provider.voice.synthesize(sentence)
        elapsed = time.time() - start

        avg_time = elapsed / num_iterations
        results.append({
            "sentence": sentence,
            "avg_time": avg_time,
            "chars": len(sentence),
            "chars_per_sec": len(sentence) / avg_time
        })

    print("\nPiper TTS Performance Benchmark")
    print("=" * 70)
    for result in results:
        print(f"Sentence: {result['sentence']}")
        print(f"  Avg Time: {result['avg_time']:.3f}s")
        print(f"  Speed: {result['chars_per_sec']:.1f} chars/sec")
        print()

    overall_avg = sum(r["avg_time"] for r in results) / len(results)
    print(f"Overall Average: {overall_avg:.3f}s per sentence")


if __name__ == "__main__":
    benchmark_piper()
```

**Expected Results:**
- Medium quality: 0.1-0.3s per sentence (real-time)
- High quality: 0.2-0.5s per sentence (still conversational)
- Much faster than pyttsx3 with significantly better quality

---

## Environment Variables

```bash
# .env
TTS_PROVIDER=piper
TTS_PIPER_MODEL_PATH=models/tts/piper/en_US-lessac-medium.onnx
TTS_PIPER_SAMPLE_RATE=22050
```

---

## Migration Checklist

- [ ] Install piper-tts package
- [ ] Download voice model(s) to models/tts/piper/
- [ ] Implement PiperTTSProvider class
- [ ] Update TTSConfig in settings.py
- [ ] Update provider factory
- [ ] Write unit tests (>80% coverage)
- [ ] Write integration tests
- [ ] Run performance benchmarks
- [ ] Update documentation
- [ ] Test on all target platforms (macOS, Linux)
- [ ] User acceptance testing (quality comparison)
- [ ] Update CLI help text
- [ ] Create migration guide for existing users

---

## Troubleshooting

### Model Download Issues

If automatic model download fails:
```bash
# Manual download from Hugging Face
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

### Audio Playback Issues

If pyaudio causes issues on macOS:
```bash
# Install via Homebrew
brew install portaudio
pip install pyaudio
```

### Import Errors

```python
# Verify installation
python -c "import piper; print(piper.__version__)"
```

---

## Resources

- **Piper GitHub:** https://github.com/rhasspy/piper
- **Voice Models:** https://github.com/rhasspy/piper/releases
- **Hugging Face Models:** https://huggingface.co/rhasspy/piper-voices
- **Voice Samples:** https://rhasspy.github.io/piper-samples/
- **Documentation:** https://github.com/rhasspy/piper/blob/master/README.md

---

## Quality Comparison

### Before (pyttsx3)
- Robotic, mechanical sound
- Limited expressiveness
- System-dependent quality
- Fast but unnatural

### After (Piper)
- Neural, natural-sounding voices
- Good prosody and intonation
- Consistent cross-platform quality
- Fast AND natural (best of both worlds)

**Recommendation:** Start with `en_US-lessac-medium` for balanced quality/speed.
Test with actual interview questions to validate quality meets requirements.
