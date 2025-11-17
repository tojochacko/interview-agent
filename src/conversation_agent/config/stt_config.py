"""Configuration for Speech-to-Text (STT) providers."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class STTConfig(BaseSettings):
    """Configuration for Speech-to-Text providers.

    Settings can be configured via environment variables with STT_ prefix,
    or by passing values directly.

    Environment Variables:
        STT_PROVIDER: Provider name (default: "whisper")
        STT_MODEL_SIZE: Whisper model size (default: "base")
        STT_LANGUAGE: Language code (default: "en")
        STT_DEVICE: Device to use (default: "cpu")
        STT_SAMPLE_RATE: Audio sample rate (default: 16000)
        STT_SILENCE_THRESHOLD: Silence detection threshold (default: 0.01)
        STT_SILENCE_DURATION: Silence duration to stop (default: 2.0)

    Example:
        # Use defaults
        config = STTConfig()

        # Override via constructor
        config = STTConfig(model_size="small", language="es")

        # Override via environment
        # export STT_MODEL_SIZE=small
        # export STT_LANGUAGE=es
        config = STTConfig()
    """

    model_config = SettingsConfigDict(
        env_prefix="STT_",
        case_sensitive=False,
        frozen=False,
    )

    provider: str = Field(
        default="whisper",
        description="STT provider to use (whisper, etc.)",
    )

    model_size: str = Field(
        default="base",
        description="Whisper model size (tiny, base, small, medium, large, turbo)",
    )

    language: str = Field(
        default="en",
        description="Language code for transcription (e.g., en, es, fr). "
        "Empty string for auto-detection.",
    )

    device: str = Field(
        default="cpu",
        description="Device to use for inference (cpu or cuda)",
    )

    sample_rate: int = Field(
        default=16000,
        ge=8000,
        le=48000,
        description="Audio sample rate in Hz (8000-48000)",
    )

    silence_threshold: float = Field(
        default=0.01,
        ge=0.0,
        le=1.0,
        description="Silence detection threshold (0.0-1.0)",
    )

    silence_duration: float = Field(
        default=2.0,
        ge=0.5,
        le=10.0,
        description="Duration of silence to stop recording (seconds)",
    )

    max_recording_duration: float = Field(
        default=60.0,
        ge=1.0,
        le=600.0,
        description="Maximum recording duration (seconds)",
    )

    def get_provider(self):
        """Get configured STT provider instance.

        Returns:
            STTProvider instance configured with current settings.

        Raises:
            ValueError: If provider name is not recognized.
        """
        from conversation_agent.providers.stt import STTError, WhisperProvider

        if self.provider.lower() == "whisper":
            try:
                provider = WhisperProvider(
                    model_size=self.model_size,
                    language=self.language,
                    device=self.device,
                )
                return provider
            except STTError as e:
                raise ValueError(f"Failed to initialize Whisper provider: {e}") from e
        else:
            raise ValueError(
                f"Unknown STT provider: {self.provider}. Supported: whisper"
            )
