"""Configuration for Text-to-Speech providers.

This module defines TTS configuration using Pydantic Settings,
allowing configuration via environment variables or defaults.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TTSConfig(BaseSettings):
    """Configuration for Text-to-Speech providers.

    Settings can be configured via environment variables with TTS_ prefix,
    or by passing values directly.

    Environment Variables:
        TTS_PROVIDER: Provider name (default: "piper")
        TTS_VOICE: Voice ID to use (default: None, uses system default)
        TTS_RATE: Speech rate in WPM (default: 175, pyttsx3 only)
        TTS_VOLUME: Volume level 0.0-1.0 (default: 0.9)
        TTS_PIPER_MODEL_PATH: Path to Piper .onnx model
        TTS_PIPER_CONFIG_PATH: Path to Piper config (optional)
        TTS_PIPER_SAMPLE_RATE: Sample rate in Hz (default: 22050)

    Example:
        # Use defaults
        config = TTSConfig()

        # Override via constructor
        config = TTSConfig(rate=150, volume=0.8)

        # Override via environment
        # export TTS_RATE=200
        # export TTS_VOLUME=1.0
        config = TTSConfig()
    """

    model_config = SettingsConfigDict(
        env_prefix="TTS_",
        case_sensitive=False,
        frozen=False,
    )

    provider: str = Field(
        default="piper",
        description="TTS provider to use (pyttsx3, piper)",
    )

    voice: Optional[str] = Field(  # noqa: UP045
        default=None,
        description="Voice ID to use. If None, uses system default.",
    )

    rate: int = Field(
        default=150,
        ge=50,
        le=400,
        description="Speech rate in words per minute (50-400)",
    )

    volume: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Volume level (0.0-1.0)",
    )

    # Piper-specific configuration (Phase 7)
    piper_model_path: Optional[str] = Field(  # noqa: UP045
        default="models/tts/piper/en_US-lessac-medium.onnx",
        description="Path to Piper ONNX model file",
    )

    piper_config_path: Optional[str] = Field(  # noqa: UP045
        default=None,
        description="Path to Piper config JSON (auto-detected if None)",
    )

    piper_sample_rate: int = Field(
        default=22050,
        description="Piper audio sample rate in Hz",
    )

    def get_provider(self):
        """Get configured TTS provider instance.

        Returns:
            TTSProvider instance configured with current settings.

        Raises:
            ValueError: If provider name is not recognized or setup fails.
        """
        from conversation_agent.providers.tts import (
            PiperTTSProvider,
            Pyttsx3Provider,
            TTSError,
        )

        if self.provider.lower() == "pyttsx3":
            try:
                provider = Pyttsx3Provider()
                provider.set_rate(self.rate)
                provider.set_volume(self.volume)

                if self.voice:
                    provider.set_voice(self.voice)

                return provider
            except TTSError as e:
                raise ValueError(f"Failed to initialize pyttsx3 provider: {e}") from e

        elif self.provider.lower() == "piper":
            try:
                provider = PiperTTSProvider(
                    model_path=self.piper_model_path,
                    config_path=self.piper_config_path,
                    sample_rate=self.piper_sample_rate,
                )
                provider.initialize()  # Load model
                provider.set_volume(self.volume)

                # Note: rate not supported for Piper (fixed prosody)
                # Note: voice requires model path change, handled separately
                return provider
            except TTSError as e:
                raise ValueError(f"Failed to initialize Piper provider: {e}") from e

        else:
            raise ValueError(
                f"Unknown TTS provider: {self.provider}. "
                f"Supported: pyttsx3, piper"
            )
