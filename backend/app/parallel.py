from langgraph.constants import Send

from .state import HRState


PARALLEL_SPECIALISTS = (
    "PAPERWORK",
    "ACCESS",
    "BENEFITS",
    "PAYROLL",
)


SPECIALIST_INPUT_FIELDS = {
    "PAPERWORK": "paperwork_question",
    "ACCESS": "access_question",
    "BENEFITS": "benefits_question",
    "PAYROLL": "payroll_question",
}


def build_parallel_sends(state: HRState) -> list[Send]:
    """
    Build parallel specialist tasks for the current HR request.

    Each specialist receives the question through its own
    branch-specific state field. This prevents concurrent writes
    to the shared question field.
    """

    question = state["question"]

    return [
        Send(
            specialist.lower() + "_specialist",
            {
                SPECIALIST_INPUT_FIELDS[specialist]: question,
            },
        )
        for specialist in PARALLEL_SPECIALISTS
    ]