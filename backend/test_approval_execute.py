from app.approval_execute import execute_approved_write
from app.provisioning import MOCK_ACCOUNTS


print("STEP 11C - APPROVAL EXECUTION GATE")
print("----------------------------------")


def clear_test_account(key: str) -> None:
    MOCK_ACCOUNTS.pop(key, None)


approval_request = {
    "employee_id": "EMP1001",
    "system": "HR_PORTAL",
    "severity": "MEDIUM",
    "idempotency_key": "step11c-test-key",
    "action": "PROVISION_SYSTEM_ACCOUNT",
    "status": "PENDING",
}


# ---------------------------------------------------------
# TEST 1 - PENDING MUST NOT WRITE
# ---------------------------------------------------------

clear_test_account("step11c-test-key")

state = {
    "approval_status": "PENDING",
    "approval_request": approval_request,
}

result = execute_approved_write(state)

print("\nTEST 1: PENDING APPROVAL")
print(result)

assert result["write_result"] == ""
assert "step11c-test-key" not in MOCK_ACCOUNTS

print("PASS")


# ---------------------------------------------------------
# TEST 2 - DENIED MUST NOT WRITE
# ---------------------------------------------------------

clear_test_account("step11c-test-key")

state = {
    "approval_status": "DENIED",
    "approval_request": approval_request,
}

result = execute_approved_write(state)

print("\nTEST 2: DENIED APPROVAL")
print(result)

assert result["write_result"] == ""
assert "step11c-test-key" not in MOCK_ACCOUNTS

print("PASS")


# ---------------------------------------------------------
# TEST 3 - APPROVED MUST WRITE
# ---------------------------------------------------------

clear_test_account("step11c-test-key")

state = {
    "approval_status": "APPROVED",
    "approval_request": approval_request,
}

result = execute_approved_write(state)

print("\nTEST 3: APPROVED REQUEST")
print(result)

assert "provisioned successfully" in result["write_result"]
assert "step11c-test-key" in MOCK_ACCOUNTS

account = MOCK_ACCOUNTS["step11c-test-key"]

assert account["employee_id"] == "EMP1001"
assert account["system"] == "HR_PORTAL"
assert account["status"] == "ACTIVE"

print("PASS")


# ---------------------------------------------------------
# TEST 4 - APPROVED REQUEST WITH MISSING DATA
# ---------------------------------------------------------

state = {
    "approval_status": "APPROVED",
    "approval_request": {
        "employee_id": "EMP1001",
        "system": "",
        "idempotency_key": "step11c-invalid-key",
    },
}

result = execute_approved_write(state)

print("\nTEST 4: INCOMPLETE APPROVED REQUEST")
print(result)

assert "Write blocked" in result["write_result"]
assert "step11c-invalid-key" not in MOCK_ACCOUNTS

print("PASS")


print("\nAll Step 11C approval-execution tests passed.")