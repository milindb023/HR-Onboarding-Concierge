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
    messages: Annotated[list[AnyMessage], add_messages]

    # Step 3 - ReAct safety controls
    iteration_count: int
    tool_call_history: list[str]
    escalated: bool