from unittest.mock import patch

from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from backend.app.approval_complete import approval_complete_node
from backend.app.approval_execute import execute_approved_write
from backend.app.approval_interrupt import approval_interrupt_node
from backend.app.approval_routing import route_approval
from backend.app.provisioning import MOCK_ACCOUNTS
from backend.app.state import HRState

from backend.app.main import app


client = TestClient(app)


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


def create_pending_state(
    thread_id: str,
    employee_id: str = "EMP1001",
    system: str = "HR_PORTAL",
):
    approval_id = f"{thread_id}-approval-key"

    graph = build_test_graph()

    config = create_config(thread_id)

    initial_state = {
        "approval_required": True,
        "approval_status": "PENDING",
        "approval_id": approval_id,
        "approval_request": {
            "employee_id": employee_id,
            "system": system,
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

    return graph, config, approval_id


# ============================================================
# TEST 1 - APPROVE THROUGH HTTP API
# ============================================================

def test_api_approve():
    thread_id = "api-test-approve"

    MOCK_ACCOUNTS.clear()

    graph, config, approval_id = create_pending_state(
        thread_id=thread_id,
    )

    with patch(
        "backend.app.main.graph",
        graph,
    ):
        response = client.post(
            "/approve",
            json={
                "thread_id": thread_id,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["approval_status"] == "APPROVED"

    assert "EMP1001" in data["write_result"]

    assert approval_id in MOCK_ACCOUNTS

    account = MOCK_ACCOUNTS[approval_id]

    assert account["employee_id"] == "EMP1001"
    assert account["system"] == "HR_PORTAL"
    assert account["status"] == "ACTIVE"

    final_snapshot = graph.get_state(config)

    assert final_snapshot.values["approval_status"] == "APPROVED"
    assert final_snapshot.next == ()

    print("PASS: HTTP /approve executed approved write")


# ============================================================
# TEST 2 - DENY THROUGH HTTP API
# ============================================================

def test_api_deny():
    thread_id = "api-test-deny"

    MOCK_ACCOUNTS.clear()

    graph, config, approval_id = create_pending_state(
        thread_id=thread_id,
    )

    with patch(
        "backend.app.main.graph",
        graph,
    ):
        response = client.post(
            "/deny",
            json={
                "thread_id": thread_id,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["approval_status"] == "DENIED"

    assert data["write_result"] == ""

    assert approval_id not in MOCK_ACCOUNTS

    final_snapshot = graph.get_state(config)

    assert final_snapshot.values["approval_status"] == "DENIED"
    assert final_snapshot.next == ()

    print("PASS: HTTP /deny blocked the write")


# ============================================================
# TEST 3 - EDIT AND APPROVE THROUGH HTTP API
# ============================================================

def test_api_edit_and_approve():
    thread_id = "api-test-edit-approve"

    MOCK_ACCOUNTS.clear()

    graph, config, approval_id = create_pending_state(
        thread_id=thread_id,
        employee_id="EMP1001",
        system="HR_PORTAL",
    )

    with patch(
        "backend.app.main.graph",
        graph,
    ):
        response = client.post(
            "/edit-and-approve",
            json={
                "thread_id": thread_id,
                "employee_id": "EMP1002",
                "system": "PAYROLL",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["approval_status"] == "APPROVED"

    assert "EMP1002" in data["write_result"]
    assert "PAYROLL" in data["write_result"]

    assert approval_id in MOCK_ACCOUNTS

    account = MOCK_ACCOUNTS[approval_id]

    assert account["employee_id"] == "EMP1002"
    assert account["system"] == "PAYROLL"
    assert account["status"] == "ACTIVE"

    final_snapshot = graph.get_state(config)

    assert final_snapshot.values["approval_status"] == "APPROVED"
    assert final_snapshot.next == ()

    print(
        "PASS: HTTP /edit-and-approve "
        "executed edited request"
    )


if __name__ == "__main__":
    test_api_approve()
    test_api_deny()
    test_api_edit_and_approve()

    print()
    print("==============================================")
    print("ALL FASTAPI APPROVAL INTEGRATION TESTS PASSED")
    print("==============================================")