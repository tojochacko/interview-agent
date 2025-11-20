"""Configuration for text normalization.

This module provides configuration for inverse text normalization (ITN),
allowing users to control which structured data types are normalized.

Example:
    # Use defaults (all enabled)
    config = NormalizationConfig()

    # Disable email normalization
    config = NormalizationConfig(enable_emails=False)

    # Via environment variables
    # export NORMALIZATION_ENABLED=false
    config = NormalizationConfig()
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NormalizationConfig(BaseSettings):
    """Configuration for text normalization (ITN).

    Settings can be configured via environment variables with NORMALIZATION_ prefix,
    or by passing values directly.

    Environment Variables:
        NORMALIZATION_ENABLED: Enable/disable normalization (default: True)
        NORMALIZATION_ENABLE_EMAILS: Normalize email addresses (default: True)
        NORMALIZATION_ENABLE_PHONES: Normalize phone numbers (default: True)
        NORMALIZATION_VERBOSE: Log normalization changes (default: False)

    Example:
        # Use defaults (emails and phones enabled)
        config = NormalizationConfig()

        # Disable specific features
        config = NormalizationConfig(enable_emails=False)

        # Override via environment
        # export NORMALIZATION_ENABLE_PHONES=false
        config = NormalizationConfig()
    """

    model_config = SettingsConfigDict(
        env_prefix="NORMALIZATION_",
        case_sensitive=False,
        frozen=False,
    )

    enabled: bool = Field(
        default=True,
        description="Enable text normalization (ITN)",
    )

    enable_emails: bool = Field(
        default=True,
        description="Normalize email addresses",
    )

    enable_phones: bool = Field(
        default=True,
        description="Normalize phone numbers",
    )

    verbose: bool = Field(
        default=False,
        description="Log normalization changes (useful for debugging)",
    )

    def get_normalizer(self):
        """Get configured text normalizer instance.

        Returns:
            TextNormalizer instance configured with current settings,
            or None if normalization is disabled.

        Example:
            config = NormalizationConfig()
            normalizer = config.get_normalizer()
            if normalizer:
                normalized = normalizer.normalize("text to normalize")
        """
        if not self.enabled:
            return None

        from conversation_agent.core.text_normalizer import TextNormalizer

        return TextNormalizer(
            enable_emails=self.enable_emails,
            enable_phones=self.enable_phones,
            verbose=self.verbose,
        )
