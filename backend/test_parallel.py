from app.parallel import (
    PARALLEL_SPECIALISTS,
    build_parallel_sends,
)


print("STEP 9A - PARALLEL SEND TEST")
print("----------------------------")


state = {
    "question": "I need help with my onboarding.",
}


print("\nTEST 1: EXPECTED SPECIALIST COUNT")

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


print("\nTEST 3: EACH SPECIALIST RECEIVES THE QUESTION")

expected_question_fields = {
    "paperwork_specialist": "paperwork_question",
    "access_specialist": "access_question",
    "benefits_specialist": "benefits_question",
    "payroll_specialist": "payroll_question",
}

for send in sends:
    field_name = expected_question_fields[send.node]

    assert send.arg[field_name] == state["question"]

print("PASS")


print("\nTEST 4: EACH BRANCH USES ITS OWN STATE FIELD")

actual_fields = {
    field_name
    for send in sends
    for field_name in send.arg.keys()
}

expected_fields = {
    "paperwork_question",
    "access_question",
    "benefits_question",
    "payroll_question",
}

assert actual_fields == expected_fields

print("PASS")


print()
print("All Step 9A parallel Send tests passed.")