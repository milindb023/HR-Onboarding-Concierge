from langgraph.constants import Send

from .state import HRState


PARALLEL_SPECIALISTS = (
    "PAPERWORK",
    "ACCESS",
    "BENEFITS",
    "PAYROLL",
)


def build_parallel_sends(state: HRState) -> list[Send]:
    """
    Build parallel specialist tasks for the current HR request.

    Each Send carries the same request to one specialist.
    Specialist findings are later combined through the
    specialist_findings reducer in HRState.
    """

    question = state["question"]

    return [
        Send(
            specialist.lower() + "_specialist",
            {
                "question": question,
                "category": specialist,
            },
        )
        for specialist in PARALLEL_SPECIALISTS
    ]