from langgraph.graph import StateGraph, START, END

from app.state import HRState
from app.graph import (
    agent_node,
    tool_node,
    should_continue,
)


def escalation_node(state: HRState) -> dict:
    return {
        "escalated": True,
        "response": (
            "The request requires human review because "
            "the agent reached a safety limit."
        ),
    }


builder = StateGraph(HRState)

builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)
builder.add_node("escalate", escalation_node)

builder.add_edge(START, "agent")

builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END,
        "escalate": "escalate",
    },
)

builder.add_edge("tools", "agent")
builder.add_edge("escalate", END)

graph = builder.compile()


result = graph.invoke(
    {
        "question": "What is the onboarding status of employee EMP1001?"
    }
)


print("\nFINAL RESULT")
print(result)


print("\nMESSAGES")

for message in result["messages"]:
    print("\n---")
    print(type(message).__name__)
    print(message)


print("\nITERATION COUNT")
print(result.get("iteration_count"))

print("\nESCALATED")
print(result.get("escalated", False))