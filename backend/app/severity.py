from typing import Literal


Severity = Literal[
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]


SEVERITY_LEVELS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


WRITE_DRAFT_MIN_SEVERITY = "MEDIUM"


def should_create_write_draft(severity: str) -> bool:
    """
    Return True only when severity reaches the
    configured write-draft threshold.
    """

    normalized = severity.strip().upper()

    if normalized not in SEVERITY_LEVELS:
        return False

    return (
        SEVERITY_LEVELS[normalized]
        >= SEVERITY_LEVELS[WRITE_DRAFT_MIN_SEVERITY]
    )