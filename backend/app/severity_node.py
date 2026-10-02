from .state import HRState
from .write_policy import determine_severity


def severity_node(state: HRState) -> dict[str, str]:
    question = state.get("question", "")

    severity = determine_severity(question)

    return {
        "severity": severity,
    }