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
        TTS_PROVIDER: Provider name (default: "pyttsx3")
        TTS_VOICE: Voice ID to use (default: None, uses system default)
        TTS_RATE: Speech rate in WPM (default: 175)
        TTS_VOLUME: Volume level 0.0-1.0 (default: 0.9)

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
        default="pyttsx3",
        description="TTS provider to use (pyttsx3, gtts, openai, etc.)",
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

    def get_provider(self):
        """Get configured TTS provider instance.

        Returns:
            TTSProvider instance configured with current settings.

        Raises:
            ValueError: If provider name is not recognized.
        """
        from conversation_agent.providers.tts import Pyttsx3Provider, TTSError

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
        else:
            raise ValueError(
                f"Unknown TTS provider: {self.provider}. Supported: pyttsx3"
            )
