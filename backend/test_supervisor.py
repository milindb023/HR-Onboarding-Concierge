from app.supervisor import (
    MAX_DELEGATIONS,
    supervisor_route,
)


def test_route(category: str, expected: str):
    state = {
        "category": category,
        "delegation_count": 0,
    }

    result = supervisor_route(state)

    assert result == expected

    print(
        f"PASS: {category} -> {result}"
    )


print("STEP 8A - SUPERVISOR ROUTING TEST")
print("--------------------------------")

print("\nTEST 1: PAPERWORK")
test_route("PAPERWORK", "PAPERWORK")

print("\nTEST 2: ACCESS")
test_route("ACCESS", "ACCESS")

print("\nTEST 3: BENEFITS")
test_route("BENEFITS", "BENEFITS")

print("\nTEST 4: PAYROLL")
test_route("PAYROLL", "PAYROLL")

print("\nTEST 5: UNKNOWN CATEGORY")
state = {
    "category": "UNKNOWN",
    "delegation_count": 0,
}

result = supervisor_route(state)

assert result == "FINISH"

print("PASS: UNKNOWN -> FINISH")

print("\nTEST 6: DELEGATION LIMIT")

state = {
    "category": "PAPERWORK",
    "delegation_count": MAX_DELEGATIONS,
}

result = supervisor_route(state)

assert result == "FINISH"

print(
    f"PASS: delegation_count={MAX_DELEGATIONS} -> FINISH"
)

print("\nTEST 7: ABOVE DELEGATION LIMIT")

state = {
    "category": "ACCESS",
    "delegation_count": MAX_DELEGATIONS + 1,
}

result = supervisor_route(state)

assert result == "FINISH"

print("PASS: delegation above limit -> FINISH")

print()
print("All Step 8A supervisor tests passed.")
