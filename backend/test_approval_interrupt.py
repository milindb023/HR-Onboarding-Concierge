from app.approval_interrupt import approval_interrupt_node


print("STEP 11B - APPROVAL INTERRUPT")
print("-----------------------------")


# TEST 1: No approval required -> no interrupt
state = {
    "approval_required": False,
    "approval_request": {},
    "approval_id": "",
}

result = approval_interrupt_node(state)

print("\nTEST 1: NO APPROVAL REQUIRED")
print(result)

assert result["approval_status"] == ""

print("PASS")


# TEST 2 is intentionally not executed directly.
#
# A valid approval request calls interrupt(), which pauses graph
# execution. The real pause/resume behavior will be tested through
# the compiled graph using the SQLite checkpointer.


print("\nTEST 2: VALID APPROVAL REQUEST")
print("Deferred to compiled-graph interrupt test.")

print("\nStep 11B node-level tests passed.")