from typing import Any

from langgraph.types import interrupt

from .state import HRState


def approval_interrupt_node(state: HRState) -> dict[str, Any]:
    """
    Pause graph execution until a human explicitly approves or denies
    the pending write request.

    No provisioning write is executed in this node.
    """
    if not state.get("approval_required", False):
        return {
            "approval_status": "",
        }

    approval_request = state.get("approval_request", {})
    current_status = state.get("approval_status", "").strip().upper()

    # If this node is resumed after an approval decision, do not
    # interrupt again.
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
        }
    )

    if not isinstance(human_response, dict):
        return {
            "approval_status": "PENDING",
        }

    status = str(
        human_response.get("status", "PENDING")
    ).strip().upper()

    if status not in {"APPROVED", "DENIED"}:
        return {
            "approval_status": "PENDING",
        }

    return {
        "approval_status": status,
    }