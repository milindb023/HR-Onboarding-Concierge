from dataclasses import dataclass
import re


@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    reason: str = ""


# Common prompt-injection patterns.
PROMPT_INJECTION_PATTERNS = [
    r"\bignore\s+(all\s+)?previous\s+instructions\b",
    r"\bignore\s+(all\s+)?prior\s+instructions\b",
    r"\bdisregard\s+(all\s+)?previous\s+instructions\b",
    r"\bforget\s+(all\s+)?previous\s+instructions\b",
    r"\breveal\s+(the\s+)?system\s+prompt\b",
    r"\bshow\s+(me\s+)?(the\s+)?system\s+prompt\b",
    r"\bprint\s+(the\s+)?system\s+prompt\b",
    r"\breveal\s+(your\s+)?instructions\b",
    r"\bshow\s+(your\s+)?instructions\b",
    r"\bact\s+as\s+(a\s+)?different\s+assistant\b",
    r"\bdeveloper\s+message\b",
]


# Common PII patterns relevant to an HR application.
PII_PATTERNS = {
    "email": re.compile(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        re.IGNORECASE,
    ),
    "phone": re.compile(
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
    ),
    "aadhaar": re.compile(
        r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)",
    ),
    "pan": re.compile(
        r"\b[A-Z]{5}\d{4}[A-Z]\b",
        re.IGNORECASE,
    ),
}


def detect_prompt_injection(text: str) -> bool:
    """Return True when the input contains a known prompt-injection pattern."""

    normalized_text = text.strip()

    return any(
        re.search(pattern, normalized_text, re.IGNORECASE)
        for pattern in PROMPT_INJECTION_PATTERNS
    )


def detect_pii(text: str) -> list[str]:
    """Return the types of PII detected in the input."""

    detected = []

    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            detected.append(pii_type)

    return detected


def evaluate_input(text: str) -> GuardrailResult:
    """
    Evaluate an employee request before it enters the agent workflow.

    Prompt injection is rejected.
    PII is rejected for this project because the Phase 3 agent
    should not unnecessarily process sensitive personal information.
    """

    if detect_prompt_injection(text):
        return GuardrailResult(
            allowed=False,
            reason="prompt_injection_detected",
        )

    pii_types = detect_pii(text)

    if pii_types:
        return GuardrailResult(
            allowed=False,
            reason=f"pii_detected:{','.join(pii_types)}",
        )

    return GuardrailResult(
        allowed=True,
        reason="safe",
    )