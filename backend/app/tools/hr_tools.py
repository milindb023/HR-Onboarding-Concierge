from langchain_core.tools import tool


MOCK_EMPLOYEES = {
    "EMP1001": {
        "employee_id": "EMP1001",
        "name": "Amit Sharma",
        "department": "Engineering",
        "joining_date": "2026-09-15",
        "onboarding_status": "IN_PROGRESS",
    },
    "EMP1002": {
        "employee_id": "EMP1002",
        "name": "Priya Patil",
        "department": "Finance",
        "joining_date": "2026-09-01",
        "onboarding_status": "COMPLETED",
    },
}


@tool
def lookup_employee(employee_id: str) -> str:
    """Look up mock HR employee information using an employee ID."""

    employee = MOCK_EMPLOYEES.get(employee_id)

    if not employee:
        return f"No employee found for employee ID: {employee_id}"

    return str(employee)


MOCK_POLICIES = {
    "onboarding_documents": (
        "New employees must submit identity proof, "
        "tax declaration, bank details, and required employment forms."
    ),
    "hr_portal_access": (
        "HR portal access is normally provisioned during onboarding "
        "after the employee record is created."
    ),
    "benefits_enrollment": (
        "Employees should complete benefits enrollment within the "
        "enrollment period communicated by HR."
    ),
    "payroll": (
        "Payroll processing depends on successful employee setup, "
        "bank details, and the applicable payroll cutoff."
    ),
}


@tool
def search_hr_policy(topic: str) -> str:
    """Search the mock HR policy knowledge base for onboarding information."""

    topic_key = topic.lower().strip()

    for key, policy in MOCK_POLICIES.items():
        if topic_key in key or key in topic_key:
            return policy

    return (
        "No matching HR policy was found in the mock policy knowledge base."
    )