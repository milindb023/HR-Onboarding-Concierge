from app.specialists import (
    paperwork_graph,
    access_graph,
    benefits_graph,
    payroll_graph,
)


# ============================================================
# TEST 1 - PAPERWORK SPECIALIST
# ============================================================

result = paperwork_graph.invoke(
    {
        "paperwork_question": "Which onboarding documents are required?",
        "category": "PAPERWORK",
    }
)

assert len(result["specialist_findings"]) == 1
assert "Paperwork specialist" in result["specialist_findings"][0]

print("TEST 1: paperwork specialist")
print("PASS")


# ============================================================
# TEST 2 - ACCESS SPECIALIST
# ============================================================

result = access_graph.invoke(
    {
        "access_question": "I need access to the HR portal.",
        "category": "ACCESS",
    }
)

assert len(result["specialist_findings"]) == 1
assert "Access specialist" in result["specialist_findings"][0]

print("TEST 2: access specialist")
print("PASS")


# ============================================================
# TEST 3 - BENEFITS SPECIALIST
# ============================================================

result = benefits_graph.invoke(
    {
        "benefits_question": "How do I enroll in benefits?",
        "category": "BENEFITS",
    }
)

assert len(result["specialist_findings"]) == 1
assert "Benefits specialist" in result["specialist_findings"][0]

print("TEST 3: benefits specialist")
print("PASS")


# ============================================================
# TEST 4 - PAYROLL SPECIALIST
# ============================================================

result = payroll_graph.invoke(
    {
        "payroll_question": "When will my first salary be processed?",
        "category": "PAYROLL",
    }
)

assert len(result["specialist_findings"]) == 1
assert "Payroll specialist" in result["specialist_findings"][0]

print("TEST 4: payroll specialist")
print("PASS")


print("\nAll Step 7 specialist subgraph tests passed.")