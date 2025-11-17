"""Audio manager for microphone capture and playback."""

from __future__ import annotations

import wave
from pathlib import Path
from typing import Optional  # noqa: UP045

import numpy as np


class AudioError(Exception):
    """Exception raised when audio operations fail."""

    pass


class AudioManager:
    """Manager for audio input/output operations using PyAudio.

    This class provides a wrapper around PyAudio for recording audio from
    microphones, detecting silence, and saving recordings to WAV files.

    Example:
        audio_mgr = AudioManager(sample_rate=16000)
        devices = audio_mgr.list_devices()
        audio_data = audio_mgr.record(duration=5.0)
        audio_mgr.save_to_wav(audio_data, "recording.wav")
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_size: int = 1024,
        channels: int = 1,
        format_bits: int = 16,
    ):
        """Initialize audio manager.

        Args:
            sample_rate: Sample rate in Hz (default: 16000 for Whisper).
            chunk_size: Number of frames per buffer (default: 1024).
            channels: Number of audio channels (1=mono, 2=stereo).
            format_bits: Bit depth (8 or 16).

        Raises:
            AudioError: If PyAudio initialization fails.
        """
        try:
            import pyaudio

            self.pyaudio = pyaudio.PyAudio()
        except ImportError as e:
            raise AudioError(
                "PyAudio not installed. Install with: pip install pyaudio"
            ) from e
        except Exception as e:
            raise AudioError(f"Failed to initialize PyAudio: {e}") from e

        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.format_bits = format_bits

        # Set PyAudio format based on bit depth
        if format_bits == 8:
            self.format = self.pyaudio.get_format_from_width(1)
        elif format_bits == 16:
            self.format = self.pyaudio.get_format_from_width(2)
        else:
            raise AudioError(f"Unsupported bit depth: {format_bits}. Use 8 or 16.")

    def __del__(self):
        """Clean up PyAudio resources."""
        if hasattr(self, "pyaudio"):
            self.pyaudio.terminate()

    def list_devices(self) -> list[dict[str, any]]:
        """List available audio input devices.

        Returns:
            List of device dictionaries with keys:
            - index: Device index
            - name: Device name
            - channels: Max input channels
            - sample_rate: Default sample rate
            - is_input: True if device supports input

        Example:
            devices = audio_mgr.list_devices()
            for device in devices:
                print(f"{device['index']}: {device['name']}")
        """
        devices = []
        for i in range(self.pyaudio.get_device_count()):
            try:
                device_info = self.pyaudio.get_device_info_by_index(i)
                # Only include input devices
                if device_info.get("maxInputChannels", 0) > 0:
                    devices.append(
                        {
                            "index": i,
                            "name": device_info.get("name", "Unknown"),
                            "channels": device_info.get("maxInputChannels", 0),
                            "sample_rate": int(
                                device_info.get("defaultSampleRate", 44100)
                            ),
                            "is_input": True,
                        }
                    )
            except Exception:
                # Skip devices that can't be queried
                continue

        return devices

    def record(
        self, duration: float, device_index: Optional[int] = None  # noqa: UP045
    ) -> bytes:
        """Record audio for a specified duration.

        Args:
            duration: Recording duration in seconds.
            device_index: Input device index (None = default device).

        Returns:
            Raw audio data as bytes (PCM format).

        Raises:
            AudioError: If recording fails.
        """
        if duration <= 0:
            raise AudioError(f"Duration must be positive, got {duration}")

        try:
            stream = self.pyaudio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
            )

            frames = []
            num_chunks = int(self.sample_rate / self.chunk_size * duration)

            for _ in range(num_chunks):
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)

            stream.stop_stream()
            stream.close()

            return b"".join(frames)

        except Exception as e:
            raise AudioError(f"Recording failed: {e}") from e

    def record_until_silence(
        self,
        silence_threshold: float = 0.01,
        silence_duration: float = 2.0,
        max_duration: float = 60.0,
        device_index: Optional[int] = None,  # noqa: UP045
    ) -> bytes:
        """Record audio until silence is detected.

        Args:
            silence_threshold: Amplitude threshold for silence (0.0-1.0).
            silence_duration: Duration of silence to stop recording (seconds).
            max_duration: Maximum recording duration (seconds).
            device_index: Input device index (None = default device).

        Returns:
            Raw audio data as bytes (PCM format).

        Raises:
            AudioError: If recording fails.
        """
        if silence_threshold < 0.0 or silence_threshold > 1.0:
            raise AudioError(
                f"Silence threshold must be 0.0-1.0, got {silence_threshold}"
            )

        if silence_duration <= 0:
            raise AudioError(f"Silence duration must be positive, got {silence_duration}")

        if max_duration <= 0:
            raise AudioError(f"Max duration must be positive, got {max_duration}")

        try:
            stream = self.pyaudio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
            )

            frames = []
            silence_chunks = 0
            silence_chunks_needed = int(
                (silence_duration * self.sample_rate) / self.chunk_size
            )
            max_chunks = int((max_duration * self.sample_rate) / self.chunk_size)

            for _ in range(max_chunks):
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)

                # Calculate amplitude
                amplitude = self._calculate_amplitude(data)

                # Check for silence
                if amplitude < silence_threshold:
                    silence_chunks += 1
                    if silence_chunks >= silence_chunks_needed:
                        break
                else:
                    silence_chunks = 0

            stream.stop_stream()
            stream.close()

            return b"".join(frames)

        except Exception as e:
            raise AudioError(f"Recording failed: {e}") from e

    def _calculate_amplitude(self, audio_data: bytes) -> float:
        """Calculate normalized amplitude of audio data.

        Args:
            audio_data: Raw audio bytes.

        Returns:
            Normalized amplitude (0.0-1.0).
        """
        try:
            # Convert bytes to numpy array
            if self.format_bits == 16:
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                max_val = 32768.0
            else:  # 8-bit
                audio_array = np.frombuffer(audio_data, dtype=np.uint8)
                max_val = 128.0

            # Calculate RMS amplitude
            rms = np.sqrt(np.mean(np.square(audio_array.astype(float))))
            normalized = rms / max_val

            return float(normalized)
        except Exception:
            return 0.0

    def save_to_wav(
        self, audio_data: bytes, filename: str, overwrite: bool = False
    ) -> None:
        """Save audio data to WAV file.

        Args:
            audio_data: Raw audio bytes (PCM format).
            filename: Output filename (must end with .wav).
            overwrite: If True, overwrite existing file.

        Raises:
            AudioError: If file save fails.
            FileExistsError: If file exists and overwrite=False.
        """
        path = Path(filename)

        if not filename.lower().endswith(".wav"):
            raise AudioError(f"Filename must end with .wav, got: {filename}")

        if path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {filename}")

        try:
            with wave.open(str(path), "wb") as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(self.format_bits // 8)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data)

        except Exception as e:
            raise AudioError(f"Failed to save WAV file '{filename}': {e}") from e

    def get_sample_rate(self) -> int:
        """Get current sample rate.

        Returns:
            Sample rate in Hz.
        """
        return self.sample_rate

    def get_channels(self) -> int:
        """Get number of channels.

        Returns:
            Number of channels (1=mono, 2=stereo).
        """
        return self.channels
