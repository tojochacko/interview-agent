# Modern TTS Libraries for Python: Comprehensive Research

**Research Date:** 2025-11-20
**Context:** Voice Interview Agent - Replacement for pyttsx3
**Requirements:** High-quality, local/offline, cross-platform, real-time capable

## Executive Summary

This research evaluates modern Text-to-Speech libraries as replacements for pyttsx3 in the conversation-agent-v11 project. The analysis focuses on neural TTS engines that run locally without cloud dependencies, prioritizing voice quality, performance, and ease of integration.

### Top Recommendations

1. **Piper** - Best balance of quality, speed, and resource efficiency
2. **Kokoro-82M** - Fastest, excellent quality, Apache license
3. **Coqui TTS (XTTS-v2)** - Highest quality with voice cloning (licensing concerns)

---

## Detailed Library Comparison

### 1. Piper TTS ⭐ RECOMMENDED

**Quality Assessment:** 9/10
- Neural-based, natural-sounding voices
- Multiple quality levels (low, medium, high)
- "Almost as fast as espeak, but sounds like Google TTS quality"
- Impressively natural despite efficiency

**Installation Complexity:** 2/10 (Very Easy)
```bash
pip install piper-tts
```

**Performance/Speed:** 10/10
- Fastest among neural TTS engines
- Real-time factor (RTF) < 0.5 on modern hardware
- Runs on Raspberry Pi 4 faster than real-time
- Lightweight neural models optimized for speed
- Low latency suitable for conversational applications

**Platform Support:** 10/10
- Linux (x86_64, ARM64)
- macOS (Intel, Apple Silicon)
- Windows
- Raspberry Pi

**Resource Requirements:**
- CPU-only operation (no GPU required)
- Minimal RAM footprint
- Model sizes: 10-60 MB (quality-dependent)
- Can run on embedded devices

**Limitations/Trade-offs:**
- Voice quality slightly lower than StyleTTS2/Coqui for highest-end use cases
- Limited voice customization compared to voice cloning models
- Quality levels create trade-off between speed and naturalness

**Usage Example:**
```python
from piper import PiperVoice

voice = PiperVoice.load("path/to/model.onnx")
audio = voice.synthesize("Hello from Piper TTS")
```

**License:** MIT
**Maintenance Status:** Active (rhasspy/piper)
**Community:** Large, well-established

---

### 2. Kokoro-82M ⭐ FASTEST

**Quality Assessment:** 8.5/10
- 4.35 MOS (Mean Opinion Score)
- Comparable quality to much larger models
- Natural prosody and intonation
- 54 voices across 8 languages

**Installation Complexity:** 2/10 (Very Easy)
```bash
pip install kokoro
```

**Performance/Speed:** 10/10
- **Fastest neural TTS in 2025**
- 3.2x faster than XTTSv2
- Sub-0.3 second processing time
- 82 million parameters (extremely lightweight)
- Optimized for real-time inference

**Platform Support:** 10/10
- Cross-platform (Linux, macOS, Windows)
- Portable Windows version available
- ONNX runtime support for additional optimization
- Runs without GPU

**Resource Requirements:**
- Model size: ~350 MB
- CPU-only capable
- Minimal memory footprint
- No GPU required for real-time performance

**Limitations/Trade-offs:**
- Newer project (less mature ecosystem)
- Fewer advanced features than Coqui
- Voice blending experimental

**Usage Example:**
```python
import kokoro

# Basic usage
audio = kokoro.tts("Hello from Kokoro", voice="af_bella")
```

**License:** Apache 2.0 (excellent for commercial use)
**Maintenance Status:** Active, rapidly evolving
**Community:** Growing

---

### 3. Coqui TTS (XTTS-v2)

**Quality Assessment:** 10/10
- State-of-the-art neural TTS
- Superior prosody and inflection
- Voice cloning from 6-second samples
- TTS Arena ELO: 1200 (highest rated)
- Multilingual support (17+ languages)

**Installation Complexity:** 4/10 (Moderate)
```bash
pip install TTS
```
Additional dependencies for voice cloning may be needed.

**Performance/Speed:** 6/10
- Requires GPU for real-time performance
- Streaming mode available with low latency on GPU
- 500ms latency on T4 GPU
- CPU inference too slow for real-time conversation
- 4-5 GB VRAM required

**Platform Support:** 9/10
- Linux, macOS, Windows
- Docker support
- GPU acceleration (CUDA)
- Limited CPU-only viability for real-time

**Resource Requirements:**
- GPU: 4-5 GB VRAM (strongly recommended)
- Model size: 1-2 GB
- CPU-only: Not suitable for real-time

**Limitations/Trade-offs:**
- **CRITICAL: CPML license forbids commercial use**
- GPU requirement for real-time performance
- Higher resource consumption
- Output may contain artifacts
- Slower than Piper/Kokoro

**Usage Example:**
```python
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
tts.tts_to_file(
    text="Hello from Coqui TTS",
    speaker_wav="reference_voice.wav",
    language="en",
    file_path="output.wav"
)
```

**License:** CPML (non-commercial)
**Maintenance Status:** Community-maintained (original team disbanded)
**Community:** Large but fragmented

---

### 4. StyleTTS2

**Quality Assessment:** 9/10
- Near human-level speech quality
- Cleaner audio than Coqui XTTS-v2
- TTS Arena ELO: 1164
- Excellent for single-speaker use
- Surpasses human recordings on LJSpeech dataset

**Installation Complexity:** 6/10 (Moderate-Complex)
```bash
pip install styletts2
# Or from source
git clone https://github.com/yl4579/StyleTTS2.git
pip install -r requirements.txt
```
Requires phonemizer and espeak-ng for full functionality.

**Performance/Speed:** 5/10
- Must run on GPU or TPU for production latency
- 500ms latency on T4 GPU
- 5-6 seconds for small text on laptop CPU
- Not optimized for Apple Silicon yet
- Inference faster than VITS (Coqui's base)

**Platform Support:** 8/10
- Linux, macOS, Windows
- Python 3.9-3.10 only (dependency constraints)
- GPU strongly recommended
- Limited CPU performance

**Resource Requirements:**
- GPU: Required for real-time (T4 or better)
- Training: 4x A100 GPUs used in paper
- Model downloads via HuggingFace (cached locally)

**Limitations/Trade-offs:**
- More robotic pace compared to Coqui
- GPU requirement for real-time use
- Phoneme converter can cause pronunciation issues
- Python version constraints
- Less flexible than voice cloning models

**Usage Example:**
```python
from styletts2 import tts

my_tts = tts.StyleTTS2()
my_tts.inference(
    "Hello from StyleTTS2",
    output_wav_file="output.wav",
    alpha=0.3,  # Timbre control
    beta=0.7,   # Prosody control
    diffusion_steps=10
)
```

**License:** MIT
**Maintenance Status:** Active research project
**Community:** Academic/research focus

---

### 5. Mimic 3

**Quality Assessment:** 8/10
- Very high-quality neural voices
- Over 100 voices available
- Quality levels (low, medium, high)
- VITS-based (same as Coqui)

**Installation Complexity:** 5/10 (Moderate)
```bash
pip3 install mycroft-mimic3-tts[all]
```
System dependencies required.

**Performance/Speed:** 7/10
- RTF < 1 on Raspberry Pi 4
- GPU acceleration available (--cuda flag)
- Server mode faster for repeated use
- Real-time capable on low-end devices

**Platform Support:** 9/10
- Linux, macOS, Windows
- Docker support
- Raspberry Pi optimized
- GPU optional

**Resource Requirements:**
- CPU-only capable
- Models auto-download to ~/.local/share/mycroft/mimic3
- onnxruntime-gpu for GPU acceleration

**Limitations/Trade-offs:**
- Mycroft ecosystem (more opinionated)
- Larger installation size
- Quality-speed trade-off similar to Piper

**Usage Example:**
```bash
mimic3 --voice en_US/vctk_low "Hello from Mimic3"
# Or use as server
mimic3-server
```

**License:** AGPL v3
**Maintenance Status:** Mycroft AI project
**Community:** Mycroft ecosystem

---

### 6. RealtimeTTS (Multi-Engine Framework)

**Quality Assessment:** Variable (depends on engine)
- Supports: System, Coqui, Piper, StyleTTS2, Parler, Kokoro, Edge, OpenAI, etc.
- Quality matches underlying engine

**Installation Complexity:** 3/10 (Easy with modular options)
```bash
pip install -U realtimetts[all]  # All engines
pip install -U realtimetts[coqui,piper]  # Specific engines
```

**Performance/Speed:** Variable
- Almost instantaneous conversion (library overhead minimal)
- Streaming support for LLM integration
- Performance depends on chosen engine
- Sentence-level chunking optimization

**Platform Support:** 10/10
- Cross-platform
- Multiple engine backends
- Flexible deployment

**Resource Requirements:**
- Depends on selected engine
- SystemEngine: Minimal (uses OS TTS)
- CoquiEngine: 4-5 GB VRAM
- PiperEngine: Minimal

**Limitations/Trade-offs:**
- Abstraction layer (slight complexity)
- Need to choose and configure engines
- Dependency management for multiple engines

**Usage Example:**
```python
from RealtimeTTS import TextToAudioStream, SystemEngine, CoquiEngine

# Use system TTS
stream = TextToAudioStream(SystemEngine())
stream.feed("Hello from RealtimeTTS")
stream.play_async()

# Or use Coqui engine
coqui = CoquiEngine()
stream = TextToAudioStream(coqui)
```

**License:** AGPL v3
**Maintenance Status:** Very active
**Community:** Growing

---

### 7. OuteTTS

**Quality Assessment:** 7/10
- Treats audio as language (novel approach)
- Voice cloning from speaker reference
- Experimental multilingual (EN, ZH, JA, KO)
- Only one default English voice currently

**Installation Complexity:** 4/10 (Hardware-specific)
```bash
# CPU-only
pip install outetts

# AMD GPU
CMAKE_ARGS="-DGGML_HIPBLAS=on" pip install outetts --upgrade

# Mac/Metal
CMAKE_ARGS="-DGGML_METAL=on" pip install outetts --upgrade
```

**Performance/Speed:** 7/10
- Uses llama.cpp backend
- Optimized for hardware acceleration
- Performance varies by backend

**Platform Support:** 9/10
- CPU, AMD GPU, Vulkan, Metal support
- Cross-platform
- Hardware-optimized builds

**Resource Requirements:**
- Variable (CPU to GPU)
- llama.cpp backend efficient

**Limitations/Trade-offs:**
- Very new project
- Limited voice options (currently)
- Requires speaker reference for consistency
- Experimental status

**License:** Check repository
**Maintenance Status:** Early development
**Community:** Emerging

---

## Comparison Matrix

| Library | Quality | Speed | Easy Install | CPU-Only | License | Best For |
|---------|---------|-------|--------------|----------|---------|----------|
| **Piper** | 9/10 | 10/10 | ✅ | ✅ | MIT | Production, embedded |
| **Kokoro-82M** | 8.5/10 | 10/10 | ✅ | ✅ | Apache 2.0 | Speed-critical apps |
| **Coqui XTTS-v2** | 10/10 | 6/10 | ⚠️ | ❌ | CPML | Non-commercial, quality |
| **StyleTTS2** | 9/10 | 5/10 | ⚠️ | ❌ | MIT | Research, quality |
| **Mimic 3** | 8/10 | 7/10 | ⚠️ | ✅ | AGPL v3 | Mycroft ecosystem |
| **RealtimeTTS** | Variable | Variable | ✅ | ✅ | AGPL v3 | Flexible integration |
| **OuteTTS** | 7/10 | 7/10 | ⚠️ | ✅ | TBD | Experimental |
| **pyttsx3** | 3/10 | 10/10 | ✅ | ✅ | MPL 2.0 | Legacy systems |

---

## Recommendations for Voice Interview Agent

### Primary Recommendation: Piper TTS

**Why Piper?**
1. **Excellent quality-speed balance** - Neural voices without GPU requirement
2. **Cross-platform** - Works on all target platforms (macOS, Linux, Windows)
3. **Low latency** - Suitable for real-time conversation
4. **Easy integration** - Simple Python API
5. **Minimal dependencies** - Clean installation
6. **Resource efficient** - No GPU needed, runs on Raspberry Pi
7. **MIT license** - No commercial restrictions
8. **Active maintenance** - Rhasspy project well-supported

**Implementation Path:**
```python
# Provider pattern integration
class PiperTTSProvider(TTSProvider):
    def __init__(self, model_path: str, config_path: str):
        self.voice = PiperVoice.load(model_path, config_path)

    def speak(self, text: str) -> None:
        audio = self.voice.synthesize(text)
        # Play audio via existing audio infrastructure
```

### Alternative Recommendation: Kokoro-82M

**Why Kokoro?**
- **Fastest neural TTS available** (3.2x faster than alternatives)
- **Apache license** - Excellent for commercial use
- **Simple API** - Easy to integrate
- **Excellent quality** - 4.35 MOS score
- **Newer technology** - State-of-the-art 2025 model

**Consider if:**
- Speed is absolutely critical
- Apache license preferred over MIT
- Multi-language support needed (8 languages)

### Not Recommended for This Project:

**Coqui TTS:**
- ❌ CPML license (non-commercial restriction)
- ❌ GPU requirement (adds deployment complexity)
- ❌ Higher resource consumption

**StyleTTS2:**
- ❌ GPU requirement for real-time
- ❌ Python version constraints (3.9-3.10 only)
- ❌ More complex setup
- ✅ Consider only if absolute highest quality needed

---

## Implementation Considerations

### Migration Strategy

1. **Create new provider interface** (maintains existing architecture)
2. **Abstract audio output** (reuse existing audio infrastructure)
3. **Configuration** (add model selection to settings)
4. **Testing** (ensure quality meets user expectations)
5. **Documentation** (update user guide with voice options)

### Configuration Design

```python
# config/settings.py
class TTSConfig(BaseSettings):
    provider: Literal["pyttsx3", "piper", "kokoro"] = "piper"

    # Piper-specific
    piper_model_path: Optional[str] = None
    piper_quality: Literal["low", "medium", "high"] = "medium"

    # Kokoro-specific
    kokoro_voice: str = "af_bella"

    # Legacy pyttsx3
    rate: int = 150
    volume: float = 0.9
```

### Testing Requirements

1. **Quality assessment** - A/B testing vs pyttsx3
2. **Performance benchmarking** - Latency measurements
3. **Platform testing** - macOS, Linux (Windows optional)
4. **Resource profiling** - CPU/memory usage
5. **User feedback** - Subjective quality evaluation

---

## Additional Resources

### Official Documentation
- **Piper:** https://github.com/rhasspy/piper
- **Kokoro:** https://github.com/hexgrad/kokoro
- **Coqui TTS:** https://github.com/coqui-ai/TTS (archived) / https://github.com/idiap/coqui-ai-TTS
- **StyleTTS2:** https://github.com/yl4579/StyleTTS2
- **RealtimeTTS:** https://github.com/KoljaB/RealtimeTTS

### Voice Samples
- **Piper:** https://rhasspy.github.io/piper-samples/
- **Coqui:** https://mbarnig.github.io/TTS-Models-Comparison/

### Benchmarks
- **2025 TTS Model Comparison:** https://www.inferless.com/learn/comparing-different-text-to-speech---tts--models-part-2

---

## Conclusion

For the conversation-agent-v11 project, **Piper TTS** offers the best combination of:
- Natural-sounding neural voices (massive improvement over pyttsx3)
- Real-time performance without GPU requirements
- Cross-platform support matching project requirements
- Simple integration maintaining existing architecture
- MIT license with no commercial restrictions
- Active maintenance and community support

**Kokoro-82M** is an excellent alternative if maximum speed is prioritized, with comparable quality and Apache licensing.

Both options represent significant quality improvements over pyttsx3 while maintaining the local/offline processing requirement critical to the project's design principles.

---

**Next Steps:**
1. Prototype Piper integration in separate branch
2. Benchmark performance on target hardware
3. A/B test voice quality with stakeholders
4. Plan migration path for existing users
5. Update documentation and user guide
