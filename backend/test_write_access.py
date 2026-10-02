from app.provisioning import (
    MOCK_ACCOUNTS,
    build_idempotency_key,
    provision_system_account,
)
from app.severity import should_create_write_draft
from app.write_access import prepare_write_draft


print("STEP 10E - GUIDE-ALIGNED WRITE ACCESS")
print("--------------------------------------")


print("\nTEST 1: LOW SEVERITY DOES NOT CREATE WRITE DRAFT")

result = prepare_write_draft(
    thread_id="thread-001",
    employee_id="EMP1001",
    system="HR_PORTAL",
    severity="LOW",
)

assert result["write_draft"] == {}
assert result["write_idempotency_key"] == ""

print("PASS")


print("\nTEST 2: MEDIUM SEVERITY CREATES WRITE DRAFT")

result = prepare_write_draft(
    thread_id="thread-001",
    employee_id="EMP1001",
    system="HR_PORTAL",
    severity="MEDIUM",
)

print(result)

assert result["write_draft"]["employee_id"] == "EMP1001"
assert result["write_draft"]["system"] == "HR_PORTAL"
assert result["write_draft"]["action"] == "PROVISION_SYSTEM_ACCOUNT"
assert result["write_draft"]["severity"] == "MEDIUM"
assert result["write_idempotency_key"]

print("PASS")


print("\nTEST 3: SAME THREAD + SAME CONTENT PRODUCES SAME KEY")

result1 = prepare_write_draft(
    thread_id="thread-001",
    employee_id="EMP1001",
    system="HR_PORTAL",
    severity="MEDIUM",
)

result2 = prepare_write_draft(
    thread_id="thread-001",
    employee_id="EMP1001",
    system="HR_PORTAL",
    severity="MEDIUM",
)

assert (
    result1["write_idempotency_key"]
    == result2["write_idempotency_key"]
)

print("PASS")


print("\nTEST 4: DIFFERENT THREAD PRODUCES DIFFERENT KEY")

result3 = prepare_write_draft(
    thread_id="thread-002",
    employee_id="EMP1001",
    system="HR_PORTAL",
    severity="MEDIUM",
)

assert (
    result1["write_idempotency_key"]
    != result3["write_idempotency_key"]
)

print("PASS")


print("\nTEST 5: DIFFERENT CONTENT PRODUCES DIFFERENT KEY")

result4 = prepare_write_draft(
    thread_id="thread-001",
    employee_id="EMP1001",
    system="PAYROLL",
    severity="MEDIUM",
)

assert (
    result1["write_idempotency_key"]
    != result4["write_idempotency_key"]
)

print("PASS")


print("\nTEST 6: SAME REQUEST WRITES ONLY ONCE")

MOCK_ACCOUNTS.clear()

draft = prepare_write_draft(
    thread_id="thread-001",
    employee_id="EMP1001",
    system="HR_PORTAL",
    severity="MEDIUM",
)

key = draft["write_idempotency_key"]

first_write = provision_system_account.invoke(
    {
        "employee_id": "EMP1001",
        "system": "HR_PORTAL",
        "idempotency_key": key,
    }
)

second_write = provision_system_account.invoke(
    {
        "employee_id": "EMP1001",
        "system": "HR_PORTAL",
        "idempotency_key": key,
    }
)

print(first_write)
print(second_write)

assert "provisioned successfully" in first_write
assert "already provisioned" in second_write
assert len(MOCK_ACCOUNTS) == 1

print("PASS")


print("\nTEST 7: HIGH SEVERITY CREATES WRITE DRAFT")

assert should_create_write_draft("HIGH") is True

print("PASS")


print("\nTEST 8: CRITICAL SEVERITY CREATES WRITE DRAFT")

assert should_create_write_draft("CRITICAL") is True

print("PASS")


print("\nTEST 9: UNKNOWN SEVERITY DOES NOT CREATE WRITE DRAFT")

assert should_create_write_draft("UNKNOWN") is False

print("PASS")


print()
print("All Step 10E write-access tests passed.")