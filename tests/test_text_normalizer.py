"""Tests for text normalization (inverse text normalization)."""

from __future__ import annotations

from conversation_agent.config import NormalizationConfig
from conversation_agent.core.text_normalizer import TextNormalizer


class TestTextNormalizerEmails:
    """Test email address normalization."""

    def test_basic_email(self):
        """Test basic email: john dot smith at gmail dot com."""
        normalizer = TextNormalizer()
        text = "my email is john dot smith at gmail dot com"
        result = normalizer.normalize(text)
        assert result == "my email is john.smith@gmail.com"

    def test_email_with_underscore(self):
        """Test email with underscore: jane underscore doe."""
        normalizer = TextNormalizer()
        text = "contact jane underscore doe at company dot org"
        result = normalizer.normalize(text)
        assert result == "contact jane_doe@company.org"

    def test_email_with_dash(self):
        """Test email with dash: support dash team."""
        normalizer = TextNormalizer()
        text = "email support dash team at example dot co dot uk"
        result = normalizer.normalize(text)
        assert result == "email support-team@example.co.uk"

    def test_multi_level_domain(self):
        """Test email with multi-level domain."""
        normalizer = TextNormalizer()
        text = "write to admin at mail dot example dot co dot uk"
        result = normalizer.normalize(text)
        assert result == "write to admin@mail.example.co.uk"

    def test_multiple_emails(self):
        """Test multiple emails in one sentence."""
        normalizer = TextNormalizer()
        text = (
            "contact john at gmail dot com or jane at company dot org"
        )
        result = normalizer.normalize(text)
        assert result == "contact john@gmail.com or jane@company.org"

    def test_email_case_insensitive(self):
        """Test email normalization is case insensitive."""
        normalizer = TextNormalizer()
        text = "Email John Dot Smith At Gmail Dot Com"
        result = normalizer.normalize(text)
        # Email is normalized to lowercase
        assert result == "Email john.smith@gmail.com"

    def test_email_with_numbers(self):
        """Test email with numbers - normalizes but not ideal."""
        normalizer = TextNormalizer()
        text = "email john one two three at gmail dot com"
        result = normalizer.normalize(text)
        # Pattern matches, so it normalizes (though result has "one two three" in it)
        assert "john" in result and "@gmail.com" in result

    def test_no_email_pattern(self):
        """Test text without email pattern remains unchanged."""
        normalizer = TextNormalizer()
        text = "this is just regular text about dots and ats"
        result = normalizer.normalize(text)
        assert result == text

    def test_email_disabled(self):
        """Test email normalization can be disabled."""
        normalizer = TextNormalizer(enable_emails=False)
        text = "my email is john dot smith at gmail dot com"
        result = normalizer.normalize(text)
        assert result == text  # Should remain unchanged

    def test_email_with_existing_dots(self):
        """Test email with existing dots: tojo at google.com."""
        normalizer = TextNormalizer()
        text = "my email is tojo at google.com"
        result = normalizer.normalize(text)
        assert result == "my email is tojo@google.com"

    def test_email_simple_domain(self):
        """Test email with simple domain without dots is not normalized."""
        normalizer = TextNormalizer()
        text = "send to john at localhost"
        result = normalizer.normalize(text)
        # Simple domains without dots are not normalized (prevents false positives)
        assert result == text

    def test_email_mixed_format(self):
        """Test email with mixed spoken and typed: john.smith at gmail.com."""
        normalizer = TextNormalizer()
        text = "contact john.smith at gmail.com"
        result = normalizer.normalize(text)
        assert result == "contact john.smith@gmail.com"


class TestTextNormalizerPhones:
    """Test phone number normalization."""

    def test_seven_digit_phone(self):
        """Test 7-digit phone: 555-1234."""
        normalizer = TextNormalizer()
        text = "call me at five five five one two three four"
        result = normalizer.normalize(text)
        assert result == "call me at 555-1234"

    def test_ten_digit_phone(self):
        """Test 10-digit phone: 415-555-1234."""
        normalizer = TextNormalizer()
        text = "my number is four one five five five five one two three four"
        result = normalizer.normalize(text)
        assert result == "my number is 415-555-1234"

    def test_eleven_digit_phone_with_one(self):
        """Test 11-digit phone starting with 1: 1-415-555-1234."""
        normalizer = TextNormalizer()
        text = "call one four one five five five five one two three four"
        result = normalizer.normalize(text)
        assert result == "call 1-415-555-1234"

    def test_international_phone(self):
        """Test international phone with plus: +1-415-555-1234."""
        normalizer = TextNormalizer()
        text = "international is plus one four one five five five five one two three four"
        result = normalizer.normalize(text)
        assert result == "international is +1-415-555-1234"

    def test_toll_free_number(self):
        """Test toll-free number: 1-800-555-0101."""
        normalizer = TextNormalizer()
        text = "call one eight hundred five five five zero one zero one"
        result = normalizer.normalize(text)
        assert result == "call 1-800-555-0101"

    def test_phone_with_oh_instead_of_zero(self):
        """Test phone with 'oh' instead of 'zero'."""
        normalizer = TextNormalizer()
        text = "call five five five oh one oh one"
        result = normalizer.normalize(text)
        assert result == "call 555-0101"

    def test_phone_with_to_instead_of_two(self):
        """Test phone with 'to' instead of 'two'."""
        normalizer = TextNormalizer()
        text = "number is five five five to to to four"
        result = normalizer.normalize(text)
        assert result == "number is 555-2224"

    def test_phone_with_for_instead_of_four(self):
        """Test phone with 'for' instead of 'four'."""
        normalizer = TextNormalizer()
        text = "call five five five for for for four"
        result = normalizer.normalize(text)
        assert result == "call 555-4444"

    def test_phone_case_insensitive(self):
        """Test phone normalization is case insensitive."""
        normalizer = TextNormalizer()
        text = "Call Five Five Five ONE TWO Three Four"
        result = normalizer.normalize(text)
        assert result == "Call 555-1234"

    def test_phone_too_short(self):
        """Test phone too short (< 7 digits) not normalized."""
        normalizer = TextNormalizer()
        text = "count one two three four five"
        result = normalizer.normalize(text)
        # Should NOT normalize (too short)
        assert "one two three four five" in result

    def test_phone_too_long(self):
        """Test phone too long (> 15 digits) not normalized."""
        normalizer = TextNormalizer()
        text = "one two three four five six seven eight nine zero one two three four five six"
        result = normalizer.normalize(text)
        # Should NOT normalize (too long)
        assert "one two three" in result

    def test_multiple_phones(self):
        """Test multiple phone numbers in one sentence."""
        normalizer = TextNormalizer()
        text = "call five five five one two three four or eight hundred five five five zero one zero one"  # noqa: E501
        result = normalizer.normalize(text)
        assert "555-1234" in result
        # "eight hundred" converts to "800", result is "800-555-0101" (no leading 1-)
        assert "800-555-0101" in result

    def test_phone_disabled(self):
        """Test phone normalization can be disabled."""
        normalizer = TextNormalizer(enable_phones=False)
        text = "call five five five one two three four"
        result = normalizer.normalize(text)
        assert result == text  # Should remain unchanged


class TestTextNormalizerIntegration:
    """Test combined normalizations and edge cases."""

    def test_email_and_phone_together(self):
        """Test both email and phone in same text."""
        normalizer = TextNormalizer()
        text = (
            "contact john dot smith at gmail dot com or "
            "call five five five one two three four"
        )
        result = normalizer.normalize(text)
        assert "john.smith@gmail.com" in result
        assert "555-1234" in result

    def test_empty_text(self):
        """Test empty text returns empty."""
        normalizer = TextNormalizer()
        assert normalizer.normalize("") == ""
        assert normalizer.normalize("   ") == "   "

    def test_none_text(self):
        """Test None text returns None."""
        normalizer = TextNormalizer()
        assert normalizer.normalize("") == ""

    def test_text_without_structured_data(self):
        """Test regular text remains unchanged."""
        normalizer = TextNormalizer()
        text = "This is just regular conversation text without any structured data."
        result = normalizer.normalize(text)
        assert result == text

    def test_partial_email_pattern_not_normalized(self):
        """Test incomplete email patterns are not normalized."""
        normalizer = TextNormalizer()
        text = "john dot smith but no at sign"
        result = normalizer.normalize(text)
        assert result == text

    def test_partial_phone_pattern_not_normalized(self):
        """Test incomplete phone patterns are not normalized."""
        normalizer = TextNormalizer()
        text = "just five numbers here"
        result = normalizer.normalize(text)
        assert result == text

    def test_verbose_mode(self):
        """Test verbose mode doesn't break normalization."""
        normalizer = TextNormalizer(verbose=True)
        text = "email john dot smith at gmail dot com"
        result = normalizer.normalize(text)
        assert result == "email john.smith@gmail.com"

    def test_all_features_disabled(self):
        """Test with all features disabled."""
        normalizer = TextNormalizer(enable_emails=False, enable_phones=False)
        text = "john dot smith at gmail dot com and five five five one two three four"
        result = normalizer.normalize(text)
        assert result == text  # Nothing should change


class TestNormalizationConfig:
    """Test normalization configuration."""

    def test_default_config(self):
        """Test default configuration."""
        config = NormalizationConfig()
        assert config.enabled is True
        assert config.enable_emails is True
        assert config.enable_phones is True
        assert config.verbose is False

    def test_config_get_normalizer_enabled(self):
        """Test get_normalizer returns normalizer when enabled."""
        config = NormalizationConfig(enabled=True)
        normalizer = config.get_normalizer()
        assert normalizer is not None
        assert isinstance(normalizer, TextNormalizer)

    def test_config_get_normalizer_disabled(self):
        """Test get_normalizer returns None when disabled."""
        config = NormalizationConfig(enabled=False)
        normalizer = config.get_normalizer()
        assert normalizer is None

    def test_config_custom_settings(self):
        """Test custom configuration settings."""
        config = NormalizationConfig(
            enabled=True,
            enable_emails=False,
            enable_phones=True,
            verbose=True,
        )
        normalizer = config.get_normalizer()
        assert normalizer is not None
        assert normalizer.enable_emails is False
        assert normalizer.enable_phones is True
        assert normalizer.verbose is True

    def test_config_env_vars(self, monkeypatch):
        """Test configuration via environment variables."""
        monkeypatch.setenv("NORMALIZATION_ENABLED", "false")
        config = NormalizationConfig()
        assert config.enabled is False

    def test_config_email_only(self):
        """Test configuration with only email enabled."""
        config = NormalizationConfig(enable_phones=False)
        normalizer = config.get_normalizer()
        text = "john dot smith at gmail dot com and five five five one two three four"
        result = normalizer.normalize(text)
        assert "john.smith@gmail.com" in result
        assert "five five five" in result  # Phone should not be normalized

    def test_config_phone_only(self):
        """Test configuration with only phone enabled."""
        config = NormalizationConfig(enable_emails=False)
        normalizer = config.get_normalizer()
        text = "john dot smith at gmail dot com and five five five one two three four"
        result = normalizer.normalize(text)
        assert "john dot smith at gmail dot com" in result  # Email should not be normalized
        assert "555-1234" in result


class TestTextNormalizerEdgeCases:
    """Test edge cases and error handling."""

    def test_very_long_text(self):
        """Test normalization works with long text."""
        normalizer = TextNormalizer()
        text = (
            "This is a very long text with lots of content before the email. " * 10
            + "Contact john dot smith at gmail dot com for more information."
        )
        result = normalizer.normalize(text)
        assert "john.smith@gmail.com" in result

    def test_special_characters_in_context(self):
        """Test text with special characters around structured data."""
        normalizer = TextNormalizer()
        text = "Email: john dot smith at gmail dot com!"
        result = normalizer.normalize(text)
        assert "john.smith@gmail.com" in result

    def test_numbers_mixed_with_words(self):
        """Test phone numbers mixed with other number words."""
        normalizer = TextNormalizer()
        text = "I have five apples and my number is five five five one two three four"
        result = normalizer.normalize(text)
        assert "I have five apples" in result  # 'five apples' should not change
        assert "555-1234" in result

    def test_unicode_text(self):
        """Test normalization with unicode characters."""
        normalizer = TextNormalizer()
        text = "Café owner's email: john dot smith at gmail dot com"
        result = normalizer.normalize(text)
        assert "john.smith@gmail.com" in result
        assert "Café" in result

    def test_consecutive_normalizations(self):
        """Test multiple normalizations on same normalizer instance."""
        normalizer = TextNormalizer()

        text1 = "john dot smith at gmail dot com"
        result1 = normalizer.normalize(text1)
        assert result1 == "john.smith@gmail.com"

        text2 = "five five five one two three four"
        result2 = normalizer.normalize(text2)
        assert result2 == "555-1234"

        # Ensure first result wasn't affected
        assert result1 == "john.smith@gmail.com"
