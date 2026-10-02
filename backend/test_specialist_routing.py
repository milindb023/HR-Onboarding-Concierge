from app.specialists import (
    paperwork_graph,
    access_graph,
    benefits_graph,
    payroll_graph,
)


def run_specialist(graph, question_field: str, category: str):
    result = graph.invoke(
        {
            question_field: f"Test question for {category}",
            "category": category,
        }
    )

    assert result.get("specialist_findings")
    assert len(result["specialist_findings"]) == 1

    return result


print("STEP 9 - SPECIALIST SUBGRAPH ROUTING TEST")
print("------------------------------------------")

print("\nTEST 1: PAPERWORK SPECIALIST")
result = run_specialist(
    paperwork_graph,
    "paperwork_question",
    "PAPERWORK",
)
assert "Paperwork specialist" in result["specialist_findings"][0]
print("PASS")

print("\nTEST 2: ACCESS SPECIALIST")
result = run_specialist(
    access_graph,
    "access_question",
    "ACCESS",
)
assert "Access specialist" in result["specialist_findings"][0]
print("PASS")

print("\nTEST 3: BENEFITS SPECIALIST")
result = run_specialist(
    benefits_graph,
    "benefits_question",
    "BENEFITS",
)
assert "Benefits specialist" in result["specialist_findings"][0]
print("PASS")

print("\nTEST 4: PAYROLL SPECIALIST")
result = run_specialist(
    payroll_graph,
    "payroll_question",
    "PAYROLL",
)
assert "Payroll specialist" in result["specialist_findings"][0]
print("PASS")

print()
print("All Step 9 specialist subgraph routing tests passed.")