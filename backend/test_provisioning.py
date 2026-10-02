from app.provisioning import MOCK_ACCOUNTS, provision_system_account


print("STEP 10A - MOCK PROVISIONING TOOL")
print("----------------------------------")


print("\nTEST 1: INITIAL ACCOUNT STORE IS EMPTY")

MOCK_ACCOUNTS.clear()

assert MOCK_ACCOUNTS == {}

print("PASS")


print("\nTEST 2: PROVISION NEW ACCOUNT")

result = provision_system_account.invoke(
    {
        "employee_id": "EMP1001",
    }
)

print(result)

assert "provisioned successfully" in result
assert "ACC-EMP1001" in result
assert "EMP1001" in MOCK_ACCOUNTS

print("PASS")


print("\nTEST 3: ACCOUNT STATE IS STORED")

account = MOCK_ACCOUNTS["EMP1001"]

assert account["employee_id"] == "EMP1001"
assert account["account_id"] == "ACC-EMP1001"
assert account["status"] == "ACTIVE"

print("PASS")


print("\nTEST 4: REPEATED PROVISIONING IS IDEMPOTENT")

result_again = provision_system_account.invoke(
    {
        "employee_id": "EMP1001",
    }
)

print(result_again)

assert "already provisioned" in result_again
assert "ACC-EMP1001" in result_again
assert len(MOCK_ACCOUNTS) == 1

print("PASS")


print("\nTEST 5: DIFFERENT EMPLOYEE GETS DIFFERENT ACCOUNT")

result = provision_system_account.invoke(
    {
        "employee_id": "EMP1002",
    }
)

print(result)

assert "provisioned successfully" in result
assert "ACC-EMP1002" in result
assert len(MOCK_ACCOUNTS) == 2

print("PASS")


print("\nTEST 6: EMPTY EMPLOYEE ID IS REJECTED")

result = provision_system_account.invoke(
    {
        "employee_id": "   ",
    }
)

print(result)

assert "employee ID is required" in result
assert len(MOCK_ACCOUNTS) == 2

print("PASS")


print()
print("All Step 10A provisioning tests passed.")