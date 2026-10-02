from backend.app.approval_interrupt import approval_interrupt_node
from backend.app.approval_execute import execute_approved_write
from backend.app.provisioning import MOCK_ACCOUNTS


def test_edit_and_approve():
    state = {
        "approval_required": True,
        "approval_status": "PENDING",
        "approval_id": "edit-test-key",
        "approval_request": {
            "employee_id": "EMP1001",
            "system": "HR_PORTAL",
            "severity": "MEDIUM",
            "idempotency_key": "edit-test-key",
            "action": "PROVISION_SYSTEM_ACCOUNT",
            "status": "PENDING",
        },
    }

    original_interrupt = approval_interrupt_node

    # The interrupt itself is intentionally not called here because
    # interrupt() requires a compiled graph execution context.
    #
    # Instead, verify the execution contract directly using the state
    # that the interrupt node is expected to produce after
    # EDIT_AND_APPROVE.

    edited_state = {
        **state,
        "approval_status": "APPROVED",
        "approval_employee_id": "EMP1002",
        "approval_system": "PAYROLL",
    }

    result = execute_approved_write(edited_state)

    assert "EMP1002" in result["write_result"]
    assert "PAYROLL" in result["write_result"]

    assert any(
        account["employee_id"] == "EMP1002"
        and account["system"] == "PAYROLL"
        for account in MOCK_ACCOUNTS.values()
    )

    print("PASS: edit-and-approve executes edited request")


def test_edit_without_approval_does_not_write():
    state = {
        "approval_status": "PENDING",
        "approval_request": {
            "employee_id": "EMP1001",
            "system": "HR_PORTAL",
            "idempotency_key": "edit-pending-key",
        },
        "approval_employee_id": "EMP1002",
        "approval_system": "PAYROLL",
    }

    result = execute_approved_write(state)

    assert result["write_result"] == ""

    print("PASS: edited request cannot write while pending")


if __name__ == "__main__":
    test_edit_and_approve()
    test_edit_without_approval_does_not_write()

    print()
    print("ALL EDIT-AND-APPROVE TESTS PASSED")