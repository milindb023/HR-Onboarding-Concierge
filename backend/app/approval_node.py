from typing import Any

from .state import HRState
from .approval import create_approval_request


def approval_request_node(state: HRState) -> dict[str, Any]:
    write_draft = state.get("write_draft", {})
    idempotency_key = state.get("write_idempotency_key", "")

    if not write_draft or not idempotency_key:
        return {
            "approval_required": False,
            "approval_status": "",
            "approval_request": {},
            "approval_id": "",
        }

    approval_request = create_approval_request(
        employee_id=write_draft["employee_id"],
        system=write_draft["system"],
        severity=write_draft["severity"],
        idempotency_key=idempotency_key,
    )

    return {
        "approval_required": True,
        "approval_status": "PENDING",
        "approval_request": approval_request,
        "approval_id": idempotency_key,
    }