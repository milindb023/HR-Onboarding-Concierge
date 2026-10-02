from .state import HRState
from .write_request import extract_write_request


def write_request_node(state: HRState) -> dict:
    question = state.get("question", "")

    request = extract_write_request(question)

    employee_id = request["employee_id"]
    requested_system = request["requested_system"]

    return {
        "employee_id": employee_id,
        "requested_system": requested_system,
        "write_request_valid": bool(
            employee_id and requested_system
        ),
    }