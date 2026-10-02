from app.parallel import (
    PARALLEL_SPECIALISTS,
    build_parallel_sends,
)


print("STEP 9A - PARALLEL SEND TEST")
print("----------------------------")


print("\nTEST 1: EXPECTED SPECIALIST COUNT")

state = {
    "question": "I need help with my onboarding.",
}

sends = build_parallel_sends(state)

assert len(sends) == 4

print("PASS")


print("\nTEST 2: ALL SPECIALISTS ARE INCLUDED")

targets = {
    send.node
    for send in sends
}

expected_targets = {
    "paperwork_specialist",
    "access_specialist",
    "benefits_specialist",
    "payroll_specialist",
}

assert targets == expected_targets

print("PASS")


print("\nTEST 3: EACH SEND PRESERVES THE QUESTION")

for send in sends:
    assert send.arg["question"] == state["question"]

print("PASS")


print("\nTEST 4: EACH SEND CONTAINS THE SPECIALIST CATEGORY")

categories = {
    send.arg["category"]
    for send in sends
}

assert categories == set(PARALLEL_SPECIALISTS)

print("PASS")


print()
print("All Step 9A parallel Send tests passed.")