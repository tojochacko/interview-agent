# Modern TTS Alternatives to pyttsx3: Comprehensive Comparison

**Research Date:** 2025-11-20
**Context:** Voice Interview Agent - Local/Offline TTS Requirements
**Current Implementation:** pyttsx3 (robotic, low quality)

---

## Executive Summary

This document compares modern Python TTS libraries suitable for replacing pyttsx3 in a voice interview agent that requires:
- High-quality, natural-sounding speech
- Local/offline processing (no cloud APIs)
- Cross-platform support (macOS/Linux/Windows)
- Reasonable real-time performance

### Top Recommendations

1. **Piper TTS** - Best overall balance of quality, speed, and ease of use
2. **MeloTTS** - Excellent for multilingual needs with MIT license
3. **Kokoro TTS** - Ultra-lightweight with surprisingly good quality
4. **StyleTTS2** - Highest quality but more complex setup

---

## Detailed Comparisons

### 1. Piper TTS ⭐ RECOMMENDED

**GitHub:** https://github.com/rhasspy/piper
**Status:** Active (spiritual successor to Mimic 3)
**License:** MIT

#### Quality Assessment
- **Voice Naturalness:** 9/10 - "Most natural sounding speech" among open-source options
- **Characteristics:** Nearly human-like intonation and timbre for English voices
- **Languages:** 40+ languages with 100+ voices
- **Trade-offs:** Pre-trained voices only (no voice cloning)

#### Installation Complexity
**Ease:** ⭐⭐⭐⭐⭐ Very Easy

```bash
# Simple pip installation
pip install piper-tts

# Usage
echo 'Welcome to the world of speech synthesis!' | piper \
  --model en_US-lessac-medium \
  --output_file welcome.wav
```

Python API:
```python
from piper import PiperVoice

voice = PiperVoice.load(model_path="en_US-lessac-medium")
with open("output.wav", "wb") as f:
    voice.synthesize("Hello world!", f)
```

#### Performance/Speed
- **RTF (Real-Time Factor):** ~0.5 (excellent)
- **Latency:** Very low - processes short texts in <1 second
- **CPU Performance:** Runs on Raspberry Pi 4 smoothly
- **Architecture:** VITS + ONNX Runtime (C++ core)

#### Platform Support
- Linux: ✅ Full support
- macOS: ✅ Full support
- Windows: ✅ Full support
- ARM (Raspberry Pi): ✅ Optimized

#### Limitations
- No voice cloning capability
- Pre-trained models only (no custom training)
- Voice customization limited to available models

#### Best For
- Production voice agents requiring consistent quality
- Edge devices and embedded systems
- Projects needing fast, reliable TTS without GPU

---

### 2. MeloTTS

**GitHub:** https://github.com/myshell-ai/MeloTTS
**Status:** Active
**License:** MIT (free for commercial use)

#### Quality Assessment
- **Voice Naturalness:** 8/10 - Natural-sounding across multiple languages
- **Characteristics:** Optimized for real-time inference
- **Languages:** English, Spanish, French, Chinese, Japanese, Korean
- **Trade-offs:** No voice cloning, but excellent multilingual support

#### Installation Complexity
**Ease:** ⭐⭐⭐⭐ Easy

```bash
git clone https://github.com/myshell-ai/MeloTTS.git
cd MeloTTS
pip install -e .
python -m unidic download
```

Python API:
```python
from melo.api import TTS

tts = TTS(language='EN')
speaker_ids = tts.hps.data.spk2id
audio = tts.tts_to_file("Hello world!", speaker_ids['EN-US'], "output.wav")
```

#### Performance/Speed
- **RTF:** <1.0 (fast)
- **Latency:** Very low - optimized for dialogue
- **CPU Performance:** Fast enough for real-time on CPU (no GPU required)
- **Architecture:** Optimized neural TTS

#### Platform Support
- Linux: ✅ Full support
- macOS: ⚠️ Docker recommended for compatibility
- Windows: ⚠️ Docker recommended for compatibility
- Docker: ✅ Recommended for cross-platform consistency

#### Limitations
- Limited to 6 languages
- No voice cloning
- Windows/macOS may need Docker for stability

#### Best For
- Multilingual applications
- Commercial projects (MIT license)
- CPU-only environments
- Projects requiring low latency dialogue

---

### 3. Kokoro TTS

**GitHub:** https://github.com/hexgrad/kokoro
**Status:** Very Active (2025)
**License:** Apache 2.0

#### Quality Assessment
- **Voice Naturalness:** 7.5/10 - Surprisingly good for size
- **Model Size:** Only 82M parameters (~350MB)
- **Languages:** 8 languages, 54+ voices
- **Characteristics:** Captures speaker timbre and prosody well

#### Installation Complexity
**Ease:** ⭐⭐⭐⭐⭐ Very Easy

```bash
pip install kokoro soundfile
# Linux
apt-get install espeak-ng
# macOS
brew install espeak
```

Python API:
```python
from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code='a')  # 'a' = American English
audio, sample_rate = pipeline("Hello world!")
sf.write("output.wav", audio, sample_rate)
```

#### Performance/Speed
- **RTF:** Extremely fast (15-95x real-time on high-end GPUs)
- **Latency:** 2-3 seconds on RTX 3050M
- **CPU Performance:** Designed for CPU efficiency
- **VRAM:** Only 2GB required

#### Platform Support
- Linux: ✅ Full support
- macOS: ✅ Full support
- Windows: ✅ Full support
- Browser: ✅ Can run in JavaScript (Transformers.js)

#### Limitations
- Quality lower than StyleTTS2 or XTTS-v2
- Smaller voice selection than Piper
- Relatively new (may have edge cases)

#### Best For
- Resource-constrained environments
- Offline-first applications
- Fast prototyping
- Lightweight deployments

---

### 4. StyleTTS2

**GitHub:** https://github.com/yl4579/StyleTTS2
**Status:** Active
**License:** MIT

#### Quality Assessment
- **Voice Naturalness:** 9.5/10 - Surpasses human recordings on single-speaker datasets
- **Characteristics:** Cleanest audio output, excellent timbre matching
- **Voice Cloning:** Yes - 5-10 second reference samples
- **Trade-offs:** Prosody can sound slightly robotic

#### Installation Complexity
**Ease:** ⭐⭐⭐ Moderate

```bash
# Requires Python 3.9-3.10
conda create -n styletts2 python=3.10
conda activate styletts2

# Install from pip package
pip install styletts2

# Or from source
git clone https://github.com/yl4579/StyleTTS2.git
cd StyleTTS2
pip install -e .
```

#### Performance/Speed
- **RTF:** 0.5-1.0 on high-end GPUs
- **Speed:** 15-95x real-time on RTX 4090
- **VRAM:** 2GB minimum, 4GB+ recommended
- **CPU Support:** Yes, but much slower

#### Platform Support
- Linux: ✅ Full support with CUDA
- macOS: ⚠️ CPU only (slower)
- Windows: ✅ Full support with CUDA
- GPU: Highly recommended for good performance

#### Limitations
- Prosody less natural than Coqui XTTS-v2
- GPU strongly recommended
- More complex setup than Piper/Kokoro
- Phoneme converter issues can cause strange annunciations

#### Best For
- High-quality voice cloning projects
- Applications where audio cleanliness is critical
- Projects with GPU access
- Research and experimentation

---

### 5. Coqui TTS (XTTS-v2)

**GitHub:** https://github.com/coqui-ai/TTS
**Status:** ⚠️ Maintenance mode (Idiap fork: https://github.com/idiap/coqui-ai-TTS)
**License:** MPL 2.0 (commercial restrictions)

#### Quality Assessment
- **Voice Naturalness:** 9/10 - Superior prosody and inflection
- **TTS Arena ELO Score:** 1200 (higher than StyleTTS2's 1164)
- **Voice Cloning:** Yes - excellent cross-lingual cloning
- **Languages:** 1100+ languages supported
- **Trade-offs:** May have artifacts, resource-intensive

#### Installation Complexity
**Ease:** ⭐⭐⭐ Moderate

```bash
pip install TTS

# Or from source
git clone https://github.com/coqui-ai/TTS/
cd TTS
make system-deps  # Linux only
make install
```

Python API:
```python
from TTS.api import TTS

tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
tts.tts_to_file(text="Hello world!", file_path="output.wav")

# Voice cloning
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
tts.tts_to_file(
    text="Hello from cloned voice",
    file_path="output.wav",
    speaker_wav="reference.wav",
    language="en"
)
```

#### Performance/Speed
- **RTF:** 1.5-3.0 (slower than Piper/MeloTTS)
- **Latency:** Higher - not suitable for real-time on CPU
- **GPU:** Required for acceptable performance
- **VRAM:** 4-8GB recommended

#### Platform Support
- Linux: ✅ Full support
- macOS: ⚠️ Limited (CPU only, slow)
- Windows: ⚠️ GPU setup can be challenging
- Docker: ✅ Recommended for consistency

#### Limitations
- Project in maintenance mode (original company defunct)
- Commercial license restrictions (MPL 2.0)
- Requires powerful GPU for real-time
- High resource consumption
- Complex setup compared to alternatives

#### Best For
- Narration and audiobook generation
- Voice cloning across languages
- Projects where prosody/expression is critical
- Non-commercial or research use

---

### 6. F5-TTS

**GitHub:** https://github.com/SWivid/F5-TTS
**Status:** Very Active (v1 released March 2025)
**License:** MIT

#### Quality Assessment
- **Voice Naturalness:** 9/10 - "ElevenLabs-level" quality
- **Architecture:** Flow matching (not diffusion) - 30 steps vs 100s
- **Characteristics:** Complex speech patterns, natural prosody
- **Voice Cloning:** Yes - zero-shot cloning

#### Installation Complexity
**Ease:** ⭐⭐ Complex

```bash
conda create -n f5-tts python=3.11
conda activate f5-tts

# Install PyTorch with CUDA
pip install torch==2.4.0+cu124 torchaudio==2.4.0+cu124 \
    --extra-index-url https://download.pytorch.org/whl/cu124

# Install F5-TTS
git clone https://github.com/SWivid/F5-TTS.git
cd F5-TTS
pip install -e .
```

Python API:
```python
# CLI usage
f5-tts_infer-cli \
    --model F5TTS_v1_Base \
    --ref_audio "reference.wav" \
    --ref_text "Reference transcription" \
    --gen_text "Text to synthesize"
```

#### Performance/Speed
- **RTF:** ~0.8-1.5 on high-end GPUs
- **Latency:** Fast (16 NFE - neural function evaluations)
- **VRAM:** 12GB+ recommended (can run on lower with optimization)
- **CPU:** Not recommended

#### Platform Support
- Linux: ✅ Full support with CUDA
- macOS: ⚠️ Limited (MPS support via MLX fork)
- Windows: ✅ Full support with CUDA
- GPU: Required

#### Limitations
- Requires GPU (preferably 12GB+ VRAM)
- Complex installation process
- No simple pip install yet
- Relatively new (may have bugs)

#### Best For
- High-quality voice synthesis projects
- Voice cloning applications
- Projects with high-end GPU access
- Research and advanced use cases

---

### 7. Bark

**GitHub:** https://github.com/suno-ai/bark
**Status:** Active
**License:** MIT

#### Quality Assessment
- **Voice Naturalness:** 8/10 - Expressive with non-speech sounds
- **Characteristics:** Can generate laughter, sighs, music
- **Voice Cloning:** Yes - unconstrained cloning available
- **Creative:** Very expressive and creative output

#### Installation Complexity
**Ease:** ⭐⭐⭐ Moderate

```bash
pip install git+https://github.com/suno-ai/bark.git

# Or
pip install bark
```

Python API:
```python
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav

preload_models()
audio_array = generate_audio("Hello, my name is Bark. [laughs]")
write_wav("output.wav", SAMPLE_RATE, audio_array)
```

#### Performance/Speed
- **RTF:** 3-10 (slow compared to others)
- **Latency:** High - not suitable for real-time
- **GPU:** Strongly recommended
- **Generation Time:** Can take minutes for longer texts

#### Platform Support
- Linux: ✅ Full support
- macOS: ✅ CPU/MPS support
- Windows: ✅ Full support
- CPU: ⚠️ Very slow but functional

#### Limitations
- Very slow generation (minutes for paragraphs)
- High computational requirements
- Unpredictable output (creative can mean inconsistent)
- Not suitable for real-time applications

#### Best For
- Creative audio projects
- Audiobook narration with emotional range
- Offline batch processing
- Projects where expression > speed

---

### 8. RealtimeTTS (Unified Interface)

**GitHub:** https://github.com/KoljaB/RealtimeTTS
**Status:** Very Active
**License:** MIT

#### Overview
RealtimeTTS is NOT a TTS engine itself - it's a **unified Python interface** that supports multiple TTS engines:

- OpenAI TTS, Azure, ElevenLabs (cloud - not suitable for this project)
- Piper, Coqui, StyleTTS2, Kokoro (local engines)
- System TTS, gTTS, Edge TTS

#### Installation
```bash
# Install with specific engines
pip install realtimetts[piper]
pip install realtimetts[coqui,styletts2,kokoro]
pip install realtimetts[all]  # All engines
```

#### Usage Pattern
```python
from RealtimeTTS import TextToAudioStream, CoquiEngine

engine = CoquiEngine()  # Or PiperEngine, KokoroEngine, etc.
stream = TextToAudioStream(engine)

stream.feed("Hello world")
stream.play_async()
```

#### Key Features
- **Streaming:** Process text streams with minimal latency
- **Fallback:** Automatic engine switching on errors
- **LLM Integration:** Works with streaming LLM outputs
- **Sentence Splitting:** Intelligent chunking for natural speech

#### Best For
- Projects that may need to switch TTS engines
- Integration with LLMs (ChatGPT, Claude, etc.)
- Applications requiring engine fallback/redundancy
- Developers wanting flexibility without code rewrites

---

## Comparison Matrix

| Library | Quality | Speed | Setup | CPU-Only | GPU Benefit | Voice Clone | License | Status |
|---------|---------|-------|-------|----------|-------------|-------------|---------|--------|
| **Piper** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Excellent | ⚠️ Minor | ❌ | MIT | ✅ Active |
| **MeloTTS** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Excellent | ⚠️ Minor | ❌ | MIT | ✅ Active |
| **Kokoro** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Good | ✅ Significant | ❌ | Apache 2.0 | ✅ Active |
| **StyleTTS2** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⚠️ Slow | ✅ Critical | ✅ | MIT | ✅ Active |
| **Coqui XTTS-v2** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ❌ Too slow | ✅ Critical | ✅ | MPL 2.0 | ⚠️ Maintenance |
| **F5-TTS** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ❌ Not viable | ✅ Required | ✅ | MIT | ✅ Active |
| **Bark** | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⚠️ Very slow | ✅ Critical | ✅ | MIT | ✅ Active |
| **pyttsx3** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Perfect | ❌ N/A | ❌ | MPL 2.0 | ⚠️ Stagnant |

---

## Use Case Recommendations

### For Voice Interview Agent (Current Project)

**Primary Recommendation: Piper TTS**

Reasons:
1. Best balance of quality and speed for real-time conversation
2. Works excellently on CPU (no GPU dependency)
3. Very simple installation and integration
4. Cross-platform support without issues
5. Consistent, professional voice quality
6. MIT license (no restrictions)

**Alternative: MeloTTS**

If multilingual support is needed:
- Same performance characteristics as Piper
- MIT license for commercial flexibility
- Optimized for dialogue scenarios

**Fallback: Kokoro TTS**

If resource constraints are extreme:
- Smallest footprint
- Still acceptable quality
- Very fast

### Not Recommended for This Project

**Coqui XTTS-v2:** Requires GPU, maintenance mode, license restrictions
**StyleTTS2:** GPU required, overkill for interview agent
**F5-TTS:** Too complex, GPU required
**Bark:** Too slow for real-time conversation
**pyttsx3:** Current implementation - poor quality

---

## Implementation Examples

### Piper TTS Integration

```python
"""Piper TTS Provider Implementation"""
from pathlib import Path
import subprocess
import tempfile
from typing import Optional

class PiperTTSProvider:
    """Text-to-speech provider using Piper."""

    def __init__(self, model: str = "en_US-lessac-medium", rate: int = 150):
        """
        Initialize Piper TTS provider.

        Args:
            model: Piper voice model name
            rate: Speech rate (words per minute)
        """
        self.model = model
        self.rate = rate
        self._verify_installation()

    def _verify_installation(self) -> None:
        """Verify Piper is installed."""
        try:
            subprocess.run(
                ["piper", "--version"],
                capture_output=True,
                check=True
            )
        except FileNotFoundError:
            raise RuntimeError(
                "Piper not found. Install with: pip install piper-tts"
            )

    def speak(self, text: str, output_file: Optional[Path] = None) -> None:
        """
        Convert text to speech.

        Args:
            text: Text to speak
            output_file: Optional output WAV file path
        """
        if output_file is None:
            # Create temp file and play immediately
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                output_file = Path(f.name)

        # Generate speech
        process = subprocess.Popen(
            ["piper", "--model", self.model, "--output_file", str(output_file)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        process.communicate(input=text.encode())

        if process.returncode != 0:
            raise RuntimeError(f"Piper failed: {process.stderr.decode()}")

        # Play audio (platform-specific)
        self._play_audio(output_file)

    def _play_audio(self, audio_file: Path) -> None:
        """Play audio file using system player."""
        import platform

        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", str(audio_file)])
        elif system == "Linux":
            subprocess.run(["aplay", str(audio_file)])
        elif system == "Windows":
            import winsound
            winsound.PlaySound(str(audio_file), winsound.SND_FILENAME)
```

### MeloTTS Integration

```python
"""MeloTTS Provider Implementation"""
from pathlib import Path
from typing import Optional
from melo.api import TTS

class MeloTTSProvider:
    """Text-to-speech provider using MeloTTS."""

    def __init__(self, language: str = "EN", speaker: str = "EN-US"):
        """
        Initialize MeloTTS provider.

        Args:
            language: Language code (EN, ES, FR, ZH, JP, KR)
            speaker: Speaker ID for the selected language
        """
        self.language = language
        self.speaker = speaker
        self.tts = TTS(language=language)
        self.speaker_id = self.tts.hps.data.spk2id.get(speaker)

        if self.speaker_id is None:
            available = list(self.tts.hps.data.spk2id.keys())
            raise ValueError(
                f"Speaker '{speaker}' not found. Available: {available}"
            )

    def speak(self, text: str, output_file: Optional[Path] = None) -> None:
        """
        Convert text to speech.

        Args:
            text: Text to speak
            output_file: Optional output WAV file path
        """
        if output_file is None:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                output_file = Path(f.name)

        # Generate speech
        self.tts.tts_to_file(text, self.speaker_id, str(output_file))

        # Play audio
        self._play_audio(output_file)

    def _play_audio(self, audio_file: Path) -> None:
        """Play audio file."""
        import sounddevice as sd
        import soundfile as sf

        data, samplerate = sf.read(str(audio_file))
        sd.play(data, samplerate)
        sd.wait()
```

### Kokoro TTS Integration

```python
"""Kokoro TTS Provider Implementation"""
from pathlib import Path
from typing import Optional
from kokoro import KPipeline
import soundfile as sf
import sounddevice as sd

class KokoroTTSProvider:
    """Text-to-speech provider using Kokoro."""

    def __init__(self, lang_code: str = "a"):
        """
        Initialize Kokoro TTS provider.

        Args:
            lang_code: Language code ('a' for American English, 'b' for British, etc.)
        """
        self.lang_code = lang_code
        self.pipeline = KPipeline(lang_code=lang_code)

    def speak(self, text: str, output_file: Optional[Path] = None) -> None:
        """
        Convert text to speech.

        Args:
            text: Text to speak
            output_file: Optional output WAV file path
        """
        # Generate speech
        audio, sample_rate = self.pipeline(text)

        # Save if output file specified
        if output_file:
            sf.write(str(output_file), audio, sample_rate)

        # Play audio
        sd.play(audio, sample_rate)
        sd.wait()
```

---

## Migration Path from pyttsx3

### Current pyttsx3 Code Pattern

```python
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
engine.say("Hello world")
engine.runAndWait()
```

### Migrating to Piper (Recommended)

**Step 1: Install Piper**
```bash
pip install piper-tts
```

**Step 2: Update Provider Class**

Replace your current TTS provider with the Piper implementation shown above.

**Step 3: Update Configuration**

```python
# Old: config.py
TTS_ENGINE = "pyttsx3"
TTS_RATE = 150

# New: config.py
TTS_ENGINE = "piper"
TTS_MODEL = "en_US-lessac-medium"  # or "en_US-lessac-high" for better quality
TTS_RATE = 150  # Optional - Piper uses natural pacing
```

**Step 4: Test**

```python
from conversation_agent.providers.tts.piper import PiperTTSProvider

tts = PiperTTSProvider(model="en_US-lessac-medium")
tts.speak("Testing Piper TTS in the interview agent")
```

### Available Piper Models

```
# Fast models (~5-10MB)
en_US-lessac-low
en_GB-alan-low

# Medium quality (~20MB) - RECOMMENDED
en_US-lessac-medium
en_GB-alan-medium

# High quality (~30MB)
en_US-lessac-high
en_GB-alan-high
```

Full list: https://rhasspy.github.io/piper-samples/

---

## Performance Benchmarks

### Real-Time Factor (RTF) Comparison

Lower RTF = faster generation (RTF < 1.0 means faster than real-time)

```
Piper:       RTF ~0.5   (⭐⭐⭐⭐⭐)
MeloTTS:     RTF ~0.6   (⭐⭐⭐⭐⭐)
Kokoro:      RTF ~0.4   (⭐⭐⭐⭐⭐)
StyleTTS2:   RTF ~0.8   (⭐⭐⭐⭐)
F5-TTS:      RTF ~1.2   (⭐⭐⭐)
Coqui XTTS:  RTF ~2.5   (⭐⭐)
Bark:        RTF ~8.0   (⭐)
pyttsx3:     RTF ~0.3   (⭐⭐⭐⭐⭐) - but poor quality
```

### Hardware Requirements

| Library | Min RAM | CPU | GPU | VRAM | Storage |
|---------|---------|-----|-----|------|---------|
| Piper | 512MB | ✅ Any | ❌ Not needed | - | 5-30MB |
| MeloTTS | 1GB | ✅ Any | ⚠️ Optional | - | 200MB |
| Kokoro | 1GB | ✅ Any | ⚠️ Helpful | 2GB | 350MB |
| StyleTTS2 | 4GB | ⚠️ Slow | ✅ Recommended | 4GB+ | 1GB |
| Coqui XTTS | 8GB | ❌ Too slow | ✅ Required | 6GB+ | 2GB |
| F5-TTS | 8GB | ❌ Not viable | ✅ Required | 12GB+ | 1.5GB |
| Bark | 8GB | ⚠️ Very slow | ✅ Recommended | 4GB+ | 3GB |
| pyttsx3 | 128MB | ✅ Any | ❌ Not needed | - | <1MB |

---

## Licensing Considerations

### Commercial-Friendly Licenses

- **MIT License:** Piper, MeloTTS, StyleTTS2, F5-TTS, Bark, RealtimeTTS
  - ✅ Free for commercial use
  - ✅ No attribution required (though appreciated)
  - ✅ Can modify and redistribute

- **Apache 2.0:** Kokoro
  - ✅ Free for commercial use
  - ✅ Patent grant included
  - ⚠️ Requires attribution and license notice

### Restrictive Licenses

- **MPL 2.0:** Coqui TTS, pyttsx3
  - ⚠️ Copyleft license
  - ⚠️ Modifications must be open-sourced
  - ⚠️ Commercial use allowed but with restrictions

---

## Known Issues & Gotchas

### Piper
- **Issue:** Limited voice customization
- **Workaround:** Pre-select appropriate voice model from samples
- **Issue:** No real-time streaming (generates full audio first)
- **Workaround:** Use sentence-by-sentence processing for long texts

### MeloTTS
- **Issue:** Docker recommended for macOS/Windows
- **Workaround:** Use virtual environment with careful dependency management
- **Issue:** Unidic download required for Japanese
- **Workaround:** Run `python -m unidic download` after install

### Kokoro
- **Issue:** Relatively new - potential edge cases
- **Workaround:** Test thoroughly with your specific use cases
- **Issue:** Quality lower than StyleTTS2/XTTS for some voices
- **Workaround:** Acceptable trade-off for speed and size

### StyleTTS2
- **Issue:** Strange annunciations from phoneme converter
- **Workaround:** Use different phonemizer backend or post-process
- **Issue:** High-pitched noise on older GPUs
- **Workaround:** Use CPU inference or upgrade GPU

### Coqui XTTS
- **Issue:** Project in maintenance mode
- **Workaround:** Use Idiap Research Institute fork
- **Issue:** Commercial license restrictions
- **Workaround:** Use alternatives (Piper, MeloTTS) for commercial projects

---

## Conclusion

### For the Voice Interview Agent: Use Piper TTS

**Justification:**
1. **Quality:** Near-human naturalness, perfect for professional interviews
2. **Performance:** Runs smoothly on CPU without GPU requirements
3. **Reliability:** Mature, actively maintained, production-ready
4. **Simplicity:** Easy installation, straightforward API
5. **Cross-platform:** Works on macOS/Linux/Windows without issues
6. **License:** MIT - no restrictions for any use case
7. **Size:** Small footprint (5-30MB models)
8. **Offline:** 100% local processing, no network required

**Implementation Priority:**
1. Start with Piper (`en_US-lessac-medium`)
2. Test voice quality with actual interview questions
3. Consider MeloTTS if multilingual support needed
4. Keep pyttsx3 as emergency fallback

### Future Considerations

If requirements change:
- **Need voice cloning:** StyleTTS2 or F5-TTS
- **Need extreme expressiveness:** Bark
- **Need absolute best quality:** StyleTTS2 or Coqui XTTS (with GPU)
- **Need multi-engine flexibility:** RealtimeTTS wrapper
- **Need multilingual:** MeloTTS

---

## Additional Resources

### Documentation Links
- **Piper:** https://rhasspy.github.io/piper-samples/
- **MeloTTS:** https://docs.myshell.ai/technology/melotts
- **Kokoro:** https://github.com/hexgrad/kokoro
- **StyleTTS2:** https://github.com/yl4579/StyleTTS2
- **RealtimeTTS:** https://github.com/KoljaB/RealtimeTTS

### Community & Support
- Piper: Rhasspy community forums
- MeloTTS: MyShell.ai Discord
- StyleTTS2: GitHub Issues actively monitored
- General TTS: r/MachineLearning, r/LocalLLaMA

### Benchmarks & Comparisons
- TTS Arena: https://huggingface.co/spaces/TTS-AGI/TTS-Arena
- Inferless TTS Comparison: https://www.inferless.com/learn/comparing-different-text-to-speech---tts--models-part-2

---

**Last Updated:** 2025-11-20
**Research By:** Claude Code (Sonnet 4.5)
**Next Review:** Consider when implementing Phase 7 (Production Polish)
