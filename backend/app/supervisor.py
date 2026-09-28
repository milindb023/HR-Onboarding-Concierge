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
    """
    Decide which specialist should handle the request.

    The supervisor uses the already-classified category.
    No LLM call is made here.

    If the request has already reached the delegation limit,
    the supervisor returns FINISH.
    """

    delegation_count = state.get("delegation_count", 0)

    if delegation_count >= MAX_DELEGATIONS:
        return "FINISH"

    category = state.get("category")

    if category in ROUTING_TABLE:
        return ROUTING_TABLE[category]

    return "FINISH"