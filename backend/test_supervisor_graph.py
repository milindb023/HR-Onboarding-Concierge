from app.graph import graph
from app.supervisor import (
    MAX_DELEGATIONS,
    supervisor_node,
)


print("STEP 8B - SUPERVISOR GRAPH TEST")
print("--------------------------------")


print("\nTEST 1: SUPERVISOR NODE EXISTS")

assert "supervisor" in graph.nodes

print("PASS")


print("\nTEST 2: SPECIALIST NODES EXIST")

expected_specialists = {
    "paperwork_specialist",
    "access_specialist",
    "benefits_specialist",
    "payroll_specialist",
}

actual_nodes = set(graph.nodes.keys())

assert expected_specialists.issubset(actual_nodes)

print("PASS")


print("\nTEST 3: SUPERVISOR ROUTES PAPERWORK")

state = {
    "category": "PAPERWORK",
    "delegation_count": 0,
}

result = supervisor_node(state)

assert result["supervisor_route"] == "PAPERWORK"
assert result["delegation_count"] == 1

print("PASS")


print("\nTEST 4: SUPERVISOR ROUTES ACCESS")

state = {
    "category": "ACCESS",
    "delegation_count": 0,
}

result = supervisor_node(state)

assert result["supervisor_route"] == "ACCESS"
assert result["delegation_count"] == 1

print("PASS")


print("\nTEST 5: SUPERVISOR ROUTES BENEFITS")

state = {
    "category": "BENEFITS",
    "delegation_count": 0,
}

result = supervisor_node(state)

assert result["supervisor_route"] == "BENEFITS"
assert result["delegation_count"] == 1

print("PASS")


print("\nTEST 6: SUPERVISOR ROUTES PAYROLL")

state = {
    "category": "PAYROLL",
    "delegation_count": 0,
}

result = supervisor_node(state)

assert result["supervisor_route"] == "PAYROLL"
assert result["delegation_count"] == 1

print("PASS")


print("\nTEST 7: DELEGATION LIMIT")

state = {
    "category": "PAPERWORK",
    "delegation_count": MAX_DELEGATIONS,
}

result = supervisor_node(state)

assert result["supervisor_route"] == "FINISH"
assert "delegation_count" not in result

print("PASS")


print("\nTEST 8: UNKNOWN CATEGORY")

state = {
    "category": "UNKNOWN",
    "delegation_count": 0,
}

result = supervisor_node(state)

assert result["supervisor_route"] == "FINISH"

print("PASS")


print()
print("All Step 8B supervisor graph tests passed.")