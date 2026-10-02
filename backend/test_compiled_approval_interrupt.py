from langgraph.types import Command

from app.graph import graph


print("STEP 11B - COMPILED GRAPH APPROVAL INTERRUPT")
print("--------------------------------------------")

thread_id = "step11b-test-thread"
config = {
    "configurable": {
        "thread_id": thread_id,
    }
}

state = {
    "question": "Please provision HR_PORTAL access for EMP1001",
}

print("\nInvoking graph...")
result = graph.invoke(state, config=config)

print("\nGRAPH RESULT:")
print(result)

print("\nCHECKPOINT STATE:")
snapshot = graph.get_state(config)

print("Next nodes:", snapshot.next)

assert snapshot.next, "Graph should be paused at the approval interrupt."

assert "approval_interrupt" in snapshot.next, (
    f"Expected graph to pause at approval_interrupt, "
    f"but paused at: {snapshot.next}"
)

checkpoint_values = snapshot.values

print("\nAPPROVAL STATE:")
print("approval_required:", checkpoint_values.get("approval_required"))
print("approval_status:", checkpoint_values.get("approval_status"))
print("approval_id:", checkpoint_values.get("approval_id"))
print("approval_request:", checkpoint_values.get("approval_request"))

assert checkpoint_values.get("approval_required") is True
assert checkpoint_values.get("approval_status") == "PENDING"

approval_request = checkpoint_values.get("approval_request", {})

assert approval_request.get("employee_id") == "EMP1001"
assert approval_request.get("system") == "HR_PORTAL"
assert approval_request.get("status") == "PENDING"

print("\nPASS: Graph paused for human approval.")

print("\nSTEP 11B COMPILED GRAPH TEST PASSED.")