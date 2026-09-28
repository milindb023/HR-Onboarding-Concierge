from app.graph import graph


print("STEP 7B - MASTER GRAPH STRUCTURE TEST")
print("-------------------------------------")


expected_nodes = {
    "guardrail",
    "classify",
    "paperwork_specialist",
    "access_specialist",
    "benefits_specialist",
    "payroll_specialist",
    "agent",
    "tools",
    "escalate",
}


actual_nodes = set(graph.nodes.keys())


print("\nEXPECTED NODES")
for node in sorted(expected_nodes):
    print(f" - {node}")


print("\nACTUAL NODES")
for node in sorted(actual_nodes):
    print(f" - {node}")


print("\nTEST 1: all specialist nodes exist")

missing_nodes = expected_nodes - actual_nodes

assert not missing_nodes, (
    f"Missing graph nodes: {missing_nodes}"
)

print("PASS")


print("\nTEST 2: no expected node is missing")

assert expected_nodes.issubset(actual_nodes)

print("PASS")


print("\nTEST 3: specialist nodes are compiled into master graph")

specialist_nodes = {
    "paperwork_specialist",
    "access_specialist",
    "benefits_specialist",
    "payroll_specialist",
}

assert specialist_nodes.issubset(actual_nodes)

print("PASS")


print()
print("All Step 7B master graph structure tests passed.")
