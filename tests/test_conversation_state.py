"""Tests for conversation state machine."""

import pytest

from conversation_agent.core.conversation_state import (
    ConversationState,
    ConversationStateMachine,
    UserIntent,
)


class TestConversationState:
    """Test ConversationState enum."""

    def test_states_exist(self):
        """Test all expected states exist."""
        assert ConversationState.INIT
        assert ConversationState.GREETING
        assert ConversationState.QUESTIONING
        assert ConversationState.CONFIRMING
        assert ConversationState.CLOSING
        assert ConversationState.COMPLETE
        assert ConversationState.ERROR

    def test_state_values(self):
        """Test state string values."""
        assert ConversationState.INIT.value == "init"
        assert ConversationState.GREETING.value == "greeting"
        assert ConversationState.QUESTIONING.value == "questioning"
        assert ConversationState.CONFIRMING.value == "confirming"
        assert ConversationState.CLOSING.value == "closing"
        assert ConversationState.COMPLETE.value == "complete"
        assert ConversationState.ERROR.value == "error"


class TestUserIntent:
    """Test UserIntent enum."""

    def test_intents_exist(self):
        """Test all expected intents exist."""
        assert UserIntent.ANSWER
        assert UserIntent.REPEAT
        assert UserIntent.CLARIFY
        assert UserIntent.SKIP
        assert UserIntent.CONFIRM_YES
        assert UserIntent.CONFIRM_NO
        assert UserIntent.START
        assert UserIntent.QUIT
        assert UserIntent.UNKNOWN

    def test_intent_values(self):
        """Test intent string values."""
        assert UserIntent.ANSWER.value == "answer"
        assert UserIntent.REPEAT.value == "repeat"
        assert UserIntent.CLARIFY.value == "clarify"
        assert UserIntent.SKIP.value == "skip"
        assert UserIntent.CONFIRM_YES.value == "confirm_yes"
        assert UserIntent.CONFIRM_NO.value == "confirm_no"
        assert UserIntent.START.value == "start"
        assert UserIntent.QUIT.value == "quit"
        assert UserIntent.UNKNOWN.value == "unknown"


class TestConversationStateMachine:
    """Test ConversationStateMachine."""

    def test_initialization_default(self):
        """Test state machine initializes with INIT state."""
        sm = ConversationStateMachine()
        assert sm.current_state == ConversationState.INIT
        assert sm.previous_state is None
        assert sm.error_message is None

    def test_initialization_custom_state(self):
        """Test state machine can initialize with custom state."""
        sm = ConversationStateMachine(initial_state=ConversationState.GREETING)
        assert sm.current_state == ConversationState.GREETING

    def test_valid_transition_init_to_greeting(self):
        """Test valid transition from INIT to GREETING."""
        sm = ConversationStateMachine()
        sm.transition_to(ConversationState.GREETING)
        assert sm.current_state == ConversationState.GREETING
        assert sm.previous_state == ConversationState.INIT

    def test_valid_transition_greeting_to_questioning(self):
        """Test valid transition from GREETING to QUESTIONING."""
        sm = ConversationStateMachine(initial_state=ConversationState.GREETING)
        sm.transition_to(ConversationState.QUESTIONING)
        assert sm.current_state == ConversationState.QUESTIONING
        assert sm.previous_state == ConversationState.GREETING

    def test_valid_transition_questioning_to_confirming(self):
        """Test valid transition from QUESTIONING to CONFIRMING."""
        sm = ConversationStateMachine(initial_state=ConversationState.QUESTIONING)
        sm.transition_to(ConversationState.CONFIRMING)
        assert sm.current_state == ConversationState.CONFIRMING

    def test_valid_transition_confirming_to_questioning(self):
        """Test valid transition from CONFIRMING back to QUESTIONING."""
        sm = ConversationStateMachine(initial_state=ConversationState.CONFIRMING)
        sm.transition_to(ConversationState.QUESTIONING)
        assert sm.current_state == ConversationState.QUESTIONING

    def test_valid_transition_questioning_to_closing(self):
        """Test valid transition from QUESTIONING to CLOSING."""
        sm = ConversationStateMachine(initial_state=ConversationState.QUESTIONING)
        sm.transition_to(ConversationState.CLOSING)
        assert sm.current_state == ConversationState.CLOSING

    def test_valid_transition_closing_to_complete(self):
        """Test valid transition from CLOSING to COMPLETE."""
        sm = ConversationStateMachine(initial_state=ConversationState.CLOSING)
        sm.transition_to(ConversationState.COMPLETE)
        assert sm.current_state == ConversationState.COMPLETE

    def test_invalid_transition_init_to_questioning(self):
        """Test invalid transition from INIT directly to QUESTIONING."""
        sm = ConversationStateMachine()
        with pytest.raises(ValueError, match="Invalid transition"):
            sm.transition_to(ConversationState.QUESTIONING)

    def test_invalid_transition_complete_to_any(self):
        """Test COMPLETE is terminal state."""
        sm = ConversationStateMachine(initial_state=ConversationState.COMPLETE)
        with pytest.raises(ValueError, match="Invalid transition"):
            sm.transition_to(ConversationState.GREETING)

    def test_transition_to_error_always_valid(self):
        """Test any state can transition to ERROR."""
        for state in [
            ConversationState.INIT,
            ConversationState.GREETING,
            ConversationState.QUESTIONING,
            ConversationState.CONFIRMING,
            ConversationState.CLOSING,
        ]:
            sm = ConversationStateMachine(initial_state=state)
            sm.transition_to(ConversationState.ERROR)
            assert sm.current_state == ConversationState.ERROR

    def test_set_error(self):
        """Test setting error state with message."""
        sm = ConversationStateMachine(initial_state=ConversationState.QUESTIONING)
        sm.set_error("Something went wrong")

        assert sm.current_state == ConversationState.ERROR
        assert sm.previous_state == ConversationState.QUESTIONING
        assert sm.error_message == "Something went wrong"

    def test_recover_from_error(self):
        """Test recovering from error state."""
        sm = ConversationStateMachine(initial_state=ConversationState.QUESTIONING)
        sm.set_error("Test error")

        sm.recover_from_error()

        assert sm.current_state == ConversationState.QUESTIONING
        assert sm.error_message is None

    def test_recover_from_error_not_in_error_state(self):
        """Test recovery fails if not in ERROR state."""
        sm = ConversationStateMachine(initial_state=ConversationState.GREETING)

        with pytest.raises(ValueError, match="not in ERROR state"):
            sm.recover_from_error()

    def test_recover_from_error_no_previous_state(self):
        """Test recovery fails if no previous state."""
        sm = ConversationStateMachine(initial_state=ConversationState.ERROR)
        sm.previous_state = None

        with pytest.raises(ValueError, match="no previous state"):
            sm.recover_from_error()

    def test_is_terminal_complete(self):
        """Test is_terminal returns True for COMPLETE."""
        sm = ConversationStateMachine(initial_state=ConversationState.COMPLETE)
        assert sm.is_terminal() is True

    def test_is_terminal_not_complete(self):
        """Test is_terminal returns False for non-COMPLETE states."""
        for state in [
            ConversationState.INIT,
            ConversationState.GREETING,
            ConversationState.QUESTIONING,
            ConversationState.CONFIRMING,
            ConversationState.CLOSING,
            ConversationState.ERROR,
        ]:
            sm = ConversationStateMachine(initial_state=state)
            assert sm.is_terminal() is False

    def test_can_transition_to(self):
        """Test can_transition_to method."""
        sm = ConversationStateMachine()

        # Can transition from INIT to GREETING
        assert sm.can_transition_to(ConversationState.GREETING) is True

        # Cannot transition from INIT to QUESTIONING
        assert sm.can_transition_to(ConversationState.QUESTIONING) is False

        # Can always transition to ERROR
        assert sm.can_transition_to(ConversationState.ERROR) is True

    def test_transition_clears_error_message(self):
        """Test successful transition clears error message."""
        sm = ConversationStateMachine(initial_state=ConversationState.GREETING)
        sm.set_error("Test error")

        assert sm.error_message == "Test error"

        sm.recover_from_error()
        sm.transition_to(ConversationState.QUESTIONING)

        assert sm.error_message is None

    def test_full_interview_flow(self):
        """Test complete interview state flow."""
        sm = ConversationStateMachine()

        # INIT -> GREETING
        sm.transition_to(ConversationState.GREETING)
        assert sm.current_state == ConversationState.GREETING

        # GREETING -> QUESTIONING
        sm.transition_to(ConversationState.QUESTIONING)
        assert sm.current_state == ConversationState.QUESTIONING

        # QUESTIONING -> CONFIRMING
        sm.transition_to(ConversationState.CONFIRMING)
        assert sm.current_state == ConversationState.CONFIRMING

        # CONFIRMING -> QUESTIONING (next question)
        sm.transition_to(ConversationState.QUESTIONING)
        assert sm.current_state == ConversationState.QUESTIONING

        # QUESTIONING -> CLOSING
        sm.transition_to(ConversationState.CLOSING)
        assert sm.current_state == ConversationState.CLOSING

        # CLOSING -> COMPLETE
        sm.transition_to(ConversationState.COMPLETE)
        assert sm.current_state == ConversationState.COMPLETE
        assert sm.is_terminal() is True

    def test_early_quit_flow(self):
        """Test early quit from GREETING."""
        sm = ConversationStateMachine()
        sm.transition_to(ConversationState.GREETING)
        sm.transition_to(ConversationState.COMPLETE)

        assert sm.current_state == ConversationState.COMPLETE
        assert sm.is_terminal() is True

    def test_questioning_loop(self):
        """Test staying in QUESTIONING for multiple questions."""
        sm = ConversationStateMachine(initial_state=ConversationState.QUESTIONING)

        # Can loop in QUESTIONING state
        sm.transition_to(ConversationState.QUESTIONING)
        assert sm.current_state == ConversationState.QUESTIONING

        sm.transition_to(ConversationState.QUESTIONING)
        assert sm.current_state == ConversationState.QUESTIONING
