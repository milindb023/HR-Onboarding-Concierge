from app.graph import graph

print("STEP 9B - PARALLEL GRAPH INTEGRATION TEST")
print("------------------------------------------")

expected_nodes = {
    "supervisor",
    "parallel_dispatch",
    "paperwork_specialist",
    "access_specialist",
    "benefits_specialist",
    "payroll_specialist",
    "synthesizer",
}

actual_nodes = set(graph.nodes.keys())

print("\nTEST 1: REQUIRED PARALLEL NODES EXIST")

missing_nodes = expected_nodes - actual_nodes

assert not missing_nodes, (
    f"Missing graph nodes: {sorted(missing_nodes)}"
)

print("PASS")

print("\nTEST 2: ALL SPECIALIST NODES EXIST")

specialist_nodes = {
    "paperwork_specialist",
    "access_specialist",
    "benefits_specialist",
    "payroll_specialist",
}

assert specialist_nodes.issubset(actual_nodes)

print("PASS")

print("\nTEST 3: SYNTHESIZER EXISTS")

assert "synthesizer" in actual_nodes

print("PASS")

print("\nTEST 4: PARALLEL DISPATCH EXISTS")

assert "parallel_dispatch" in actual_nodes

print("PASS")

print()
print("All Step 9B parallel graph integration tests passed.")