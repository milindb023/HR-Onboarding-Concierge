from typing import Any

from .state import HRState


def approval_complete_node(state: HRState) -> dict[str, Any]:
    """
    Complete the human approval workflow without invoking the LLM.

    APPROVED:
        The write has already been executed by approval_execute.

    DENIED:
        No write is executed.

    This node intentionally contains no LLM call.
    """
    status = state.get("approval_status", "").strip().upper()

    if status == "APPROVED":
        write_result = state.get("write_result", "").strip()

        if write_result:
            return {
                "response": write_result,
            }

        return {
            "response": (
                "The request was approved, but no provisioning result "
                "was recorded."
            ),
        }

    if status == "DENIED":
        return {
            "response": (
                "The requested system account provisioning was denied. "
                "No account was created."
            ),
            "write_result": "",
        }

    return {
        "response": (
            "The approval workflow could not be completed because "
            "the approval status is not valid."
        ),
    }