from app.approval_node import approval_request_node


print("STEP 11A - APPROVAL REQUEST NODE")
print("--------------------------------")


# TEST 1: Valid write draft creates pending approval
state = {
    "write_draft": {
        "employee_id": "EMP1001",
        "system": "HR_PORTAL",
        "action": "PROVISION_SYSTEM_ACCOUNT",
        "severity": "MEDIUM",
    },
    "write_idempotency_key": "test-key-001",
}

result = approval_request_node(state)

print("\nTEST 1: VALID WRITE DRAFT")
print(result)

assert result["approval_required"] is True
assert result["approval_status"] == "PENDING"
assert result["approval_id"] == "test-key-001"
assert result["approval_request"]["employee_id"] == "EMP1001"
assert result["approval_request"]["system"] == "HR_PORTAL"
assert result["approval_request"]["severity"] == "MEDIUM"
assert result["approval_request"]["status"] == "PENDING"

print("PASS")


# TEST 2: Empty write draft must not create approval
state = {
    "write_draft": {},
    "write_idempotency_key": "",
}

result = approval_request_node(state)

print("\nTEST 2: EMPTY WRITE DRAFT")
print(result)

assert result["approval_required"] is False
assert result["approval_status"] == ""
assert result["approval_request"] == {}
assert result["approval_id"] == ""

print("PASS")


# TEST 3: Missing idempotency key must not create approval
state = {
    "write_draft": {
        "employee_id": "EMP1001",
        "system": "HR_PORTAL",
        "action": "PROVISION_SYSTEM_ACCOUNT",
        "severity": "MEDIUM",
    },
    "write_idempotency_key": "",
}

result = approval_request_node(state)

print("\nTEST 3: MISSING IDEMPOTENCY KEY")
print(result)

assert result["approval_required"] is False
assert result["approval_request"] == {}

print("PASS")


print("\nAll Step 11A approval-request tests passed.")