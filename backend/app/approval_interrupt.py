from typing import Any

from langgraph.types import interrupt

from .state import HRState


def approval_interrupt_node(state: HRState) -> dict[str, Any]:
    """
    Pause graph execution until a human explicitly approves, denies,
    or edits-and-approves the pending write request.

    No provisioning write is executed in this node.
    """

    if not state.get("approval_required", False):
        return {
            "approval_status": "",
        }

    approval_request = state.get("approval_request", {})
    current_status = state.get("approval_status", "").strip().upper()

    # If this node is resumed after a final approval decision,
    # do not interrupt again.
    if current_status in {"APPROVED", "DENIED"}:
        return {
            "approval_status": current_status,
        }

    human_response = interrupt(
        {
            "type": "WRITE_APPROVAL_REQUIRED",
            "approval_id": state.get("approval_id", ""),
            "request": approval_request,
            "message": (
                "Human approval is required before the system account "
                "can be provisioned."
            ),
            "allowed_actions": [
                "APPROVED",
                "DENIED",
                "EDIT_AND_APPROVE",
            ],
        }
    )

    if not isinstance(human_response, dict):
        return {
            "approval_status": "PENDING",
        }

    status = str(
        human_response.get("status", "PENDING")
    ).strip().upper()

    if status == "EDIT_AND_APPROVE":
        edited_employee_id = str(
            human_response.get(
                "employee_id",
                approval_request.get("employee_id", ""),
            )
        ).strip()

        edited_system = str(
            human_response.get(
                "system",
                approval_request.get("system", ""),
            )
        ).strip()

        if not edited_employee_id or not edited_system:
            return {
                "approval_status": "PENDING",
            }

        return {
            "approval_status": "APPROVED",
            "approval_employee_id": edited_employee_id,
            "approval_system": edited_system,
        }

    if status == "APPROVED":
        return {
            "approval_status": "APPROVED",
            "approval_employee_id": str(
                approval_request.get("employee_id", "")
            ).strip(),
            "approval_system": str(
                approval_request.get("system", "")
            ).strip(),
        }

    if status == "DENIED":
        return {
            "approval_status": "DENIED",
        }

    return {
        "approval_status": "PENDING",
    }