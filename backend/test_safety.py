from app.graph import should_continue, MAX_ITERATIONS, MAX_DUPLICATE_TOOL_CALLS


def test_no_tool_call_ends():
    state = {
        "messages": [],
        "iteration_count": 1,
        "tool_call_history": [],
    }

    assert should_continue(state) == "end"


def test_tool_call_continues():
    state = {
        "messages": [
            type(
                "FakeMessage",
                (),
                {
                    "tool_calls": [
                        {
                            "name": "lookup_employee",
                            "args": {
                                "employee_id": "EMP1001"
                            },
                        }
                    ]
                },
            )()
        ],
        "iteration_count": 1,
        "tool_call_history": [],
    }

    assert should_continue(state) == "tools"


def test_max_iterations_escalates():
    state = {
        "messages": [
            type(
                "FakeMessage",
                (),
                {
                    "tool_calls": [
                        {
                            "name": "lookup_employee",
                            "args": {
                                "employee_id": "EMP1001"
                            },
                        }
                    ]
                },
            )()
        ],
        "iteration_count": MAX_ITERATIONS,
        "tool_call_history": [],
    }

    assert should_continue(state) == "escalate"


def test_duplicate_tool_call_escalates():
    fingerprint = "lookup_employee:{'employee_id': 'EMP1001'}"

    state = {
        "messages": [
            type(
                "FakeMessage",
                (),
                {
                    "tool_calls": [
                        {
                            "name": "lookup_employee",
                            "args": {
                                "employee_id": "EMP1001"
                            },
                        }
                    ]
                },
            )()
        ],
        "iteration_count": 2,
        "tool_call_history": [
            fingerprint,
            fingerprint,
        ],
    }

    assert should_continue(state) == "escalate"


print("TEST 1: no tool call -> end")
test_no_tool_call_ends()
print("PASS")

print("TEST 2: tool call -> tools")
test_tool_call_continues()
print("PASS")

print("TEST 3: max iterations -> escalate")
test_max_iterations_escalates()
print("PASS")

print("TEST 4: duplicate tool call -> escalate")
test_duplicate_tool_call_escalates()
print("PASS")

print("\nAll Step 3 safety tests passed.")