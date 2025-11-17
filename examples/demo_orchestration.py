"""Demo script for Phase 4: Interview Orchestration.

This demonstrates the conversation state machine, intent recognition,
and interview orchestration without requiring actual audio hardware.
"""

from conversation_agent.core.conversation_state import (
    ConversationState,
    ConversationStateMachine,
    UserIntent,
)
from conversation_agent.core.intent_recognizer import IntentRecognizer


def demo_state_machine():
    """Demonstrate conversation state machine."""
    print("=" * 70)
    print("1. CONVERSATION STATE MACHINE DEMO")
    print("=" * 70)

    sm = ConversationStateMachine()
    print(f"\nInitial state: {sm.current_state.value}")

    # Simulate interview flow
    print("\n--- Simulating interview flow ---")

    sm.transition_to(ConversationState.GREETING)
    print(f"1. Greeted user: {sm.current_state.value}")

    sm.transition_to(ConversationState.QUESTIONING)
    print(f"2. Asking questions: {sm.current_state.value}")

    sm.transition_to(ConversationState.CONFIRMING)
    print(f"3. Confirming answer: {sm.current_state.value}")

    sm.transition_to(ConversationState.QUESTIONING)
    print(f"4. Next question: {sm.current_state.value}")

    sm.transition_to(ConversationState.CLOSING)
    print(f"5. Closing interview: {sm.current_state.value}")

    sm.transition_to(ConversationState.COMPLETE)
    print(f"6. Complete: {sm.current_state.value}")
    print(f"   Is terminal: {sm.is_terminal()}")

    # Demonstrate error handling
    print("\n--- Error handling ---")
    sm2 = ConversationStateMachine()
    sm2.transition_to(ConversationState.GREETING)

    sm2.set_error("Microphone not found")
    print(f"Error state: {sm2.current_state.value}")
    print(f"Error message: {sm2.error_message}")
    print(f"Previous state: {sm2.previous_state.value}")

    sm2.recover_from_error()
    print(f"Recovered to: {sm2.current_state.value}")

    # Demonstrate invalid transitions
    print("\n--- Invalid transition example ---")
    sm3 = ConversationStateMachine()
    try:
        sm3.transition_to(ConversationState.QUESTIONING)  # Invalid from INIT
    except ValueError as e:
        print(f"Caught error: {e}")


def demo_intent_recognition():
    """Demonstrate intent recognition."""
    print("\n" + "=" * 70)
    print("2. INTENT RECOGNITION DEMO")
    print("=" * 70)

    recognizer = IntentRecognizer()

    test_cases = [
        # Repeat requests
        ("repeat that", "REPEAT"),
        ("say that again", "REPEAT"),
        ("I didn't catch that", "REPEAT"),
        # Clarify requests
        ("can you clarify", "CLARIFY"),
        ("I don't understand", "CLARIFY"),
        ("what do you mean", "CLARIFY"),
        # Skip requests
        ("skip this question", "SKIP"),
        ("I don't know", "SKIP"),
        ("next question", "SKIP"),
        # Confirmations
        ("yes", "CONFIRM_YES"),
        ("that's correct", "CONFIRM_YES"),
        ("no", "CONFIRM_NO"),
        ("that's wrong", "CONFIRM_NO"),
        # Start/Quit
        ("yes I'm ready", "START"),
        ("let's begin", "START"),
        ("quit", "QUIT"),
        ("I'm done", "QUIT"),
        # Answers
        ("I work as a software engineer", "ANSWER"),
        ("My favorite color is blue", "ANSWER"),
    ]

    print("\n--- Testing intent recognition ---")
    print(f"{'User Input':<40} {'Intent':<15} {'Confidence':>10}")
    print("-" * 70)

    for text, expected_intent in test_cases:
        intent, confidence = recognizer.recognize(text)
        match = "✓" if intent.name == expected_intent else "✗"
        print(f"{text:<40} {intent.name:<15} {confidence:>9.2f} {match}")


def demo_context_aware_recognition():
    """Demonstrate context-aware intent recognition."""
    print("\n" + "=" * 70)
    print("3. CONTEXT-AWARE RECOGNITION DEMO")
    print("=" * 70)

    recognizer = IntentRecognizer()

    print("\n--- Without context ---")
    text = "yup"
    intent, confidence = recognizer.recognize(text)
    print(f"Input: '{text}'")
    print(f"Intent: {intent.name}, Confidence: {confidence:.2f}")

    print("\n--- With context (expecting confirmation) ---")
    intent_ctx, confidence_ctx = recognizer.recognize(
        text, context_intent=UserIntent.CONFIRM_YES
    )
    print(f"Input: '{text}'")
    print(f"Intent: {intent_ctx.name}, Confidence: {confidence_ctx:.2f}")
    print(f"Confidence boost: +{confidence_ctx - confidence:.2f}")


def demo_expected_intents():
    """Demonstrate expected intents per state."""
    print("\n" + "=" * 70)
    print("4. EXPECTED INTENTS PER STATE")
    print("=" * 70)

    recognizer = IntentRecognizer()

    states = ["greeting", "questioning", "confirming", "closing"]

    for state in states:
        intents = recognizer.get_expected_intents(state)
        print(f"\n{state.upper()} state expects:")
        if intents:
            for intent in intents:
                print(f"  - {intent.name}")
        else:
            print("  (no user input expected)")


def demo_full_conversation_simulation():
    """Simulate a complete conversation flow."""
    print("\n" + "=" * 70)
    print("5. FULL CONVERSATION SIMULATION")
    print("=" * 70)

    sm = ConversationStateMachine()
    recognizer = IntentRecognizer()

    conversation = [
        # Greeting
        (ConversationState.GREETING, "yes I'm ready", UserIntent.START),
        # Question 1
        (ConversationState.QUESTIONING, "I'm a software engineer", UserIntent.ANSWER),
        (ConversationState.CONFIRMING, "yes that's correct", UserIntent.CONFIRM_YES),
        # Question 2
        (ConversationState.QUESTIONING, "repeat that", UserIntent.REPEAT),
        (
            ConversationState.QUESTIONING,
            "I enjoy reading and hiking",
            UserIntent.ANSWER,
        ),
        (ConversationState.CONFIRMING, "no that's wrong", UserIntent.CONFIRM_NO),
        (ConversationState.QUESTIONING, "I enjoy programming", UserIntent.ANSWER),
        (ConversationState.CONFIRMING, "yes", UserIntent.CONFIRM_YES),
        # Question 3
        (ConversationState.QUESTIONING, "can you clarify", UserIntent.CLARIFY),
        (ConversationState.QUESTIONING, "I don't know", UserIntent.SKIP),
        # Closing
        (ConversationState.CLOSING, None, None),
    ]

    print("\n--- Simulating conversation ---\n")

    sm.transition_to(ConversationState.GREETING)
    print("Agent: Hello! Are you ready to begin?")

    question_num = 1

    for _i, (expected_state, user_input, _expected_intent) in enumerate(
        conversation, 1
    ):
        if expected_state == ConversationState.GREETING:
            print(f"\nUser: {user_input}")
            intent, confidence = recognizer.recognize(user_input)
            print(f"  [Intent: {intent.name}, Confidence: {confidence:.2f}]")

            if intent == UserIntent.START:
                sm.transition_to(ConversationState.QUESTIONING)
                print(f"\nAgent: Great! Question {question_num}: What is your job?")
                question_num += 1

        elif expected_state == ConversationState.QUESTIONING:
            if user_input:
                print(f"\nUser: {user_input}")
                intent, confidence = recognizer.recognize(user_input)
                print(f"  [Intent: {intent.name}, Confidence: {confidence:.2f}]")

                if intent == UserIntent.ANSWER:
                    sm.transition_to(ConversationState.CONFIRMING)
                    print(f"Agent: You said: '{user_input}'. Is that correct?")
                elif intent == UserIntent.REPEAT:
                    print(f"Agent: Sure! Question {question_num - 1}: What is your job?")
                elif intent == UserIntent.CLARIFY:
                    print("Agent: This question asks about your occupation.")
                elif intent == UserIntent.SKIP:
                    print("Agent: Okay, moving on.")
                    if question_num <= 3:
                        print(f"Agent: Question {question_num}: What are your hobbies?")
                        question_num += 1

        elif expected_state == ConversationState.CONFIRMING:
            print(f"\nUser: {user_input}")
            intent, confidence = recognizer.recognize(user_input)
            print(f"  [Intent: {intent.name}, Confidence: {confidence:.2f}]")

            if intent == UserIntent.CONFIRM_YES:
                sm.transition_to(ConversationState.QUESTIONING)
                if question_num <= 3:
                    print(f"\nAgent: Question {question_num}: What are your hobbies?")
                    question_num += 1
                else:
                    sm.transition_to(ConversationState.CLOSING)
            elif intent == UserIntent.CONFIRM_NO:
                sm.transition_to(ConversationState.QUESTIONING)
                print("Agent: Let's try again. Please answer the question.")

        elif expected_state == ConversationState.CLOSING:
            sm.transition_to(ConversationState.CLOSING)
            sm.transition_to(ConversationState.COMPLETE)
            print("\nAgent: Thank you! Your responses have been recorded.")
            print(f"\n[Interview complete: state={sm.current_state.value}]")


def main():
    """Run all demo sections."""
    print("\n" + "=" * 70)
    print("PHASE 4: INTERVIEW ORCHESTRATION - DEMONSTRATION")
    print("=" * 70)
    print("\nThis demo shows the conversation state machine and intent")
    print("recognition capabilities without requiring audio hardware.\n")

    try:
        demo_state_machine()
        demo_intent_recognition()
        demo_context_aware_recognition()
        demo_expected_intents()
        demo_full_conversation_simulation()

        print("\n" + "=" * 70)
        print("DEMO COMPLETE")
        print("=" * 70)
        print("\nPhase 4 Components:")
        print("  ✓ Conversation State Machine")
        print("  ✓ User Intent Recognition")
        print("  ✓ Interview Orchestrator")
        print("  ✓ Natural Conversation Support")
        print("\nNext: Phase 5 (CSV Export)")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
