from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from app.summarization import (
    MAX_MESSAGES_BEFORE_SUMMARY,
    MESSAGES_TO_KEEP,
    build_summary_text,
    prepare_summary_context,
    should_summarize,
)


def create_messages(count: int):
    messages = []

    for index in range(count):
        if index % 2 == 0:
            messages.append(
                HumanMessage(
                    content=f"Employee question {index}"
                )
            )
        else:
            messages.append(
                AIMessage(
                    content=f"Assistant response {index}"
                )
            )

    return messages


# ------------------------------------------------------------
# Test 1 - Below threshold
# ------------------------------------------------------------

messages = create_messages(MAX_MESSAGES_BEFORE_SUMMARY)

assert should_summarize(messages) is False

print("TEST 1: below threshold -> no summarization")
print("PASS")


# ------------------------------------------------------------
# Test 2 - Above threshold
# ------------------------------------------------------------

messages = create_messages(
    MAX_MESSAGES_BEFORE_SUMMARY + 2
)

assert should_summarize(messages) is True

print("TEST 2: above threshold -> summarization required")
print("PASS")


# ------------------------------------------------------------
# Test 3 - Split old and recent messages
# ------------------------------------------------------------

old_messages, recent_messages = prepare_summary_context(
    messages
)

assert len(recent_messages) == MESSAGES_TO_KEEP
assert len(old_messages) == (
    len(messages) - MESSAGES_TO_KEEP
)

print("TEST 3: conversation split")
print("OLD MESSAGES:", len(old_messages))
print("RECENT MESSAGES:", len(recent_messages))
print("PASS")


# ------------------------------------------------------------
# Test 4 - Summary text generation
# ------------------------------------------------------------

summary_text = build_summary_text(old_messages)

assert summary_text
assert "Employee question" in summary_text
assert "Assistant response" in summary_text

print("TEST 4: summary context generation")
print("PASS")


print("\nAll Step 5 summarization preparation tests passed.")

# TEST 5 - tool-call boundary protection

messages = [
    HumanMessage(content="Question 0"),
    AIMessage(content="Response 1"),
    HumanMessage(content="Question 2"),
    AIMessage(content="Response 3"),
    HumanMessage(content="Question 4"),
    AIMessage(content="Response 5"),
    HumanMessage(content="Question 6"),
    AIMessage(content="Response 7"),
    HumanMessage(content="Question 8"),
    AIMessage(
        content="",
        tool_calls=[
            {
                "name": "lookup_employee",
                "args": {"employee_id": "EMP1001"},
                "id": "tool-call-1",
                "type": "tool_call",
            }
        ],
    ),
    ToolMessage(
        content="Employee EMP1001 found",
        tool_call_id="tool-call-1",
    ),
    HumanMessage(content="Question 11"),
]

old_messages, recent_messages = prepare_summary_context(messages)

assert recent_messages
assert type(recent_messages[0]).__name__ != "ToolMessage"

print("TEST 5: tool-call boundary protection")
print("OLD MESSAGES:", len(old_messages))
print("RECENT MESSAGES:", len(recent_messages))
print("FIRST RECENT MESSAGE:", type(recent_messages[0]).__name__)
print("PASS")

print("\nAll Step 5 summarization preparation tests passed.")