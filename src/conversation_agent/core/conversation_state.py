"""Conversation state machine for interview orchestration."""

from __future__ import annotations

from enum import Enum
from typing import Optional


class ConversationState(Enum):
    """States in the interview conversation flow.

    States:
        INIT: Initial state before interview starts
        GREETING: Agent greets user and explains process
        QUESTIONING: Agent asks questions and receives answers
        CONFIRMING: Agent confirms user's answer
        CLOSING: Agent thanks user and wraps up
        COMPLETE: Interview finished successfully
        ERROR: Error state requiring recovery
    """

    INIT = "init"
    GREETING = "greeting"
    QUESTIONING = "questioning"
    CONFIRMING = "confirming"
    CLOSING = "closing"
    COMPLETE = "complete"
    ERROR = "error"


class UserIntent(Enum):
    """User intents recognized during conversation.

    Intents:
        ANSWER: User provided an answer
        REPEAT: User wants question repeated
        CLARIFY: User wants clarification
        SKIP: User wants to skip question
        CONFIRM_YES: User confirms answer is correct
        CONFIRM_NO: User wants to change answer
        START: User ready to start interview
        QUIT: User wants to exit interview
        UNKNOWN: Intent not recognized
    """

    ANSWER = "answer"
    REPEAT = "repeat"
    CLARIFY = "clarify"
    SKIP = "skip"
    CONFIRM_YES = "confirm_yes"
    CONFIRM_NO = "confirm_no"
    START = "start"
    QUIT = "quit"
    UNKNOWN = "unknown"


class ConversationStateMachine:
    """Manages interview conversation state transitions.

    Attributes:
        current_state: Current state in the conversation
        previous_state: Previous state (for error recovery)
        error_message: Error message if in ERROR state
    """

    def __init__(self, initial_state: ConversationState = ConversationState.INIT):
        """Initialize state machine.

        Args:
            initial_state: Starting state (default: INIT)
        """
        self.current_state = initial_state
        self.previous_state: Optional[ConversationState] = None  # noqa: UP045
        self.error_message: Optional[str] = None  # noqa: UP045

    def transition_to(self, new_state: ConversationState) -> None:
        """Transition to a new state.

        Args:
            new_state: State to transition to

        Raises:
            ValueError: If transition is invalid
        """
        if not self._is_valid_transition(self.current_state, new_state):
            raise ValueError(
                f"Invalid transition from {self.current_state.value} "
                f"to {new_state.value}"
            )

        self.previous_state = self.current_state
        self.current_state = new_state
        self.error_message = None  # Clear error on successful transition

    def set_error(self, error_message: str) -> None:
        """Set error state with message.

        Args:
            error_message: Description of the error
        """
        self.previous_state = self.current_state
        self.current_state = ConversationState.ERROR
        self.error_message = error_message

    def recover_from_error(self) -> None:
        """Recover from error state to previous state.

        Raises:
            ValueError: If not in ERROR state or no previous state
        """
        if self.current_state != ConversationState.ERROR:
            raise ValueError("Cannot recover: not in ERROR state")

        if self.previous_state is None:
            raise ValueError("Cannot recover: no previous state available")

        self.current_state = self.previous_state
        self.error_message = None

    def _is_valid_transition(
        self, from_state: ConversationState, to_state: ConversationState
    ) -> bool:
        """Check if state transition is valid.

        Args:
            from_state: Current state
            to_state: Target state

        Returns:
            True if transition is valid, False otherwise
        """
        # Define valid transitions
        valid_transitions = {
            ConversationState.INIT: [ConversationState.GREETING],
            ConversationState.GREETING: [
                ConversationState.QUESTIONING,
                ConversationState.COMPLETE,  # User quits immediately
            ],
            ConversationState.QUESTIONING: [
                ConversationState.QUESTIONING,  # Next question
                ConversationState.CONFIRMING,  # Confirm answer
                ConversationState.CLOSING,  # No more questions
                ConversationState.COMPLETE,  # User quits
            ],
            ConversationState.CONFIRMING: [
                ConversationState.QUESTIONING,  # Confirmed, next question
                ConversationState.CLOSING,  # Confirmed, no more questions
            ],
            ConversationState.CLOSING: [ConversationState.COMPLETE],
            ConversationState.COMPLETE: [],  # Terminal state
            ConversationState.ERROR: [
                # Can transition from error to any previous state
                ConversationState.INIT,
                ConversationState.GREETING,
                ConversationState.QUESTIONING,
                ConversationState.CONFIRMING,
                ConversationState.CLOSING,
            ],
        }

        # Any state can transition to ERROR
        if to_state == ConversationState.ERROR:
            return True

        return to_state in valid_transitions.get(from_state, [])

    def is_terminal(self) -> bool:
        """Check if current state is terminal.

        Returns:
            True if in COMPLETE state
        """
        return self.current_state == ConversationState.COMPLETE

    def can_transition_to(self, state: ConversationState) -> bool:
        """Check if can transition to given state.

        Args:
            state: Target state to check

        Returns:
            True if transition is valid
        """
        return self._is_valid_transition(self.current_state, state)
