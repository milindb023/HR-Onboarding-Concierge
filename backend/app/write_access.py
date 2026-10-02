from typing import Any

from .provisioning import build_idempotency_key
from .severity import should_create_write_draft


def prepare_write_draft(
    *,
    thread_id: str,
    employee_id: str,
    system: str,
    severity: str,
) -> dict[str, Any]:
    """
    Prepare a gated write draft.

    No write draft is created when severity is below
    the configured threshold.
    """

    if not should_create_write_draft(severity):
        return {
            "write_draft": {},
            "write_idempotency_key": "",
        }

    content = {
        "employee_id": employee_id,
        "system": system,
        "action": "PROVISION_SYSTEM_ACCOUNT",
    }

    idempotency_key = build_idempotency_key(
        thread_id,
        content,
    )

    return {
        "write_draft": {
            "employee_id": employee_id,
            "system": system,
            "action": "PROVISION_SYSTEM_ACCOUNT",
            "severity": severity.strip().upper(),
        },
        "write_idempotency_key": idempotency_key,
    }