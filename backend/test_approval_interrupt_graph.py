from app.graph import graph


THREAD_ID = "step-11b-interrupt-test-001"

config = {
    "configurable": {
        "thread_id": THREAD_ID,
    }
}


print("STEP 11B - COMPILED GRAPH INTERRUPT")
print("------------------------------------")


question = "Provision HR_PORTAL access for EMP1001"

print("\nStarting graph...")
print(f"Thread ID: {THREAD_ID}")
print(f"Question: {question}")


result = graph.invoke(
    {
        "question": question,
    },
    config=config,
)


print("\nGraph invocation returned.")
print("Result:")
print(result)


# The graph must stop at the approval interrupt.
assert "__interrupt__" in result, (
    "Expected graph execution to pause at interrupt(), "
    "but no __interrupt__ value was returned."
)

interrupts = result["__interrupt__"]

assert interrupts, "Expected at least one pending interrupt."

print("\nTEST 1: GRAPH PAUSED AT APPROVAL INTERRUPT - PASS")


# Inspect the interrupt payload.
interrupt_value = interrupts[0].value

print("\nInterrupt payload:")
print(interrupt_value)


assert interrupt_value["type"] == "WRITE_APPROVAL_REQUIRED"
assert interrupt_value["approval_id"]
assert interrupt_value["request"]["employee_id"] == "EMP1001"
assert interrupt_value["request"]["system"] == "HR_PORTAL"
assert interrupt_value["request"]["severity"] == "MEDIUM"
assert interrupt_value["request"]["status"] == "PENDING"

print("\nTEST 2: PENDING APPROVAL PAYLOAD IS CORRECT - PASS")


# The graph must have created a write draft before pausing.
state_values = result

assert state_values["write_draft"]["employee_id"] == "EMP1001"
assert state_values["write_draft"]["system"] == "HR_PORTAL"

print("\nTEST 3: WRITE DRAFT EXISTS BEFORE INTERRUPT - PASS")


# Most importantly, the actual provisioning result must not exist.
assert state_values.get("write_result", "") == ""

print("\nTEST 4: NO PROVISIONING WRITE EXECUTED - PASS")


print("\nAll Step 11B compiled-graph interrupt tests passed.")