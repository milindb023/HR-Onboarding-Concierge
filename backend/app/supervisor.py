from typing import Literal

from .state import HRState


SupervisorRoute = Literal[
    "PAPERWORK",
    "ACCESS",
    "BENEFITS",
    "PAYROLL",
    "FINISH",
]


MAX_DELEGATIONS = 3


ROUTING_TABLE: dict[str, SupervisorRoute] = {
    "PAPERWORK": "PAPERWORK",
    "ACCESS": "ACCESS",
    "BENEFITS": "BENEFITS",
    "PAYROLL": "PAYROLL",
}


def supervisor_route(state: HRState) -> SupervisorRoute:
    if state.get("specialists_completed", False):
        return "FINISH"

    delegation_count = state.get("delegation_count", 0)

    if delegation_count >= MAX_DELEGATIONS:
        return "FINISH"

    category = state.get("category")

    if category in ROUTING_TABLE:
        return ROUTING_TABLE[category]

    return "FINISH"


def supervisor_node(state: HRState) -> dict:
    """
    Execute one supervisor decision.

    When a specialist is selected, increment the delegation count.
    FINISH does not create another delegation.
    """

    route = supervisor_route(state)

    delegation_count = state.get("delegation_count", 0)

    if route == "FINISH":
        return {
            "supervisor_route": route,
        }

    return {
        "supervisor_route": route,
        "delegation_count": delegation_count + 1,
    }