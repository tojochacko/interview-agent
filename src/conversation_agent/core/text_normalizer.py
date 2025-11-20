"""Text normalization for structured data (emails, phone numbers, etc.).

This module provides regex-based inverse text normalization (ITN) to convert
spoken-domain transcriptions into written-domain format.

Example:
    normalizer = TextNormalizer()
    text = "my email is john dot smith at gmail dot com"
    result = normalizer.normalize(text)
    # "my email is john.smith@gmail.com"
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


class TextNormalizer:
    """Normalize spoken-domain text to written-domain format.

    Handles structured data that STT systems transcribe phonetically:
    - Email addresses
    - Phone numbers
    - (Future: dates, currency, numbers)

    This is a lightweight, zero-dependency implementation using regex patterns.
    For production-grade normalization with 99% accuracy, consider upgrading
    to NeMo ITN (requires conda on macOS).

    Example:
        normalizer = TextNormalizer()

        # Email normalization
        text = "contact me at john dot smith at gmail dot com"
        normalized = normalizer.normalize(text)
        # "contact me at john.smith@gmail.com"

        # Phone normalization
        text = "call me at five five five one two three four"
        normalized = normalizer.normalize(text)
        # "call me at 555-1234"

        # Multiple normalizations
        text = (
            "email john dot smith at gmail dot com or "
            "call five five five one two three four"
        )
        normalized = normalizer.normalize(text)
        # "email john.smith@gmail.com or call 555-1234"
    """

    # Word-to-digit mapping for phone numbers
    DIGIT_WORDS = {
        "zero": "0",
        "oh": "0",
        "o": "0",
        "one": "1",
        "two": "2",
        "to": "2",
        "too": "2",
        "three": "3",
        "four": "4",
        "for": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "ate": "8",
        "nine": "9",
        "hundred": "00",  # "eight hundred" → "800"
    }

    def __init__(
        self,
        enable_emails: bool = True,
        enable_phones: bool = True,
        verbose: bool = False,
    ) -> None:
        """Initialize text normalizer.

        Args:
            enable_emails: Enable email address normalization
            enable_phones: Enable phone number normalization
            verbose: Log normalization changes (useful for debugging)
        """
        self.enable_emails = enable_emails
        self.enable_phones = enable_phones
        self.verbose = verbose

        # Compile regex patterns once for performance
        self._compile_patterns()

    def normalize(self, text: str) -> str:
        """Normalize all structured data in text.

        Args:
            text: Raw STT transcription

        Returns:
            Normalized text with structured data formatted properly
        """
        if not text:
            return text

        original = text

        # Apply normalizations in order
        if self.enable_emails:
            text = self._normalize_emails(text)

        if self.enable_phones:
            text = self._normalize_phone_numbers(text)

        # Log if changes were made
        if text != original and self.verbose:
            logger.info(f"📝 Normalized: '{original}' → '{text}'")

        return text

    def _normalize_emails(self, text: str) -> str:
        """Normalize email addresses.

        Patterns supported:
        - "john dot smith at gmail dot com" → "john.smith@gmail.com"
        - "jane underscore doe at company dot org" → "jane_doe@company.org"
        - "support dash team at example dot co dot uk" → "support-team@example.co.uk"

        Args:
            text: Input text

        Returns:
            Text with normalized email addresses
        """

        def replace_email(match: re.Match) -> str:
            local = match.group(1)  # "john dot smith"
            domain = match.group(2)  # "gmail dot com"

            # Convert local part (case-insensitive replacement)
            local_lower = local.lower()
            local_normalized = local_lower.replace(" dot ", ".")
            local_normalized = local_normalized.replace(" underscore ", "_")
            local_normalized = local_normalized.replace(" dash ", "-")
            local_normalized = local_normalized.replace(" ", "")

            # Convert domain part (case-insensitive replacement)
            domain_lower = domain.lower()
            domain_normalized = domain_lower.replace(" dot ", ".")
            domain_normalized = domain_normalized.replace(" ", "")

            email = f"{local_normalized}@{domain_normalized}"
            if self.verbose:
                logger.debug(f"Email normalized: {match.group(0)} → {email}")
            return email

        return self._email_pattern.sub(replace_email, text)

    def _normalize_phone_numbers(self, text: str) -> str:
        """Normalize phone numbers.

        Patterns supported:
        - "five five five one two three four" → "555-1234"
        - "one eight hundred five five five zero one zero one" → "1-800-555-0101"
        - "plus one four one five five five five one two three four" → "+1-415-555-1234"

        Args:
            text: Input text

        Returns:
            Text with normalized phone numbers
        """

        def replace_phone(match: re.Match) -> str:
            prefix = match.group(1)  # "plus " or None
            words = match.group(2).lower().split()

            # Convert words to digits
            digits = "".join(self.DIGIT_WORDS.get(w, w) for w in words)

            # Only format if it looks like a phone number (7-15 digits)
            if not (7 <= len(digits) <= 15 and digits.isdigit()):
                return match.group(0)  # Keep original

            # Format based on length and prefix
            formatted = self._format_phone_digits(digits, prefix is not None)

            if self.verbose:
                logger.debug(f"Phone normalized: {match.group(0)} → {formatted}")

            return formatted

        return self._phone_pattern.sub(replace_phone, text)

    def _format_phone_digits(self, digits: str, is_international: bool) -> str:
        """Format digit string as phone number.

        Args:
            digits: String of digits
            is_international: Whether this is an international number (has "plus" prefix)

        Returns:
            Formatted phone number string
        """
        if is_international:
            # International: +1-415-555-1234
            if len(digits) == 11:  # e.g., 14155551234
                return f"+{digits[0]}-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
            elif len(digits) == 10:  # e.g., 4155551234
                return f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        else:
            # US format
            if len(digits) == 10:  # e.g., 4155551234
                return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits[0] == "1":  # e.g., 14155551234
                return f"1-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
            elif len(digits) == 7:  # e.g., 5551234
                return f"{digits[:3]}-{digits[3:]}"

        # Default: return digits as-is
        return digits

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for performance."""
        # Email pattern: Matches various formats:
        # - "john dot smith at gmail dot com" (fully spoken)
        # - "john at gmail.com" (hybrid: spoken @ + typed domain)
        # - "john.smith at gmail dot com" (hybrid: typed local + spoken domain)
        # Local part: alphanumeric with optional dots/special separators
        # Domain part: Must have either a dot (.) OR "dot" word to be valid
        self._email_pattern = re.compile(
            r"\b([a-z0-9]+(?:[._-][a-z0-9]+)*(?:\s+(?:dot|underscore|dash)\s+[a-z0-9]+)*)"
            r"\s+at\s+"
            r"([a-z0-9]+(?:[.][a-z0-9]+)+|[a-z0-9]+(?:\s+dot\s+[a-z0-9]+)+)\b",
            re.IGNORECASE,
        )

        # Phone pattern: (plus)? sequence of digit words
        # Captures: "five five five one two three four"
        digit_words = "|".join(self.DIGIT_WORDS.keys())
        self._phone_pattern = re.compile(
            rf"\b(plus\s+)?"  # Optional "plus" for international
            rf"((?:{digit_words})"  # First digit word
            rf"(?:\s+(?:{digit_words}))+)\b",  # Remaining digit words
            re.IGNORECASE,
        )


class NormalizationError(Exception):
    """Exception raised when normalization fails."""

    pass
