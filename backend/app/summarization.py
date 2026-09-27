from langchain_core.messages import AnyMessage


MAX_MESSAGES_BEFORE_SUMMARY = 10
MESSAGES_TO_KEEP = 6


def message_to_text(message: AnyMessage) -> str:
    message_type = type(message).__name__
    content = getattr(message, "content", "")

    if isinstance(content, list):
        content = " ".join(
            str(block.get("text", ""))
            for block in content
            if isinstance(block, dict)
        )

    tool_calls = getattr(message, "tool_calls", [])

    text = f"{message_type}: {content}"

    if tool_calls:
        text += f" | Tool calls: {tool_calls}"

    return text


def build_summary_text(messages: list[AnyMessage]) -> str:
    if not messages:
        return ""

    return "\n".join(
        message_to_text(message)
        for message in messages
    )


def should_summarize(messages: list[AnyMessage]) -> bool:
    return len(messages) > MAX_MESSAGES_BEFORE_SUMMARY


def _has_tool_calls(message: AnyMessage) -> bool:
    return bool(getattr(message, "tool_calls", []))


def _is_tool_message(message: AnyMessage) -> bool:
    return type(message).__name__ == "ToolMessage"


def prepare_summary_context(
    messages: list[AnyMessage],
) -> tuple[list[AnyMessage], list[AnyMessage]]:

    if not should_summarize(messages):
        return [], list(messages)

    split_index = max(
        0,
        len(messages) - MESSAGES_TO_KEEP,
    )

    # Never split immediately before/after a tool interaction.
    # Keep the AI tool-call message and its ToolMessage together.
    while split_index > 0 and _is_tool_message(messages[split_index]):
        split_index -= 1

    while split_index > 0 and _has_tool_calls(messages[split_index]):
        split_index -= 1

    old_messages = messages[:split_index]
    recent_messages = messages[split_index:]

    return old_messages, recent_messages