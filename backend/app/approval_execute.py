from typing import Any

from .provisioning import provision_system_account
from .state import HRState


def execute_approved_write(state: HRState) -> dict[str, Any]:
    """
    Execute the pending provisioning write only after explicit approval.

    The provisioning tool must never execute unless approval_status
    is explicitly APPROVED.
    """
    approval_status = state.get("approval_status", "").strip().upper()

    if approval_status != "APPROVED":
        return {
            "write_result": "",
        }

    approval_request = state.get("approval_request", {})

    employee_id = approval_request.get("employee_id", "").strip()
    system = approval_request.get("system", "").strip()
    idempotency_key = approval_request.get("idempotency_key", "").strip()

    if not employee_id or not system or not idempotency_key:
        return {
            "write_result": "Write blocked: incomplete approval request.",
        }

    result = provision_system_account.invoke(
        {
            "employee_id": employee_id,
            "system": system,
            "idempotency_key": idempotency_key,
        }
    )

    return {
        "write_result": result,
    }