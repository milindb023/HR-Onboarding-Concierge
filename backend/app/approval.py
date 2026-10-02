from typing import Literal

ApprovalStatus = Literal[
    "PENDING",
    "APPROVED",
    "DENIED",
]


def create_approval_request(
    *,
    employee_id: str,
    system: str,
    severity: str,
    idempotency_key: str,
) -> dict[str, str]:
    return {
        "employee_id": employee_id,
        "system": system,
        "severity": severity,
        "idempotency_key": idempotency_key,
        "action": "PROVISION_SYSTEM_ACCOUNT",
        "status": "PENDING",
    }