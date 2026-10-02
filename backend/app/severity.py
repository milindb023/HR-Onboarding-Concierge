from typing import Literal


Severity = Literal[
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]


# Provisioning is allowed only for requests that are
# explicitly classified as LOW or MEDIUM severity.
ALLOWED_PROVISIONING_SEVERITIES = {
    "LOW",
    "MEDIUM",
}


def can_provision(severity: str) -> bool:
    """
    Determine whether a request is allowed to proceed
    to the provisioning operation.
    """
    normalized = severity.strip().upper()

    return normalized in ALLOWED_PROVISIONING_SEVERITIES