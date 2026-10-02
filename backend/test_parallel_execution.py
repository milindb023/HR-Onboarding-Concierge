import uuid

from app.graph import graph

THREAD_ID = f"step9-parallel-execution-test-{uuid.uuid4()}"
config = {"configurable": {"thread_id": THREAD_ID}}


print("STEP 9D - ACTUAL COMPILED GRAPH PARALLEL EXECUTION")
print("---------------------------------------------------")


print("\nTEST 1: PREPARE SUPERVISOR CHECKPOINT")

# Seed the actual compiled graph at the supervisor stage.
#
# We use update_state() so the test can start directly from the
# supervisor decision without invoking the Gemini classification node.
graph.update_state(
    config,
    {
        "question": "I need help with my onboarding.",
        "category": "PAPERWORK",
        "supervisor_route": "PAPERWORK",
        "delegation_count": 1,
        "specialist_findings": [],
    },
    as_node="supervisor",
)

snapshot = graph.get_state(config)

assert snapshot
assert snapshot.values["category"] == "PAPERWORK"
assert snapshot.values["supervisor_route"] == "PAPERWORK"

print("PASS")


print("\nTEST 2: VERIFY GRAPH IS READY FOR PARALLEL DISPATCH")

assert snapshot.next == ("parallel_dispatch",)

print("PASS")


print("\nTEST 3: EXECUTE REAL PARALLEL SPECIALIST BRANCHES")

# Stop immediately before the LLM agent node.
#
# This allows the real specialist branches and synthesizer to execute
# without making a Gemini API request.
events = list(
    graph.stream(
        None,
        config,
        interrupt_before=["agent"],
    )
)

assert events

print("PASS")


print("\nTEST 4: VERIFY ALL FOUR SPECIALIST FINDINGS WERE MERGED")

final_snapshot = graph.get_state(config)
values = final_snapshot.values
findings = values.get("specialist_findings", [])

assert len(findings) == 4
assert any("Paperwork specialist" in finding for finding in findings)
assert any("Access specialist" in finding for finding in findings)
assert any("Benefits specialist" in finding for finding in findings)
assert any("Payroll specialist" in finding for finding in findings)

print("PASS")


print("\nTEST 5: VERIFY SYNTHESIZER RECEIVED MERGED FINDINGS")

response = values.get("response", "")

assert response
assert "Paperwork specialist" in response
assert "Access specialist" in response
assert "Benefits specialist" in response
assert "Payroll specialist" in response

print("PASS")


print("\nTEST 6: VERIFY GRAPH IS INTERRUPTED BEFORE AGENT")

assert final_snapshot.next == ("agent",)

print("PASS")


print("\nTEST 7: VERIFY CHECKPOINTED STATE")

restored_snapshot = graph.get_state(config)

restored_findings = restored_snapshot.values.get(
    "specialist_findings",
    [],
)

assert len(restored_findings) == 4

assert restored_snapshot.values.get("response")

print("PASS")


print("\nMERGED SPECIALIST FINDINGS")
print("--------------------------")

for finding in restored_findings:
    print(f"- {finding}")


print("\nSYNTHESIZER RESPONSE")
print("--------------------")
print(restored_snapshot.values["response"])


print()
print("All Step 9D actual compiled graph tests passed.")