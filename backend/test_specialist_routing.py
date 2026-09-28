from app.specialists import (
    paperwork_graph,
    access_graph,
    benefits_graph,
    payroll_graph,
)


def run_specialist(graph, category: str):
    result = graph.invoke(
        {
            "question": f"Test question for {category}",
            "category": category,
        }
    )

    assert result.get("response")
    assert result.get("specialist_findings")
    assert len(result["specialist_findings"]) == 1

    return result


print("STEP 7B - SPECIALIST ROUTING TEST")
print("---------------------------------")


print("TEST 1: PAPERWORK")
result = run_specialist(
    paperwork_graph,
    "PAPERWORK",
)
assert "Paperwork specialist" in result["specialist_findings"][0]
print("PASS")


print("TEST 2: ACCESS")
result = run_specialist(
    access_graph,
    "ACCESS",
)
assert "Access specialist" in result["specialist_findings"][0]
print("PASS")


print("TEST 3: BENEFITS")
result = run_specialist(
    benefits_graph,
    "BENEFITS",
)
assert "Benefits specialist" in result["specialist_findings"][0]
print("PASS")


print("TEST 4: PAYROLL")
result = run_specialist(
    payroll_graph,
    "PAYROLL",
)
assert "Payroll specialist" in result["specialist_findings"][0]
print("PASS")


print()
print("All Step 7B specialist routing tests passed.")