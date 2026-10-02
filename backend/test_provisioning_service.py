from app.provisioning import MOCK_ACCOUNTS
from app.provisioning_service import request_provisioning


print("STEP 10C - SAFE PROVISIONING SERVICE")
print("--------------------------------------")


MOCK_ACCOUNTS.clear()


print("\nTEST 1: LOW SEVERITY CAN PROVISION")

result = request_provisioning(
    employee_id="EMP1001",
    severity="LOW",
)

print(result)

assert "provisioned successfully" in result
assert "EMP1001" in MOCK_ACCOUNTS

print("PASS")


print("\nTEST 2: HIGH SEVERITY CANNOT PROVISION")

result = request_provisioning(
    employee_id="EMP1002",
    severity="HIGH",
)

print(result)

assert "Provisioning blocked" in result
assert "EMP1002" not in MOCK_ACCOUNTS

print("PASS")


print("\nTEST 3: CRITICAL SEVERITY CANNOT PROVISION")

result = request_provisioning(
    employee_id="EMP1003",
    severity="CRITICAL",
)

print(result)

assert "Provisioning blocked" in result
assert "EMP1003" not in MOCK_ACCOUNTS

print("PASS")


print("\nTEST 4: MEDIUM SEVERITY CAN PROVISION")

result = request_provisioning(
    employee_id="EMP1002",
    severity="MEDIUM",
)

print(result)

assert "provisioned successfully" in result
assert "EMP1002" in MOCK_ACCOUNTS

print("PASS")


print("\nTEST 5: REPEATED ALLOWED REQUEST IS IDEMPOTENT")

result = request_provisioning(
    employee_id="EMP1001",
    severity="LOW",
)

print(result)

assert "already provisioned" in result
assert len(MOCK_ACCOUNTS) == 2

print("PASS")


print("\nTEST 6: UNKNOWN SEVERITY CANNOT PROVISION")

result = request_provisioning(
    employee_id="EMP1004",
    severity="UNKNOWN",
)

print(result)

assert "Provisioning blocked" in result
assert "EMP1004" not in MOCK_ACCOUNTS

print("PASS")


print()
print("All Step 10C provisioning-service tests passed.")