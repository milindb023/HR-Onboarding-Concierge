from .provisioning import provision_system_account
from .severity import can_provision


def request_provisioning(
    employee_id: str,
    severity: str,
) -> str:
    """
    Safely handle a provisioning request.

    Provisioning is allowed only when the severity gate permits it.
    The underlying provisioning tool remains idempotent.
    """

    if not can_provision(severity):
        return (
            f"Provisioning blocked for employee {employee_id}. "
            f"Severity '{severity}' does not permit provisioning."
        )

    return provision_system_account.invoke(
        {
            "employee_id": employee_id,
        }
    )