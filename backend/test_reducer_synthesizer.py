from app.state import HRState
from app.synthesizer import synthesizer_node


print("STEP 9C - REDUCER / SYNTHESIZER TEST")
print("------------------------------------")


print("\nTEST 1: MULTIPLE SPECIALIST FINDINGS ARE ACCUMULATED")

first_findings = [
    "Paperwork specialist reviewed identity documents."
]

second_findings = [
    "Access specialist reviewed HR portal access."
]

# Simulate the reducer behavior:
# Annotated[list[str], operator.add]
combined_findings = first_findings + second_findings

assert combined_findings == [
    "Paperwork specialist reviewed identity documents.",
    "Access specialist reviewed HR portal access.",
]

assert len(combined_findings) == 2

print("PASS")


print("\nTEST 2: FINDINGS FROM ALL FOUR SPECIALISTS ARE PRESERVED")

specialist_batches = [
    ["Paperwork specialist finding"],
    ["Access specialist finding"],
    ["Benefits specialist finding"],
    ["Payroll specialist finding"],
]

all_findings = []

for batch in specialist_batches:
    all_findings = all_findings + batch

assert len(all_findings) == 4

assert all_findings == [
    "Paperwork specialist finding",
    "Access specialist finding",
    "Benefits specialist finding",
    "Payroll specialist finding",
]

print("PASS")


print("\nTEST 3: SYNTHESIZER RECEIVES ALL FINDINGS")

state: HRState = {
    "question": "I need help with onboarding.",
    "specialist_findings": all_findings,
}

result = synthesizer_node(state)

assert result.get("response")
assert "Paperwork specialist finding" in result["response"]
assert "Access specialist finding" in result["response"]
assert "Benefits specialist finding" in result["response"]
assert "Payroll specialist finding" in result["response"]

print("PASS")


print("\nTEST 4: SYNTHESIZER HANDLES EMPTY FINDINGS")

empty_state: HRState = {
    "question": "Test request.",
    "specialist_findings": [],
}

empty_result = synthesizer_node(empty_state)

assert empty_result["response"] == (
    "No specialist findings were available."
)

print("PASS")


print()
print("All Step 9C reducer/synthesizer tests passed.")