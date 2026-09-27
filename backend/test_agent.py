from app.graph import agent_node

state = {
    "question": "What is the onboarding status of employee EMP1001?",
}

result = agent_node(state)

print("AGENT RESULT")
print(result)

print("\nMESSAGES")

for message in result["messages"]:
    print("\n---")
    print(type(message).__name__)
    print(message)

print("\nTOOL CALLS")

for message in result["messages"]:
    tool_calls = getattr(message, "tool_calls", [])

    if tool_calls:
        print(tool_calls)