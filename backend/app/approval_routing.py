from typing import Literal

from .state import HRState


ApprovalRoute = Literal[
    "approved",
    "denied",
    "pending",
    "not_required",
]


def route_approval(state: HRState) -> ApprovalRoute:
    """
    Route the graph based on the current human approval status.

    If no write approval is required, continue through the existing
    agent flow without entering a human approval loop.
    """
    if not state.get("approval_required", False):
        return "not_required"

    status = state.get("approval_status", "").strip().upper()

    if status == "APPROVED":
        return "approved"

    if status == "DENIED":
        return "denied"

    return "pending"