"""Intent recognition for natural conversation understanding."""

from __future__ import annotations

import re

from conversation_agent.core.conversation_state import UserIntent


class IntentRecognizer:
    """Recognizes user intents from transcribed speech.

    Uses pattern matching to identify user intents like repeat, clarify,
    skip, confirm, etc. Patterns are case-insensitive and flexible.
    """

    # Intent patterns (lowercase for case-insensitive matching)
    PATTERNS = {
        UserIntent.REPEAT: [
            r"\b(repeat|say that again|what did you say|pardon)\b",
            r"\b(didn't (hear|catch) that)\b",
            r"\b(come again|one more time)\b",
        ],
        UserIntent.CLARIFY: [
            r"\b(clarify|clarification|what do you mean)\b",
            r"\b(don't understand|unclear|explain)\b",
            r"\b(can you (elaborate|expand))\b",
        ],
        UserIntent.SKIP: [
            r"\b(skip|pass|next question)\b",
            r"\b(don't (know|remember)|no answer)\b",
            r"\b(move on|skip this)\b",
        ],
        UserIntent.CONFIRM_YES: [
            r"\b(yes|yeah|yep|yup|correct|right|exactly)\b",
            r"\b(that's (right|correct))\b",
            r"\b(sounds good|looks good)\b",
        ],
        UserIntent.CONFIRM_NO: [
            r"\b(no|nope|nah|incorrect|wrong)\b",
            r"\b(that's (not right|wrong|incorrect))\b",
            r"\b(change|redo|try again)\b",
        ],
        UserIntent.START: [
            r"\b(start|begin|ready|let's go)\b",
            r"\b(yes(,)? (let's|I'm) (start|ready))\b",
            r"\b(okay|ok)(,)? (let's|I'm) ready\b",
        ],
        UserIntent.QUIT: [
            r"\b(quit|exit|stop|cancel|end)\b",
            r"\b(I('m| am) done|that's (it|all))\b",
            r"\b(no more|stop (the |this )?interview)\b",
        ],
    }

    def __init__(self, confidence_threshold: float = 0.7):
        """Initialize intent recognizer.

        Args:
            confidence_threshold: Minimum confidence for intent recognition
                                (0.0-1.0, default: 0.7)

        Raises:
            ValueError: If confidence_threshold not in range [0.0, 1.0]
        """
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")

        self.confidence_threshold = confidence_threshold

    def recognize(
        self, text: str, context_intent: UserIntent | None = None
    ) -> tuple[UserIntent, float]:
        """Recognize intent from user text.

        Args:
            text: Transcribed user speech
            context_intent: Expected intent based on conversation context
                          (e.g., CONFIRM_YES/NO when confirming)

        Returns:
            Tuple of (intent, confidence_score)
            Returns (UNKNOWN, 0.0) if no intent recognized
        """
        if not text or not text.strip():
            return (UserIntent.UNKNOWN, 0.0)

        text_lower = text.lower().strip()

        # Check each intent's patterns
        best_match = (UserIntent.UNKNOWN, 0.0)

        for intent, patterns in self.PATTERNS.items():
            confidence = self._match_patterns(text_lower, patterns)

            # Boost confidence if matches context
            if context_intent and intent == context_intent:
                confidence = min(1.0, confidence * 1.2)

            if confidence > best_match[1]:
                best_match = (intent, confidence)

        # If no pattern matched well, check for simple answers
        if best_match[1] < self.confidence_threshold:
            # Check if it's a simple answer (not a command)
            if self._is_likely_answer(text_lower):
                return (UserIntent.ANSWER, 0.8)

        # Return best match or UNKNOWN
        if best_match[1] >= self.confidence_threshold:
            return best_match

        return (UserIntent.UNKNOWN, best_match[1])

    def _match_patterns(self, text: str, patterns: list[str]) -> float:
        """Match text against list of regex patterns.

        Args:
            text: Text to match (lowercase)
            patterns: List of regex patterns

        Returns:
            Confidence score (0.0-1.0)
        """
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Calculate confidence based on match quality
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Higher confidence for longer/more specific matches
                    match_length = len(match.group(0))
                    text_length = len(text)
                    base_confidence = 0.7

                    # Boost if match covers significant portion of text
                    if match_length / text_length > 0.5:
                        base_confidence = 0.9
                    elif match_length / text_length > 0.3:
                        base_confidence = 0.8

                    return base_confidence

        return 0.0

    def _is_likely_answer(self, text: str) -> bool:
        """Check if text is likely an answer vs. a command.

        Args:
            text: Text to check (lowercase)

        Returns:
            True if text appears to be an answer
        """
        # Short phrases likely commands
        if len(text.split()) <= 2:
            return False

        # Check for question words (likely not an answer)
        question_words = ["what", "when", "where", "who", "why", "how"]
        if any(text.startswith(word) for word in question_words):
            return False

        # Otherwise assume it's an answer
        return True

    def is_confirmation_context(self, state_name: str) -> bool:
        """Check if current state expects confirmation.

        Args:
            state_name: Name of current conversation state

        Returns:
            True if state expects yes/no confirmation
        """
        return state_name.lower() == "confirming"

    def get_expected_intents(self, state_name: str) -> list[UserIntent]:
        """Get list of expected intents for a conversation state.

        Args:
            state_name: Name of current conversation state

        Returns:
            List of UserIntent values expected in this state
        """
        state_lower = state_name.lower()

        if state_lower == "greeting":
            return [UserIntent.START, UserIntent.QUIT]
        elif state_lower == "questioning":
            return [
                UserIntent.ANSWER,
                UserIntent.REPEAT,
                UserIntent.CLARIFY,
                UserIntent.SKIP,
                UserIntent.QUIT,
            ]
        elif state_lower == "confirming":
            return [UserIntent.CONFIRM_YES, UserIntent.CONFIRM_NO, UserIntent.QUIT]
        elif state_lower == "closing":
            return []  # No input expected

        return []
