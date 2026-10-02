from .state import HRState


def synthesizer_node(state: HRState) -> dict:
    """
    Combine findings returned by parallel specialist subgraphs.
    """

    findings = state.get("specialist_findings", [])

    if not findings:
        return {
            "response": "No specialist findings were available."
        }

    combined = "\n".join(
        f"- {finding}"
        for finding in findings
    )

    return {
        "response": (
            "The following specialist findings were gathered "
            "for your onboarding request:\n"
            f"{combined}"
        )
    }