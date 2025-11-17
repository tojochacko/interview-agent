"""Tests for intent recognition."""

import pytest

from conversation_agent.core.conversation_state import UserIntent
from conversation_agent.core.intent_recognizer import IntentRecognizer


class TestIntentRecognizer:
    """Test IntentRecognizer."""

    def test_initialization_default(self):
        """Test default initialization."""
        recognizer = IntentRecognizer()
        assert recognizer.confidence_threshold == 0.7

    def test_initialization_custom_threshold(self):
        """Test custom confidence threshold."""
        recognizer = IntentRecognizer(confidence_threshold=0.8)
        assert recognizer.confidence_threshold == 0.8

    def test_initialization_invalid_threshold_low(self):
        """Test invalid threshold below 0.0."""
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            IntentRecognizer(confidence_threshold=-0.1)

    def test_initialization_invalid_threshold_high(self):
        """Test invalid threshold above 1.0."""
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            IntentRecognizer(confidence_threshold=1.5)

    def test_recognize_empty_text(self):
        """Test recognition with empty text."""
        recognizer = IntentRecognizer()
        intent, confidence = recognizer.recognize("")
        assert intent == UserIntent.UNKNOWN
        assert confidence == 0.0

    def test_recognize_whitespace_only(self):
        """Test recognition with whitespace only."""
        recognizer = IntentRecognizer()
        intent, confidence = recognizer.recognize("   ")
        assert intent == UserIntent.UNKNOWN
        assert confidence == 0.0

    # REPEAT intent tests
    def test_recognize_repeat_explicit(self):
        """Test recognizing explicit repeat requests."""
        recognizer = IntentRecognizer()

        test_cases = [
            "repeat",
            "repeat that",
            "say that again",
            "what did you say",
            "pardon",
            "I didn't hear that",
            "I didn't catch that",
            "come again",
            "one more time",
        ]

        for text in test_cases:
            intent, confidence = recognizer.recognize(text)
            assert intent == UserIntent.REPEAT, f"Failed for: {text}"
            assert confidence >= 0.7

    def test_recognize_repeat_case_insensitive(self):
        """Test repeat recognition is case-insensitive."""
        recognizer = IntentRecognizer()

        for text in ["REPEAT", "Repeat", "RePeAt"]:
            intent, _ = recognizer.recognize(text)
            assert intent == UserIntent.REPEAT

    # CLARIFY intent tests
    def test_recognize_clarify(self):
        """Test recognizing clarification requests."""
        recognizer = IntentRecognizer()

        test_cases = [
            "clarify",
            "can you clarify",
            "I need clarification",
            "what do you mean",
            "I don't understand",
            "that's unclear",
            "can you explain",
            "can you elaborate",
            "can you expand on that",
        ]

        for text in test_cases:
            intent, confidence = recognizer.recognize(text)
            assert intent == UserIntent.CLARIFY, f"Failed for: {text}"
            assert confidence >= 0.7

    # SKIP intent tests
    def test_recognize_skip(self):
        """Test recognizing skip requests."""
        recognizer = IntentRecognizer()

        test_cases = [
            "skip",
            "pass",
            "next question",
            "I don't know",
            "I don't remember",
            "no answer",
            "move on",
            "skip this",
        ]

        for text in test_cases:
            intent, confidence = recognizer.recognize(text)
            assert intent == UserIntent.SKIP, f"Failed for: {text}"
            assert confidence >= 0.7

    # CONFIRM_YES intent tests
    def test_recognize_confirm_yes(self):
        """Test recognizing yes confirmations."""
        recognizer = IntentRecognizer()

        test_cases = [
            "yes",
            "yeah",
            "yep",
            "yup",
            "correct",
            "right",
            "exactly",
            "that's right",
            "that's correct",
            "sounds good",
            "looks good",
        ]

        for text in test_cases:
            intent, confidence = recognizer.recognize(text)
            assert intent == UserIntent.CONFIRM_YES, f"Failed for: {text}"
            assert confidence >= 0.7

    # CONFIRM_NO intent tests
    def test_recognize_confirm_no(self):
        """Test recognizing no confirmations."""
        recognizer = IntentRecognizer()

        test_cases = [
            "no",
            "nope",
            "nah",
            "incorrect",
            "wrong",
            "that's not right",
            "that's wrong",
            "that's incorrect",
            "change",
            "redo",
            "try again",
        ]

        for text in test_cases:
            intent, confidence = recognizer.recognize(text)
            assert intent == UserIntent.CONFIRM_NO, f"Failed for: {text}"
            assert confidence >= 0.7

    # START intent tests
    def test_recognize_start(self):
        """Test recognizing start commands."""
        recognizer = IntentRecognizer()

        test_cases = [
            "start",
            "begin",
            "ready",
            "let's go",
            "yes let's start",
            "yes I'm ready",
            "okay let's ready",
            "ok I'm ready",
        ]

        for text in test_cases:
            intent, confidence = recognizer.recognize(text)
            assert intent == UserIntent.START, f"Failed for: {text}"
            assert confidence >= 0.7

    # QUIT intent tests
    def test_recognize_quit(self):
        """Test recognizing quit commands."""
        recognizer = IntentRecognizer()

        test_cases = [
            "quit",
            "exit",
            "stop",
            "cancel",
            "end",
            "I'm done",
            "I am done",
            "that's it",
            "that's all",
            "no more",
            "stop the interview",
            "stop this interview",
        ]

        for text in test_cases:
            intent, confidence = recognizer.recognize(text)
            assert intent == UserIntent.QUIT, f"Failed for: {text}"
            assert confidence >= 0.7

    # ANSWER intent tests
    def test_recognize_answer_sentence(self):
        """Test recognizing longer sentences as answers."""
        recognizer = IntentRecognizer()

        test_cases = [
            "I work as a software engineer",
            "My favorite color is blue",
            "The project was completed in March",
        ]

        for text in test_cases:
            intent, confidence = recognizer.recognize(text)
            assert intent == UserIntent.ANSWER, f"Failed for: {text}"

    def test_recognize_answer_not_question(self):
        """Test questions are not recognized as answers."""
        recognizer = IntentRecognizer()

        test_cases = [
            "What should I say?",
            "When did it happen?",
            "Where was that?",
            "Who did this?",
            "Why would I?",
            "How does this work?",
        ]

        for text in test_cases:
            intent, _ = recognizer.recognize(text)
            assert intent != UserIntent.ANSWER, f"Should not be answer: {text}"

    # Context-aware recognition
    def test_recognize_with_context_boost(self):
        """Test context boosts confidence for expected intents."""
        recognizer = IntentRecognizer(confidence_threshold=0.9)

        # Without context, might not meet threshold
        intent, confidence = recognizer.recognize("yup")

        # With context, confidence boosted
        intent_ctx, confidence_ctx = recognizer.recognize(
            "yup", context_intent=UserIntent.CONFIRM_YES
        )

        assert intent_ctx == UserIntent.CONFIRM_YES
        assert confidence_ctx >= confidence  # Context boosts confidence

    # Edge cases
    def test_recognize_ambiguous_text(self):
        """Test handling of ambiguous text."""
        recognizer = IntentRecognizer()

        # Very short, unclear text
        intent, confidence = recognizer.recognize("hmm")
        assert intent == UserIntent.UNKNOWN or confidence < 0.7

    def test_recognize_mixed_intent(self):
        """Test text with multiple potential intents."""
        recognizer = IntentRecognizer()

        # Should pick the strongest match
        intent, _ = recognizer.recognize("repeat that please")
        assert intent == UserIntent.REPEAT

    # Helper method tests
    def test_is_confirmation_context(self):
        """Test is_confirmation_context method."""
        recognizer = IntentRecognizer()

        assert recognizer.is_confirmation_context("confirming") is True
        assert recognizer.is_confirmation_context("Confirming") is True
        assert recognizer.is_confirmation_context("CONFIRMING") is True
        assert recognizer.is_confirmation_context("questioning") is False
        assert recognizer.is_confirmation_context("greeting") is False

    def test_get_expected_intents_greeting(self):
        """Test expected intents for greeting state."""
        recognizer = IntentRecognizer()
        intents = recognizer.get_expected_intents("greeting")

        assert UserIntent.START in intents
        assert UserIntent.QUIT in intents
        assert len(intents) == 2

    def test_get_expected_intents_questioning(self):
        """Test expected intents for questioning state."""
        recognizer = IntentRecognizer()
        intents = recognizer.get_expected_intents("questioning")

        assert UserIntent.ANSWER in intents
        assert UserIntent.REPEAT in intents
        assert UserIntent.CLARIFY in intents
        assert UserIntent.SKIP in intents
        assert UserIntent.QUIT in intents

    def test_get_expected_intents_confirming(self):
        """Test expected intents for confirming state."""
        recognizer = IntentRecognizer()
        intents = recognizer.get_expected_intents("confirming")

        assert UserIntent.CONFIRM_YES in intents
        assert UserIntent.CONFIRM_NO in intents
        assert UserIntent.QUIT in intents

    def test_get_expected_intents_closing(self):
        """Test expected intents for closing state."""
        recognizer = IntentRecognizer()
        intents = recognizer.get_expected_intents("closing")

        assert len(intents) == 0  # No input expected

    def test_get_expected_intents_unknown_state(self):
        """Test expected intents for unknown state."""
        recognizer = IntentRecognizer()
        intents = recognizer.get_expected_intents("unknown_state")

        assert len(intents) == 0

    # Confidence threshold behavior
    def test_low_confidence_threshold(self):
        """Test with very low confidence threshold."""
        recognizer = IntentRecognizer(confidence_threshold=0.1)

        # Should recognize even weak matches
        intent, confidence = recognizer.recognize("maybe skip")
        assert intent != UserIntent.UNKNOWN
        assert confidence >= 0.1

    def test_high_confidence_threshold(self):
        """Test with very high confidence threshold."""
        recognizer = IntentRecognizer(confidence_threshold=0.99)

        # Most matches won't meet threshold
        intent, confidence = recognizer.recognize("skip")
        # Might not meet threshold depending on match quality
        if confidence < 0.99:
            assert intent == UserIntent.UNKNOWN
