import hashlib
import json

from langchain_core.tools import tool


MOCK_ACCOUNTS: dict[str, dict[str, str]] = {}


def build_idempotency_key(
    thread_id: str,
    content: dict[str, str],
) -> str:
    """
    Create a deterministic idempotency key from
    thread_id + write content.
    """

    normalized_content = json.dumps(
        content,
        sort_keys=True,
        separators=(",", ":"),
    )

    raw_value = f"{thread_id}:{normalized_content}"

    return hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()


@tool
def provision_system_account(
    employee_id: str,
    system: str,
    idempotency_key: str,
) -> str:
    """
    Provision a mock system account.

    The idempotency key prevents the same logical request
    from creating duplicate accounts.
    """

    employee_id = employee_id.strip()
    system = system.strip()

    if not employee_id:
        return "Provisioning failed: employee ID is required."

    if not system:
        return "Provisioning failed: system is required."

    if not idempotency_key:
        return "Provisioning failed: idempotency key is required."

    existing_account = MOCK_ACCOUNTS.get(idempotency_key)

    if existing_account:
        return (
            "Account already provisioned for this request. "
            f"Account ID: {existing_account['account_id']}"
        )

    account_id = f"ACC-{employee_id}-{system.upper()}"

    MOCK_ACCOUNTS[idempotency_key] = {
        "employee_id": employee_id,
        "system": system,
        "account_id": account_id,
        "status": "ACTIVE",
        "idempotency_key": idempotency_key,
    }

    return (
        f"System account provisioned successfully for "
        f"employee {employee_id}. "
        f"System: {system}. "
        f"Account ID: {account_id}"
    )