import operator
from typing import Annotated, Literal

from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


HRCategory = Literal[
    "PAPERWORK",
    "ACCESS",
    "BENEFITS",
    "PAYROLL",
]


class HRState(TypedDict, total=False):
    question: str
    category: HRCategory
    response: str

    # Conversation messages
    messages: Annotated[list[AnyMessage], add_messages]

    # Step 5 - Context summarization
    conversation_summary: str

    # Step 6 - Input guardrails
    guardrail_blocked: bool
    guardrail_reason: str

    # Step 7 - Specialist findings
    specialist_findings: Annotated[list[str], operator.add]

    # Step 3 - ReAct safety controls
    iteration_count: int
    tool_call_history: list[str]
    escalated: bool
