from app.write_request_node import write_request_node
from app.severity_node import severity_node
from app.write_draft_node import write_draft_node


THREAD_ID = "step-10g-integration-test"


def build_state(question: str) -> dict:
    state = {
        "question": question,
    }

    state.update(write_request_node(state))
    state.update(severity_node(state))

    return state


print("STEP 10G - GATED WRITE FLOW")
print("---------------------------")


print("\nTEST 1: VALID MEDIUM-SEVERITY REQUEST")

state = build_state(
    "Provision HR_PORTAL access for EMP1001"
)

print("State before write draft:")
print(state)

draft_result = write_draft_node(
    state,
    {
        "configurable": {
            "thread_id": THREAD_ID,
        }
    },
)

print("Write draft:")
print(draft_result)

assert state["employee_id"] == "EMP1001"
assert state["requested_system"] == "HR_PORTAL"
assert state["write_request_valid"] is True
assert state["severity"] == "MEDIUM"
assert draft_result["write_draft"]["employee_id"] == "EMP1001"
assert draft_result["write_draft"]["system"] == "HR_PORTAL"
assert draft_result["write_idempotency_key"]

print("PASS")


print("\nTEST 2: INCOMPLETE REQUEST DOES NOT CREATE WRITE DRAFT")

state = build_state(
    "Provision HR_PORTAL access"
)

print("State:")
print(state)

draft_result = write_draft_node(
    state,
    {
        "configurable": {
            "thread_id": THREAD_ID,
        }
    },
)

print("Write draft:")
print(draft_result)

assert state["write_request_valid"] is False
assert draft_result["write_draft"] == {}
assert draft_result["write_idempotency_key"] == ""

print("PASS")


print("\nTEST 3: LOW-SEVERITY REQUEST DOES NOT CREATE WRITE DRAFT")

state = build_state(
    "What documents do I need for onboarding?"
)

print("State:")
print(state)

draft_result = write_draft_node(
    state,
    {
        "configurable": {
            "thread_id": THREAD_ID,
        }
    },
)

print("Write draft:")
print(draft_result)

assert state["severity"] == "LOW"
assert draft_result["write_draft"] == {}
assert draft_result["write_idempotency_key"] == ""

print("PASS")


print("\nTEST 4: SAME THREAD + SAME REQUEST PRODUCES SAME KEY")

state1 = build_state(
    "Provision HR_PORTAL access for EMP1001"
)

state2 = build_state(
    "Provision HR_PORTAL access for EMP1001"
)

draft1 = write_draft_node(
    state1,
    {
        "configurable": {
            "thread_id": THREAD_ID,
        }
    },
)

draft2 = write_draft_node(
    state2,
    {
        "configurable": {
            "thread_id": THREAD_ID,
        }
    },
)

assert (
    draft1["write_idempotency_key"]
    == draft2["write_idempotency_key"]
)

print("PASS")


print()
print("All Step 10G gated-write-flow tests passed.")