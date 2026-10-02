from typing import Any

from langchain_core.runnables import RunnableConfig

from .state import HRState
from .write_access import prepare_write_draft


def write_draft_node(
    state: HRState,
    config: RunnableConfig,
) -> dict[str, Any]:
    configurable = config.get("configurable", {})
    thread_id = configurable.get("thread_id")

    employee_id = state.get("employee_id", "").strip()
    requested_system = state.get("requested_system", "").strip()
    severity = state.get("severity", "").strip()

    if not thread_id:
        return {
            "write_draft": {},
            "write_idempotency_key": "",
        }

    if not employee_id or not requested_system:
        return {
            "write_draft": {},
            "write_idempotency_key": "",
        }

    return prepare_write_draft(
        thread_id=thread_id,
        employee_id=employee_id,
        system=requested_system,
        severity=severity,
    )