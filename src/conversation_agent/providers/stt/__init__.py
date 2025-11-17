"""Speech-to-Text (STT) providers for conversation agent.

This module provides abstract interfaces and concrete implementations for
various STT providers (Whisper, etc.).
"""

from __future__ import annotations

from conversation_agent.providers.stt.base import STTError, STTProvider
from conversation_agent.providers.stt.whisper_provider import WhisperProvider

__all__ = [
    "STTProvider",
    "STTError",
    "WhisperProvider",
]
