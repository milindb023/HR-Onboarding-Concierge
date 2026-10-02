from typing import Literal


Severity = Literal[
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]


def determine_severity(question: str) -> Severity:
    normalized = question.strip().lower()

    critical_keywords = (
        "security breach",
        "data breach",
        "account compromised",
        "terminate all access",
    )

    high_keywords = (
        "urgent",
        "locked out",
        "cannot access",
        "payroll missing",
        "payroll failure",
        "security issue",
    )

    medium_keywords = (
    "provision",
    "access",
    "account",
    "portal",
    )

    if any(keyword in normalized for keyword in critical_keywords):
        return "CRITICAL"

    if any(keyword in normalized for keyword in high_keywords):
        return "HIGH"

    if any(keyword in normalized for keyword in medium_keywords):
        return "MEDIUM"

    return "LOW"