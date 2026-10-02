from app.provisioning import (
    MOCK_ACCOUNTS,
    build_idempotency_key,
    provision_system_account,
)


print("STEP 10F - PROVISIONING TOOL CONTRACT")
print("--------------------------------------")


MOCK_ACCOUNTS.clear()


print("\nTEST 1: MISSING EMPLOYEE ID IS REJECTED")

result = provision_system_account.invoke(
    {
        "employee_id": "",
        "system": "HR_PORTAL",
        "idempotency_key": "key-001",
    }
)

print(result)

assert "employee ID is required" in result
assert len(MOCK_ACCOUNTS) == 0

print("PASS")


print("\nTEST 2: MISSING SYSTEM IS REJECTED")

result = provision_system_account.invoke(
    {
        "employee_id": "EMP1001",
        "system": "",
        "idempotency_key": "key-001",
    }
)

print(result)

assert "system is required" in result
assert len(MOCK_ACCOUNTS) == 0

print("PASS")


print("\nTEST 3: MISSING IDEMPOTENCY KEY IS REJECTED")

result = provision_system_account.invoke(
    {
        "employee_id": "EMP1001",
        "system": "HR_PORTAL",
        "idempotency_key": "",
    }
)

print(result)

assert "idempotency key is required" in result
assert len(MOCK_ACCOUNTS) == 0

print("PASS")


print("\nTEST 4: VALID REQUEST CREATES ACCOUNT")

content = {
    "employee_id": "EMP1001",
    "system": "HR_PORTAL",
    "action": "PROVISION_SYSTEM_ACCOUNT",
}

key = build_idempotency_key(
    "thread-001",
    content,
)

result = provision_system_account.invoke(
    {
        "employee_id": "EMP1001",
        "system": "HR_PORTAL",
        "idempotency_key": key,
    }
)

print(result)

assert "provisioned successfully" in result
assert len(MOCK_ACCOUNTS) == 1

print("PASS")


print("\nTEST 5: SAME IDEMPOTENCY KEY DOES NOT DOUBLE-WRITE")

result = provision_system_account.invoke(
    {
        "employee_id": "EMP1001",
        "system": "HR_PORTAL",
        "idempotency_key": key,
    }
)

print(result)

assert "already provisioned" in result
assert len(MOCK_ACCOUNTS) == 1

print("PASS")


print("\nTEST 6: DIFFERENT IDEMPOTENCY KEY CREATES DIFFERENT WRITE")

different_key = build_idempotency_key(
    "thread-002",
    content,
)

result = provision_system_account.invoke(
    {
        "employee_id": "EMP1001",
        "system": "HR_PORTAL",
        "idempotency_key": different_key,
    }
)

print(result)

assert "provisioned successfully" in result
assert len(MOCK_ACCOUNTS) == 2

print("PASS")


print()
print("All Step 10F provisioning contract tests passed.")