from langchain_core.tools import tool


# Mock system-account store.
# This represents the external system that would normally
# receive the provisioning request.
MOCK_ACCOUNTS: dict[str, dict[str, str]] = {}


@tool
def provision_system_account(employee_id: str) -> str:
    """
    Provision a mock system account for an employee.

    The operation is idempotent: if an account already exists
    for the employee, no duplicate account is created.
    """
    employee_id = employee_id.strip()

    if not employee_id:
        return "Provisioning failed: employee ID is required."

    existing_account = MOCK_ACCOUNTS.get(employee_id)

    if existing_account:
        return (
            f"Account already provisioned for employee {employee_id}. "
            f"Account ID: {existing_account['account_id']}"
        )

    account_id = f"ACC-{employee_id}"

    MOCK_ACCOUNTS[employee_id] = {
        "employee_id": employee_id,
        "account_id": account_id,
        "status": "ACTIVE",
    }

    return (
        f"System account provisioned successfully for employee "
        f"{employee_id}. Account ID: {account_id}"
    )