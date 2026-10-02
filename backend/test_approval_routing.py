from app.approval_routing import route_approval


print("STEP 11C-2A - APPROVAL ROUTING")
print("-------------------------------")


# ============================================================
# TEST 1 - APPROVED
# ============================================================

print("\nTEST 1: APPROVED")

state = {
    "approval_required": True,
    "approval_status": "APPROVED",
}

result = route_approval(state)

print("Route:", result)

assert result == "approved"

print("PASS")


# ============================================================
# TEST 2 - DENIED
# ============================================================

print("\nTEST 2: DENIED")

state = {
    "approval_required": True,
    "approval_status": "DENIED",
}

result = route_approval(state)

print("Route:", result)

assert result == "denied"

print("PASS")


# ============================================================
# TEST 3 - PENDING
# ============================================================

print("\nTEST 3: PENDING")

state = {
    "approval_required": True,
    "approval_status": "PENDING",
}

result = route_approval(state)

print("Route:", result)

assert result == "pending"

print("PASS")


# ============================================================
# TEST 4 - EMPTY STATUS
# ============================================================

print("\nTEST 4: EMPTY STATUS")

state = {
    "approval_required": True,
    "approval_status": "",
}

result = route_approval(state)

print("Route:", result)

assert result == "pending"

print("PASS")


# ============================================================
# TEST 5 - LOWERCASE APPROVED
# ============================================================

print("\nTEST 5: LOWERCASE APPROVED")

state = {
    "approval_required": True,
    "approval_status": "approved",
}

result = route_approval(state)

print("Route:", result)

assert result == "approved"

print("PASS")


# ============================================================
# TEST 6 - APPROVAL NOT REQUIRED
# ============================================================

print("\nTEST 6: APPROVAL NOT REQUIRED")

state = {
    "approval_required": False,
    "approval_status": "",
}

result = route_approval(state)

print("Route:", result)

assert result == "not_required"

print("PASS")


print("\nAll Step 11C-2A approval-routing tests passed.")