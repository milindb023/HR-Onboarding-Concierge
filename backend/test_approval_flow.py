from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from app.approval_execute import execute_approved_write
from app.approval_interrupt import approval_interrupt_node
from app.approval_routing import route_approval
from app.provisioning import MOCK_ACCOUNTS
from app.state import HRState
from app.approval_complete import approval_complete_node


print("STEP 11C-5 - DETERMINISTIC APPROVAL FLOW")
print("----------------------------------------")


def build_test_graph():
    builder = StateGraph(HRState)

    builder.add_node(
        "approval_interrupt",
        approval_interrupt_node,
    )

    builder.add_node(
        "approval_execute",
        execute_approved_write,
    )

    builder.add_node(
        "approval_complete",
        approval_complete_node,
    )

    builder.add_edge(
        START,
        "approval_interrupt",
    )

    builder.add_conditional_edges(
        "approval_interrupt",
        route_approval,
        {
            "approved": "approval_execute",
            "denied": "approval_complete",
            "pending": "approval_interrupt",
        },
    )

    builder.add_edge(
        "approval_execute",
        "approval_complete",
    )

    builder.add_edge(
        "approval_complete",
        END,
    )

    return builder.compile(
        checkpointer=MemorySaver()
    )


def create_config(thread_id: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
        }
    }


# ============================================================
# TEST 1 - APPROVED
# ============================================================

print("\nTEST 1: APPROVED REQUEST")

graph = build_test_graph()

approve_thread = "step11c-deterministic-approve"
config = create_config(approve_thread)

approval_id = "deterministic-approve-key"

initial_state = {
    "approval_required": True,
    "approval_status": "PENDING",
    "approval_id": approval_id,
    "approval_request": {
        "employee_id": "EMP1001",
        "system": "HR_PORTAL",
        "severity": "MEDIUM",
        "idempotency_key": approval_id,
        "action": "PROVISION_SYSTEM_ACCOUNT",
        "status": "PENDING",
    },
}

result = graph.invoke(
    initial_state,
    config=config,
)

assert "__interrupt__" in result

snapshot = graph.get_state(config)

assert snapshot.values["approval_required"] is True
assert snapshot.values["approval_status"] == "PENDING"

assert approval_id not in MOCK_ACCOUNTS

print("PASS: Graph paused for human approval.")
print("Approval status:", snapshot.values["approval_status"])

print("Resuming with APPROVED...")

approved_result = graph.invoke(
    Command(
        resume={
            "status": "APPROVED"
        }
    ),
    config=config,
)

print("Approved result:")
print(approved_result)

assert approval_id in MOCK_ACCOUNTS

account = MOCK_ACCOUNTS[approval_id]

assert account["employee_id"] == "EMP1001"
assert account["system"] == "HR_PORTAL"
assert account["status"] == "ACTIVE"

final_snapshot = graph.get_state(config)

assert final_snapshot.values["approval_status"] == "APPROVED"

assert (
    final_snapshot.values["response"]
    == "System account provisioned successfully for employee "
       "EMP1001. System: HR_PORTAL. "
       "Account ID: ACC-EMP1001-HR_PORTAL"
)

assert final_snapshot.next == ()

print("PASS: APPROVED request executed.")
print("PASS: Approved flow reached END.")
print("PASS: No LLM was required.")


# ============================================================
# TEST 2 - DENIED
# ============================================================

print("\nTEST 2: DENIED REQUEST")

graph = build_test_graph()

deny_thread = "step11c-deterministic-deny"
config = create_config(deny_thread)

approval_id = "deterministic-deny-key"

initial_state = {
    "approval_required": True,
    "approval_status": "PENDING",
    "approval_id": approval_id,
    "approval_request": {
        "employee_id": "EMP1001",
        "system": "HR_PORTAL",
        "severity": "MEDIUM",
        "idempotency_key": approval_id,
        "action": "PROVISION_SYSTEM_ACCOUNT",
        "status": "PENDING",
    },
}

result = graph.invoke(
    initial_state,
    config=config,
)

assert "__interrupt__" in result

snapshot = graph.get_state(config)

assert snapshot.values["approval_status"] == "PENDING"

assert approval_id not in MOCK_ACCOUNTS

print("PASS: Graph paused for human approval.")
print("Approval status:", snapshot.values["approval_status"])

print("Resuming with DENIED...")

denied_result = graph.invoke(
    Command(
        resume={
            "status": "DENIED"
        }
    ),
    config=config,
)

print("Denied result:")
print(denied_result)

assert approval_id not in MOCK_ACCOUNTS

final_snapshot = graph.get_state(config)

assert final_snapshot.values["approval_status"] == "DENIED"

assert (
    final_snapshot.values["response"]
    == "The requested system account provisioning was denied. "
       "No account was created."
)

assert final_snapshot.values["write_result"] == ""

assert final_snapshot.next == ()

print("PASS: DENIED request did not execute the write.")
print("PASS: Denied flow reached END.")
print("PASS: No LLM was required.")


# ============================================================
# FINAL
# ============================================================

print("\n==============================================")
print("ALL STEP 11C-5 TESTS PASSED")
print("==============================================")