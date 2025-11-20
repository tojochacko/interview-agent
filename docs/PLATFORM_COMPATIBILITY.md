# Platform Compatibility Guide

## STT Provider Compatibility

### Whisper (Default)

**Platform Support**: ✅ All platforms
- macOS: ✅ Fully supported
- Linux: ✅ Fully supported
- Windows: ✅ Fully supported

**Installation**:
```bash
pip install -e ".[dev]"
```

**Usage**:
```bash
export STT_PROVIDER=whisper
export STT_MODEL_SIZE=base
```

### Parakeet (Optional)

**Platform Support**: ⚠️ Linux and Windows only
- macOS: ❌ **Not supported** (Triton dependency unavailable)
- Linux: ✅ Fully supported
- Windows: ✅ Fully supported

**Why macOS is not supported**:
Parakeet requires the NeMo toolkit, which depends on Nvidia's Triton library. Triton only supports Linux and Windows platforms and does not provide macOS builds.

**Installation** (Linux/Windows only):
```bash
pip install -e ".[dev,parakeet]"
```

**Usage** (Linux/Windows):
```bash
export STT_PROVIDER=parakeet
export STT_PARAKEET_MODEL=nvidia/parakeet-tdt-0.6b-v3
```

## TTS Provider Compatibility

### Piper TTS (Default)

**Platform Support**: ✅ All platforms
- macOS: ✅ Fully supported
- Linux: ✅ Fully supported
- Windows: ✅ Fully supported

### pyttsx3 (Fallback)

**Platform Support**: ✅ All platforms
- macOS: ✅ Fully supported
- Linux: ✅ Fully supported
- Windows: ✅ Fully supported

## Platform-Specific Installation

### macOS

```bash
# Install system dependencies
brew install portaudio

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with development dependencies (Whisper + Piper)
pip install -e ".[dev]"

# Note: Parakeet is NOT available on macOS
# Use Whisper for STT instead
export STT_PROVIDER=whisper
```

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get install portaudio19-dev python3-pyaudio

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with all features including Parakeet
pip install -e ".[dev,parakeet]"

# Use Parakeet for faster STT
export STT_PROVIDER=parakeet
export STT_PARAKEET_MODEL=nvidia/parakeet-tdt-0.6b-v3
```

### Windows

```bash
# PyAudio should install from wheels automatically

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install with all features including Parakeet
pip install -e ".[dev,parakeet]"

# Use Parakeet for faster STT
set STT_PROVIDER=parakeet
set STT_PARAKEET_MODEL=nvidia/parakeet-tdt-0.6b-v3
```

## Feature Matrix

| Feature | macOS | Linux | Windows |
|---------|-------|-------|---------|
| Whisper STT | ✅ | ✅ | ✅ |
| Parakeet STT | ❌ | ✅ | ✅ |
| Piper TTS | ✅ | ✅ | ✅ |
| pyttsx3 TTS | ✅ | ✅ | ✅ |
| PDF Parsing | ✅ | ✅ | ✅ |
| CSV Export | ✅ | ✅ | ✅ |
| Text Normalization | ✅ | ✅ | ✅ |
| CLI Interface | ✅ | ✅ | ✅ |

## GPU Support

### Whisper
- **CUDA (Nvidia)**: ✅ Supported on Linux/Windows
- **macOS (Metal)**: Limited support, CPU recommended
- **CPU**: ✅ Works on all platforms

### Parakeet
- **CUDA (Nvidia)**: ✅ Strongly recommended (50x faster)
- **CPU**: ✅ Works but significantly slower

## Recommendations by Platform

### macOS Users
**Recommended Configuration**:
```bash
export STT_PROVIDER=whisper
export STT_MODEL_SIZE=base
export STT_DEVICE=cpu
export TTS_PROVIDER=piper
```

**Performance**: Good for development and moderate use cases. Whisper on CPU is reasonably fast for short audio clips.

### Linux Users (with Nvidia GPU)
**Recommended Configuration**:
```bash
export STT_PROVIDER=parakeet
export STT_PARAKEET_MODEL=nvidia/parakeet-tdt-0.6b-v3
export STT_DEVICE=cuda
export TTS_PROVIDER=piper
```

**Performance**: Excellent - 50x faster STT with Parakeet on GPU.

### Windows Users (with Nvidia GPU)
**Recommended Configuration**:
```bash
set STT_PROVIDER=parakeet
set STT_PARAKEET_MODEL=nvidia/parakeet-tdt-0.6b-v3
set STT_DEVICE=cuda
set TTS_PROVIDER=piper
```

**Performance**: Excellent - 50x faster STT with Parakeet on GPU.

### Any Platform (CPU only)
**Recommended Configuration**:
```bash
export STT_PROVIDER=whisper
export STT_MODEL_SIZE=base
export STT_DEVICE=cpu
export TTS_PROVIDER=piper
```

**Performance**: Good for development and light usage.

## Migration Path

If you develop on macOS but deploy to Linux/Windows:

1. **Development (macOS)**:
   ```bash
   export STT_PROVIDER=whisper
   export STT_MODEL_SIZE=base
   ```

2. **Production (Linux/Windows with GPU)**:
   ```bash
   export STT_PROVIDER=parakeet
   export STT_PARAKEET_MODEL=nvidia/parakeet-tdt-0.6b-v3
   ```

Both providers implement the same `STTProvider` interface, so your code works identically on both platforms.

## Testing

Tests are designed to work on all platforms:
```bash
# Run all tests (works on all platforms)
python -m pytest tests/ -v

# Tests automatically mock NeMo/Triton on macOS
# No need to install Parakeet dependencies for testing
```

## Support

For platform-specific issues, see:
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Parakeet STT Guide](parakeet-stt-guide.md) (Linux/Windows only)
- [STT Implementation](phases/phase-03-stt-implementation.md)
