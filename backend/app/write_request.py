from typing import Any


SUPPORTED_SYSTEMS = {
    "HR_PORTAL",
    "PAYROLL",
    "BENEFITS",
}


def extract_write_request(question: str) -> dict[str, Any]:
    """
    Extract the minimum information required for a provisioning write.

    Expected format examples:
      "Provision HR_PORTAL access for EMP1001"
      "Create PAYROLL account for employee EMP1002"
    """

    normalized = question.strip()

    if not normalized:
        return {
            "employee_id": "",
            "requested_system": "",
        }

    tokens = normalized.replace(",", " ").split()

    employee_id = ""
    requested_system = ""

    for token in tokens:
        candidate = token.strip().upper()

        if candidate.startswith("EMP") and candidate[3:].isdigit():
            employee_id = candidate

        if candidate in SUPPORTED_SYSTEMS:
            requested_system = candidate

    return {
        "employee_id": employee_id,
        "requested_system": requested_system,
    }